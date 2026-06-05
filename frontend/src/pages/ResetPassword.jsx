import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './login.css'; // Reutilizamos estilos

function ResetPassword() {
  const { token } = useParams(); // Obtenemos el token de la URL
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden.');
      return;
    }

    setError('');
    setMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.message);

      setMessage(result.message + ' Serás redirigido al inicio de sesión en 3 segundos...');
      setTimeout(() => {
        navigate('/login');
      }, 3000);

    } catch (err) {
      setError(err.message || 'Ocurrió un error. El enlace puede haber expirado.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Ingresa tu Nueva Contraseña</h2>
        <div className="form-group">
          <label htmlFor="password">Nueva Contraseña (mín. 8 caracteres)</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength="8"
          />
        </div>
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirmar Contraseña</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>
        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}
        <button type="submit" className="login-button" disabled={isLoading || !!message}>
          {isLoading ? 'Actualizando...' : 'Actualizar Contraseña'}
        </button>
      </form>
    </div>
  );
}

export default ResetPassword;