import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import './EditReservationModal.css';

function EditReservationModal({ reservation, onClose, onUpdate, isCreating }) {
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    usuario_id: reservation?.usuario?.id || '',
    fecha_dia: reservation?.fecha?.dia || '',
    valor_alquiler: reservation?.valor_alquiler || 0,
    estado: reservation?.estado || 'confirmada',
    cantidad_personas: reservation?.cantidad_personas || 40,
    hora_inicio: reservation?.hora_inicio || '', 
    hora_fin: reservation?.hora_fin || '',
  });

  const [localReservation, setLocalReservation] = useState(reservation);
  
  // Estados para el buscador en vivo
  const [userSearchTerm, setUserSearchTerm] = useState('');
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [showUserList, setShowUserList] = useState(false);
  const [searchTimeout, setSearchTimeout] = useState(null);
  
  const [newPayment, setNewPayment] = useState({ monto: '' });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  // --- EFECTO: Inicializar el nombre si estamos editando ---
  useEffect(() => {
    if (!isCreating && reservation?.usuario) {
      setUserSearchTerm(`${reservation.usuario.nombre} ${reservation.usuario.apellido}`);
    }
  }, [isCreating, reservation]);

  // --- FUNCIÓN: Contactar por WhatsApp ---
  const handleContactWhatsApp = () => {
    const telefono = localReservation?.usuario?.telefono;
    if (!telefono) {
      alert("El usuario no tiene un teléfono registrado.");
      return;
    }

    // Limpiar el teléfono para la URL (sacar espacios/guiones)
    const cleanPhone = telefono.replace(/\s+/g, '').replace(/-/g, '');
    
    const texto = `Hola ${localReservation.usuario.nombre}, te contacto desde el Salón de Eventos por tu reserva del día ${formData.fecha_dia}. Queríamos coordinar los detalles: capacidad para ${formData.cantidad_personas} personas y horario de ${formData.hora_inicio || '11:00'} a ${formData.hora_fin || '20:00'} hs.`;
    
    const url = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(texto)}`;
    window.open(url, '_blank');
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // --- NUEVA FUNCIÓN: Buscador en vivo con Debounce ---
  const handleUserSearch = (e) => {
    const term = e.target.value;
    setUserSearchTerm(term);

    // Limpiamos el temporizador anterior si el usuario sigue escribiendo
    if (searchTimeout) clearTimeout(searchTimeout);

    if (term.trim().length >= 2) {
      // Esperamos 300ms antes de llamar al backend
      const timeoutId = setTimeout(async () => {
        const token = localStorage.getItem('authToken');
        try {
          const response = await fetch(`/api/v1/usuario/buscar?q=${encodeURIComponent(term)}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          const result = await response.json();
          
          if (response.ok) {
            setFilteredUsers(result.data || []);
            setShowUserList(true);
          }
        } catch (err) {
          console.error("Error en búsqueda en vivo:", err);
        }
      }, 300);
      setSearchTimeout(timeoutId);
    } else {
      setFilteredUsers([]);
      setShowUserList(false);
    }
  };

  const handleUserSelect = (user) => {
    setFormData(prev => ({ ...prev, usuario_id: user.id }));
    setUserSearchTerm(`${user.nombre} ${user.apellido} (DNI: ${user.dni})`);
    setShowUserList(false);
  };

  const handlePaymentChange = (e) => {
    setNewPayment({ monto: e.target.value });
  };

  const handleAddPayment = async () => {
    const montoAAgregar = parseFloat(newPayment.monto);
    if (!montoAAgregar || montoAAgregar <= 0) {
      setError('El monto del pago debe ser un número positivo.');
      return;
    }
    if (montoAAgregar > localReservation.saldo_restante) {
      setError('El pago no puede ser mayor que el saldo restante.');
      return;
    }
    
    setError('');
    const token = localStorage.getItem('authToken');
    try {
      const response = await fetch(`/api/v1/reserva/${reservation.id}/pagos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ monto: montoAAgregar }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message);
      
      const nuevoPago = {
        id: result.pago?.id || result.id || Date.now(),
        monto: montoAAgregar,
        fecha_pago: result.pago?.fecha_pago || result.fecha_pago || new Date().toISOString()
      };

      setLocalReservation(prev => ({
        ...prev,
        pagos: [...(prev.pagos || []), nuevoPago],
        saldo_restante: prev.saldo_restante - montoAAgregar
      }));

      await onUpdate(); 
      setMessage('Pago añadido con éxito.');
      setNewPayment({ monto: '' });
    } catch (err) {
      setError(err.message);
    }
  };
  
  const handleDeletePayment = async (pagoId) => {
    const masterPassword = window.prompt("Para eliminar este pago, por favor ingresa la contraseña maestra:");
    if (!masterPassword) return;

    setError('');
    setMessage('');
    const token = localStorage.getItem('authToken');

    try {
      const response = await fetch(`/api/v1/pago/${pagoId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ master_password: masterPassword })
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Error al eliminar el pago.');

      const pagoEliminado = localReservation.pagos.find(p => p.id === pagoId);
      const montoRecuperado = pagoEliminado ? parseFloat(pagoEliminado.monto) : 0;

      setLocalReservation(prev => ({
        ...prev,
        pagos: prev.pagos.filter(p => p.id !== pagoId),
        saldo_restante: prev.saldo_restante + montoRecuperado
      }));

      await onUpdate();
      setMessage('Pago eliminado correctamente.');
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    const token = localStorage.getItem('authToken');
    
    const dataToSend = { ...formData };
    if (!dataToSend.hora_inicio) delete dataToSend.hora_inicio;
    if (!dataToSend.hora_fin) delete dataToSend.hora_fin;

    const method = isCreating ? 'POST' : 'PUT';
    const url = isCreating ? '/api/v1/reserva/crear' : `/api/v1/reserva/${reservation.id}`;

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(dataToSend),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Ocurrió un error.');
      
      setMessage(isCreating ? 'Reserva creada con éxito.' : 'Reserva actualizada con éxito.');
      
      if (formData.estado === 'confirmada' && !isCreating) {
        setMessage('Reserva confirmada. El contrato definitivo ha sido enviado.');
      }

      await onUpdate();
      queryClient.invalidateQueries({ queryKey: ['fechas'] });
      onClose();
    } catch (err) {
      setError(err.message);
    }
  };
  
  const handleDelete = async () => {
    if (!window.confirm(`¿Estás seguro de que quieres archivar la reserva?`)) return;
    setIsDeleting(true);
    const token = localStorage.getItem('authToken');
    try {
      const response = await fetch(`/api/v1/reserva/${reservation.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Error al archivar.');
      setMessage('¡Reserva archivada!');
      await onUpdate();
      queryClient.invalidateQueries({ queryKey: ['fechas'] });
      onClose();
    } catch (err) {
      setError(err.message);
      setIsDeleting(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header-with-action">
          <h2>{isCreating ? 'Crear Nueva Reserva' : `Gestionar Reserva`}</h2>
          
          {!isCreating && localReservation?.usuario?.telefono && (
            <button 
              type="button" 
              className="btn-whatsapp-contact" 
              onClick={handleContactWhatsApp}
              title="Contactar por WhatsApp antes de confirmar"
            >
              <span className="wa-icon">💬</span> Contactar Cliente
            </button>
          )}
        </div>

      {!isCreating && localReservation?.comprobante_url && (
        <div className="receipt-view-section">
          <div className="receipt-header-row">
            <h4>Comprobante de Solicitud</h4>
            <span className="receipt-status-badge">Adjunto</span>
          </div>
          <div className="receipt-action-container">
            <a
              href={localReservation.comprobante_url}
              target="_blank"
              rel="noopener noreferrer"
              className="receipt-action-btn"
            >
              <span className="icon">📄</span>
              <div className="text-content">
                <span className="main-text">Abrir Comprobante</span>
              </div>
              <span className="external-link-icon">↗</span>
            </a>
          </div>
        </div>
      )}

        {!isCreating && localReservation?.usuario && (
          <p><strong>Usuario:</strong> {localReservation.usuario.nombre} {localReservation.usuario.apellido}</p>
        )}
        
        <form onSubmit={handleSubmit}>
          {isCreating && (
            <div className="form-group">
              <label htmlFor="usuario_search">Usuario</label>
              <div className="user-search-container">
                <input
                  type="text"
                  id="usuario_search"
                  value={userSearchTerm}
                  onChange={handleUserSearch}
                  placeholder="Buscar por nombre o DNI..."
                  autoComplete="off"
                  className="user-search-input"
                  onBlur={() => setTimeout(() => setShowUserList(false), 300)}
                />
                {showUserList && filteredUsers.length > 0 && (
                  <ul className="user-search-results">
                    {filteredUsers.map(user => (
                      <li key={user.id} onClick={() => handleUserSelect(user)}>
                        <strong>{user.apellido}, {user.nombre}</strong> <br/>
                        <small>DNI: {user.dni} | {user.correo}</small>
                      </li>
                    ))}
                  </ul>
                )}
                {showUserList && userSearchTerm.length >= 2 && filteredUsers.length === 0 && (
                   <ul className="user-search-results">
                     <li className="no-results" style={{ padding: '10px', color: '#666' }}>No se encontraron usuarios...</li>
                   </ul>
                )}
              </div>
            </div>
          )}
          
          <div className="form-group">
            <label htmlFor="fecha_dia">Fecha del Evento</label>
            <input type="date" name="fecha_dia" value={formData.fecha_dia} onChange={handleChange} required />
          </div>

          <div className="form-group-row">
            <div className="form-group">
              <label htmlFor="valor_alquiler">Valor del Alquiler ($)</label>
              <input type="number" name="valor_alquiler" value={formData.valor_alquiler} onChange={handleChange} min="0" />
            </div>

            <div className="form-group">
              <label htmlFor="cantidad_personas">Cantidad de Personas</label>
              <input 
                type="number" 
                name="cantidad_personas" 
                value={formData.cantidad_personas} 
                onChange={handleChange} 
                min="1" 
                required 
              />
            </div>
          </div>

          <div className="form-group-row">
            <div className="form-group">
              <label htmlFor="hora_inicio">Hora Inicio</label>
              <input 
                type="time" 
                name="hora_inicio" 
                value={formData.hora_inicio} 
                onChange={handleChange} 
              />
            </div>
            <div className="form-group">
              <label htmlFor="hora_fin">Hora Fin</label>
              <input 
                type="time" 
                name="hora_fin" 
                value={formData.hora_fin} 
                onChange={handleChange} 
              />
            </div>
          </div>
          <p className="status-help-text" style={{marginTop: '-10px', marginBottom: '15px'}}>
            Si se dejan vacíos, el contrato usará el horario base (11:00 a 20:00).
          </p>
          
          <div className="form-group">
            <label htmlFor="estado">Estado de la Reserva</label>
            <select name="estado" value={formData.estado} onChange={handleChange}>
              <option value="pendiente">Pendiente (Revisión de comprobante)</option>
              <option value="confirmada">Confirmada (Envía contrato definitivo)</option>
              <option value="cancelada">Cancelada</option>
            </select>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-close" onClick={onClose}>Cerrar</button>
            <button type="submit" className="btn-save">
              {isCreating ? 'Crear Reserva' : 'Guardar y Confirmar'}
            </button>
          </div>
        </form>

        {!isCreating && (
          <div className="payments-section">
            <h4>Pagos Registrados</h4>
            <ul className="payment-list">
              {localReservation.pagos && localReservation.pagos.length > 0 ? (
                localReservation.pagos.map(pago => (
                  <li key={pago.id}>
                    <div>
                      <span>{new Date(pago.fecha_pago).toLocaleDateString('es-ES')}</span>
                      <strong> - ${(pago.monto || 0).toLocaleString('es-AR')}</strong>
                    </div>
                    <button className="btn-delete-pago" onClick={() => handleDeletePayment(pago.id)} title="Eliminar pago">&times;</button>
                  </li>
                ))
              ) : (
                <li className="no-payments">No hay pagos registrados.</li>
              )}
            </ul>
            <p className="saldo-restante">
              Saldo Restante: <strong>${(localReservation.saldo_restante || 0).toLocaleString('es-AR')}</strong>
            </p>

            <div className="add-payment-form">
              <input
                type="number"
                placeholder="Monto nuevo pago"
                value={newPayment.monto}
                onChange={handlePaymentChange}
                min="0"
              />
              <button type="button" className="btn-add-payment" onClick={handleAddPayment}>Añadir Pago</button>
            </div>
          </div>
        )}

        {!isCreating && (
          <div className="delete-section">
            <button onClick={handleDelete} className="btn-delete" disabled={isDeleting}>
              {isDeleting ? 'Archivando...' : 'Archivar Reserva'}
            </button>
          </div>
        )}

        {error && <p className="error-message">{error}</p>}
        {message && <p className="message-area" style={{color: 'green', textAlign: 'center', marginTop: '10px'}}>{message}</p>}
      </div>
    </div>
  );
}

export default EditReservationModal;