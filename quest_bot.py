import os
import logging
from datetime import datetime, time
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from db_operations import EdgeOSDB
from ai_interactions import AIInteractions

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin user ID (your Telegram ID)
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))

# Initialize AI
try:
    ai = AIInteractions()
except Exception as e:
    logger.error(f"Failed to initialize AI: {e}")
    ai = None

# Conversation states
SEND_MESSAGE = 0
SEND_WELCOME = 1
SELECT_POPUP = 2
COMPOSE_WELCOME = 3
FEELING_INPUT = 4

# Permission slip messages
PERMISSION_SLIPS = [
    "✨ COSMIC PERMISSION SLIP OF THE DAY! ✨\n\n"
    "🌟 YOU HAVE DIVINE PERMISSION TO:\n"
    "Be absolutely, unashamedly CURIOUS! Go find someone new and ask them about their wildest dream. "
    "Their answer might just change your life! Remember: Every stranger is just a friend you haven't met yet! 🚀",

    "🌈 TODAY'S CHAOS-APPROVED PERMISSION SLIP! 🌈\n\n"
    "💫 YOU ARE HEREBY GRANTED PERMISSION TO:\n"
    "Radiate pure, unfiltered joy! Find someone wearing something that makes you smile and tell them! "
    "Your compliment might be the spark that ignites their whole day! SPREAD THE HAPPINESS! ✨",

    "🎭 YOUR MAGICAL PERMISSION SLIP HAS ARRIVED! 🎭\n\n"
    "🔮 THE UNIVERSE GRANTS YOU PERMISSION TO:\n"
    "Be gloriously, magnificently BOLD! Share a passion project with someone new - "
    "let your enthusiasm be contagious! Your energy could inspire a revolution! 🌟",

    "⚡️ PERMISSION SLIP OF INFINITE POSSIBILITIES! ⚡️\n\n"
    "🎪 YOU ARE COSMICALLY AUTHORIZED TO:\n"
    "Create unexpected connections! Find someone who looks interesting and share your favorite life-changing book/movie/song. "
    "You might just start a chain reaction of awesomeness! 🎨",

    "🌟 YOUR CHAOS-POWERED PERMISSION SLIP! 🌟\n\n"
    "🎯 YOU HAVE SUPERNATURAL PERMISSION TO:\n"
    "Be extraordinarily KIND! Do something unexpectedly nice for someone you've never talked to. "
    "Small acts of kindness can cascade into WAVES of positive change! 💫",

    "🎪 YOUR PERMISSION SLIP OF PURE POTENTIAL! 🎪\n\n"
    "🎭 YOU ARE OFFICIALLY EMPOWERED TO:\n"
    "Break the routine! Start a conversation about something that lights your soul on fire. "
    "Your passion could be the catalyst someone else needs! GO FORTH AND INSPIRE! ⚡️",

    "🌈 YOUR DAILY DOSE OF PERMISSION MAGIC! 🌈\n\n"
    "✨ YOU HAVE COSMIC CLEARANCE TO:\n"
    "Be delightfully RANDOM! Share a fascinating fact or story with someone new. "
    "The universe works in mysterious ways - your random connection could change everything! 🚀"
]

# Store subscribers
subscribers = set()

# Initialize EdgeOS DB connection
try:
    edge_db = EdgeOSDB()
except Exception as e:
    logger.error(f"Failed to initialize EdgeOS DB connection: {e}")
    edge_db = None

