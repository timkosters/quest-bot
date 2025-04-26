import os
import logging
from datetime import datetime, time
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from ai_interactions import AIInteractions
from quest_db import QuestBotDB

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize AI and DB
try:
    ai = AIInteractions()
    db = QuestBotDB()
    db.create_subscribers_table()  # Ensure the subscribers table exists
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    ai = None
    db = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    keyboard = [
        [KeyboardButton("/subscribe"), KeyboardButton("/unsubscribe")],
        [KeyboardButton("/quest"), KeyboardButton("/help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "✨ Welcome to Daily Quests & Affirmations! ✨\n\n"
        "I'm your friendly companion for creating more mindful, joyful moments in your day. "
        "Think of me as your enthusiastic friend who's here to help you notice the magic in everyday moments! 🌟\n\n"
        "🌅 Every morning at 9 AM, subscribers receive:\n"
        "• A powerful personal affirmation to boost your spirit\n"
        "• A gentle quest to help you find moments of joy and presence\n\n"
        "These aren't about big changes - they're about finding little pockets of magic in your regular day. "
        "Like pausing to feel the sunlight on your face, or taking a moment to really notice the world around you. ✨\n\n"
        "Commands:\n"
        "🎯 /subscribe - Get daily messages at 9 AM\n"
        "🎲 /quest - Get an instant affirmation and quest\n"
        "❌ /unsubscribe - Stop daily messages\n"
        "❓ /help - Show more information",
        reply_markup=reply_markup
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribe to daily messages."""
    if not db:
        await update.message.reply_text("Sorry, the subscription service is currently unavailable.")
        return

    user = update.effective_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name if hasattr(user, 'last_name') else None
    username = user.username if hasattr(user, 'username') else None

    if not db.is_subscribed(user_id):
        success, error = db.add_subscriber(user_id, first_name, last_name, username)
        if success:
            await update.message.reply_text(
                "🌟 You're subscribed! You'll receive your first affirmation and quest "
                "tomorrow at 9 AM.\n\nCan't wait? Use /quest to get a fun permission slip right now!"
            )
        else:
            await update.message.reply_text(
                f"Sorry, there was an error subscribing you. Please try again later!\n\nError: {error}"
            )
    else:
        db.update_user_info(user_id, first_name, last_name, username)
        await update.message.reply_text(
            "✨ You're already subscribed! Use /quest to get a fun permission slip now!"
        )

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe from daily messages."""
    if not db:
        await update.message.reply_text("Sorry, the subscription service is currently unavailable.")
        return

    user_id = update.effective_user.id
    if db.is_subscribed(user_id):
        if db.remove_subscriber(user_id):
            await update.message.reply_text(
                "👋 You've been unsubscribed. You'll no longer receive daily messages.\n"
                "You can resubscribe anytime with /subscribe!"
            )
        else:
            await update.message.reply_text(
                "Sorry, there was an error unsubscribing you. Please try again later!"
            )
    else:
        await update.message.reply_text(
            "You're not currently subscribed to daily messages."
        )

async def quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send an affirmation and quest immediately."""
    if not ai:
        await update.message.reply_text("Sorry, the AI service is currently unavailable.")
        return

    user = update.effective_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name if hasattr(user, 'last_name') else None
    username = user.username if hasattr(user, 'username') else None
    db.update_user_info(user_id, first_name, last_name, username)

    try:
        mood = db.get_mood(user_id) or "Surprise me"
        permission_slip = ai.generate_permission_slip(mood)
        await update.message.reply_text(permission_slip)
    except Exception as e:
        logger.error(f"Error generating quest: {e}")
        await update.message.reply_text(
            "Sorry, I couldn't generate your quest right now. Please try again later!"
        )

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get today's affirmation and quest immediately."""
    if not ai:
        await update.message.reply_text("Sorry, the AI service is currently unavailable.")
        return

    try:
        daily_message = ai.generate_daily_message()
        await update.message.reply_text(daily_message)
    except Exception as e:
        logger.error(f"Error sending daily message: {e}")
        await update.message.reply_text(
            "Sorry, I couldn't generate today's message. Please try again later!"
        )

async def send_daily_messages(context: ContextTypes.DEFAULT_TYPE):
    """Send daily affirmations and quests to all subscribers."""
    if not ai or not db:
        logger.error("Required services are not available")
        return

    try:
        subscribers = db.get_all_subscribers()
        if not subscribers:
            logger.info("No subscribers to send messages to")
            return

        for user_id in subscribers:
            try:
                mood = db.get_mood(user_id) or "Surprise me"
                daily_message = ai.generate_permission_slip(mood)
                await context.bot.send_message(chat_id=user_id, text=daily_message)
                logger.info(f"Sent daily message to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
    except Exception as e:
        logger.error(f"Error generating daily message: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "🌟 Daily Quests & Affirmations Help 🌟\n\n"
        "Every morning at 9 AM, subscribers receive:\n"
        "• A personal affirmation to boost their day\n"
        "• An interesting quest to make life more meaningful\n\n"
        "Commands:\n"
        "• /start - Start the bot\n"
        "• /subscribe - Get daily messages\n"
        "• /unsubscribe - Stop daily messages\n"
        "• /quest - Get an instant affirmation and quest\n"
        "• /today - Get today's affirmation and quest\n"
        "• /help - Show this help message"
    )
    await update.message.reply_text(help_text)

async def db_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check database status and subscriber count."""
    logger.info("Received /dbstatus command")
    if not db:
        logger.warning("Database connection is not available")
        await update.message.reply_text("❌ Database connection is not available")
        return

    try:
        logger.info("Attempting to get subscriber count")
        # Test database connection by getting subscriber count
        subscriber_count = len(db.get_all_subscribers())
        logger.info(f"Successfully got subscriber count: {subscriber_count}")
        await update.message.reply_text(
            "✅ Database connection is working!\n\n"
            f"📊 Current subscriber count: {subscriber_count}\n\n"
            "The database will store:\n"
            "• Subscriber Telegram IDs\n"
            "• When each person subscribed\n\n"
            "This helps the bot remember subscribers even if it restarts!"
        )
    except Exception as e:
        logger.error(f"Error checking database status: {e}")
        await update.message.reply_text(
            "❌ Error connecting to database. Please try again later!"
        )

# --- Mood Selection Handlers ---
MOODS = ["Creative", "Physical", "Social", "Reflection", "Unhinged", "Unhinged Maximum", "Surprise me"]
MOOD_KEYBOARD = [[KeyboardButton(mood)] for mood in MOODS]

async def setmood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Let the user choose their quest mood."""
    reply_markup = ReplyKeyboardMarkup(MOOD_KEYBOARD, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Choose your quest mood! This will influence the style of your daily and instant quests:",
        reply_markup=reply_markup
    )
    return 1

async def mood_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name if hasattr(user, 'last_name') else None
    username = user.username if hasattr(user, 'username') else None
    db.update_user_info(user_id, first_name, last_name, username)

    mood = update.message.text
    if mood not in MOODS:
        await update.message.reply_text("Please choose a mood using the buttons.")
        return 1
    db.set_mood(user_id, mood)
    await update.message.reply_text(f"Your mood is now set to: {mood}", reply_markup=ReplyKeyboardMarkup([["/quest", "/setmood"]], resize_keyboard=True))
    return ConversationHandler.END

async def quest_completed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark the user's quest as completed and increment their counter. Works as a reply or standalone."""
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name if hasattr(user, 'last_name') else None
    username = user.username if hasattr(user, 'username') else None
    db.update_user_info(user_id, first_name, last_name, username)

    is_reply = update.message.reply_to_message is not None
    # Optionally: Check if the replied-to message was sent by the bot and contains a quest (could check for emoji or keywords)
    if is_reply and update.message.reply_to_message.from_user.id == context.bot.id:
        # You could add further checks here for quest/affirmation keywords if desired
        special = True
    else:
        special = False

    db.increment_quests_completed(user_id)
    new_total = db.get_quests_completed(user_id)

    if special:
        await update.message.reply_text(f"🔥 You completed a quest you received from me! That's <b>{new_total}</b> total quests! Legendary!", parse_mode="HTML")
    else:
        await update.message.reply_text(f"🎉 Quest completed! You have now completed <b>{new_total}</b> quests!", parse_mode="HTML")

    leaderboard = db.get_leaderboard(limit=1)
    if new_total > 0 and leaderboard and leaderboard[0][0] == user_id:
        await update.message.reply_text("🏆 You're at the top of the leaderboard! Keep it up!")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the top users by quests completed."""
    if not db:
        await update.message.reply_text("Leaderboard is currently unavailable.")
        return
    leaderboard = db.get_leaderboard(limit=10)
    if not leaderboard:
        await update.message.reply_text("No leaderboard data yet!")
        return
    lines = ["🏆 <b>Quest Leaderboard</b> 🏆\n"]
    for idx, row in enumerate(leaderboard, 1):
        user_id, first_name, username, quests_completed = row
        display = f"@{username}" if username else (first_name or "Anonymous")
        lines.append(f"{idx}. {display}: <b>{quests_completed or 0}</b> quests")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("quest", quest))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(CommandHandler("dbstatus", db_status))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("quest_completed", quest_completed))

    # Mood selection conversation handler
    mood_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("setmood", setmood)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, mood_selection)]
        },
        fallbacks=[]
    )
    application.add_handler(mood_conv_handler)

    # Set up the daily job (9 AM)
    job_queue = application.job_queue
    job_queue.run_daily(
        send_daily_messages,
        time=time(hour=9, minute=0),  # 9:00 AM
        days=(0, 1, 2, 3, 4, 5, 6)  # Every day
    )

    # Start the Bot
    application.run_polling()


if __name__ == '__main__':
    main() 