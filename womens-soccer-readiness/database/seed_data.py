#!/usr/bin/env python3
"""
Generate synthetic data for 20 players over 10 weeks.
This creates realistic training and wellness data for testing.
"""

import os
import sys
import random
import uuid
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
import hashlib

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models import Team, User, Player, TrainingSession, WellnessCheck, ReadinessScore
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Constants for data generation
POSITIONS = ["GK", "DEF", "MID", "FWD"]
CYCLE_PHASES = ["menstrual", "follicular", "ovulation", "luteal"]
SESSION_TYPES = ["training", "match", "recovery"]

def random_date(start: date, end: date) -> date:
    """Generate a random date between start and end"""
    time_between = end - start
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start + timedelta(days=random_days)

def generate_hr_zones(avg_hr: int, max_hr: int) -> Dict[str, int]:
    """Generate time spent in each heart rate zone"""
    zones = {
        "zone1": random.randint(5, 15),  # Recovery
        "zone2": random.randint(20, 40),  # Aerobic
        "zone3": random.randint(15, 30),  # Threshold
        "zone4": random.randint(10, 20),  # VO2 Max
        "zone5": random.randint(5, 15),   # Max
    }
    # Normalize to 100%
    total = sum(zones.values())
    return {k: int(v * 100 / total) for k, v in zones.items()}

def calculate_training_load(duration: int, avg_hr: int, max_hr: int) -> float:
    """Simple training load calculation"""
    intensity = avg_hr / max_hr
    return round(duration * intensity * random.uniform(0.8, 1.2), 2)

