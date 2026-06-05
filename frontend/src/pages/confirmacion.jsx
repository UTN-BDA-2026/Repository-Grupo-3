import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './confirmacion.css';

// Componente con TU contrato original sin tocar ni una coma
const ContractTerms = () => (
  <>
    <h3>Términos y Condiciones</h3>
    <p>
      <strong>Contrato de Alquiler de Salón de Eventos.</strong>
    </p>
    <p>
      El presente contrato se celebra entre EL LOCADOR (propietario del salón) y EL LOCATARIO 
      (usuario que realiza la reserva a través de la página web, cuyos datos personales se 
      registran en el formulario de reserva), sujeto a las siguientes cláusulas:
    </p>
    
    <ol>
      <li>
        <strong>Objeto:</strong> EL LOCADOR alquila a EL LOCATARIO el salón de eventos 
        ubicado en Bolivar 1425, para uso exclusivo en la fecha y horario acordados en la reserva.
      </li>
      <li>
        <strong>Uso y Responsabilidad:</strong> EL LOCADOR no se responsabiliza por el tipo 
        de actividad o evento que se realice, siempre que sea lícito. Queda prohibida la venta 
        de entradas, la venta o suministro de alcohol a menores de edad, el consumo de 
        sustancias ilegales y cualquier actividad contraria a la ley. EL LOCATARIO es único 
        responsable por cualquier daño material, accidente o hecho ocurrido durante el evento, 
        así como de las acciones de los invitados y terceros que ingresen al salón.
      </li>
      <li>
        <strong>Cumplimiento Legal:</strong> EL LOCATARIO asume toda responsabilidad por cumplir 
        con las disposiciones legales vigentes en materia de seguridad, salubridad y control de 
        menores. En caso de incumplimiento, EL LOCADOR queda totalmente exento de toda 
        responsabilidad civil, penal o administrativa.
      </li>
      <li>
        <strong>Daños y Limpieza:</strong> EL LOCATARIO deberá restituir el salón en las mismas 
        condiciones en que lo recibió, siendo responsable por cualquier daño ocasionado a las 
        instalaciones, mobiliario o equipamiento. Los gastos de reparación o reposición correrán 
        por cuenta del LOCATARIO.
      </li>
      <li>
        <strong>Pagos y Cancelaciones:</strong> EL LOCATARIO deberá abonar la seña establecida 
        al momento de la reserva. En caso de cancelación, no 
        habrá devolución de la seña. En caso de cancelación por parte del LOCADOR por causas de 
        fuerza mayor, se reintegrará el monto abonado sin derecho a reclamos adicionales.
      </li>
      <li>
        <strong>Penalidades:</strong> En caso de incumplimiento de alguna cláusula, EL LOCADOR 
        podrá suspender el evento sin derecho a reclamo o reembolso, además de iniciar las 
        acciones legales correspondientes.
      </li>
      <li>
        <strong>Capacidad Base y Ajustes:</strong> El presente contrato se emite inicialmente bajo una estimación de <strong>40 personas</strong>. En caso de requerir una capacidad superior, EL LOCATARIO deberá coordinar con EL LOCADOR el ajuste de capacidad y precio final. El contrato definitivo con el valor legal final será enviado por correo electrónico una vez que EL LOCADOR confirme la reserva desde el panel de administración.
      </li>
      <li>
        <strong>Jurisdicción:</strong> Para cualquier conflicto legal derivado del presente, las partes se someten a la jurisdicción de los Tribunales Ordinarios de la Segunda Circunscripción Judicial de la Provincia de Mendoza, con asiento en la ciudad de San Rafael.
      </li>
      <li>
        <strong>Aceptación Digital:</strong> La aceptación del presente contrato mediante el 
        sistema de reservas online equivale a la firma manuscrita y constituye plena conformidad 
        legal por parte de EL LOCATARIO.
      </li>
      <li>
        <strong>Firma y Conformidad:</strong> Ambas partes declaran haber leído y comprendido 
        el presente contrato, aceptando las cláusulas aquí establecidas.
      </li>
    </ol>
  </>
);

