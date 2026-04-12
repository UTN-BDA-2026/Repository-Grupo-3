WITH nuevas_personas AS (
  INSERT INTO persona (nombre, apellido, correo, dni, telefono, password_hash, tipo, activo)
  SELECT
    (ARRAY[
      'Maxi', 'Natalia', 'Roxana', 'Alvaro', 'Juan', 'Maria', 'Carlos', 'Laura', 'Sofia', 'Diego',
      'Matias', 'Lucia', 'Agustin', 'Florencia', 'Martin', 'Camila', 'Facundo', 'Micaela', 'Lucas', 'Julieta',
      'Franco', 'Valentina', 'Tomas', 'Martina', 'Nicolas', 'Antonella', 'Joaquin', 'Delfina', 'Ignacio', 'Paula',
      'Gonzalo', 'Victoria', 'Emiliano', 'Daniela', 'Federico', 'Melina', 'Gaston', 'Belen', 'Leandro', 'Rocio'
    ])[floor(random() * 40 + 1)],
    
    (ARRAY[
      'Eula', 'Guzman', 'Ulloa', 'Castro', 'Garcia', 'Lopez', 'Perez', 'Rodriguez', 'Martinez', 'Gomez',
      'Fernandez', 'Gonzalez', 'Diaz', 'Alvarez', 'Romero', 'Ruiz', 'Alonso', 'Torres', 'Dominguez', 'Vazquez',
      'Ramos', 'Gil', 'Ramirez', 'Sosa', 'Quiroga', 'Paz', 'Silva', 'Molina', 'Ortiz', 'Morales',
      'Herrera', 'Aguilar', 'Medina', 'Rios', 'Gimenez', 'Rojas', 'Mendoza', 'Vega', 'Cruz', 'Iglesias'
    ])[floor(random() * 40 + 1)],
    
    'cliente_' || i || '@test.com',
    (10000000 + i),
    '2604' || lpad(floor(random() * 999999)::text, 6, '0'),
    'hash_falso_de_prueba_123',
    'usuario',
    true
  FROM generate_series(1, 1000000) as i
  RETURNING id
)
INSERT INTO usuario (id)
SELECT id FROM nuevas_personas;
