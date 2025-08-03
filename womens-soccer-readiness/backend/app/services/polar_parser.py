import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
from sqlalchemy.orm import Session
from .. import models
import logging

logger = logging.getLogger(__name__)

class PolarCSVParser:
    """
    Parser for Polar Team Pro CSV exports.
    
    Teaching moment: Why a class instead of functions?
    - Encapsulates parsing logic and state
    - Easy to extend for different Polar formats
    - Testable in isolation
    """
    
    # Expected columns in Polar CSV (adjust based on actual exports)
    REQUIRED_COLUMNS = {
        'Date', 'Name', 'Duration', 'Distance', 
        'HR Average', 'HR Max', 'Training Load'
    }
    
    def __init__(self, db: Session, team_id: str):
        self.db = db
        self.team_id = team_id
        self.errors: List[str] = []
        
    def parse_csv(self, file_path: str) -> Dict[str, any]:
        """
        Parse Polar CSV and return structured data.
        
        Why pandas? Built for this exact use case - CSV parsing,
        data cleaning, and transformation.
        """
        try:
            # Read CSV with error handling
            df = pd.read_csv(file_path, parse_dates=['Date'])
            
            # Validate required columns
            missing_cols = self.REQUIRED_COLUMNS - set(df.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Clean and transform data
            df['Duration_Minutes'] = pd.to_timedelta(df['Duration']).dt.total_seconds() / 60
            df['Distance_KM'] = pd.to_numeric(df['Distance'], errors='coerce')
            df['HR_Average'] = pd.to_numeric(df['HR Average'], errors='coerce')
            df['HR_Max'] = pd.to_numeric(df['HR Max'], errors='coerce')
            df['Training_Load'] = pd.to_numeric(df['Training Load'], errors='coerce')
            
            # Group by player
            sessions_by_player = []
            for name, player_data in df.groupby('Name'):
                player = self._get_or_create_player(name)
                if player:
                    sessions = self._create_training_sessions(player.id, player_data)
                    sessions_by_player.append({
                        'player': player,
                        'sessions': sessions
                    })
            
            return {
                'success': True,
                'sessions_count': len(df),
                'players_count': df['Name'].nunique(),
                'data': sessions_by_player,
                'errors': self.errors
            }
            
        except Exception as e:
            logger.error(f"Error parsing Polar CSV: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'errors': self.errors
            }
    
    def _get_or_create_player(self, name: str) -> Optional[models.Player]:
        """
        Find player by name or create new one.
        
        Design decision: Using name matching for MVP.
        Production should use unique IDs or email.
        """
        # Normalize name for matching
        normalized_name = name.strip().lower()
        
        player = self.db.query(models.Player).filter(
            models.Player.team_id == self.team_id,
            models.Player.name.ilike(f"%{normalized_name}%")
        ).first()
        
        if not player:
            # Auto-create player (with confirmation in production)
            try:
                player = models.Player(
                    team_id=self.team_id,
                    name=name,
                    email=f"{normalized_name.replace(' ', '.')}@team.placeholder",
                    position="Unknown",  # Coach can update later
                    active=True
                )
                self.db.add(player)
                self.db.flush()  # Get ID without committing
                logger.info(f"Created new player: {name}")
            except Exception as e:
                self.errors.append(f"Failed to create player {name}: {str(e)}")
                return None
                
        return player
    
    def _create_training_sessions(self, player_id: str, sessions_df: pd.DataFrame) -> List[models.TrainingSession]:
        """
        Create training session records from player data.
        
        Why return a list? Allows for batch operations and 
        validation before committing to database.
        """
        sessions = []
        
        for _, row in sessions_df.iterrows():
            # Generate unique hash to prevent duplicates
            session_hash = self._generate_session_hash(player_id, row)
            
            # Check if session already exists
            existing = self.db.query(models.TrainingSession).filter(
                models.TrainingSession.import_hash == session_hash
            ).first()
            
            if existing:
                logger.debug(f"Session already exists for player {player_id} on {row['Date']}")
                continue
            
            try:
                session = models.TrainingSession(
                    player_id=player_id,
                    session_date=row['Date'],
                    duration_minutes=row['Duration_Minutes'],
                    distance_km=row['Distance_KM'],
                    avg_heart_rate=row['HR_Average'],
                    max_heart_rate=row['HR_Max'],
                    training_load=row['Training_Load'],
                    session_type=self._classify_session_type(row),
                    import_hash=session_hash,
                    raw_data=row.to_dict()  # Store original for debugging
                )
                sessions.append(session)
                
            except Exception as e:
                self.errors.append(f"Failed to create session for {row['Date']}: {str(e)}")
                
        return sessions
    
    def _generate_session_hash(self, player_id: str, row: pd.Series) -> str:
        """
        Generate unique hash for session to prevent duplicates.
        
        Teaching point: Always implement idempotency for imports!
        Users WILL upload the same file multiple times.
        """
        hash_string = f"{player_id}|{row['Date']}|{row['Duration']}|{row['Training Load']}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _classify_session_type(self, row: pd.Series) -> str:
        """
        Classify training session type based on metrics.
        
        This is a simple heuristic - production should use
        coach-defined rules or ML classification.
        """
        duration = row['Duration_Minutes']
        training_load = row['Training_Load']
        
        if duration < 30:
            return "Recovery"
        elif training_load > 300:
            return "High Intensity"
        elif duration > 90:
            return "Endurance"
        else:
            return "Regular Training"
    
    def commit_sessions(self) -> bool:
        """Commit all parsed sessions to database."""
        try:
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to commit sessions: {str(e)}")
            self.db.rollback()
            return False