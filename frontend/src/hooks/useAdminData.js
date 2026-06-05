import { useMutation, useQuery } from '@tanstack/react-query';
import api from '../api/client';

export const useReservas = () => {
  return useQuery({
    queryKey: ['reservas'],
    queryFn: () => api.get('/reserva'),
    select: (response) => {
      const rawData = response.data || [];
      return rawData.sort((a, b) => new Date(a.fecha?.dia) - new Date(b.fecha?.dia))
        .reduce((acc, reserva) => {
          if (!reserva.fecha?.dia) return acc;
          const dateParts = reserva.fecha.dia.split('-');
          const fecha = new Date(Date.UTC(dateParts[0], dateParts[1] - 1, dateParts[2]));
          const monthYear = new Intl.DateTimeFormat('es-ES', { 
              month: 'long', year: 'numeric', timeZone: 'UTC' 
          }).format(fecha);
          if (!acc[monthYear]) acc[monthYear] = [];
          acc[monthYear].push(reserva);
          return acc;
      }, {});
    }
  });
};

export const useAnalytics = (mes, anio) => {
  return useQuery({
    queryKey: ['analytics', mes, anio],
    queryFn: () => api.get(`/analytics?mes=${mes}&anio=${anio}`),
    enabled: !!mes && !!anio,
  });
};

export const useMisReservas = () => {
  return useQuery({
    queryKey: ['mis-reservas'],
    queryFn: () => api.get('/reserva/mis-reservas'),
    enabled: !!localStorage.getItem('authToken'),
  });
};

// Hook del Chatbot: Llama a /api/v1/chatbot/query
export const useChatbot = () => {
  return useMutation({
    mutationFn: (message) => api.post('/chatbot/query', { message }),
  });
};