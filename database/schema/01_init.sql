CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    city VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS signal_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE RESTRICT,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE RESTRICT,
    rssi INTEGER NOT NULL CHECK (rssi BETWEEN -140 AND 0),
    network_type VARCHAR(20) NOT NULL,
    device_model VARCHAR(120) NOT NULL,
    device_os VARCHAR(120) NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    speed_mps DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    signal_log_id INTEGER UNIQUE NOT NULL REFERENCES signal_logs(id) ON DELETE CASCADE,
    predicted_signal_strength DOUBLE PRECISION NOT NULL,
    dead_zone_probability DOUBLE PRECISION NOT NULL,
    recommended_operator VARCHAR(100),
    coverage_class VARCHAR(50) NOT NULL,
    anomaly_score DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_signal_logs_recorded_at ON signal_logs(recorded_at);
CREATE INDEX IF NOT EXISTS idx_signal_logs_user_id ON signal_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_locations_lat_lon ON locations(latitude, longitude);
