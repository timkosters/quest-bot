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
        """Create the subscribers table if it doesn't exist, with all required columns."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot create subscribers table")
            return False
        try:
            logger.info("Attempting to create subscribers table if not exists...")
            query = text("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    user_id BIGINT PRIMARY KEY,
                    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    mood TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    quests_completed INTEGER DEFAULT 0
                );
            """)
            with self.engine.connect() as conn:
                conn.execute(query)
                conn.commit()
            logger.info("Subscribers table checked/created successfully.")
            return True
        except Exception as e:
            logger.error(f"Error creating subscribers table: {e}")
            logger.error(traceback.format_exc())
            return False

    def ensure_subscribers_schema(self):
        """Ensure all required columns exist in the subscribers table. Adds any missing columns."""
        required_columns = {
            'mood': "TEXT",
            'first_name': "TEXT",
            'last_name': "TEXT",
            'username': "TEXT",
            'quests_completed': "INTEGER DEFAULT 0"
        }
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot check subscribers schema")
            return
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='subscribers'"))
                existing_columns = {row[0] for row in result}
                for col, coltype in required_columns.items():
                    if col not in existing_columns:
                        logger.info(f"Adding missing column '{col}' to subscribers table.")
                        alter = text(f"ALTER TABLE subscribers ADD COLUMN {col} {coltype}")
                        conn.execute(alter)
                        conn.commit()
        except Exception as e:
            logger.error(f"Error ensuring subscribers schema: {e}")
            logger.error(traceback.format_exc())

    def add_subscriber(self, user_id: int, first_name: str = None, last_name: str = None, username: str = None) -> tuple[bool, str | None]:
        """Add a new subscriber. Returns (success, error_message)."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot add subscriber")
            return False, "No database connection"
        try:
            query = text("""
                INSERT INTO subscribers (user_id, first_name, last_name, username)
                VALUES (:user_id, :first_name, :last_name, :username)
                ON CONFLICT (user_id) DO NOTHING
            """)
            with self.engine.connect() as conn:
                conn.execute(query, {
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username
                })
                conn.commit()
            return True, None
        except Exception as e:
            logger.error(f"Error adding subscriber {user_id}: {e}")
            logger.error(traceback.format_exc())
            return False, str(e)

    def update_user_info(self, user_id: int, first_name: str = None, last_name: str = None, username: str = None):
        """Update a user's first_name, last_name, or username."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot update user info")
            return False
        try:
            query = text("""
                UPDATE subscribers
                SET first_name = COALESCE(:first_name, first_name),
                    last_name = COALESCE(:last_name, last_name),
                    username = COALESCE(:username, username)
                WHERE user_id = :user_id
            """)
            with self.engine.connect() as conn:
                conn.execute(query, {
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username
                })
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating user info for {user_id}: {e}")
            logger.error(traceback.format_exc())
            return False

    def increment_quests_completed(self, user_id: int):
        """Increment quests_completed for a user."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot increment quests_completed")
            return False
        try:
            logger.info(f"Incrementing quests_completed for user_id {user_id}...")
            query = text("""
                INSERT INTO subscribers (user_id, quests_completed)
                VALUES (:user_id, 1)
                ON CONFLICT (user_id) DO UPDATE SET quests_completed = subscribers.quests_completed + 1
            """)
            with self.engine.connect() as conn:
                conn.execute(query, {"user_id": user_id})
                conn.commit()
            logger.info(f"quests_completed incremented for user_id {user_id}.")
            return True
        except Exception as e:
            logger.error(f"Error incrementing quests_completed for {user_id}: {e}")
            logger.error(traceback.format_exc())
            return False

    def get_quests_completed(self, user_id: int) -> int:
        """Get the number of quests completed by a user."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot fetch quests_completed")
            return 0
        try:
            logger.info(f"Fetching quests_completed for user_id {user_id}...")
            query = text("SELECT quests_completed FROM subscribers WHERE user_id = :user_id")
            with self.engine.connect() as conn:
                result = conn.execute(query, {"user_id": user_id})
                row = result.fetchone()
                if row and row[0] is not None:
                    logger.info(f"quests_completed for user_id {user_id}: {row[0]}")
                    return row[0]
                else:
                    logger.info(f"No quests_completed found for user_id {user_id}, returning 0.")
                    return 0
        except Exception as e:
            logger.error(f"Error fetching quests_completed for {user_id}: {e}")
            logger.error(traceback.format_exc())
            return 0

    def get_leaderboard(self, limit: int = 10):
        """Return a list of top users by quests_completed."""
        if not hasattr(self, 'engine') or not self.engine:
            logger.warning("No database connection - cannot get leaderboard")
            return []
        try:
            query = text("""
                SELECT user_id, first_name, username, quests_completed
                FROM subscribers
                ORDER BY quests_completed DESC NULLS LAST, user_id ASC
                LIMIT :limit
            """)    
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                return result.fetchall()
        except Exception as e:
            logger.error(f"Error fetching leaderboard: {e}")
            logger.error(traceback.format_exc())
            return []

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