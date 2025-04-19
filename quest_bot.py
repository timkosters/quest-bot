import os
import logging
from datetime import datetime, time
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin user ID (your Telegram ID)
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))  # Set this in Railway env vars

# Conversation states
SEND_MESSAGE = 0

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

def is_admin(user_id: int) -> bool:
    """Check if the user is an admin."""
    return user_id == ADMIN_USER_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    
    if is_admin(user_id):
        # Show admin keyboard
        keyboard = [
            [KeyboardButton("/admin"), KeyboardButton("/broadcast")],
            [KeyboardButton("/stats"), KeyboardButton("/test")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Welcome to Permission Slip Bot Admin Panel! 🎟️\n\n"
            "Admin Commands:\n"
            "/admin - Show admin panel\n"
            "/broadcast - Send custom message to all subscribers\n"
            "/stats - Show subscriber statistics\n"
            "/test - Send test permission slip",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Welcome to Permission Slip Bot! 🎟️\n\n"
            "Every day, you'll receive a special permission slip that gives you "
            "the courage to interact with someone new in your community.\n\n"
            "Use /subscribe to start receiving daily permission slips!"
        )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel command."""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Sorry, this command is for administrators only.")
        return

    stats_text = f"📊 Bot Statistics:\n\n" \
                 f"Total Subscribers: {len(subscribers)}\n" \
                 f"Last Permission Slip: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n" \
                 f"Available Commands:\n" \
                 f"/broadcast - Send custom message to subscribers\n" \
                 f"/stats - Show detailed statistics\n" \
                 f"/test - Send test permission slip"
    
    await update.message.reply_text(stats_text)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the broadcast conversation."""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Sorry, this command is for administrators only.")
        return

    await update.message.reply_text(
        "Please enter the message you want to send to all subscribers.\n"
        "Type /cancel to cancel."
    )
    return SEND_MESSAGE

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the broadcast message to all subscribers."""
    message_text = update.message.text
    success_count = 0
    
    for subscriber_id in subscribers:
        try:
            await context.bot.send_message(chat_id=subscriber_id, text=message_text)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send message to {subscriber_id}: {e}")
    
    await update.message.reply_text(
        f"✅ Message sent successfully to {success_count} subscribers!"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed statistics."""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Sorry, this command is for administrators only.")
        return

    stats_text = f"📊 Detailed Statistics\n\n" \
                 f"Total Subscribers: {len(subscribers)}\n" \
                 f"Active Today: {len(subscribers)}\n" \
                 f"Messages Sent Today: {len(subscribers)}\n\n" \
                 f"Subscriber List:\n"
    
    for sub_id in subscribers:
        try:
            user = await context.bot.get_chat(sub_id)
            stats_text += f"- {user.first_name} (ID: {sub_id})\n"
        except Exception as e:
            stats_text += f"- Unknown User (ID: {sub_id})\n"
    
    await update.message.reply_text(stats_text)

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
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("stats", stats))

    # Add conversation handler for broadcast
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast)],
        states={
            SEND_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_broadcast)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(conv_handler)

    # Schedule daily permission slips at 9:00 AM
    job_queue = application.job_queue
    job_queue.run_daily(send_daily_permission_slips, time=time(9, 0))

    # Start the Bot
    logger.info("Bot started! Ready to send permission slips!")
    application.run_polling()

if __name__ == '__main__':
    main() 