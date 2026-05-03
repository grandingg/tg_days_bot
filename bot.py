import os
import json
from datetime import date
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
EVENTS_FILE = "events.json"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в Render Environment Variables")

print("Бот запускается...")

def load_events():
    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_events(events):
    with open(EVENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(events, file, ensure_ascii=False, indent=4)


def get_chat_id(update: Update):
    return str(update.effective_chat.id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 🌸\n\n"
        "Я могу запоминать события отдельно для каждой беседы.\n\n"
        "Добавить событие:\n"
        "/add отпуск 2026-06-01\n\n"
        "Проверить событие:\n"
        "/event отпуск\n\n"
        "Посмотреть события этой беседы:\n"
        "/list\n\n"
        "Удалить событие:\n"
        "/delete отпуск\n\n"
        "Разовый подсчёт без сохранения:\n"
        "/left 2026-12-31 Новый год"
    )


async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        event_name = context.args[0].lower()
        date_str = context.args[1]

        date.fromisoformat(date_str)

        chat_id = get_chat_id(update)
        events = load_events()

        if chat_id not in events:
            events[chat_id] = {}

        events[chat_id][event_name] = date_str
        save_events(events)

        await update.message.reply_text(
            f"Готово! ✨\n"
            f"Я запомнила событие «{event_name}» на дату {date_str}."
        )

    except:
        await update.message.reply_text(
            "Напиши так:\n"
            "/add отпуск 2026-06-01"
        )


async def event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        event_name = context.args[0].lower()

        chat_id = get_chat_id(update)
        events = load_events()
        chat_events = events.get(chat_id, {})

        if event_name not in chat_events:
            await update.message.reply_text(
                f"Я пока не знаю событие «{event_name}» в этой беседе 🙈\n\n"
                "Добавь его так:\n"
                f"/add {event_name} 2026-06-01"
            )
            return

        event_date = date.fromisoformat(chat_events[event_name])
        today = date.today()
        days_left = (event_date - today).days

        if days_left > 0:
            text = f"✨ До события «{event_name}» осталось {days_left} дней."
        elif days_left == 0:
            text = f"🎉 Событие «{event_name}» уже сегодня!"
        else:
            text = f"🌙 Событие «{event_name}» уже прошло."

        await update.message.reply_text(text)

    except:
        await update.message.reply_text(
            "Напиши так:\n"
            "/event отпуск"
        )


async def list_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = get_chat_id(update)
    events = load_events()
    chat_events = events.get(chat_id, {})

    if not chat_events:
        await update.message.reply_text(
            "В этой беседе пока нет сохранённых событий 🌱\n\n"
            "Добавь первое так:\n"
            "/add отпуск 2026-06-01"
        )
        return

    text = "Вот события, сохранённые в этой беседе 📌\n\n"

    for name, date_str in chat_events.items():
        event_date = date.fromisoformat(date_str)
        days_left = (event_date - date.today()).days

        if days_left > 0:
            text += f"• {name} — {date_str} — осталось {days_left} дней\n"
        elif days_left == 0:
            text += f"• {name} — {date_str} — сегодня 🎉\n"
        else:
            text += f"• {name} — {date_str} — уже прошло\n"

    await update.message.reply_text(text)


async def delete_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        event_name = context.args[0].lower()

        chat_id = get_chat_id(update)
        events = load_events()
        chat_events = events.get(chat_id, {})

        if event_name not in chat_events:
            await update.message.reply_text(
                f"Я не нашла событие «{event_name}» в этой беседе 🙈"
            )
            return

        del events[chat_id][event_name]
        save_events(events)

        await update.message.reply_text(
            f"Готово! 🗑️\n"
            f"Событие «{event_name}» удалено из этой беседы."
        )

    except:
        await update.message.reply_text(
            "Напиши так:\n"
            "/delete отпуск"
        )


async def left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date_str = context.args[0]
        event_name = " ".join(context.args[1:])

        if not event_name:
            event_name = "событие"

        event_date = date.fromisoformat(date_str)
        today = date.today()
        days_left = (event_date - today).days

        if days_left > 0:
            text = f"✨ До события «{event_name}» осталось {days_left} дней."
        elif days_left == 0:
            text = f"🎉 Событие «{event_name}» уже сегодня!"
        else:
            text = f"🌙 Событие «{event_name}» уже прошло."

        await update.message.reply_text(text)

    except:
        await update.message.reply_text(
            "Напиши так:\n"
            "/left 2026-12-31 Новый год"
        )


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_event))
app.add_handler(CommandHandler("event", event))
app.add_handler(CommandHandler("list", list_events))
app.add_handler(CommandHandler("delete", delete_event))
app.add_handler(CommandHandler("left", left))

app.run_polling()
