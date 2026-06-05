import { jwtDecode } from 'jwt-decode';
import { useEffect, useState } from 'react';
import { FaClock, FaGamepad, FaMapMarkerAlt, FaSwimmingPool, FaUtensils } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import MiReserva from '../components/MiReserva';
import PhotoGallery from '../components/PhotoGallery';
import { useMisReservas } from '../hooks/useAdminData';
import './home.css';

// Agrega aquí las rutas de tus 6 imágenes. 
// Asumiendo que están en la carpeta 'public'.
const heroImages = [
  '/foto_salon.jpeg', //
  '/img1.png',       //
  '/img2.png',       //
  '/img3.png',       //
  '/img4.png',       //
  '/img5.png',       //
  '/img6.png'        //
];

function Home() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [showReservas, setShowReservas] = useState(false);
  
  // Estado para controlar qué imagen del carrusel se está mostrando
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      try {
        const decodedToken = jwtDecode(token);
        setUser(decodedToken);
      } catch (error) {
        console.error("Error al decodificar el token:", error);
      }
    }
  }, []);

  // Efecto para cambiar la imagen automáticamente cada 5 segundos
  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentImageIndex((prevIndex) => 
        prevIndex === heroImages.length - 1 ? 0 : prevIndex + 1
      );
    }, 5000); // 5000 milisegundos = 5 segundos

    // Limpiamos el intervalo cuando el componente se desmonta
    return () => clearInterval(intervalId);
  }, []);

  // Obtenemos reservas con el hook de React Query para evitar errores de JSON
  const { data: response, isLoading } = useMisReservas();
  const reservas = response?.data || [];

  const handleReserveClick = () => {
    navigate('/reservar');
  };

  const toggleReservas = () => {
    setShowReservas(prev => !prev);
  };

  return (
    <div className="home-container">
      {/* --- SECCIÓN HERO (AHORA CON CARRUSEL) --- */}
      <section className="hero-section">
        {/* Renderizamos las imágenes del carrusel */}
        {heroImages.map((img, index) => (
          <div
            key={index}
            className={`hero-slide ${index === currentImageIndex ? 'active' : ''}`}
            style={{ backgroundImage: `url(${img})` }}
          ></div>
        ))}
        
        {/* Capa oscura superpuesta */}
        <div className="hero-overlay"></div>

        <div className="hero-content">
          <h1>Tu Evento Soñado, Hecho Realidad</h1>
          <p>Calidad, elegancia y un servicio excepcional para tus momentos más especiales.</p>
          <button onClick={handleReserveClick} className="hero-button">Reserva Ahora</button>
        </div>
      </section>

      {/* --- SECCIÓN BIENVENIDA --- */}
      <section className="about-section">
        <div className="about-content">
          <div className="about-text">
            <h2>Bienvenidos a Nuestro Salón</h2>
            <p>
              Olvídate de las complicaciones. Te ofrecemos un espacio privado y totalmente equipado, pensado para tu disfrute. Tienes todo lo necesario para tu celebración: una cocina completa, un amplio espacio interior y un fantástico parque con pileta. Además, ¡la diversión está incluida!
            </p>
          </div>
          <div className="about-image">
            <img src="/foto_salon.jpeg" alt="Exterior del salón de eventos" />
          </div>
        </div>
      </section>

      {/* --- SECCIÓN UBICACIÓN --- */}
      <section className="location-section">
        <div className="location-content">
          <div className="location-info">
            <h2 className="section-title">Ubicación y Horarios</h2>
            <div className="info-item">
              <FaMapMarkerAlt className="info-icon" />
              <div>
                <h3>Dirección</h3>
                <p>Bolivar 1425, San Rafael, Mendoza, Argentina </p>
              </div>
            </div>
            <div className="info-item">
              <FaClock className="info-icon" />
              <div>
                <h3>Horarios de Alquiler</h3>
                <p>Lunes a Domingos: 11:00 a 20:00 hs</p>
                <p>Turnos de noche: Consultar</p>
              </div>
            </div>
          </div>
          <div className="location-map">
            {/* URL corregida para mostrar la ubicación real en San Rafael */}
            <iframe
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3282.653457813076!2d-68.313890123447!3d-34.63821707294406!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x9679a9bdbd71ebbd%3A0xf07b4cc0a177c032!2sSal%C3%B3n%20de%20eventos!5e0!3m2!1ses-419!2sar!4v1709584000000!5m2!1ses-419!2sar"
              width="100%"
              height="100%"
              style={{ border: 0 }}
              allowFullScreen=""
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
            ></iframe>
          </div>
        </div>
      </section>

      {/* --- SECCIÓN SERVICIOS --- */}
      <section className="services-section">
        <h2 className="section-title">¿Qué Incluye el Alquiler?</h2>
        <div className="services-grid">
          <div className="service-item">
            <FaUtensils className="service-icon" />
            <h3>Salón Totalmente Equipado</h3>
            <p>Incluye 25 sillas, 4 mesones, cocina con heladera, freezer, pava eléctrica y 4 baños.</p>
          </div>
          <div className="service-item">
            <FaGamepad className="service-icon" />
            <h3>Diversión Asegurada</h3>
            <p>Disfruta de mesa de pool, ping pong, metegol y máquinas de videojuegos arcade.</p>
          </div>
          <div className="service-item">
            <FaSwimmingPool className="service-icon" />
            <h3>Amplios Exteriores</h3>
            <p>Contamos con un gran parque, pileta para el verano y cocheras privadas.</p>
          </div>
        </div>
      </section>

      {/* --- GALERÍA --- */}
      <section className="gallery-section">
        <h2 className="section-title">Fotos del Salón</h2>
        <PhotoGallery />
      </section>

      {/* --- PANEL FLOTANTE DE RESERVAS --- */}
      {user && !isLoading && reservas.length > 0 && (
        <>
          <button onClick={toggleReservas} className="mis-reservas-button">
            Mis Reservas ({reservas.length})
          </button>
          {showReservas && <MiReserva reservas={reservas} onClose={toggleReservas} />}
        </>
      )}
    </div>
  );
}

export default Home;