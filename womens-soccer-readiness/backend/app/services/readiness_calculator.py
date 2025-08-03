from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
import logging

logger = logging.getLogger(__name__)

class ReadinessCalculator:
    """
    Calculate player readiness based on training load, wellness, and cycle data.
    
    Teaching moment: This is your SECRET SAUCE. The algorithm here
    determines if coaches trust your product.
    """
    
    # ACWR thresholds based on sports science research
    ACWR_SWEET_SPOT = (0.8, 1.3)  # Optimal range
    ACWR_DANGER_ZONE_LOW = 0.8    # Undertraining
    ACWR_DANGER_ZONE_HIGH = 1.5   # Injury risk spike
    
    # Readiness score weights (must sum to 1.0)
    WEIGHTS = {
        'acwr': 0.40,          # Training load ratio
        'wellness': 0.30,      # Self-reported wellness
        'recovery': 0.20,      # Time since last session
        'cycle': 0.10          # Menstrual cycle phase
    }
    
    def __init__(self, db: Session):
        self.db = db
        
    def calculate_team_readiness(self, team_id: str, date: datetime) -> Dict[str, any]:
        """
        Calculate readiness for entire team on given date.
        
        Why team-level? Coaches need the 30,000 foot view first,
        then drill down to individuals.
        """
        players = self.db.query(models.Player).filter(
            models.Player.team_id == team_id,
            models.Player.active == True
        ).all()
        
        team_scores = []
        flagged_players = []
        
        for player in players:
            readiness = self.calculate_player_readiness(player.id, date)
            team_scores.append(readiness)
            
            if readiness['flag'] != 'green':
                flagged_players.append({
                    'player': player,
                    'readiness': readiness
                })
        
        # Calculate team aggregates
        avg_score = np.mean([r['overall_score'] for r in team_scores])
        
        return {
            'date': date,
            'team_id': team_id,
            'average_readiness': avg_score,
            'player_count': len(players),
            'green_count': sum(1 for r in team_scores if r['flag'] == 'green'),
            'yellow_count': sum(1 for r in team_scores if r['flag'] == 'yellow'),
            'red_count': sum(1 for r in team_scores if r['flag'] == 'red'),
            'flagged_players': flagged_players,
            'player_scores': team_scores
        }
    
    def calculate_player_readiness(self, player_id: str, date: datetime) -> Dict[str, any]:
        """
        Calculate individual player readiness.
        
        This is where the magic happens - combining multiple
        data sources into one actionable score.
        """
        # Get component scores
        acwr, acwr_details = self._calculate_acwr(player_id, date)
        wellness_score = self._get_wellness_score(player_id, date)
        recovery_score = self._calculate_recovery_score(player_id, date)
        cycle_adjustment = self._get_cycle_adjustment(player_id, date)
        
        # Calculate weighted overall score
        overall_score = (
            self.WEIGHTS['acwr'] * self._normalize_acwr(acwr) +
            self.WEIGHTS['wellness'] * wellness_score +
            self.WEIGHTS['recovery'] * recovery_score +
            self.WEIGHTS['cycle'] * cycle_adjustment
        )
        
        # Determine flag color
        flag = self._determine_flag(overall_score, acwr, wellness_score)
        
        # Get recommendations
        recommendations = self._generate_recommendations(
            overall_score, acwr, wellness_score, recovery_score
        )
        
        return {
            'player_id': player_id,
            'date': date,
            'overall_score': round(overall_score, 2),
            'flag': flag,
            'components': {
                'acwr': round(acwr, 2),
                'acwr_normalized': round(self._normalize_acwr(acwr), 2),
                'wellness': round(wellness_score, 2),
                'recovery': round(recovery_score, 2),
                'cycle_adjustment': round(cycle_adjustment, 2)
            },
            'details': {
                'acute_load': acwr_details['acute_load'],
                'chronic_load': acwr_details['chronic_load'],
                'days_since_last_session': acwr_details.get('days_since_last', 0)
            },
            'recommendations': recommendations
        }
    
    def _calculate_acwr(self, player_id: str, date: datetime) -> Tuple[float, Dict]:
        """
        Calculate Acute:Chronic Workload Ratio.
        
        Why 7:28? Research shows 7-day acute load vs 28-day chronic
        load best predicts injury risk.
        """
        # Define windows
        acute_start = date - timedelta(days=7)
        chronic_start = date - timedelta(days=28)
        
        # Get training sessions
        sessions = self.db.query(models.TrainingSession).filter(
            models.TrainingSession.player_id == player_id,
            models.TrainingSession.session_date >= chronic_start,
            models.TrainingSession.session_date <= date
        ).all()
        
        if not sessions:
            return 1.0, {'acute_load': 0, 'chronic_load': 0}
        
        # Convert to DataFrame for easier calculation
        df = pd.DataFrame([{
            'date': s.session_date,
            'load': s.training_load or 0
        } for s in sessions])
        
        # Calculate loads
        acute_mask = df['date'] >= acute_start
        acute_load = df[acute_mask]['load'].sum()
        chronic_load = df['load'].sum()
        
        # Calculate daily averages
        acute_daily = acute_load / 7
        chronic_daily = chronic_load / 28
        
        # Calculate ACWR (with protection against division by zero)
        if chronic_daily > 0:
            acwr = acute_daily / chronic_daily
        else:
            acwr = 1.0 if acute_daily == 0 else 1.5
        
        # Days since last session
        if len(df) > 0:
            last_session = df['date'].max()
            days_since_last = (date - last_session).days
        else:
            days_since_last = 99
        
        return acwr, {
            'acute_load': round(acute_load, 1),
            'chronic_load': round(chronic_load, 1),
            'acute_daily': round(acute_daily, 1),
            'chronic_daily': round(chronic_daily, 1),
            'days_since_last': days_since_last
        }
    
    def _normalize_acwr(self, acwr: float) -> float:
        """
        Normalize ACWR to 0-100 scale.
        
        Teaching point: Users understand 0-100 better than 0.8-1.5.
        Always translate technical metrics to human-friendly scales.
        """
        if self.ACWR_SWEET_SPOT[0] <= acwr <= self.ACWR_SWEET_SPOT[1]:
            # In sweet spot: map to 80-100
            return 80 + (acwr - self.ACWR_SWEET_SPOT[0]) * 20 / (self.ACWR_SWEET_SPOT[1] - self.ACWR_SWEET_SPOT[0])
        elif acwr < self.ACWR_SWEET_SPOT[0]:
            # Below sweet spot: map to 0-80
            return max(0, acwr * 80 / self.ACWR_SWEET_SPOT[0])
        else:
            # Above sweet spot: map to 0-80 (inverse)
            excess = acwr - self.ACWR_SWEET_SPOT[1]
            return max(0, 80 - excess * 80 / (self.ACWR_DANGER_ZONE_HIGH - self.ACWR_SWEET_SPOT[1]))
    
    def _get_wellness_score(self, player_id: str, date: datetime) -> float:
        """Get most recent wellness check score."""
        wellness = self.db.query(models.WellnessCheck).filter(
            models.WellnessCheck.player_id == player_id,
            models.WellnessCheck.check_date <= date
        ).order_by(models.WellnessCheck.check_date.desc()).first()
        
        if not wellness or (date - wellness.check_date).days > 1:
            # No recent wellness check
            return 70.0  # Neutral default
        
        # Average of wellness metrics (each 1-10 scale)
        scores = [
            wellness.sleep_quality,
            wellness.energy_level,
            wellness.muscle_soreness,
            wellness.stress_level,
            wellness.mood
        ]
        
        # Convert to 0-100 scale
        return np.mean([s for s in scores if s is not None]) * 10
    
    def _calculate_recovery_score(self, player_id: str, date: datetime) -> float:
        """
        Calculate recovery based on time since last session.
        
        Why this matters: Adequate recovery prevents overtraining.
        Too much recovery leads to detraining.
        """
        last_session = self.db.query(models.TrainingSession).filter(
            models.TrainingSession.player_id == player_id,
            models.TrainingSession.session_date < date
        ).order_by(models.TrainingSession.session_date.desc()).first()
        
        if not last_session:
            return 100.0  # Fully recovered
        
        days_since = (date - last_session.session_date).days
        
        if days_since == 0:
            return 40.0  # Same day training
        elif days_since == 1:
            return 70.0  # Standard recovery
        elif days_since == 2:
            return 90.0  # Good recovery
        elif days_since >= 3:
            return 100.0  # Full recovery
    
    def _get_cycle_adjustment(self, player_id: str, date: datetime) -> float:
        """
        Adjust readiness based on menstrual cycle phase.
        
        Critical for women's sports: Performance varies by cycle phase.
        This is your competitive advantage over generic tools.
        """
        # For MVP: Simple adjustment. Production: Use cycle tracking integration
        return 85.0  # Neutral for now
    
    def _determine_flag(self, overall_score: float, acwr: float, wellness: float) -> str:
        """
        Determine flag color based on multiple factors.
        
        Business logic: Conservative flagging prevents injuries
        but too conservative frustrates coaches.
        """
        # Red flags (immediate attention)
        if overall_score < 60:
            return 'red'
        if acwr > self.ACWR_DANGER_ZONE_HIGH:
            return 'red'
        if wellness < 40:
            return 'red'
        
        # Yellow flags (caution)
        if overall_score < 75:
            return 'yellow'
        if acwr < self.ACWR_DANGER_ZONE_LOW or acwr > self.ACWR_SWEET_SPOT[1]:
            return 'yellow'
        if wellness < 60:
            return 'yellow'
        
        # Green flag (good to go)
        return 'green'
    
    def _generate_recommendations(self, overall: float, acwr: float, 
                                 wellness: float, recovery: float) -> List[str]:
        """Generate actionable recommendations for coaches."""
        recommendations = []
        
        if acwr > self.ACWR_DANGER_ZONE_HIGH:
            recommendations.append("⚠️ High injury risk - reduce training load")
        elif acwr > self.ACWR_SWEET_SPOT[1]:
            recommendations.append("📊 Monitor closely - approaching high load")
        elif acwr < self.ACWR_DANGER_ZONE_LOW:
            recommendations.append("📈 Can increase training load safely")
        
        if wellness < 60:
            recommendations.append("😴 Check in on sleep and stress levels")
        
        if recovery < 70:
            recommendations.append("⏱️ Consider lighter session or recovery work")
        
        if not recommendations:
            recommendations.append("✅ Ready for normal training")
        
        return recommendations