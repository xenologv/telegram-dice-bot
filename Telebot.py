import re
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ================================
#  Бот D&D с кнопками для всех стандартных кубов и комбинированных бросков
#  Без модификаторов
# ================================

NAT20_MSG = "Фига подкрутка🎉"
NAT1_MSG = "ЛОХ 😬"
HELLO_MSG = (
    "Привет Пидрила, я кидаю кости за тебя в ДнД\n"
    "Тыкай кнопку и будет збс\n\n"
    )

DICE_RE = re.compile(r"(\d*)d(\d+)", re.IGNORECASE)

def parse_notation(text: str):
    text = text.replace(' ', '')
    m = DICE_RE.match(text)
    if not m:
        return None
    n_str, m_str = m.groups()
    n = int(n_str) if n_str else 1
    sides = int(m_str)
    return n, sides

def roll_dice(n, sides):
    return [random.randint(1, sides) for _ in range(n)]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1d4", callback_data="1d4"), InlineKeyboardButton("1d6", callback_data="1d6"), InlineKeyboardButton("1d8", callback_data="1d8")],
        [InlineKeyboardButton("1d10", callback_data="1d10"), InlineKeyboardButton("1d12", callback_data="1d12"), InlineKeyboardButton("1d20", callback_data="1d20")],
        [InlineKeyboardButton("———— Комбинации ————", callback_data="ignore")],
        [InlineKeyboardButton("2d4", callback_data="2d4"), InlineKeyboardButton("2d6", callback_data="2d6"), InlineKeyboardButton("2d8", callback_data="2d8")],
        [InlineKeyboardButton("2d10", callback_data="2d10"), InlineKeyboardButton("2d12", callback_data="2d12"), InlineKeyboardButton("2d20", callback_data="2d20")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(HELLO_MSG, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    expr = query.data

    if expr == "ignore":
        return

    parsed = parse_notation(expr)
    if not parsed:
        await query.edit_message_text("Ошибка формата.")
        return

    n, sides = parsed
    results = roll_dice(n, sides)

    msg_lines = []
    for r in results:
        line = f"Бросок: {r}"
        if sides == 20 and r == 20:
            line += f" — {NAT20_MSG}"
        if sides == 20 and r == 1:
            line += f" — {NAT1_MSG}"
        msg_lines.append(line)

    total = sum(results)
    msg_lines.append(f"Итоговый результат: {total}")

    await query.edit_message_text("\n".join(msg_lines))

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    parsed = parse_notation(text)

    if not parsed:
        await update.message.reply_text("Неверный формат. Пример: 2d20")
        return

    n, sides = parsed
    results = roll_dice(n, sides)

    msg_lines = []
    for r in results:
        line = f"Бросок: {r}"
        if sides == 20 and r == 20:
            line += f" — {NAT20_MSG}"
        if sides == 20 and r == 1:
            line += f" — {NAT1_MSG}"
        msg_lines.append(line)

    total = sum(results)
    msg_lines.append(f"Итоговый результат: {total}")

    await update.message.reply_text("\n".join(msg_lines))

if __name__ == "__main__":
    app = ApplicationBuilder().token("8559903050:AAG0GPePcYfvu76GLv6maFexkdPb9vLF5jE").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, roll))

    print("Бот запущен. Напиши ему в Telegram!")
    app.run_polling()