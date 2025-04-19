import os
import logging
from datetime import datetime, time
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Permission slip messages
PERMISSION_SLIPS = [
    "🎟️ Today's Permission Slip 🎟️\n\nYou have permission to:\n- Approach someone new and ask them about their favorite book",
    "🎟️ Today's Permission Slip 🎟️\n\nYou have permission to:\n- Compliment someone's outfit and ask where they got it",
    "🎟️ Today's Permission Slip 🎟️\n\nYou have permission to:\n- Ask someone about their favorite travel destination",
    "🎟️ Today's Permission Slip 🎟️\n\nYou have permission to:\n- Share a fun fact about yourself with someone new",
    "🎟️ Today's Permission Slip 🎟️\n\nYou have permission to:\n- Ask someone about their favorite hobby"
]

# Store subscribers
subscribers = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Welcome to Permission Slip Bot! 🎟️\n\n"
        "Every day, you'll receive a special permission slip that gives you "
        "the courage to interact with someone new in your community.\n\n"
        "Use /subscribe to start receiving daily permission slips!"
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribe the user to daily permission slips."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    global subscribers
    subscribers.add(user_id)
    
    logger.info(f"New subscriber: {user_name} (ID: {user_id})")
    logger.info(f"Current subscribers: {len(subscribers)}")
    
    await update.message.reply_text(
        "✅ You're now subscribed to daily permission slips!\n\n"
        "You'll receive a new permission slip every day at 9:00 AM.\n"
        "Use /test to get today's permission slip right now!"
    )

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a test permission slip immediately."""
    global subscribers
    
    if not subscribers:
        await update.message.reply_text("No subscribers yet! Use /subscribe to be the first!")
        return

    # Send today's permission slip
    permission_slip = "🎟️ Special Permission Slip! 🎟️\n\nYou have permission to:\n- Say hello to someone new and ask them what brings them joy!"
    
    success_count = 0
    for user_id in subscribers:
        try:
            await context.bot.send_message(chat_id=user_id, text=permission_slip)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {e}")
    
    await update.message.reply_text(
        f"✅ Permission slip sent to {success_count} subscribers!\n"
        f"Total subscribers: {len(subscribers)}"
    )

async def send_daily_permission_slips(context: ContextTypes.DEFAULT_TYPE):
    """Send permission slips to all subscribers."""
    global subscribers
    if not subscribers:
        return
    
    # Get today's permission slip
    today_index = datetime.now().day % len(PERMISSION_SLIPS)
    permission_slip = PERMISSION_SLIPS[today_index]
    
    for user_id in subscribers:
        try:
            await context.bot.send_message(chat_id=user_id, text=permission_slip)
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {e}")

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("test", test))

    # Schedule daily permission slips at 9:00 AM
    job_queue = application.job_queue
    job_queue.run_daily(send_daily_permission_slips, time=datetime.time(hour=9, minute=0))

    # Start the Bot
    logger.info("Bot started! Ready to send permission slips!")
    application.run_polling()

if __name__ == '__main__':
    main() 