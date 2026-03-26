import tempfile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from rag import rag_pipeline
from vision import caption_image
from memory import memory

TOKEN = "Enter_Your_Telegram_Bot_Token_Here"


# -------------------------------
# /start
# -------------------------------
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Welcome to GenAI Bot!\n\n"
        "Use:\n"
        "/ask <query> → Ask questions (RAG)\n"
        "/image → Upload image for description\n"
        "/help → Show help"
    )


# -------------------------------
# /help (REQUIRED)
# -------------------------------
async def help_cmd(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Bot Usage:\n\n"
        "1️⃣ /ask <query>\n"
        "   Then ask your question\n\n"
        "2️⃣ /image\n"
        "   Then upload an image\n\n"
        "3️⃣ /help\n"
        "   Show this message"
    )


# -------------------------------
# /ask (RAG)
# -------------------------------
async def ask(update, context):
    user_id = update.effective_user.id
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("❗ Please provide a query")
        return

    msg = await update.message.reply_text("⏳ Thinking...")

    result = rag_pipeline(query)

    answers = result["answers"]
    snippets = result["snippets"]

    response = "📌 *Top Answers*\n\n"

    # -------------------------
    # Answers
    # -------------------------
    for i, (source, answer, _) in enumerate(answers, 1):

        if source.startswith("http"):
            source_name = "🌐 Wikipedia"
        else:
            source_name = "📚 Local Knowledge"

        response += f"*{i}. {source_name}*\n"
        response += f"{answer.strip()}\n\n"

    # -------------------------
    # Sources
    # -------------------------
    response += "📚 *Sources*\n"

    for i, (source, _, _) in enumerate(answers, 1):
        if source.startswith("http"):
            response += f"{i}. {source}\n"
        else:
            response += f"{i}. Local Knowledge Base\n"

    # -------------------------
    # Snippets
    # -------------------------
    if snippets:
        response += "\n📄 *Context Used*\n"
        for s in snippets:
            response += f"- {s}\n"

    # Save to memory
    memory.add(user_id, f"Q: {query}\nA: {answers[0][1]}")

    await msg.edit_text(response[:4000], parse_mode="Markdown")


# -------------------------------
# /image
# -------------------------------
async def image(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 Please upload an image after this command.")


# -------------------------------
# Handle Image Upload
# -------------------------------
async def handle_photo(update, context):
    user_id = update.effective_user.id

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        await file.download_to_drive(tmp.name)

        caption, tags = caption_image(tmp.name)

    result = f"Caption: {caption}\nTags: {', '.join(tags)}"

    memory.add(user_id, result)

    await update.message.reply_text(result)


async def summarize(update, context):
    user_id = update.effective_user.id
    history = memory.get(user_id)

    if not history:
        await update.message.reply_text("No history to summarize.")
        return

    text = "\n".join(history)

    prompt = f"""
Summarize the following conversation briefly:

{text}
"""

    summary = call_llm(prompt)

    await update.message.reply_text(f"📝 Summary:\n{summary}")


# -------------------------------
# Unknown Command (Good UX)
# -------------------------------
async def unknown(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Unknown command.\nUse /help to see available commands."
    )


# -------------------------------
# MAIN
# -------------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("image", image))
    app.add_handler(CommandHandler("summarize", summarize))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    

    # catch unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("✅ Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()