def is_admin(user_id: int) -> bool:
    """Check if the user is an admin."""
    return user_id == ADMIN_USER_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    
    if is_admin(user_id):
        # Show admin keyboard with EdgeOS integration
        keyboard = [
            [KeyboardButton("/admin"), KeyboardButton("/broadcast")],
            [KeyboardButton("/stats"), KeyboardButton("/test")],
            [KeyboardButton("/welcome_citizens"), KeyboardButton("/view_popups")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "✨ GREETINGS, MASTER OF CHAOS AND COMMUNITY! ✨\n\n"
            "Your powers include:\n"
            "🎭 /admin - Command your cosmic dashboard\n"
            "📢 /broadcast - Send waves of inspiration to all\n"
            "📊 /stats - Glimpse into the community soul\n"
            "🎪 /test - Release a test permission slip\n"
            "🌟 /welcome_citizens - Embrace new community members\n"
            "🏙️ /view_popups - Explore the realms of possibility",
            reply_markup=reply_markup
        )
    else:
        keyboard = [
            [KeyboardButton("/subscribe"), KeyboardButton("/feeling")],
            [KeyboardButton("/help")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "✨ WELCOME TO THE PERMISSION SLIP BOT! ✨\n\n"
            "🌟 Get ready for daily doses of encouragement, inspiration, and permission to be "
            "your most authentic, amazing self!\n\n"
            "Every day, you'll receive a special permission slip that empowers you to create "
            "magical connections in your community! 🚀\n\n"
            "🎭 Use /subscribe to start your journey of endless possibilities!\n"
            "💫 Use /feeling to share how you're feeling and get a personalized permission slip!",
            reply_markup=reply_markup
        )

async def view_popups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available popup cities."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Sorry, this command is for administrators only.")
        return

    if not edge_db:
        await update.message.reply_text("EdgeOS database connection not available.")
        return

    popups = edge_db.get_popups()
    if not popups:
        await update.message.reply_text("No active popup cities found.")
        return

    popup_text = "Available Popup Cities:\n\n"
    for popup in popups:
        popup_text += f"🏙️ {popup['name']}\n"
        popup_text += f"ID: {popup['id']}\n"
        if popup.get('description'):
            popup_text += f"Description: {popup['description']}\n"
        popup_text += "\n"

    await update.message.reply_text(popup_text)

async def welcome_citizens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the welcome message flow."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Sorry, this command is for administrators only.")
        return

    if not edge_db:
        await update.message.reply_text("EdgeOS database connection not available.")
        return

    popups = edge_db.get_popups()
    if not popups:
        await update.message.reply_text("No active popup cities found.")
        return

    keyboard = []
    for popup in popups:
        keyboard.append([InlineKeyboardButton(
            popup['name'], 
            callback_data=f"popup_{popup['id']}"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Select a popup city to send welcome messages:",
        reply_markup=reply_markup
    )
    return SELECT_POPUP

async def popup_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle popup selection."""
    query = update.callback_query
    await query.answer()
    
    popup_id = query.data.replace("popup_", "")
    context.user_data['selected_popup'] = popup_id
    
    await query.message.reply_text(
        "Please compose your welcome message. You can use these placeholders:\n"
        "{first_name} - Citizen's first name\n"
        "{last_name} - Citizen's last name\n"
        "{email} - Citizen's email\n\n"
        "Type your message now:"
    )
    return COMPOSE_WELCOME

async def send_welcome_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome messages to citizens."""
    message_template = update.message.text
    popup_id = context.user_data.get('selected_popup')
    
    if not popup_id:
        await update.message.reply_text("Error: No popup city selected.")
        return ConversationHandler.END
    
    citizens = edge_db.get_popup_citizens(popup_id)
    success_count = 0
    total_count = len(citizens)
    
    for citizen in citizens:
        telegram_id = edge_db.get_citizen_telegram(citizen['id'])
        if telegram_id:
            try:
                # Format message with citizen's info
                message = message_template.format(
                    first_name=citizen.get('first_name', ''),
                    last_name=citizen.get('last_name', ''),
                    email=citizen.get('email', '')
                )
                await context.bot.send_message(chat_id=telegram_id, text=message)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send welcome message to {citizen['id']}: {e}")
    
    await update.message.reply_text(
        f"Welcome messages sent!\n"
        f"Successfully sent: {success_count}/{total_count} messages\n"
        f"Failed: {total_count - success_count} messages"
    )
    return ConversationHandler.END

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
        "🎉 CONGRATULATIONS, BRAVE SOUL! 🎉\n\n"
        "You've just joined a community of amazing humans dedicated to creating "
        "magical moments and connections! ✨\n\n"
        "🌟 Every day at 9:00 AM, you'll receive a new permission slip - "
        "your cosmic authorization to spread joy, curiosity, and positive chaos!\n\n"
        "Can't wait? Use /test to get today's permission slip right now! 🚀"
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

async def feeling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask user how they're feeling."""
    await update.message.reply_text(
        "✨ GREETINGS, WONDERFUL HUMAN! ✨\n\n"
        "How are you feeling right now? Share your thoughts, emotions, or state of mind, "
        "and I'll craft a special permission slip just for you! 🌟\n\n"
        "(Or use /cancel to keep it random!)"
    )
    return FEELING_INPUT

async def handle_feeling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a personalized permission slip based on user's feeling."""
    if not ai:
        # Fall back to random permission slip if AI isn't available
        slip = PERMISSION_SLIPS[datetime.now().day % len(PERMISSION_SLIPS)]
    else:
        slip = ai.generate_permission_slip(update.message.text)
    
    await update.message.reply_text(slip)
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "✨ BEHOLD, THE COSMIC GUIDE! ✨\n\n"
        "🌟 Available Commands:\n"
        "/subscribe - Join the daily permission slip adventure\n"
        "/feeling - Share your feelings for a personalized permission slip\n"
        "/help - Show this magical guide\n\n"
        "Every day at 9:00 AM, you'll receive a special permission slip to inspire "
        "connection and joy in your community! ✨"
    )

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
    application.add_handler(CommandHandler("view_popups", view_popups))
    application.add_handler(CommandHandler("help", help_command))

    # Add conversation handler for broadcast
    broadcast_handler = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast)],
        states={
            SEND_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_broadcast)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(broadcast_handler)

    # Add conversation handler for welcome messages
    welcome_handler = ConversationHandler(
        entry_points=[CommandHandler("welcome_citizens", welcome_citizens)],
        states={
            SELECT_POPUP: [CallbackQueryHandler(popup_selected, pattern=r"^popup_")],
            COMPOSE_WELCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_welcome_messages)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(welcome_handler)

    # Add conversation handler for feelings
    feeling_handler = ConversationHandler(
        entry_points=[CommandHandler("feeling", feeling)],
        states={
            FEELING_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feeling)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(feeling_handler)

    # Schedule daily permission slips at 9:00 AM
    job_queue = application.job_queue
    job_queue.run_daily(send_daily_permission_slips, time=time(9, 0))

    # Start the Bot
    logger.info("Bot started! Ready to send permission slips!")
    application.run_polling()

if __name__ == '__main__':
    main() 