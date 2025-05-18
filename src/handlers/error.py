import logging

async def error_handler(update, context):
    logging.error(f"Update {update} caused error {context.error}")
    if update.message:
        await update.message.reply_text("⚠️ An error occurred. Please try again.")

def setup_errors(application):
    application.add_error_handler(error_handler)