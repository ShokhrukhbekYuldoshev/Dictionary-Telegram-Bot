import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import os
from dotenv import load_dotenv

load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


# Define a few command handlers. These usually take the two arguments update and context.
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hi!')


async def define_word(update: Update, context: CallbackContext) -> None:
    word = update.message.text
    print(word)
    response = requests.get(
        f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')

    if response.status_code == 200:
        data = response.json()[0]
        word = data['word']
        phonetics_list = data['phonetics']
        meanings_list = data['meanings']
        source_list = data.get('sourceUrls', [])

        # Initialize empty lists for each phonetic type
        uk_phonetics = []
        us_phonetics = []
        au_phonetics = []

        # Separate the phonetics into their respective lists based on audio
        for phonetic in phonetics_list:
            audio = phonetic.get('audio', '')

            if 'uk' in audio.lower():
                uk_phonetics.append(f"UK: {audio}")
            elif 'us' in audio.lower():
                us_phonetics.append(f"US: {audio}")
            elif 'au' in audio.lower():
                au_phonetics.append(f"AU: {audio}")

        # Combine the phonetic lists into a single formatted string
        all_phonetics = []

        if uk_phonetics:
            all_phonetics.extend(uk_phonetics)
        if us_phonetics:
            all_phonetics.extend(us_phonetics)
        if au_phonetics:
            all_phonetics.extend(au_phonetics)

        # Create a final phonetics string with newline separators
        phonetics = '\n'.join(all_phonetics)

        # Format meanings
        meanings = '\n\n'.join(
            f"Part of Speech: {meaning['partOfSpeech']}\n"
            f"Definitions:\n{', '.join(definition['definition'] for definition in meaning['definitions'])}"
            for meaning in meanings_list
        )

        # Format source URLs
        source_urls = '\n'.join(source_list)

        # Prepare the final message with Markdown formatting
        message = (
            f"*Word:* {word}\n\n"  # Use asterisks for bold in Markdown
            f"*Phonetics:*\n{phonetics}\n\n"
            f"*Meanings:*\n{meanings}\n\n"
            f"*Source URLs:*\n{source_urls}"
        )
        # Send the message with Markdown parsing
        await update.message.reply_text(message, parse_mode='Markdown')

    else:
        await update.message.reply_text(
            'Sorry, I could not find a definition for that word.')


def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(
        os.getenv('BOT_TOKEN')).build()

    # Add a handler for the /start command
    application.add_handler(CommandHandler('start', start))

    application.add_handler(MessageHandler(
        filters=filters.TEXT, callback=define_word))

    # Add conversation handler as needed
    # ...

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
