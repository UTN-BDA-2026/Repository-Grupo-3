import { jwtDecode } from 'jwt-decode';
import { Navigate, Outlet } from 'react-router-dom';

function ProtectedRoute() {
  const token = localStorage.getItem('authToken');

  if (!token) {
    // Si no hay token, redirige al login
    return <Navigate to="/login" replace />;
  }

  try {
    const decodedToken = jwtDecode(token);
    // Si el rol no es 'administrador', redirige al inicio
    if (decodedToken.role !== 'administrador') {
      return <Navigate to="/" replace />;
    }
  } catch (error) {
    // Si el token es inválido, redirige al login
    return <Navigate to="/login" replace />;
  }

  // Si el token es válido y el rol es correcto, muestra el contenido de la ruta
  return <Outlet />;
}
export default ProtectedRoute; 