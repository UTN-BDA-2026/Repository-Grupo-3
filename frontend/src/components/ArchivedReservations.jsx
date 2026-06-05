
import { useEffect, useState } from 'react';
import '../pages/AdminPanel.css'; // Reutilizamos los estilos

function ArchivedReservations() {
  const [archived, setArchived] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchArchived = async () => {
      const token = localStorage.getItem('authToken');
      try {
        const response = await fetch('/api/v1/reserva/archivadas', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) {
          throw new Error('No se pudieron cargar las reservas archivadas.');
        }
        const data = await response.json();
        setArchived(data.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchArchived();
  }, []);

  if (isLoading) return <p>Cargando reservas archivadas...</p>;
  if (error) return <p className="error-message">{error}</p>;

  return (
    <div className="archived-section">
      <h3>Reservas Archivadas</h3>
      {archived.length > 0 ? (
        <div className="table-container">
          <table className="reservas-table">
            <thead>
              <tr>
                <th>Fecha Evento</th>
                <th>Usuario</th>
                <th>Estado</th>
                <th>Valor Pagado</th>
              </tr>
            </thead>
            <tbody>
              {archived.map(reserva => (
                <tr key={reserva.id}>
                  <td>{new Date(reserva.fecha.dia + 'T00:00:00Z').toLocaleDateString('es-ES', { timeZone: 'UTC' })}</td>
                  <td>{`${reserva.usuario?.nombre || ''} ${reserva.usuario?.apellido || ''}`}</td>
                  <td><span className={`status ${reserva.estado}`}>{reserva.estado}</span></td>
                  <td>${(reserva.valor_alquiler - reserva.saldo_restante).toLocaleString('es-AR')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p>No hay reservas archivadas para mostrar.</p>
      )}
    </div>
  );
}

export default ArchivedReservations;