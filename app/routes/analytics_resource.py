import locale
import os
from datetime import date, datetime, timedelta

import pytz
import sentry_sdk
from flask import Blueprint, Response, render_template, request
from flask_jwt_extended import jwt_required
from sqlalchemy import extract, func
from sqlalchemy.orm import joinedload
from weasyprint import HTML

from app.config.response_builder import ResponseBuilder
from app.extensions import db, limiter
from app.mapping import ResponseSchema
from app.models import Fecha, Gasto, Pago, Reserva
from app.utils.decorators import admin_required

# Definición del Blueprint
Analytics = Blueprint('Analytics', __name__)

@Analytics.route('/analytics', methods=['GET'])
@jwt_required()
@admin_required()
@limiter.limit("100 per minute") # Límite aumentado para la carga inicial del dashboard
def get_analytics():
    """
    Endpoint que calcula y devuelve métricas de contabilidad y tendencias.
    """
    # Instanciamos dentro para evitar errores de contexto
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        today = datetime.utcnow()
        mes_seleccionado = int(request.args.get('mes', today.month))
        anio_seleccionado = int(request.args.get('anio', today.year))

        # --- CÁLCULO DE GASTOS ---
        gastos_mes_seleccionado = db.session.query(func.sum(Gasto.monto)).filter(
            extract('year', Gasto.fecha) == anio_seleccionado,
            extract('month', Gasto.fecha) == mes_seleccionado
        ).scalar() or 0.0

        # --- CÁLCULO DE INGRESOS ---
        ingresos_mes_seleccionado = db.session.query(func.sum(Pago.monto)).filter(
            extract('year', Pago.fecha_pago) == anio_seleccionado,
            extract('month', Pago.fecha_pago) == mes_seleccionado
        ).scalar() or 0.0
        
        # --- CÁLCULO DE INGRESOS MES ANTERIOR (TENDENCIA) ---
        fecha_mes_seleccionado = date(anio_seleccionado, mes_seleccionado, 1)
        fecha_mes_anterior = (fecha_mes_seleccionado - timedelta(days=1)).replace(day=1)
        
        ingresos_mes_anterior = db.session.query(func.sum(Pago.monto)).filter(
            extract('year', Pago.fecha_pago) == fecha_mes_anterior.year,
            extract('month', Pago.fecha_pago) == fecha_mes_anterior.month
        ).scalar() or 0.0

        # --- LÓGICA DE RESERVAS Y GRÁFICOS ---
        # Nota: Usamos db.session.query para ser consistentes con los rollbacks
        reservas_confirmadas = db.session.query(Reserva).options(
            joinedload(Reserva.pagos),
            joinedload(Reserva.usuario)
        ).filter_by(estado='confirmada').all()
        
        total_a_liquidar = sum(reserva.saldo_restante for reserva in reservas_confirmadas)

        ingresos_por_mes_query = db.session.query(
            func.to_char(Pago.fecha_pago, 'YYYY-MM').label('mes'),
            func.sum(Pago.monto).label('ingresos_reales')
        ).filter(extract('year', Pago.fecha_pago) == anio_seleccionado).group_by('mes').order_by('mes').all()

        reservas_por_mes_query = db.session.query(
            func.to_char(Fecha.dia, 'YYYY-MM').label('mes'),
            func.count(Reserva.id).label('cantidad_reservas')
        ).join(Fecha).filter(
            Reserva.estado == 'confirmada',
            extract('year', Fecha.dia) == anio_seleccionado
        ).group_by('mes').all()
        
        stats_por_mes = {}
        for res in ingresos_por_mes_query:
            stats_por_mes[res.mes] = {"ingresos": float(res.ingresos_reales) if res.ingresos_reales else 0, "reservas": 0}
        
        for res in reservas_por_mes_query:
            if res.mes in stats_por_mes:
                stats_por_mes[res.mes]["reservas"] = res.cantidad_reservas
            else:
                stats_por_mes[res.mes] = {"ingresos": 0, "reservas": res.cantidad_reservas}
        
        ingresos_año_completo = {}
        for month in range(1, 13):
            month_key = f"{anio_seleccionado}-{month:02d}"
            ingresos_año_completo[month_key] = stats_por_mes.get(month_key, {"ingresos": 0, "reservas": 0})
        
        reservas_mes_seleccionado = ingresos_año_completo.get(f"{anio_seleccionado}-{mes_seleccionado:02d}", {}).get('reservas', 0)

        # --- TENDENCIA ---
        tendencia_ingresos = 0
        if ingresos_mes_anterior > 0:
            tendencia_ingresos = ((ingresos_mes_seleccionado - ingresos_mes_anterior) / ingresos_mes_anterior) * 100
        elif ingresos_mes_seleccionado > 0:
            tendencia_ingresos = 100
            
        # =====================================================================
        # LÓGICA PARA EL DESGLOSE DE GASTOS (Gráfico de Torta)
        # =====================================================================
        agrupados = db.session.query(
            Gasto.categoria.label('nombre_cat'), 
            func.sum(Gasto.monto).label('total')
        ).filter(
            extract('year', Gasto.fecha) == anio_seleccionado,
            extract('month', Gasto.fecha) == mes_seleccionado
        ).group_by(Gasto.categoria).all()

        PALETA_COLORES = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
        desglose_gastos = []
        for i, row in enumerate(agrupados):
            desglose_gastos.append({
                "name": getattr(row, 'nombre_cat', 'Otros') or "Otros",
                "value": float(row.total) if row.total else 0,
                "color": PALETA_COLORES[i % len(PALETA_COLORES)]
            })

        # =====================================================================
        # LÓGICA PARA LOS ÚLTIMOS MOVIMIENTOS (Feed lateral)
        # =====================================================================
        art_tz = pytz.timezone('America/Argentina/Buenos_Aires')
        movimientos_crudos = []
        
        # Función auxiliar para normalizar y evitar que las fechas puras (00:00) resten 3 horas
        def normalizar_fecha(d):
            if not d:
                return datetime.now(art_tz)
            if isinstance(d, date) and not isinstance(d, datetime):
                # Si es un Date puro (ej. Gastos), lo atamos directamente a la hora local a las 00:00
                return art_tz.localize(datetime.combine(d, datetime.min.time()))
            
            # Si es un Datetime (ej. Reservas), asumimos que viene en UTC de la BD
            if d.tzinfo is None:
                return pytz.utc.localize(d)
            return d
        
        # 1. Buscamos los 10 gastos más recientes
        gastos_recientes = db.session.query(Gasto).filter(
            extract('year', Gasto.fecha) == anio_seleccionado,
            extract('month', Gasto.fecha) == mes_seleccionado
        ).order_by(Gasto.fecha.desc()).limit(10).all()
        
        for g in gastos_recientes:
            cat = getattr(g, 'categoria', None) or getattr(g, 'concepto', None) or 'Otros'
            movimientos_crudos.append({
                "id": f"gasto_{g.id}",
                "type": "gasto",
                "text": f"Gasto registrado: {cat}",
                "amount": -float(g.monto),
                "raw_date": normalizar_fecha(g.fecha)
            })

        # 2. Buscamos las 10 reservas más recientes
        reservas_recientes = db.session.query(Reserva).filter(
            extract('year', Reserva.fecha_aceptacion) == anio_seleccionado,
            extract('month', Reserva.fecha_aceptacion) == mes_seleccionado
        ).order_by(Reserva.fecha_aceptacion.desc()).limit(10).all()
        
        for r in reservas_recientes:
            texto = f"Reserva {r.estado.capitalize()}"
            if r.usuario:
                texto += f": {r.usuario.nombre} {r.usuario.apellido}"
                
            tipo_mov = "ingreso" if r.estado == "confirmada" else "info"
            monto_mov = float(r.valor_alquiler) if r.estado == "confirmada" else None
            
            movimientos_crudos.append({
                "id": f"reserva_{r.id}",
                "type": tipo_mov,
                "text": texto,
                "amount": monto_mov,
                "raw_date": normalizar_fecha(r.fecha_aceptacion)
            })

        # 3. Ordenamos usando el objeto datetime real
        movimientos_crudos.sort(key=lambda x: x['raw_date'], reverse=True)
        
        # 4. Formateamos a la hora local
        ultimos_movimientos = []
        for m in movimientos_crudos[:7]:
            dt_local = m['raw_date'].astimezone(art_tz)
            
            # Si el registro no tiene hora exacta (es 00:00), mostramos solo la fecha
            if dt_local.hour == 0 and dt_local.minute == 0:
                str_date = dt_local.strftime('%d/%m')
            else:
                str_date = dt_local.strftime('%d/%m %H:%M')
            
            ultimos_movimientos.append({
                "id": m["id"],
                "type": m["type"],
                "text": m["text"],
                "amount": m["amount"],
                "date": str_date
            })

        # --- EMPAQUETADO FINAL DEL JSON ---
        data = {
            "ingresos_mes_seleccionado": ingresos_mes_seleccionado,
            "gastos_mes_seleccionado": gastos_mes_seleccionado,
            "beneficio_neto_mes": ingresos_mes_seleccionado - gastos_mes_seleccionado,
            "reservas_mes_seleccionado": reservas_mes_seleccionado,
            "tendencia_ingresos_porcentaje": round(tendencia_ingresos, 2),
            "dinero_por_liquidar": total_a_liquidar,
            "ingresos_por_mes": ingresos_año_completo,
            "desglose_gastos": desglose_gastos,         
            "ultimos_movimientos": ultimos_movimientos  
        }
        
        response_builder.add_message("Analíticas generadas con éxito").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200

    except Exception as e:
        db.session.rollback() 
        sentry_sdk.capture_exception(e)
        response_builder.add_message(f"Error al generar analíticas: {str(e)}").add_status_code(500)
        return response_schema.dump(response_builder.build()), 500


