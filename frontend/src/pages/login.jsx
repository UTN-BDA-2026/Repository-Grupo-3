import { useState } from 'react';
import { Link, useNavigate, useOutletContext } from 'react-router-dom';
import './login.css';

function Login() {
  const navigate = useNavigate();
  const { handleLogin } = useOutletContext();

  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    try {
      const response = await fetch('/api/v1/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo, password }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'Credenciales inválidas.');
      }

      if (result.data.token) {
        handleLogin(result.data.token);
        navigate('/');
      }

    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Iniciar Sesión</h2>
        <div className="form-group">
          <label htmlFor="correo">Correo Electrónico</label>
          <input
            type="email"
            id="correo"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Contraseña</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="error-message">{error}</p>}
        <button type="submit" className="login-button">Ingresar</button>

        {/* --- ENLACE AÑADIDO --- */}
        <div className="forgot-password-link">
          <Link to="/forgot-password">¿Olvidaste tu contraseña?</Link>
        </div>
      </form>
    </div>
  );
}

export default Login;