import * as Sentry from "@sentry/react";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StrictMode } from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

// Importaciones de tus componentes y páginas
import App from './App.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import './index.css';
import AdminPanel from './pages/AdminPanel.jsx';
import Confirmacion from './pages/confirmacion.jsx';
import ForgotPassword from './pages/ForgotPassword.jsx';
import Home from './pages/home.jsx';
import Login from './pages/login.jsx';
import Register from './pages/register.jsx';
import Reservas from './pages/reservas.jsx';
import ResetPassword from './pages/ResetPassword.jsx';

// 1. Configuración de Sentry
Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN_FRONTEND,
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

// 2. Configuración de React Query (AJUSTADA)
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Reducimos retry a 1 para no atacar al servidor si ya está dando error 500
      retry: 1, 
      refetchOnWindowFocus: false,
      // Los datos se mantienen "frescos" por 5 minutos
      staleTime: 1000 * 60 * 5,
      // Tiempo que los datos permanecen en caché antes de eliminarse (5 min)
      gcTime: 1000 * 60 * 5,
      // Evita reintentos si el error es por falta de conexión
      refetchOnReconnect: false,
    },
  },
});

// 3. Definición de Rutas
const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Home /> },
      { path: "/login", element: <Login /> },
      { path: "/register", element: <Register /> },
      { path: "/forgot-password", element: <ForgotPassword /> },
      { path: "/reset-password/:token", element: <ResetPassword /> },
      { path: "/reservar", element: <Reservas /> },
      { path: "/reservar/:dateString", element: <Confirmacion /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: "/admin-panel", element: <AdminPanel /> }
        ]
      },
    ]
  },
]);

// 4. Renderizado Final con ErrorBoundary de Sentry
ReactDOM.createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Sentry.ErrorBoundary fallback={<p>Algo salió mal. Por favor, refresca la página.</p>}>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </Sentry.ErrorBoundary>
  </StrictMode>
);