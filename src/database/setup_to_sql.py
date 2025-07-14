from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from src.database.sqlite_database import StrategoDatabase, get_db_connection
from src.checks.staging_consistency_checks import check_piece_consistency

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SetupProcessor:
    """Processes Stratego game setups and stores them in the database."""
    
    def __init__(self, database: Optional[StrategoDatabase] = None):
        """
        Initialize the setup processor.
        
        Args:
            database: Optional database instance. If None, creates a new one.
        """
        self.db = database or StrategoDatabase()
        self.temp_setup_id = 1
    
    def process_setup(self, setup_details: Dict[str, Any]) -> int:
        """
        Process a complete game setup and store it in the database.
        
        Args:
            setup_details: Dictionary containing game details including setup, date, opponent, etc.
            
        Returns:
            The setup_id that was used for storing the game record.
            
        Raises:
            ValueError: If setup_details is invalid
            DatabaseError: If database operations fail
        """
        try:
            logger.info(f"Processing setup for opponent: {setup_details.get('opponent_name', 'Unknown')}")
            
            # Validate input
            self._validate_setup_details(setup_details)
            
            new_setup_id = self.db.determine_new_setup_id_from_game_setups()
            json_setup = setup_details["setup"]
            
            # Process setup through staging
            self._stage_setup(json_setup)
            self._check_consistency()
            
            # Check for duplicates
            duplicate_setup_id = self.db.check_duplicate_setup()
            
            if duplicate_setup_id is None:
                # New unique setup
                self._save_new_setup(json_setup, new_setup_id)
                used_setup_id = new_setup_id
                logger.info(f"Created new setup with ID: {new_setup_id}")
            else:
                # Existing setup found
                used_setup_id = duplicate_setup_id
                logger.info(f"Using existing setup with ID: {duplicate_setup_id}")
            
            # Save game record
            self._save_game_record(setup_details, used_setup_id)
            
            # Clean up staging
            self.db.delete_from_temp_setup()
            
            logger.info(f"Successfully processed setup, used setup_id: {used_setup_id}")
            return used_setup_id
            
        except Exception as e:
            logger.error(f"Error processing setup: {e}")
            # Clean up staging on error
            try:
                self.db.delete_from_temp_setup()
            except:
                pass
            raise
    
    def _validate_setup_details(self, setup_details: Dict[str, Any]) -> None:
        """Validate the setup details dictionary."""
        required_fields = ['setup', 'date_played', 'opponent_name', 'result', 'moves', 'noob_killer']
        
        for field in required_fields:
            if field not in setup_details:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate setup structure
        setup = setup_details['setup']
        if not isinstance(setup, dict):
            raise ValueError("Setup must be a dictionary")
        
        # Validate that we have 4 rows
        if len(setup) != 4:
            raise ValueError(f"Setup must have exactly 4 rows, got {len(setup)}")
        
        # Validate each row has 10 pieces
        for row_num, pieces in setup.items():
            if len(pieces) != 10:
                raise ValueError(f"Row {row_num} must have exactly 10 pieces, got {len(pieces)}")
    
    def _stage_setup(self, json_setup: Dict[str, List[str]]) -> None:
        """Stage the setup in the temporary table."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for row, values in json_setup.items():
                for index, value in enumerate(values):
                    cursor.execute(
                        "INSERT INTO TempSetup (setup_id, row, col, piece) VALUES (?, ?, ?, ?)",
                        (self.temp_setup_id, int(row), index + 1, str(value))
                    )
            conn.commit()
    
    def _check_consistency(self) -> None:
        """Check the staged setup for piece consistency."""
        pieces = self.db.select_pieces_from_staging_setup(self.temp_setup_id)
        check_piece_consistency(pieces)
    
    def _save_new_setup(self, json_setup: Dict[str, List[str]], setup_id: int) -> None:
        """Save a new setup to the GameSetups table."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for row, values in json_setup.items():
                for index, value in enumerate(values):
                    cursor.execute(
                        "INSERT INTO GameSetups (setup_id, row, col, piece) VALUES (?, ?, ?, ?)",
                        (setup_id, int(row), index + 1, str(value))
                    )
            conn.commit()
    
    def _save_game_record(self, setup_details: Dict[str, Any], setup_id: int) -> None:
        """Save the game record to the GameRecords table."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Handle optional fields
            opponent_id = setup_details.get('opponent_id')
            noob_killer = setup_details['noob_killer']
            
            cursor.execute(
                "INSERT INTO GameRecords (setup_id, date_played, opponent_id, opponent_name, result, moves, noob_killer) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (setup_id,
                 setup_details["date_played"],
                 opponent_id,
                 setup_details["opponent_name"],
                 setup_details["result"],
                 setup_details["moves"],
                 noob_killer)
            )
            conn.commit()


def process_game_setup(setup_details: Dict[str, Any]) -> int:
    """
    Convenience function to process a game setup.
    
    Args:
        setup_details: Dictionary containing game details
        
    Returns:
        The setup_id used for the game record
    """
    processor = SetupProcessor()
    return processor.process_setup(setup_details)


# Example usage (for testing purposes only)
def _create_sample_setup() -> Dict[str, Any]:
    """Create a sample setup for testing purposes."""
    return {
        'date_played': datetime(2025, 4, 24, 0, 0),
        'opponent_id': 10,
        'opponent_name': 'Sekertzis1973',
        'result': 'win',
        'moves': 777,
        'noob_killer': 1,
        'setup': {
            '1': ['6', '2', '6', '4', '8', '2', '5', '2', '2', '5'],
            '2': ['3', '5', '2', '9', '7', '5', '2', 'B', '4', '8'],
            '3': ['B', '2', '7', '1', '6', '2', '7', '10', '6', '3'],
            '4': ['B', '4', 'B', '3', 'B', '3', 'B', '4', '3', 'F']
        }
    }


if __name__ == "__main__":
    # Only run if this file is executed directly
    sample_setup = _create_sample_setup()
    try:
        setup_id = process_game_setup(sample_setup)
        print(f"Setup processed successfully with ID: {setup_id}")
    except Exception as e:
        print(f"Error processing setup: {e}")