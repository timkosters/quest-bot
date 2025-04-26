from sqlalchemy import create_engine, text
from typing import List
import os
import logging

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