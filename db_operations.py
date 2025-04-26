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

    def create_subscribers_table(self):
        """Create the subscribers table if it doesn't exist."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot create subscribers table")
            return False
            
        try:
            query = text("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    user_id BIGINT PRIMARY KEY,
                    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            with self.engine.connect() as conn:
                conn.execute(query)
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating subscribers table: {e}")
            return False

    def add_subscriber(self, user_id: int) -> bool:
        """Add a new subscriber."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot add subscriber")
            return False
            
        try:
            query = text("""
                INSERT INTO subscribers (user_id)
                VALUES (:user_id)
                ON CONFLICT (user_id) DO NOTHING
            """)
            
            with self.engine.connect() as conn:
                conn.execute(query, {"user_id": user_id})
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding subscriber {user_id}: {e}")
            return False

    def remove_subscriber(self, user_id: int) -> bool:
        """Remove a subscriber."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot remove subscriber")
            return False
            
        try:
            query = text("""
                DELETE FROM subscribers
                WHERE user_id = :user_id
            """)
            
            with self.engine.connect() as conn:
                conn.execute(query, {"user_id": user_id})
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing subscriber {user_id}: {e}")
            return False

    def get_all_subscribers(self) -> List[int]:
        """Get all subscriber user IDs."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot fetch subscribers")
            return []
            
        try:
            query = text("SELECT user_id FROM subscribers")
            with self.engine.connect() as conn:
                result = conn.execute(query)
                return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error fetching subscribers: {e}")
            return []

    def is_subscribed(self, user_id: int) -> bool:
        """Check if a user is subscribed."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot check subscription")
            return False
            
        try:
            query = text("""
                SELECT EXISTS(
                    SELECT 1 FROM subscribers WHERE user_id = :user_id
                )
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"user_id": user_id})
                return result.scalar()
        except Exception as e:
            logger.error(f"Error checking subscription for {user_id}: {e}")
            return False 