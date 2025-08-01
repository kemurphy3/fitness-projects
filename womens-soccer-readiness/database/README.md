# Database Setup

## Prerequisites
- PostgreSQL 14+ installed and running
- Python 3.8+ with pip

## Initial Setup

1. Create the database and schema:
```bash
python database/init_db.py
```

2. Generate synthetic test data (20 players × 10 weeks):
```bash
python database/seed_data.py
```

## Connection Details
Default connection string:
```
postgresql://postgres:postgres@localhost:5432/soccer_readiness
```

## Schema Overview

### Core Tables
- **teams**: Organizations using the app
- **users**: Coaches and staff accounts
- **players**: Soccer player profiles

### Data Tables
- **training_sessions**: GPS and heart rate data from training
- **wellness_checks**: Daily subjective wellness surveys
- **readiness_scores**: Calculated readiness scores and recommendations
- **polar_imports**: Track imported Polar device data

## Data Model Notes

### Training Load Calculation
- Acute load: 7-day rolling average
- Chronic load: 28-day rolling average
- ACWR (Acute:Chronic Workload Ratio): Acute / Chronic
- Target range: 0.8 - 1.3 (green zone)

### Readiness Score Components
- Training load score (40%): Based on ACWR
- Wellness score (40%): Based on subjective metrics
- Recovery score (20%): Based on sleep and HRV trends

### Wellness Metrics (1-5 scale)
- Sleep quality
- Soreness level
- Fatigue level
- Stress level
- Mood
- Hydration
- Nutrition quality

## Shared Database Access

Both the Women's Soccer and Marathon apps share the same PostgreSQL instance but use different databases:
- Women's Soccer: `soccer_readiness`
- Marathon: `marathon_training`

Configure via environment variables:
```bash
DATABASE_URL=postgresql://user:pass@host:port/database_name
```