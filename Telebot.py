import re
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8559903050:AAG0GPePcYfvu76GLv6maFexkdPb9vLF5jE"

DICE_RE = re.compile(r"(\d*)d(\d+)", re.IGNORECASE)

user_stats = {}

def parse_dice(text: str):
    m = DICE_RE.fullmatch(text.replace(" ", ""))
    if not m:
        return None
    n_str, sides_str = m.groups()
    n = int(n_str) if n_str else 1
    sides = int(sides_str)
    return n, sides

def roll_dice(n, sides):
    return [random.randint(1, sides) for _ in range(n)]

def format_roll(n, sides, results):
    lines = []
    for i, r in enumerate(results, 1):
        line = f"Кость {i}д{sides}: {r}"
        if sides == 20 and r == 20:
            line += " — Фига подкрутка 🎉"
        if sides == 20 and r == 1:
            line += " — ЛОХ 😬"
        lines.append(line)
    total = sum(results)
    lines.append("-" * 20)
    lines.append(f"Итог: {total}")
    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1d4", callback_data="1d4"),
         InlineKeyboardButton("1d6", callback_data="1d6"),
         InlineKeyboardButton("1d8", callback_data="1d8")],
        [InlineKeyboardButton("1d10", callback_data="1d10"),
         InlineKeyboardButton("1d12", callback_data="1d12"),
         InlineKeyboardButton("1d20", callback_data="1d20")],
        [InlineKeyboardButton("Рандомный бросок", callback_data="random")],
        [InlineKeyboardButton("Статистика", callback_data="stats")],
        [InlineKeyboardButton("Уйди противный (Выход)", callback_data="exit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет, Пупсик! Я кидаю кости за тебя в ДнД 🎲\n"
        "Ну ты понял короче) Бот должен работать и кидать новые значения пока не нажмешь выход, только при /roll XdY(7d6) он закрывается и нужно заново тыкать на /start Вовка вас любит",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "exit":
        await query.edit_message_text("Сессия завершена. Пиши /start чтобы начать снова.")
        return

    if data == "stats":
        stats = user_stats.get(user_id, [])
        if not stats:
            await query.edit_message_text("У вас пока нет бросков.")
        else:
            await query.edit_message_text("Ваша статистика:\n\n" + "\n\n".join(stats))
        return

    if data == "random":
        sides = random.choice([4,6,8,10,12,20])
        n = 1
        results = roll_dice(n, sides)
    else:
        parsed = parse_dice(data)
        if not parsed:
            await query.edit_message_text("Ошибка формата")
            return
        n, sides = parsed
        results = roll_dice(n, sides)

    msg = format_roll(n, sides, results)
    user_stats.setdefault(user_id, []).append(msg)


    keyboard = [
        [InlineKeyboardButton("1d4", callback_data="1d4"),
         InlineKeyboardButton("1d6", callback_data="1d6"),
         InlineKeyboardButton("1d8", callback_data="1d8")],
        [InlineKeyboardButton("1d10", callback_data="1d10"),
         InlineKeyboardButton("1d12", callback_data="1d12"),
         InlineKeyboardButton("1d20", callback_data="1d20")],
        [InlineKeyboardButton("Рандомный бросок", callback_data="random")],
        [InlineKeyboardButton("Статистика", callback_data="stats")],
        [InlineKeyboardButton("Уйди противный (Выход)", callback_data="exit")]
    ]
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def roll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Укажи бросок. Пример: /roll 4d7")
        return

    text = context.args[0]
    parsed = parse_dice(text)
    if not parsed:
        await update.message.reply_text("Неверный формат. Пример: /roll 4d7")
        return

    n, sides = parsed
    results = roll_dice(n, sides)
    msg = format_roll(n, sides, results)
    user_stats.setdefault(user_id, []).append(msg)
    await update.message.reply_text(msg)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("roll", roll_command))
    app.add_handler(CallbackQueryHandler(button))

    print("Бот запущен! Пиши ему в Telegram.")
    app.run_polling()
