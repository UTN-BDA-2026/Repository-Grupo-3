import { FaTimes } from 'react-icons/fa'; // Ícono para el botón de cerrar
import './MiReserva.css';

const MiReserva = ({ reservas, onClose }) => {

    // Función para formatear la fecha de manera legible
    const formatDisplayDate = (isoDate) => {
        if (!isoDate) return 'Fecha no disponible';
        // Aseguramos que la fecha se interprete como UTC para evitar problemas de zona horaria
        const date = new Date(isoDate + 'T00:00:00Z');
        return new Intl.DateTimeFormat('es-ES', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            timeZone: 'UTC'
        }).format(date);
    };

    // Objeto para mapear los estados de la reserva a clases de CSS para los colores
    const statusClasses = {
        'pendiente': 'status-pendiente',
        'confirmada': 'status-confirmada',
        'cancelada': 'status-cancelada'
    };

    // --- LÓGICA DE FILTRADO ---
    // Filtramos las reservas para mostrar solo las futuras y las pasadas de hace menos de 15 días
    const reservasVisibles = reservas.filter(reserva => {
        // Validación básica por si falta el dato
        if (!reserva.fecha || !reserva.fecha.dia) return false;

        // Convertimos la fecha de la reserva 
        const fechaReserva = new Date(reserva.fecha.dia + 'T00:00:00');
        const hoy = new Date();

        // Calculamos la diferencia en milisegundos y la pasamos a días
        const diferenciaTiempo = hoy - fechaReserva;
        const diferenciaDias = diferenciaTiempo / (1000 * 3600 * 24);

        // Mantenemos si:
        // 1. Es futura (diferencia negativa)
        // 2. O si es pasada, que la diferencia sea menor o igual a 15 días
        return diferenciaDias <= 15;
    });

    return (
        <div className="mi-reserva-wrapper">
            <div className="mi-reserva-header">
                <h2 className="mi-reserva-title">Tus Reservas</h2>
                <button onClick={onClose} className="close-button">
                    <FaTimes />
                </button>
            </div>
            <div className="mi-reserva-grid">
                {/* Usamos reservasVisibles en lugar de reservas */}
                {reservasVisibles.length > 0 ? (
                    reservasVisibles.map(reserva => (
                        <div key={reserva.id} className="reserva-card-modern">
                            <div className="reserva-header">
                                <span className="reserva-date">{formatDisplayDate(reserva.fecha.dia)}</span>
                                <span className={`reserva-status ${statusClasses[reserva.estado] || ''}`}>
                                    {reserva.estado}
                                </span>
                            </div>
                            <div className="reserva-body">
                                <div className="reserva-info-item">
                                    <span className="info-label">Valor Total</span>
                                    <span className="info-value">${(reserva.valor_alquiler || 0).toLocaleString('es-AR')}</span>
                                </div>
                                <div className="reserva-info-item saldo">
                                    <span className="info-label">Saldo Pendiente</span>
                                    <span className="info-value">${(reserva.saldo_restante || 0).toLocaleString('es-AR')}</span>
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <p style={{ textAlign: 'center', color: '#666', gridColumn: '1 / -1' }}>
                        No tienes reservas recientes.
                    </p>
                )}
            </div>
        </div>
    );
};

export default MiReserva;