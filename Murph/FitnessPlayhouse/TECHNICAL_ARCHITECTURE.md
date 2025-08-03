# Technical Architecture

## Shared Infrastructure

```
shared-core/
├── database/
│   ├── users.sql           # Shared user management
│   ├── auth.sql           # Authentication tables
│   └── analytics.sql      # Shared analytics events
├── api/
│   ├── fastapi_base.py    # Base FastAPI setup
│   ├── auth.py            # JWT authentication
│   ├── middleware.py      # Logging, rate limiting
│   └── utils.py           # Shared utilities
├── ml_models/
│   ├── pattern_detection.py
│   ├── anomaly_detection.py
│   └── recommendation.py
└── frontend_components/
    ├── charts/            # Recharts components
    ├── dashboards/        # Shared layouts
    └── mobile/            # Responsive components
```

## Women's Soccer App Architecture

### Database Schema
```sql
-- Players table
CREATE TABLE players (
    player_id UUID PRIMARY KEY,
    team_id UUID REFERENCES teams(team_id),
    name VARCHAR(100),
    position VARCHAR(20),
    baseline_rhr INTEGER,
    baseline_hrv FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Training sessions
CREATE TABLE training_sessions (
    session_id UUID PRIMARY KEY,
    player_id UUID REFERENCES players(player_id),
    date DATE,
    duration_min INTEGER,
    distance_m FLOAT,
    high_speed_running_m FLOAT,
    accelerations INTEGER,
    decelerations INTEGER,
    avg_hr INTEGER,
    max_hr INTEGER,
    training_load FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Wellness checks
CREATE TABLE wellness_checks (
    check_id UUID PRIMARY KEY,
    player_id UUID REFERENCES players(player_id),
    date DATE,
    sleep_hours FLOAT,
    sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 5),
    soreness INTEGER CHECK (soreness BETWEEN 1 AND 5),
    fatigue INTEGER CHECK (fatigue BETWEEN 1 AND 5),
    mood INTEGER CHECK (mood BETWEEN 1 AND 5),
    cycle_phase VARCHAR(20),
    cycle_symptoms TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Readiness scores
CREATE TABLE readiness_scores (
    score_id UUID PRIMARY KEY,
    player_id UUID REFERENCES players(player_id),
    date DATE,
    overall_score FLOAT,
    training_load_score FLOAT,
    wellness_score FLOAT,
    readiness_flag VARCHAR(10), -- 'green', 'yellow', 'red'
    recommendations TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Key Components
```python
# ingestion/polar_parser.py
class PolarParser:
    def parse_csv(self, filepath: str) -> Dict:
        # Column mapping logic
        # Unit conversions
        # Validation rules
        
# analytics/readiness_scorer.py        
class ReadinessScorer:
    def calculate_readiness(self, player_id: str) -> ReadinessScore:
        # Acute:Chronic workload ratio
        # Wellness integration
        # Cycle phase adjustments
        # Flag generation
```

## Decision-Free Planner Architecture

### Database Schema
```sql
-- User preferences
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY,
    wake_time TIME,
    sleep_time TIME,
    work_hours JSONB,
    fitness_goals TEXT[],
    productivity_style VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Daily plans
CREATE TABLE daily_plans (
    plan_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    date DATE,
    tasks JSONB,
    completed_tasks JSONB,
    adaptations_made TEXT[],
    satisfaction_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Habits and streaks
CREATE TABLE habits (
    habit_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    name VARCHAR(100),
    frequency VARCHAR(20), -- 'daily', 'weekly'
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_completed DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Adaptive Algorithm
```python
# planner/adaptive_scheduler.py
class AdaptiveScheduler:
    def generate_daily_plan(self, user_id: str, date: date) -> DailyPlan:
        # Load user preferences
        # Check previous completion rates
        # Adjust difficulty based on streaks
        # Balance domains (fitness, work, wellness)
        # Return optimized schedule
        
    def adjust_for_missed_tasks(self, plan_id: str) -> DailyPlan:
        # Detect missed morning workout
        # Suggest evening alternative
        # Maintain weekly targets
        # Update future recommendations
```

## Tech Stack

### Backend
- **Database**: PostgreSQL 14+
- **API**: FastAPI + Pydantic
- **ML**: Scikit-learn, Pandas, NumPy
- **Task Queue**: Celery + Redis
- **Auth**: JWT tokens

### Frontend
- **MVP**: Streamlit (quick prototyping)
- **Production**: React + TypeScript
- **Charts**: Recharts
- **Mobile**: React Native (future)
- **State**: Redux Toolkit

### Infrastructure
- **Hosting**: DigitalOcean / Railway
- **Storage**: S3-compatible
- **Monitoring**: Sentry + Datadog
- **CI/CD**: GitHub Actions
- **Backups**: Daily automated

## API Design

### Soccer App Endpoints
```
POST   /api/teams/{team_id}/players
POST   /api/players/{player_id}/training-session
POST   /api/players/{player_id}/wellness-check
GET    /api/teams/{team_id}/readiness
GET    /api/players/{player_id}/recommendations
```

### Planner App Endpoints
```
POST   /api/users/preferences
GET    /api/users/{user_id}/daily-plan
PATCH  /api/plans/{plan_id}/complete-task
GET    /api/users/{user_id}/streaks
POST   /api/feedback/satisfaction
```