-- Women's Soccer Readiness App Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Teams table (organizations using the app)
CREATE TABLE teams (
    team_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    organization VARCHAR(100), -- e.g., "University of X", "NWSL Team Y"
    level VARCHAR(50), -- e.g., "NCAA D1", "NCAA D2", "NWSL", "Youth Elite"
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Users table (coaches, staff, admins)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'admin', 'head_coach', 'assistant_coach', 'staff'
    team_id UUID REFERENCES teams(team_id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Players table
CREATE TABLE players (
    player_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(team_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(20), -- 'GK', 'DEF', 'MID', 'FWD'
    jersey_number INTEGER,
    birth_date DATE,
    baseline_rhr INTEGER, -- Baseline resting heart rate
    baseline_hrv FLOAT, -- Baseline heart rate variability
    max_hr INTEGER, -- Maximum heart rate
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Training sessions table
CREATE TABLE training_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID REFERENCES players(player_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    session_type VARCHAR(50), -- 'training', 'match', 'recovery'
    duration_min INTEGER,
    distance_m FLOAT,
    high_speed_running_m FLOAT, -- Distance covered above speed threshold
    sprint_distance_m FLOAT,
    accelerations INTEGER,
    decelerations INTEGER,
    avg_hr INTEGER,
    max_hr INTEGER,
    hr_zones JSONB, -- Time spent in each HR zone
    training_load FLOAT, -- Calculated training load score
    rpe INTEGER CHECK (rpe BETWEEN 1 AND 10), -- Rate of Perceived Exertion
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Wellness checks table
CREATE TABLE wellness_checks (
    check_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID REFERENCES players(player_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    sleep_hours FLOAT CHECK (sleep_hours BETWEEN 0 AND 24),
    sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 5),
    soreness INTEGER CHECK (soreness BETWEEN 1 AND 5),
    fatigue INTEGER CHECK (fatigue BETWEEN 1 AND 5),
    stress INTEGER CHECK (stress BETWEEN 1 AND 5),
    mood INTEGER CHECK (mood BETWEEN 1 AND 5),
    hydration INTEGER CHECK (hydration BETWEEN 1 AND 5),
    nutrition_quality INTEGER CHECK (nutrition_quality BETWEEN 1 AND 5),
    cycle_phase VARCHAR(20), -- 'menstrual', 'follicular', 'ovulation', 'luteal'
    cycle_symptoms TEXT,
    injury_status VARCHAR(50), -- 'healthy', 'minor', 'moderate', 'severe'
    injury_notes TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Readiness scores table
CREATE TABLE readiness_scores (
    score_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID REFERENCES players(player_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    overall_score FLOAT CHECK (overall_score BETWEEN 0 AND 100),
    training_load_score FLOAT CHECK (training_load_score BETWEEN 0 AND 100),
    wellness_score FLOAT CHECK (wellness_score BETWEEN 0 AND 100),
    recovery_score FLOAT CHECK (recovery_score BETWEEN 0 AND 100),
    acute_load FLOAT, -- 7-day rolling average
    chronic_load FLOAT, -- 28-day rolling average
    acwr FLOAT, -- Acute:Chronic Workload Ratio
    readiness_flag VARCHAR(10) CHECK (readiness_flag IN ('green', 'yellow', 'red')),
    recommendations TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Polar data imports table (for tracking CSV uploads)
CREATE TABLE polar_imports (
    import_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID REFERENCES players(player_id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    file_hash VARCHAR(64), -- SHA256 hash to prevent duplicate imports
    import_date TIMESTAMP DEFAULT NOW(),
    records_imported INTEGER,
    status VARCHAR(20), -- 'pending', 'processing', 'completed', 'failed'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_players_team ON players(team_id);
CREATE INDEX idx_training_sessions_player_date ON training_sessions(player_id, date DESC);
CREATE INDEX idx_wellness_checks_player_date ON wellness_checks(player_id, date DESC);
CREATE INDEX idx_readiness_scores_player_date ON readiness_scores(player_id, date DESC);
CREATE INDEX idx_readiness_scores_flag ON readiness_scores(readiness_flag);
CREATE INDEX idx_users_email ON users(email);

-- Unique constraints to prevent duplicate entries
CREATE UNIQUE INDEX idx_training_sessions_unique ON training_sessions(player_id, date, session_type);
CREATE UNIQUE INDEX idx_wellness_checks_unique ON wellness_checks(player_id, date);
CREATE UNIQUE INDEX idx_readiness_scores_unique ON readiness_scores(player_id, date);

-- Updated timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_training_sessions_updated_at BEFORE UPDATE ON training_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE teams IS 'Organizations using the app (universities, pro teams, etc.)';
COMMENT ON TABLE users IS 'Coaches, staff, and administrators';
COMMENT ON TABLE players IS 'Soccer players with baseline metrics';
COMMENT ON TABLE training_sessions IS 'Training and match data from Polar or other devices';
COMMENT ON TABLE wellness_checks IS 'Daily subjective wellness questionnaires';
COMMENT ON TABLE readiness_scores IS 'Calculated readiness scores and recommendations';
COMMENT ON TABLE polar_imports IS 'Track CSV file imports to prevent duplicates';

COMMENT ON COLUMN training_sessions.acwr IS 'Acute:Chronic Workload Ratio - key injury risk metric';
COMMENT ON COLUMN wellness_checks.cycle_phase IS 'Menstrual cycle phase for female-specific training adjustments';
COMMENT ON COLUMN readiness_scores.readiness_flag IS 'Traffic light system: green=ready, yellow=caution, red=rest/modify';