function Confirmacion() {
  const { dateString } = useParams();
  const navigate = useNavigate();

  const [fechaInfo, setFechaInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  
  const [contractAccepted, setContractAccepted] = useState(false);
  const [receiptFile, setReceiptFile] = useState(null);

  // Estados para CVU y feedback de copiado
  const [paymentCVU, setPaymentCVU] = useState(null);
  const [copied, setCopied] = useState(false);

  // --- FUNCIÓN PARA COPIAR AL PORTAPAPELES ---
  const handleCopyCVU = () => {
    if (paymentCVU) {
      navigator.clipboard.writeText(paymentCVU)
        .then(() => {
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        })
        .catch(err => console.error("Error al copiar CVU: ", err));
    }
  };

  const formatDisplayDate = (isoDate) => {
    if (!isoDate) return '';
    const dateParts = isoDate.split('-');
    const date = new Date(Date.UTC(dateParts[0], dateParts[1] - 1, dateParts[2]));
    return date.toLocaleDateString('es-ES', {
      day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC'
    });
  };

  const displayDate = formatDisplayDate(dateString);

  useEffect(() => {
    const getPageData = async () => {
      setIsLoading(true);
      const token = localStorage.getItem('authToken');
      if (!token) { navigate('/login'); return; }

      try {
        const [fechaResponse, paymentResponse] = await Promise.all([
          fetch(`/api/v1/fecha/by-date/${dateString}`),
          fetch('/api/v1/payment-info', {
            headers: { 'Authorization': `Bearer ${token}` }
          })
        ]);

        const fechaResult = await fechaResponse.json();
        if (!fechaResponse.ok) throw new Error(fechaResult.message);
        
        if (fechaResult.data.estado !== 'disponible') {
          throw new Error('Esta fecha ya no está disponible.');
        }
        setFechaInfo(fechaResult.data);

        const paymentResult = await paymentResponse.json();
        if (!paymentResponse.ok) throw new Error(paymentResult.message);
        
        // Seteamos el CVU (o alias si la API aún no cambió el campo)
        setPaymentCVU(paymentResult.data.cvu || paymentResult.data.alias);

      } catch (err) {
        setError(err.message);
        setFechaInfo(null);
      } finally {
        setIsLoading(false);
      }
    };
    getPageData();
  }, [dateString, navigate]);

  const handleRequestReservation = async () => {
    if (!contractAccepted || !receiptFile) {
      setError('Debes aceptar los términos y subir el comprobante.');
      return;
    }
    const token = localStorage.getItem('authToken');
    setIsLoading(true);

    const formData = new FormData();
    formData.append('fecha_id', fechaInfo.id);
    formData.append('comprobante', receiptFile);
    formData.append('capacidad_declarada', 40);

    try {
      const response = await fetch('/api/v1/reserva/solicitar', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message);

      setMessage('¡Solicitud enviada con éxito! El administrador revisará tu comprobante y confirmará la capacidad final.');
      setTimeout(() => navigate('/'), 4000);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) return <div className="confirm-container"><p>Cargando información de la reserva...</p></div>;
  
  return (
    <div className="confirm-container">
      <div className="confirm-box">
        {fechaInfo ? (
          <>
            <h2>Solicitud de Reserva</h2>
            <p className="confirm-text">Fecha a solicitar:</p>
            <p className="confirm-date">{displayDate}</p>

            <div className="payment-info">
              <p>Realiza la transferencia al siguiente <strong>CVU</strong> y adjunta el comprobante:</p>
              
              {paymentCVU ? (
                <div className="cvu-copy-box">
                  <span className="cvu-number">{paymentCVU}</span>
                  <button 
                    type="button" 
                    className={`copy-button ${copied ? 'copied' : ''}`}
                    onClick={handleCopyCVU}
                  >
                    {copied ? '¡Copiado!' : 'Copiar CVU'}
                  </button>
                </div>
              ) : (
                <p>Cargando datos de pago...</p>
              )}
              
              <p className="payment-seña">SEÑA: 30% del valor estimado para iniciar el proceso.</p>
            </div>

            <div className="contract-box">
              <ContractTerms />
            </div>
            
            <div className="form-check">
              <input 
                type="checkbox" id="accept"
                checked={contractAccepted}
                onChange={() => setContractAccepted(!contractAccepted)}
              />
              <label htmlFor="accept">He leído y acepto los términos base del contrato.</label>
            </div>

            <div className="form-group">
              <label htmlFor="receipt">Subir Comprobante de Pago</label>
              <input 
                type="file" id="receipt"
                onChange={(e) => setReceiptFile(e.target.files[0])}
                accept="image/png, image/jpeg, application/pdf"
              />
            </div>

            <button 
              onClick={handleRequestReservation} 
              className="confirm-button"
              disabled={isLoading || !contractAccepted || !receiptFile}
            >
              {isLoading ? 'Enviando...' : 'Enviar Solicitud'}
            </button>
          </>
        ) : (
          <h2>{error || 'Fecha no disponible'}</h2>
        )}

        {message && <p className="message-area success">{message}</p>}
        {error && <p className="error-message">{error}</p>}
      </div>
    </div>
  );
}

export default Confirmacion;