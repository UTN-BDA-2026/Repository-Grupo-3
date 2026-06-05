import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AnalyticsDashboard from '../components/AnalyticsDashboard';
import ArchivedReservations from '../components/ArchivedReservations';
import EditReservationModal from '../components/EditReservationModal';
import GastosManager from '../components/GastosManager';
import PriceEditor from '../components/PriceEditor';
import UserList from '../components/UserList';
import { useReservas } from '../hooks/useAdminData';
import './AdminPanel.css';

// --- SUB-COMPONENTE: PAGINACIÓN ---
const Pagination = ({ itemsPerPage, totalItems, paginate, currentPage }) => {
  const pageNumbers = [];
  for (let i = 1; i <= Math.ceil(totalItems / itemsPerPage); i++) {
    pageNumbers.push(i);
  }
  if (pageNumbers.length <= 1) return null;

  return (
    <nav className="pagination-container">
      <ul className="pagination">
        {pageNumbers.map(number => (
          <li key={number} className={`page-item ${currentPage === number ? 'active' : ''}`}>
            <a onClick={() => paginate(number)} href="#!" className="page-link">
              {number}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
};

// --- SUB-COMPONENTE: GESTIÓN DE RESERVAS UNIFICADA ---
const ReservasManager = () => {
  const { data: reservas = {}, isLoading, error, refetch } = useReservas();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedReservation, setSelectedReservation] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  const [showArchived, setShowArchived] = useState(false);

  // --- FILTROS ---
  const [searchTerm, setSearchTerm] = useState('');
  const [searchTimeout, setSearchTimeout] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  
  const [statusFilter, setStatusFilter] = useState('todas');
  const [monthFilter, setMonthFilter] = useState('todos');
  
  // NUEVO: Estado para mostrar u ocultar reservas pasadas
  const [showPastReservations, setShowPastReservations] = useState(false);
  
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Obtener la fecha de hoy en formato YYYY-MM-DD para comparar strings
  const today = new Date().toISOString().split('T')[0];

  const formatDisplayDate = (isoDate) => {
    if (!isoDate) return 'N/A';
    const dateParts = isoDate.split('-');
    const date = new Date(Date.UTC(dateParts[0], dateParts[1] - 1, dateParts[2]));
    return new Intl.DateTimeFormat('es-ES', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC'
    }).format(date);
  };

  const handleSearchChange = (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    setCurrentPage(1);
    if (searchTimeout) clearTimeout(searchTimeout);

    if (term.trim().length >= 2) {
      setIsSearching(true);
      const timeoutId = setTimeout(async () => {
        const token = localStorage.getItem('authToken');
        try {
          const response = await fetch(`/api/v1/reserva/buscar?q=${encodeURIComponent(term)}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          const result = await response.json();
          if (response.ok) setSearchResults(result.data || []);
        } catch (err) {
          console.error("Error:", err);
        } finally { setIsSearching(false); }
      }, 300);
      setSearchTimeout(timeoutId);
    } else {
      setSearchResults(null);
    }
  };

  const availableMonths = Object.keys(reservas || {});
  let listToRender = [];
  
  if (searchResults !== null) {
    listToRender = searchResults;
  } else if (monthFilter !== 'todos') {
    listToRender = reservas[monthFilter] || [];
  } else {
    listToRender = availableMonths.reduce((acc, month) => [...acc, ...reservas[month]], []);
  }

  // --- FILTRO CRUCIAL: Solo próximas o incluir pasadas ---
  if (!showPastReservations && searchResults === null) {
    // Si NO queremos ver pasadas (y no estamos buscando a alguien específico), filtramos:
    listToRender = listToRender.filter(r => r.fecha?.dia >= today);
  }

  if (statusFilter !== 'todas') {
    listToRender = listToRender.filter(r => r.estado === statusFilter);
  }

  listToRender.sort((a, b) => new Date(a.fecha?.dia || 0) - new Date(b.fecha?.dia || 0));

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = listToRender.slice(indexOfFirstItem, indexOfLastItem);

  return (
    <div className="admin-section-fade">
      <div className="reservas-header">
        <div className="title-with-refresh">
          <h2 className="section-title">Gestión de Reservas</h2>
        </div>
        <div className="reservas-actions">
          <button className="btn-toggle-archived" onClick={() => setShowArchived(!showArchived)}>
            {showArchived ? 'Ocultar Archivadas' : 'Ver Archivadas'}
          </button>
          <button className="btn-create" onClick={() => { setSelectedReservation(null); setIsCreating(true); setIsModalOpen(true); }}>
            + Nueva Reserva
          </button>
        </div>
      </div>

      {showArchived && <ArchivedReservations />}

      <div className="filters-toolbar">
        <input
          type="text"
          placeholder="Buscar cliente, DNI o fecha..."
          className="search-input toolbar-input"
          value={searchTerm}
          onChange={handleSearchChange}
        />
        
        <select className="toolbar-select" value={monthFilter} onChange={(e) => { setMonthFilter(e.target.value); setCurrentPage(1); }} disabled={searchResults !== null}>
          <option value="todos">Todos los meses</option>
          {availableMonths.map(month => (
            <option key={month} value={month}>{month.charAt(0).toUpperCase() + month.slice(1)}</option>
          ))}
        </select>

        <select className="toolbar-select" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1); }}>
          <option value="todas">Todos los estados</option>
          <option value="confirmada">Confirmadas</option>
          <option value="pendiente">Pendientes</option>
        </select>

        {/* --- NUEVO TOGGLE PARA PASADAS --- */}
        <label className="show-past-toggle">
          <input 
            type="checkbox" 
            checked={showPastReservations} 
            onChange={(e) => setShowPastReservations(e.target.checked)} 
          />
          Ver reservas pasadas
        </label>
      </div>

      <div className="table-container">
        <table className="reservas-table user-table">
          <thead>
            <tr>
              <th>Fecha del Evento</th>
              <th>Cliente</th>
              <th>Estado</th>
              <th>Alquiler</th>
              <th>Saldo Pendiente</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {isSearching ? (
              <tr><td colSpan="6" style={{textAlign: 'center', padding: '2rem'}}>Buscando...</td></tr>
            ) : currentItems.length > 0 ? (
              currentItems.map(reserva => (
                <tr key={reserva.id} className={reserva.fecha?.dia < today ? 'row-past-reservation' : ''}>
                  <td><strong>{formatDisplayDate(reserva.fecha?.dia)}</strong></td>
                  <td>{`${reserva.usuario?.nombre || ''} ${reserva.usuario?.apellido || ''}`}</td>
                  <td><span className={`status ${reserva.estado}`}>{reserva.estado}</span></td>
                  <td>${(reserva.valor_alquiler || 0).toLocaleString('es-AR')}</td>
                  <td style={{ fontWeight: reserva.saldo_restante > 0 ? 'bold' : 'normal', color: reserva.saldo_restante > 0 ? '#e74c3c' : '#27ae60' }}>
                    ${(reserva.saldo_restante || 0).toLocaleString('es-AR')}
                  </td>
                  <td>
                    <button className="btn-view-reserva" onClick={() => { setSelectedReservation(reserva); setIsCreating(false); setIsModalOpen(true); }}>
                      Gestionar
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr><td colSpan="6" style={{textAlign: 'center'}}>No hay reservas próximas que coincidan.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {!isSearching && <Pagination itemsPerPage={itemsPerPage} totalItems={listToRender.length} paginate={setCurrentPage} currentPage={currentPage} />}

      {isModalOpen && <EditReservationModal isCreating={isCreating} reservation={selectedReservation} onClose={() => setIsModalOpen(false)} onUpdate={refetch} />}
    </div>
  );
};
// --- COMPONENTE PRINCIPAL: ADMIN PANEL (Intacto) ---
function AdminPanel() {
  const [activeTab, setActiveTab] = useState(() => {
    return localStorage.getItem('adminActiveTab') || 'accounting';
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    localStorage.setItem('adminActiveTab', activeTab);
  }, [activeTab]);

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('adminActiveTab'); 
    navigate('/login');
  };

  return (
    <div className="admin-wrapper">
      <aside className="admin-sidebar" style={{ backgroundColor: '#bc9e74', color: '#f1f5f9' }}>
        <div className="sidebar-logo">
          <h3>SALÓN ADMIN</h3>
        </div>
        <nav className="sidebar-nav">
          <button className="nav-btn" onClick={() => navigate('/')}>🏠 Inicio</button>
          <div className="nav-divider">Gestión</div>
          <button className={`nav-btn ${activeTab === 'accounting' ? 'active' : ''}`} onClick={() => setActiveTab('accounting')}>📊 Contabilidad</button>
          <button className={`nav-btn ${activeTab === 'prices' ? 'active' : ''}`} onClick={() => setActiveTab('prices')}>💰 Precios</button>
          <button className={`nav-btn ${activeTab === 'expenses' ? 'active' : ''}`} onClick={() => setActiveTab('expenses')}>📉 Gastos</button>
          <button className={`nav-btn ${activeTab === 'reservations' ? 'active' : ''}`} onClick={() => setActiveTab('reservations')}>📅 Reservas</button>
          <button className={`nav-btn ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>👤 Usuarios</button>
          <div className="sidebar-footer">
            <button className="nav-btn logout-btn" onClick={handleLogout}>🚪 Cerrar Sesión</button>
          </div>
        </nav>
      </aside>

      <main className="admin-main-content">
        <header className="admin-top-header">
          <h1>{
            activeTab === 'accounting' ? 'Resumen de Contabilidad' :
            activeTab === 'prices' ? 'Configuración de Precios' :
            activeTab === 'expenses' ? 'Control de Gastos' :
            activeTab === 'reservations' ? 'Calendario de Reservas' : 'Gestión de Usuarios'
          }</h1>
        </header>

        <section className="admin-content-area">
          {activeTab === 'accounting' && <AnalyticsDashboard />}
          {activeTab === 'prices' && <PriceEditor />}
          {activeTab === 'expenses' && <GastosManager />}
          {activeTab === 'reservations' && <ReservasManager />}
          {activeTab === 'users' && <UserList />}
        </section>
      </main>
    </div>
  );
}

export default AdminPanel;