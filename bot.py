import os

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]
# =========================
# BOOK CLASS
# =========================

class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages

    def describe(self):
        return f"'{self.title}' by {self.author}, {self.pages} pages."


# =========================
# SAMPLE BOOKS
# =========================

book1 = Book("The Alchemist", "Paulo Coelho", 208)
book2 = Book("Python Crash Course", "Eric Matthes", 544)


# =========================
# KEYBOARD
# =========================

main_keyboard = [
    ["📚 My Favorite Books"],
    ["➕ Add Book"],
    ["🗑️ Delete All Books"],
]

keyboard = ReplyKeyboardMarkup(
    main_keyboard,
    resize_keyboard=True
)


# =========================
# CONVERSATION STATES
# =========================

TITLE, AUTHOR, PAGES = range(3)


# =========================
# START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Create a separate book list for each user
    if "books" not in context.user_data:
        context.user_data["books"] = [
            book1,
            book2
        ]

    await update.message.reply_text(
        "📚 Welcome to your Favorite Books Bot!\n\n"
        "You can add your own favorite books and "
        "view them anytime.\n\n"
        "Choose an option below:",
        reply_markup=keyboard
    )


# =========================
# SHOW BOOKS
# =========================

async def show_books(update: Update, context: ContextTypes.DEFAULT_TYPE):

    books = context.user_data.get("books", [])

    if not books:
        await update.message.reply_text(
            "📚 You don't have any favorite books yet.\n\n"
            "Tap ➕ Add Book to add one."
        )
        return

    message = "❤️ Your Favorite Books:\n\n"

    for number, book in enumerate(books, start=1):
        message += f"{number}. {book.describe()}\n"

    await update.message.reply_text(message)


# =========================
# ADD BOOK - START
# =========================

async def add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📕 Great!\n\n"
        "What is the title of the book?"
    )

    return TITLE


# =========================
# GET TITLE
# =========================

async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["new_book_title"] = update.message.text

    await update.message.reply_text(
        "✍️ Who is the author?"
    )

    return AUTHOR


# =========================
# GET AUTHOR
# =========================

async def get_author(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["new_book_author"] = update.message.text

    await update.message.reply_text(
        "📄 How many pages does the book have?"
    )

    return PAGES


# =========================
# GET PAGES AND SAVE BOOK
# =========================

async def get_pages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pages_text = update.message.text

    # Check that pages is a number
    if not pages_text.isdigit():

        await update.message.reply_text(
            "❌ Please enter the number of pages.\n\n"
            "For example: 320"
        )

        return PAGES

    pages = int(pages_text)

    title = context.user_data["new_book_title"]
    author = context.user_data["new_book_author"]

    # Create the new Book object
    new_book = Book(title, author, pages)

    # Make sure the user has a book list
    if "books" not in context.user_data:
        context.user_data["books"] = []

    # Add the book to the user's list
    context.user_data["books"].append(new_book)

    await update.message.reply_text(
        "✅ Book added successfully!\n\n"
        f"❤️ {new_book.describe()}",
        reply_markup=keyboard
    )

    # Clean temporary data
    context.user_data.pop("new_book_title", None)
    context.user_data.pop("new_book_author", None)

    return ConversationHandler.END


# =========================
# CANCEL ADDING BOOK
# =========================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Adding the book was cancelled.",
        reply_markup=keyboard
    )

    return ConversationHandler.END


# =========================
# DELETE ALL BOOKS
# =========================

async def delete_books(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["books"] = []

    await update.message.reply_text(
        "🗑️ All your favorite books have been deleted.\n\n"
        "You can add new ones using ➕ Add Book.",
        reply_markup=keyboard
    )


# =========================
# HANDLE KEYBOARD BUTTONS
# =========================

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "📚 My Favorite Books":
        await show_books(update, context)

    elif text == "➕ Add Book":
        return await add_book(update, context)

    elif text == "🗑️ Delete All Books":
        await delete_books(update, context)


# =========================
# MAIN PROGRAM
# =========================

def main():



    app = Application.builder().token(TOKEN).build()

    # Start command
    app.add_handler(
        CommandHandler("start", start)
    )

    # Add book conversation
    add_book_conversation = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^➕ Add Book$"),
                add_book
            )
        ],

        states={

            TITLE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_title
                )
            ],

            AUTHOR: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_author
                )
            ],

            PAGES: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_pages
                )
            ],
        },

        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
    )

    app.add_handler(add_book_conversation)

    # Other keyboard buttons
    app.add_handler(
        MessageHandler(
            filters.Regex("^📚 My Favorite Books$"),
            show_books
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^🗑️ Delete All Books$"),
            delete_books
        )
    )

    print("📚 Book Bot is running...")

    app.run_polling()


# =========================
# RUN BOT
# =========================

if __name__ == "__main__":
    main()

