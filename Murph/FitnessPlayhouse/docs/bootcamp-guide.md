# Fitness Playhouse Bootcamp Guide

## Table of Contents
1. [Authentication Deep Dive](#authentication-deep-dive)
2. [Data Management & Idempotency](#data-management--idempotency)
3. [Sports Science Calculations](#sports-science-calculations)
4. [API Development & Testing](#api-development--testing)
5. [Dashboard Development](#dashboard-development)
6. [Recovery Strategies](#recovery-strategies)
7. [Environment Configuration](#environment-configuration)
8. [Knowledge Gap Study Guide](#knowledge-gap-study-guide)

---

## Authentication Deep Dive

### What is JWT (JSON Web Token)?

JWT is a compact, URL-safe means of representing claims between two parties. Think of it as a secure digital ID card.

**Structure of a JWT:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

This has three parts separated by dots:
1. **Header**: Algorithm & token type
2. **Payload**: User data (claims)
3. **Signature**: Verification

### JWT vs Sessions: The Key Differences

**Sessions (Traditional)**
```
1. User logs in
2. Server creates session, stores in database/memory
3. Server sends session ID as cookie
4. Every request needs database lookup
```

**JWT (Modern)**
```
1. User logs in
2. Server creates JWT with user info
3. Server sends JWT to client
4. Client includes JWT in headers
5. Server validates JWT (no database needed)
```

**Why Use JWT?**
- **Stateless**: No server-side storage needed
- **Scalable**: Works across multiple servers
- **Mobile-friendly**: Not cookie-dependent
- **Self-contained**: Contains user info

**When to Use Sessions:**
- Need instant revocation
- Storing sensitive server-side data
- Working with older browsers

### Practical JWT Implementation

```python
# Creating a JWT
import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: int, team_id: int):
    payload = {
        "sub": str(user_id),  # Subject (user ID)
        "team_id": team_id,
        "exp": datetime.utcnow() + timedelta(hours=24),  # Expiration
        "iat": datetime.utcnow(),  # Issued at
        "type": "access"
    }
    
    # SECRET_KEY should be from environment variable
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# Verifying a JWT
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## Data Management & Idempotency

### What is Idempotency?

Idempotency means that no matter how many times you perform an operation, the result is the same. It's like pressing an elevator button multiple times - the elevator only comes once.

**Why It Matters:**
- Network failures can cause retries
- Users might double-click submit
- Mobile apps might retry on poor connections

### How import_hash Prevents Duplicates

The `import_hash` is a unique fingerprint of uploaded data:

```python
import hashlib
import json

def generate_import_hash(data):
    """
    Creates a unique hash from data to prevent duplicate imports
    """
    # Sort data to ensure consistent hashing
    sorted_data = json.dumps(data, sort_keys=True)
    
    # Create SHA-256 hash
    hash_object = hashlib.sha256(sorted_data.encode())
    return hash_object.hexdigest()

# In your upload endpoint
def upload_training_data(file_data):
    # Generate hash from file content
    import_hash = generate_import_hash(file_data)
    
    # Check if already imported
    existing = db.query(Upload).filter_by(import_hash=import_hash).first()
    if existing:
        return {"message": "Data already imported", "upload_id": existing.id}
    
    # Process new upload
    new_upload = Upload(import_hash=import_hash, data=file_data)
    db.add(new_upload)
    db.commit()
```

### Why Users Upload Same Data Multiple Times

1. **Device Syncing**: Wearables auto-upload daily
2. **Team Requirements**: Coaches want daily reports
3. **User Uncertainty**: "Did my data save?"
4. **Multiple Platforms**: Garmin + Whoop + Manual entry

### Error Handling Without Data Loss

```python
from sqlalchemy import begin_nested

def safe_bulk_upload(sessions_data):
    """
    Upload multiple sessions with rollback on error
    """
    processed = []
    errors = []
    
    with db.begin_nested():  # Savepoint
        for session in sessions_data:
            try:
                # Process individual session
                result = process_session(session)
                processed.append(result)
            except ValidationError as e:
                # Log error but continue
                errors.append({
                    "session": session.get("date"),
                    "error": str(e)
                })
                # Rollback just this session
                db.rollback()
    
    # Commit successful sessions
    if processed:
        db.commit()
    
    return {
        "processed": len(processed),
        "errors": errors,
        "success": len(errors) == 0
    }
```

---

## Sports Science Calculations

### ACWR vs Readiness: Understanding the Difference

**ACWR (Acute:Chronic Workload Ratio)**
- Compares recent training load to historical baseline
- Injury prevention metric
- Formula: Last 7 days average ÷ Last 28 days average
- Sweet spot: 0.8-1.3 (per Gabbett, 2016)

**Readiness Score**
- Daily assessment of ability to train
- Combines multiple factors
- More holistic than just training load

### ACWR Calculation

```python
def calculate_acwr(training_loads: List[float]) -> float:
    """
    Calculate ACWR using exponentially weighted moving average
    Based on Gabbett (2016) research
    """
    if len(training_loads) < 28:
        return None
    
    # Acute load (last 7 days)
    acute = sum(training_loads[-7:]) / 7
    
    # Chronic load (last 28 days)
    chronic = sum(training_loads[-28:]) / 28
    
    # Prevent division by zero
    if chronic == 0:
        return 0
    
    return round(acute / chronic, 2)

def interpret_acwr(ratio: float) -> dict:
    """
    Based on Gabbett's injury risk zones
    """
    if ratio < 0.8:
        return {
            "zone": "Under-training",
            "risk": "Low fitness gains",
            "recommendation": "Gradually increase load"
        }
    elif 0.8 <= ratio <= 1.3:
        return {
            "zone": "Sweet spot",
            "risk": "Lowest injury risk",
            "recommendation": "Maintain current progression"
        }
    elif 1.3 < ratio <= 1.5:
        return {
            "zone": "Caution",
            "risk": "Moderate injury risk",
            "recommendation": "Monitor closely, avoid spikes"
        }
    else:
        return {
            "zone": "Danger",
            "risk": "High injury risk (2-4x)",
            "recommendation": "Reduce load immediately"
        }
```

### Readiness Score Calculation

```python
def calculate_readiness_score(metrics: dict) -> float:
    """
    Composite readiness score based on multiple factors
    Weights derived from McLean et al. (2010) and custom sports science input
    """
    weights = {
        "sleep_quality": 0.25,      # 0-10 scale
        "muscle_soreness": 0.20,    # 0-10 (inverted)
        "energy_level": 0.20,       # 0-10 scale
        "stress_level": 0.15,       # 0-10 (inverted)
        "hrv_score": 0.20          # Normalized 0-100
    }
    
    # Normalize and weight each component
    readiness = 0
    
    # Sleep (higher is better)
    readiness += metrics.get("sleep_quality", 5) * weights["sleep_quality"]
    
    # Soreness (lower is better, so invert)
    readiness += (10 - metrics.get("muscle_soreness", 5)) * weights["muscle_soreness"]
    
    # Energy (higher is better)
    readiness += metrics.get("energy_level", 5) * weights["energy_level"]
    
    # Stress (lower is better, so invert)
    readiness += (10 - metrics.get("stress_level", 5)) * weights["stress_level"]
    
    # HRV (normalize from 0-100 to 0-10)
    hrv_normalized = metrics.get("hrv_score", 50) / 10
    readiness += hrv_normalized * weights["hrv_score"]
    
    return round(readiness, 1)
```

### Wellness Score Components

A comprehensive wellness score typically includes:

1. **Physical Components (40%)**
   - HRV (Heart Rate Variability)
   - Resting Heart Rate
   - Sleep Duration & Quality
   - Muscle Soreness

2. **Mental Components (30%)**
   - Stress Level
   - Mood
   - Motivation

3. **Lifestyle Components (30%)**
   - Hydration
   - Nutrition Quality
   - Recovery Activities

**Sources:**
- Gabbett, T. J. (2016). The training—injury prevention paradox
- McLean, B. D., et al. (2010). Neuromuscular, endocrine, and perceptual fatigue responses

---

## API Development & Testing

### Creating Authorization Dependencies

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Dependency to extract and verify user from JWT
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        # Fetch user from database
        user = await get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Using the dependency
@app.get("/api/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}
```

### Auth Endpoints Structure

```python
# auth/router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    # Verify credentials
    user = await authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_access_token(user.id, user.team_id)
    
    return TokenResponse(access_token=token)

@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Get new token before expiration"""
    new_token = create_access_token(current_user["id"], current_user["team_id"])
    return TokenResponse(access_token=new_token)

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout (client-side token removal)"""
    # Optional: Add token to blacklist if using one
    return {"message": "Logged out successfully"}
```

### Testing with Postman/cURL

**1. Login (Get Token)**
```bash
# cURL
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "athlete@team.com", "password": "secure123"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**2. Use Token for Protected Endpoints**
```bash
# cURL
curl -X GET http://localhost:8000/api/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# Postman Setup:
# 1. Go to Authorization tab
# 2. Select "Bearer Token"
# 3. Paste your token
# 4. Send request
```

**3. Upload Training Data**
```bash
# cURL with file upload
curl -X POST http://localhost:8000/api/upload/training \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -F "file=@training_data.csv"
```

### Team Access Control

```python
from enum import Enum

class TeamRole(str, Enum):
    ATHLETE = "athlete"
    COACH = "coach"
    ADMIN = "admin"
    VIEWER = "viewer"

class TeamPermissions:
    """Define what each role can do"""
    
    PERMISSIONS = {
        TeamRole.ATHLETE: [
            "view_own_data",
            "upload_own_data",
            "view_team_schedule"
        ],
        TeamRole.COACH: [
            "view_all_athlete_data",
            "create_training_plans",
            "export_team_reports",
            "manage_athletes"
        ],
        TeamRole.ADMIN: [
            "all_permissions",
            "manage_team_settings",
            "manage_users"
        ],
        TeamRole.VIEWER: [
            "view_public_data",
            "view_team_stats"
        ]
    }

def check_team_permission(
    user: dict,
    required_permission: str
) -> bool:
    """Check if user has specific permission"""
    user_role = user.get("team_role", TeamRole.ATHLETE)
    permissions = TeamPermissions.PERMISSIONS.get(user_role, [])
    
    return (
        required_permission in permissions or
        "all_permissions" in permissions
    )

# Permission dependency
def require_permission(permission: str):
    async def permission_checker(
        current_user: dict = Depends(get_current_user)
    ):
        if not check_team_permission(current_user, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission}"
            )
        return current_user
    return permission_checker

# Usage
@app.get("/api/team/athletes")
async def get_team_athletes(
    user: dict = Depends(require_permission("view_all_athlete_data"))
):
    return await get_athletes_for_team(user["team_id"])
```

### Service Directory Structure

```
app/
├── __init__.py
├── main.py              # FastAPI app initialization
├── config.py            # Configuration management
├── database.py          # Database connection
│
├── api/                 # API layer
│   ├── __init__.py
│   ├── dependencies.py  # Shared dependencies
│   └── v1/
│       ├── __init__.py
│       ├── auth.py      # Auth endpoints
│       ├── athletes.py  # Athlete endpoints
│       ├── training.py  # Training endpoints
│       └── wellness.py  # Wellness endpoints
│
├── core/                # Core business logic
│   ├── __init__.py
│   ├── security.py      # JWT, hashing
│   ├── config.py        # App settings
│   └── exceptions.py    # Custom exceptions
│
├── models/              # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── team.py
│   ├── training.py
│   └── wellness.py
│
├── schemas/             # Pydantic schemas
│   ├── __init__.py
│   ├── user.py
│   ├── training.py
│   └── wellness.py
│
├── services/            # Business logic services
│   ├── __init__.py
│   ├── auth_service.py
│   ├── training_service.py
│   ├── wellness_service.py
│   └── analytics_service.py
│
├── utils/               # Utilities
│   ├── __init__.py
│   ├── validators.py
│   └── calculators.py
│
└── tests/               # Test files
    ├── __init__.py
    ├── test_auth.py
    ├── test_training.py
    └── test_wellness.py
```

---

## Dashboard Development

### Architecture Options

**1. Power BI (Good for NCAA Environment)**
```
Pros:
- Familiar to athletic departments
- Great for scheduled reports
- Easy sharing with coaches
- Built-in mobile apps

Cons:
- Licensing costs
- Less real-time capability
- Limited customization
```

**2. Custom Web Dashboard (Recommended)**
```
Tech Stack:
- Frontend: React + Chart.js/D3.js
- Backend: FastAPI
- Real-time: WebSockets
- Caching: Redis

Benefits:
- Full control
- Real-time updates
- Custom visualizations
- White-label capability
```

**3. Snowflake + Streamlit (Quick Start)**
```python
# Quick dashboard with Streamlit
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Athlete Readiness Dashboard")

# Load data
@st.cache_data
def load_athlete_data(athlete_id):
    # Connect to Snowflake
    return pd.read_sql("""
        SELECT date, readiness_score, training_load, sleep_hours
        FROM athlete_metrics
        WHERE athlete_id = %s
        ORDER BY date DESC
        LIMIT 30
    """, conn, params=[athlete_id])

# Readiness trend
df = load_athlete_data(selected_athlete)
fig = px.line(df, x='date', y='readiness_score', 
              title='30-Day Readiness Trend')
st.plotly_chart(fig)
```

### Adding Caching

**What is Caching?**
Storing frequently accessed data in fast memory to avoid repeated calculations/database queries.

**Implementation with Redis:**
```python
import redis
import json
from datetime import timedelta

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_cached_or_compute(key: str, compute_func, expire_time: int = 3600):
    """
    Generic caching function
    """
    # Try to get from cache
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    # Compute if not cached
    result = compute_func()
    
    # Store in cache
    redis_client.setex(
        key,
        timedelta(seconds=expire_time),
        json.dumps(result)
    )
    
    return result

# Usage example
@app.get("/api/team/{team_id}/stats")
async def get_team_stats(team_id: int):
    cache_key = f"team_stats:{team_id}"
    
    def compute_stats():
        # Expensive calculation
        return calculate_team_statistics(team_id)
    
    return get_cached_or_compute(cache_key, compute_stats, expire_time=1800)
```

**In-Memory Caching (Simple):**
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_athlete_readiness(athlete_id: int, date: str):
    """Cached for repeated calls"""
    return calculate_readiness(athlete_id, date)

# Time-based cache
class TimedCache:
    def __init__(self, expire_minutes=5):
        self.cache = {}
        self.expire_delta = timedelta(minutes=expire_minutes)
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.expire_delta:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())
```

---

## Recovery Strategies

### Training Pattern Analysis

**Option 1: Alternating Days**
```
Mon: Hard
Tue: Recovery
Wed: Moderate
Thu: Recovery
Fri: Hard
Sat: Recovery
Sun: Moderate
```
Benefits:
- Consistent recovery
- Lower injury risk
- Good for older athletes
- Easier to maintain

**Option 2: Block Training**
```
Mon-Wed: Hard training block
Thu-Fri: Complete rest
Sat-Sun: Moderate block
```
Benefits:
- Deeper adaptations
- Better for younger athletes
- Mimics competition schedule
- More time-efficient

**Research-Based Recommendation:**
For soccer players, research suggests:
- 2-3 consecutive training days followed by recovery
- Matches perceived adaptation windows
- Allows for tactical work continuity
- Key: Monitor individual response

```python
def recommend_training_pattern(athlete_profile):
    """
    Recommend training pattern based on athlete profile
    """
    age = athlete_profile["age"]
    injury_history = athlete_profile["injury_count_last_year"]
    position = athlete_profile["position"]
    
    if age > 25 or injury_history > 2:
        return {
            "pattern": "alternating",
            "reason": "Higher recovery needs",
            "sample_week": {
                "monday": "High intensity",
                "tuesday": "Recovery/Skills",
                "wednesday": "Moderate",
                "thursday": "Recovery",
                "friday": "High intensity",
                "weekend": "Match or rest"
            }
        }
    else:
        return {
            "pattern": "block",
            "reason": "Can handle higher load density",
            "sample_week": {
                "monday-wednesday": "Training block",
                "thursday": "Recovery",
                "friday-saturday": "Training block",
                "sunday": "Recovery"
            }
        }
```

---

## Environment Configuration

### SECRET_KEY Best Practices

**Never hardcode secrets!** Here's the proper setup:

**1. Generate a secure SECRET_KEY:**
```bash
# Generate secure key
python -c "import secrets; print(secrets.token_hex(32))"
# Output: a8f5f167f7c9c8d9e6f5e4d3c2b1a0918273645564738291
```

**2. File Structure:**
```
.env                 # Your actual secrets (NEVER commit)
.env.example         # Template with dummy values (CAN commit)
config.py           # Loads from environment
```

**.env (LOCAL ONLY - Add to .gitignore):**
```bash
# Real values - NEVER commit this file
SECRET_KEY=a8f5f167f7c9c8d9e6f5e4d3c2b1a0918273645564738291
DATABASE_URL=postgresql://user:password@localhost/fitness_db
REDIS_URL=redis://localhost:6379
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**.env.example (TEMPLATE - Safe to commit):**
```bash
# Example values - Copy to .env and fill with real values
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
```

**config.py:**
```python
from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # AWS
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

# Usage
settings = get_settings()
SECRET_KEY = settings.secret_key  # Loaded from environment
```

---

## Knowledge Gap Study Guide

Based on our discussion, here are the key areas to study:

### 1. Web Security Fundamentals
**Topics:**
- Authentication vs Authorization
- OWASP Top 10
- SQL Injection & XSS Prevention
- HTTPS/TLS

**Resources:**
- [OWASP Security Cheat Sheets](https://cheatsheetseries.owasp.org/)
- Course: "Web Security Fundamentals" on Pluralsight

### 2. API Development
**Topics:**
- REST principles
- HTTP methods & status codes
- API versioning
- Rate limiting

**Resources:**
- Book: "Designing Web APIs" by Brenda Jin
- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/

### 3. Database Design
**Topics:**
- Normalization
- Indexes & Performance
- Transactions
- Migration strategies

**Resources:**
- Course: "Database Design" on Coursera
- PostgreSQL Documentation

### 4. Sports Science Basics
**Topics:**
- Training load principles
- Recovery science
- Performance metrics
- Injury prevention

**Resources:**
- Book: "Science and Application of High-Intensity Interval Training" by Laursen & Buchheit
- Course: "Sports Performance Analytics" on Coursera

### 5. Data Visualization
**Topics:**
- Chart selection
- Dashboard UX principles
- Real-time updates
- Mobile responsiveness

**Resources:**
- Book: "Storytelling with Data" by Cole Nussbaumer Knaflic
- D3.js tutorials

### 6. DevOps Basics
**Topics:**
- Docker containers
- CI/CD pipelines
- Monitoring & logging
- Cloud deployment

**Resources:**
- Docker Documentation
- GitHub Actions tutorials

---

## Veo Game Footage Integration

Your Veo footage could be valuable for:

1. **Performance Context**: Link training load to match performance
2. **Injury Analysis**: Review footage before injuries occurred
3. **Recovery Validation**: Compare performance after different recovery protocols

However, this would be Phase 2 after core metrics are working:
```python
# Future integration example
class MatchPerformance(BaseModel):
    match_id: str
    veo_video_id: str
    distance_covered: float
    sprint_count: int
    high_intensity_runs: int
    
    # Link to training data
    acwr_at_match: float
    readiness_score: float
```

---

## Action Items & Timeline

Given your 7-8 month timeline for Spring 2026:

**Months 1-2 (Now - October):**
- Complete authentication system
- Build basic data upload
- Create simple ACWR calculations

**Months 3-4 (November - December):**
- Add wellness tracking
- Build first dashboard
- Start testing with your team

**Months 5-6 (January - February):**
- Add team features
- Integrate with wearables
- Polish UI/UX

**Month 7-8 (March - April):**
- NCAA team pilots
- Performance optimization
- Documentation

This gives you buffer time before the critical January 2027 deadline.