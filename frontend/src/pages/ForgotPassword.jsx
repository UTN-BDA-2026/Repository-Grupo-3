import { useState } from 'react';
import { Link } from 'react-router-dom';
import './login.css'; // Reutilizamos los estilos del login

function ForgotPassword() {
  const [correo, setCorreo] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo }),
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.message || 'Ocurrió un error al procesar la solicitud.');
      }

      setMessage(result.message);

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Restablecer Contraseña</h2>
        <p style={{marginBottom: '1.5rem', textAlign: 'center', lineHeight: '1.6'}}>
          Ingresa tu correo electrónico y te enviaremos un enlace para recuperar tu cuenta.
        </p>
        
        {!message && (
          <div className="form-group">
            <label htmlFor="correo">Correo Electrónico</label>
            <input
              type="email"
              id="correo"
              value={correo}
              onChange={(e) => setCorreo(e.target.value)}
              required
              placeholder="tu@email.com"
            />
          </div>
        )}

        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}

        {!message && (
            <button type="submit" className="login-button" disabled={isLoading}>
                {isLoading ? 'Enviando...' : 'Enviar Enlace de Recuperación'}
            </button>
        )}

        <div className="forgot-password-link">
            <Link to="/login">Volver a Iniciar Sesión</Link>
        </div>
      </form>
    </div>
  );
}

export default ForgotPassword;