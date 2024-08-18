import logging
import os
import json
import random
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the environment
BOT_TOKEN = os.getenv("TOKEN")

# Load responses from a JSON file
def load_responses(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}

# Save responses to a JSON file
def save_responses(filename, responses):
    with open(filename, 'w') as file:
        json.dump(responses, file, indent=4)

# Load responses
responses = load_responses('customize.json')

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to keep track of user states
user_states = {}

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("My Oga, How far na? 🙌.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('/how can I be of help to you, my oga')

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("This is a random command response.")

# Custom response handler
async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.lower()
    chat_id = update.message.chat.id
    
    # Default response if no match is found
    default_response = "this is new, What is the response to that?"

    # Find a response
    response_list = responses.get(user_message, [default_response])
    response = random.choice(response_list)
    
    if response == default_response:
        # If no match is found, ask the user for a new response
        if chat_id not in user_states:
            user_states[chat_id] = {'awaiting_response': user_message}
            await update.message.reply_text(response)
            # await update.message.reply_text("What should I say in response to that?")
        else:
            await update.message.reply_text("I'm still waiting for your response.")
    else:
        # Reply with the appropriate message
        await update.message.reply_text(response)

# New function to handle user responses for learning
async def learn_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat.id
    if chat_id in user_states and 'awaiting_response' in user_states[chat_id]:
        user_message = user_states[chat_id]['awaiting_response']
        new_response = update.message.text
        
        # Update the responses with the new user-provided response
        if user_message in responses:
            responses[user_message].append(new_response)
        else:
            responses[user_message] = [new_response]
        
        # Save the updated responses to the JSON file
        save_responses('customize.json', responses)
        
        await update.message.reply_text(f"Got it! I'll remember that: '{new_response}'")
        del user_states[chat_id]  # Clear the stored input
    elif chat_id not in user_states:
        # Handle unexpected messages
        await update.message.reply_text("I didn't understand that. Please start over.")
    else:
        # Handle messages when waiting is not active
        await update.message.reply_text("I'm not currently waiting for a new response.")

# Main function to run the bot
def main() -> None:
    # Initialize the Application with your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("random", random_command))

    # Add message handler for general text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))

    # Add message handler for learning responses
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, learn_response), group=1)

    # Start polling for updates
    application.run_polling()

if __name__ == '__main__':
    main()