@Analytics.route('/analytics/reporte-pdf', methods=['GET'])
@jwt_required()
@admin_required()
def download_report():
    try:
        # Intento seguro de establecer locale para Docker
        try:
            locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')
        except locale.Error:
            locale.setlocale(locale.LC_ALL, 'C')

        art_tz = pytz.timezone('America/Argentina/Buenos_Aires')
        today_utc = datetime.utcnow()
        mes = int(request.args.get('mes', today_utc.month))
        anio = int(request.args.get('anio', today_utc.year))

        pagos_del_mes = db.session.query(Pago).filter(
            extract('year', Pago.fecha_pago) == anio,
            extract('month', Pago.fecha_pago) == mes
        ).order_by(Pago.fecha_pago).all()

        gastos_del_mes = db.session.query(Gasto).filter(
            extract('year', Gasto.fecha) == anio,
            extract('month', Gasto.fecha) == mes
        ).order_by(Gasto.fecha).all()

        total_ingresos = sum(p.monto for p in pagos_del_mes)
        total_gastos = sum(g.monto for g in gastos_del_mes)
        beneficio_neto = total_ingresos - total_gastos

        nombre_mes = date(anio, mes, 1).strftime('%B').capitalize()
        fecha_generacion_local = today_utc.replace(tzinfo=pytz.utc).astimezone(art_tz)
        fecha_generacion_formateada = fecha_generacion_local.strftime('%d/%m/%Y %H:%M:%S')

        def format_currency(value):
            try:
                return locale.currency(value, symbol=True, grouping=True)
            except:
                return f"${value:,.2f}"

        html_renderizado = render_template(
            'reporte_contable.html',
            mes=nombre_mes,
            anio=anio,
            fecha_generacion=fecha_generacion_formateada,
            total_ingresos=total_ingresos,
            total_gastos=total_gastos,
            beneficio_neto=beneficio_neto,
            pagos=pagos_del_mes,
            gastos=gastos_del_mes,
            format_currency=format_currency
        )

        pdf = HTML(string=html_renderizado).write_pdf()
        return Response(
            pdf,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment;filename=reporte_{nombre_mes.lower()}_{anio}.pdf'}
        )
    except Exception as e:
        db.session.rollback()
        sentry_sdk.capture_exception(e)
        return {"message": f"Error al generar el reporte: {str(e)}"}, 500