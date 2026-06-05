import { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // 1. Importar useNavigate
import './register.css';

function Register() {
  const navigate = useNavigate(); // 2. Inicializar el hook de navegación

  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [dni, setDni] = useState('');
  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [telefono, setTelefono] = useState('');
  
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false); // Estado para el mensaje de éxito

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setSuccess(false);

    // El endpoint de tu API para crear un usuario
    const url = '/api/v1/usuario';

    // Los datos que enviaremos, coinciden con tu UsuarioSchema
    const userData = {
      nombre,
      apellido,
      dni: parseInt(dni, 10), // Aseguramos que el DNI sea un número
      correo,
      telefono,
      password,
    };

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });

      const result = await response.json();

      if (!response.ok) {
        // Si el backend devuelve un error (ej: email duplicado)
        // El mensaje de error vendrá en result.data o result.message
        const errorMessage = result.data?.correo?.[0] || result.message || 'Error al registrar el usuario';
        throw new Error(errorMessage);
      }
      
      // Si todo sale bien
      console.log('Usuario registrado:', result.data);
      setSuccess(true);

      // 3. Redirigir al login después de 2 segundos
      setTimeout(() => {
        navigate('/login');
      }, 2000);

    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="register-container">
      <form className="register-form" onSubmit={handleSubmit}>
        <h2>Crear una Cuenta</h2>

        {/* Mensaje de éxito */}
        {success && (
          <p className="success-message">
            ¡Registro exitoso! Redirigiendo al inicio de sesión...
          </p>
        )}
        
        <div className="form-group">
          <label htmlFor="nombre">Nombre</label>
          <input
            type="text" id="nombre" value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
            placeholder='Ingresa tu nombre'
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="apellido">Apellido</label>
          <input
            type="text" id="apellido" value={apellido}
            onChange={(e) => setApellido(e.target.value)}
            required
            placeholder='Ingresa tu apellido'
          />
        </div>

        <div className="form-group">
          <label htmlFor="dni">DNI</label>
          <input
            type="number" id="dni" value={dni}
            onChange={(e) => setDni(e.target.value)}
            required
            placeholder='Ingresa tu DNI'
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="correo">Correo Electrónico</label>
          <input
            type="email" id="correo" value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
            placeholder="Ingresa tu email"
          />
        </div>

        <div className="form-group">
          <label htmlFor="telefono">Teléfono</label>
          <input
            type="tel" id="telefono" value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            placeholder="Ingresa tu número de teléfono"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Contraseña</label>
          <input
            type="password" id="password" value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength="8"
            required
            placeholder='Ingresa tu contraseña'
          />
        </div>
        
        {error && <p className="error-message">{error}</p>}

        <button type="submit" className="register-button" disabled={success}>
          {success ? 'Registrado' : 'Registrarse'}
        </button>
      </form>
    </div>
  );
}

export default Register;