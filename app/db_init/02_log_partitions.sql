-- Tabla log particionada por rango de fecha
-- (sin FK a persona para evitar problemas de orden de creación)
CREATE TABLE IF NOT EXISTS log (
    id          SERIAL,
    fecha       TIMESTAMP NOT NULL DEFAULT NOW(),
    accion      VARCHAR(100) NOT NULL,
    entidad     VARCHAR(50),
    entidad_id  INTEGER,
    descripcion TEXT,
    ip          VARCHAR(45),
    resultado   VARCHAR(20) NOT NULL DEFAULT 'exitoso',
    usuario_id  INTEGER
) PARTITION BY RANGE (fecha);

-- Partición 2025
CREATE TABLE IF NOT EXISTS log_2025
    PARTITION OF log
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Partición 2026
CREATE TABLE IF NOT EXISTS log_2026
    PARTITION OF log
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- Partición 2027
CREATE TABLE IF NOT EXISTS log_2027
    PARTITION OF log
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

-- Índices sobre las particiones
CREATE INDEX IF NOT EXISTS idx_log_fecha      ON log (fecha);
CREATE INDEX IF NOT EXISTS idx_log_usuario_id ON log (usuario_id);
CREATE INDEX IF NOT EXISTS idx_log_accion     ON log (accion);
