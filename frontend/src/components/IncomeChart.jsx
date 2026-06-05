import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from 'chart.js';
import { useEffect, useState } from 'react'; // <-- IMPORTAMOS useState y useEffect
import { Bar } from 'react-chartjs-2';
import './IncomeChart.css';

// Registramos los componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function IncomeChart({ monthlyData }) {
  // 1. ESTADO PARA DETECTAR SI LA VISTA ES MÓVIL
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    // Función para actualizar el estado cuando cambia el tamaño de la ventana
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener('resize', handleResize);

    // Limpiamos el event listener cuando el componente se desmonta
    return () => window.removeEventListener('resize', handleResize);
  }, []);


  if (!monthlyData || Object.keys(monthlyData).length === 0) {
    return <div className="chart-container"><p>No hay datos de ingresos mensuales para mostrar.</p></div>;
  }

  const sortedMonths = Object.keys(monthlyData).sort();
  const chartData = {
    labels: sortedMonths.map(month => {
      const [year, monthNum] = month.split('-');
      
      // 2. ELEGIMOS EL FORMATO DE FECHA SEGÚN EL TAMAÑO DE LA PANTALLA
      const formatOptions = isMobile
        ? { month: 'short', year: '2-digit' } // Formato corto para móvil: "sep '25"
        : { month: 'long', year: 'numeric' };   // Formato largo para escritorio: "septiembre de 2025"

      const date = new Date(year, monthNum - 1);
      // Capitalizamos la primera letra del mes corto
      let formattedDate = new Intl.DateTimeFormat('es-ES', formatOptions).format(date);
      return formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1);
    }),
    datasets: [
      {
        label: 'Ingresos por Mes ($)',
        data: sortedMonths.map(month => monthlyData[month].ingresos),
        backgroundColor: 'rgba(52, 152, 219, 0.7)',
        borderColor: 'rgba(41, 128, 185, 1)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false, // Añadido para mejor control de tamaño
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Resumen de Ingresos Registrados por Mes',
        font: {
          size: 16 // Tamaño de fuente ajustado
        }
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return '$' + value.toLocaleString('es-AR');
          }
        }
      }
    }
  };

  return (
    // Ajustamos el contenedor para darle una altura fija
    <div className="chart-container" style={{ height: '400px', position: 'relative' }}>
      <Bar data={chartData} options={chartOptions} />
    </div>
  );
}

export default IncomeChart;