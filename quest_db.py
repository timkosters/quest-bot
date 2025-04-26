from sqlalchemy import create_engine, text
from typing import List
import os
import logging
import traceback

logger = logging.getLogger(__name__)

class QuestBotDB:
    def __init__(self):
        # Try Railway's DATABASE_URL first, then fall back to QUEST_BOT_DATABASE_URL
        db_url = os.getenv('DATABASE_URL') or os.getenv('QUEST_BOT_DATABASE_URL')
        if not db_url:
            logger.warning("No database URL found - database features will be disabled")
            return
        try:
            self.engine = create_engine(db_url)
            logger.info("Successfully connected to Quest Bot database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.engine = None

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

    def add_subscriber(self, user_id: int) -> tuple[bool, str | None]:
        """Add a new subscriber. Returns (success, error_message)."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot add subscriber")
            return False, "No database connection"
        try:
            query = text("""
                INSERT INTO subscribers (user_id)
                VALUES (:user_id)
                ON CONFLICT (user_id) DO NOTHING
            """)
            with self.engine.connect() as conn:
                conn.execute(query, {"user_id": user_id})
                conn.commit()
            return True, None
        except Exception as e:
            logger.error(f"Error adding subscriber {user_id}: {e}")
            logger.error(traceback.format_exc())
            return False, str(e)

    def set_mood(self, user_id: int, mood: str) -> bool:
        """Set the mood for a user."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot set mood")
            return False
        try:
            query = text("""
                UPDATE subscribers SET mood = :mood WHERE user_id = :user_id
            """)
            with self.engine.connect() as conn:
                conn.execute(query, {"user_id": user_id, "mood": mood})
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting mood for {user_id}: {e}")
            logger.error(traceback.format_exc())
            return False

    def get_mood(self, user_id: int) -> str:
        """Get the mood for a user. Returns None if not set."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot get mood")
            return None
        try:
            query = text("SELECT mood FROM subscribers WHERE user_id = :user_id")
            with self.engine.connect() as conn:
                result = conn.execute(query, {"user_id": user_id})
                row = result.fetchone()
                return row[0] if row and row[0] else None
        except Exception as e:
            logger.error(f"Error getting mood for {user_id}: {e}")
            logger.error(traceback.format_exc())
            return None

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