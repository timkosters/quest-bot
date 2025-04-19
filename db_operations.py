from sqlalchemy import create_engine, text
from typing import List, Dict
import os
import logging

logger = logging.getLogger(__name__)

class EdgeOSDB:
    def __init__(self):
        db_url = os.getenv('EDGEOS_DATABASE_URL')
        if not db_url:
            logger.warning("EDGEOS_DATABASE_URL not set - EdgeOS features will be disabled")
            return
        try:
            self.engine = create_engine(db_url)
            logger.info("Successfully connected to EdgeOS database")
        except Exception as e:
            logger.error(f"Failed to connect to EdgeOS database: {e}")
            self.engine = None

    def get_popup_citizens(self, popup_id: str) -> List[Dict]:
        """
        Get all citizens for a specific popup city.
        Returns list of dictionaries with citizen info.
        """
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot fetch citizens")
            return []
            
        try:
            query = text("""
                SELECT DISTINCT c.*
                FROM citizens c
                JOIN applications a ON a.citizen_id = c.id
                WHERE a.popup_id = :popup_id
                AND a.final_status = 'ACCEPTED'
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"popup_id": popup_id})
                citizens = [dict(row) for row in result]
                return citizens
        except Exception as e:
            logger.error(f"Error fetching citizens for popup {popup_id}: {e}")
            return []

    def get_popups(self) -> List[Dict]:
        """
        Get all available popups.
        Returns list of dictionaries with popup info.
        """
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot fetch popups")
            return []
            
        try:
            query = text("SELECT id, name, description FROM popups WHERE is_active = true")
            with self.engine.connect() as conn:
                result = conn.execute(query)
                popups = [dict(row) for row in result]
                return popups
        except Exception as e:
            logger.error(f"Error fetching popups: {e}")
            return []

    def get_citizen_telegram(self, citizen_id: str) -> str:
        """
        Get citizen's Telegram ID if available.
        """
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot fetch Telegram ID")
            return None
            
        try:
            query = text("""
                SELECT telegram_id 
                FROM citizens 
                WHERE id = :citizen_id 
                AND telegram_id IS NOT NULL
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"citizen_id": citizen_id})
                row = result.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Error fetching Telegram ID for citizen {citizen_id}: {e}")
            return None 