def calculate_readiness_scores(
    training_loads: List[float],
    wellness: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate readiness scores based on training and wellness data"""
    # Acute load (7-day average)
    acute_load = sum(training_loads[-7:]) / min(len(training_loads[-7:]), 7) if training_loads else 0
    
    # Chronic load (28-day average)
    chronic_load = sum(training_loads) / len(training_loads) if training_loads else 0
    
    # ACWR
    acwr = acute_load / chronic_load if chronic_load > 0 else 1.0
    
    # Wellness score (normalized 0-100)
    wellness_factors = [
        wellness.get("sleep_quality", 3) * 20,
        (6 - wellness.get("fatigue", 3)) * 20,
        (6 - wellness.get("soreness", 3)) * 20,
        wellness.get("mood", 3) * 20,
        wellness.get("hydration", 3) * 20,
    ]
    wellness_score = sum(wellness_factors) / 5
    
    # Training load score (based on ACWR)
    if acwr < 0.8:
        training_load_score = 70  # Undertraining
    elif acwr <= 1.3:
        training_load_score = 90  # Optimal
    elif acwr <= 1.5:
        training_load_score = 60  # Caution
    else:
        training_load_score = 30  # High risk
    
    # Recovery score (random for now)
    recovery_score = random.uniform(60, 95)
    
    # Overall score
    overall_score = (wellness_score * 0.4 + training_load_score * 0.4 + recovery_score * 0.2)
    
    # Readiness flag
    if overall_score >= 80:
        flag = "green"
    elif overall_score >= 60:
        flag = "yellow"
    else:
        flag = "red"
    
    # Recommendations
    recommendations = []
    if acwr > 1.5:
        recommendations.append("High injury risk - reduce training load")
    if wellness.get("fatigue", 3) >= 4:
        recommendations.append("Consider recovery session or rest day")
    if wellness.get("sleep_hours", 7) < 6:
        recommendations.append("Prioritize sleep - aim for 8+ hours")
    
    return {
        "overall_score": round(overall_score, 2),
        "training_load_score": round(training_load_score, 2),
        "wellness_score": round(wellness_score, 2),
        "recovery_score": round(recovery_score, 2),
        "acute_load": round(acute_load, 2),
        "chronic_load": round(chronic_load, 2),
        "acwr": round(acwr, 2),
        "readiness_flag": flag,
        "recommendations": recommendations
    }

def create_synthetic_data(db: Session):
    """Create synthetic data for testing"""
    print("Creating synthetic data...")
    
    # Create a test team
    team = Team(
        name="University Women's Soccer",
        organization="State University",
        level="NCAA D1"
    )
    db.add(team)
    db.commit()
    print(f"Created team: {team.name}")
    
    # Create a test coach user
    coach = User(
        email="coach@university.edu",
        password_hash=pwd_context.hash("password123"),
        full_name="Sarah Johnson",
        role="head_coach",
        team_id=team.team_id
    )
    db.add(coach)
    db.commit()
    print(f"Created coach user: {coach.email}")
    
    # Create 20 players
    players = []
    for i in range(20):
        player = Player(
            team_id=team.team_id,
            name=f"Player {i+1}",
            position=random.choice(POSITIONS),
            jersey_number=i+1,
            birth_date=date(2000 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
            baseline_rhr=random.randint(50, 70),
            baseline_hrv=random.uniform(40, 80),
            max_hr=random.randint(185, 200)
        )
        db.add(player)
        players.append(player)
    
    db.commit()
    print(f"Created {len(players)} players")
    
    # Generate 10 weeks of data
    start_date = date.today() - timedelta(weeks=10)
    
    for player in players:
        training_loads = []
        
        for week in range(10):
            week_start = start_date + timedelta(weeks=week)
            
            # Generate 4-6 training sessions per week
            num_sessions = random.randint(4, 6)
            for _ in range(num_sessions):
                session_date = random_date(week_start, week_start + timedelta(days=6))
                
                # Training session data
                session_type = random.choice(SESSION_TYPES)
                duration = random.randint(60, 120) if session_type == "training" else random.randint(90, 110)
                
                session = TrainingSession(
                    player_id=player.player_id,
                    date=session_date,
                    session_type=session_type,
                    duration_min=duration,
                    distance_m=random.uniform(3000, 8000),
                    high_speed_running_m=random.uniform(500, 2000),
                    sprint_distance_m=random.uniform(100, 500),
                    accelerations=random.randint(20, 60),
                    decelerations=random.randint(20, 60),
                    avg_hr=random.randint(130, 170),
                    max_hr=random.randint(170, player.max_hr),
                    hr_zones=generate_hr_zones(150, player.max_hr),
                    training_load=calculate_training_load(duration, 150, player.max_hr),
                    rpe=random.randint(4, 9)
                )
                db.add(session)
                training_loads.append(session.training_load)
            
            # Generate daily wellness checks
            for day in range(7):
                check_date = week_start + timedelta(days=day)
                
                wellness = WellnessCheck(
                    player_id=player.player_id,
                    date=check_date,
                    sleep_hours=random.uniform(5, 9),
                    sleep_quality=random.randint(1, 5),
                    soreness=random.randint(1, 5),
                    fatigue=random.randint(1, 5),
                    stress=random.randint(1, 5),
                    mood=random.randint(1, 5),
                    hydration=random.randint(2, 5),
                    nutrition_quality=random.randint(2, 5),
                    cycle_phase=random.choice(CYCLE_PHASES) if random.random() > 0.3 else None,
                    injury_status="healthy" if random.random() > 0.1 else "minor"
                )
                db.add(wellness)
                
                # Calculate readiness score
                wellness_data = {
                    "sleep_hours": wellness.sleep_hours,
                    "sleep_quality": wellness.sleep_quality,
                    "fatigue": wellness.fatigue,
                    "soreness": wellness.soreness,
                    "mood": wellness.mood,
                    "hydration": wellness.hydration
                }
                
                readiness_data = calculate_readiness_scores(training_loads, wellness_data)
                
                readiness = ReadinessScore(
                    player_id=player.player_id,
                    date=check_date,
                    **readiness_data
                )
                db.add(readiness)
    
    db.commit()
    print("Generated 10 weeks of training and wellness data")

def main():
    """Main function"""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_teams = db.query(Team).count()
        if existing_teams > 0:
            response = input("Data already exists. Clear and regenerate? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
            
            # Clear existing data
            db.query(ReadinessScore).delete()
            db.query(WellnessCheck).delete()
            db.query(TrainingSession).delete()
            db.query(Player).delete()
            db.query(User).delete()
            db.query(Team).delete()
            db.commit()
            print("Cleared existing data")
        
        # Create synthetic data
        create_synthetic_data(db)
        
        print("\nSynthetic data created successfully!")
        print("\nTest credentials:")
        print("Email: coach@university.edu")
        print("Password: password123")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()