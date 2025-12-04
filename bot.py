import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    MessageReactionHandler,
    CommandHandler,
    ContextTypes,
    filters
)

TOKEN = "8180312496:AAGUVMqZfX1AdREKnTfPq6KZzJdZufpHeAc"
ADMIN_ID = 592552916

link = {}

print("BOT CARGANDO...")

# ---------------------------
# /start - mensaje de bienvenida
# ---------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Bienvenido al soporte.\n"
        "Escríbeme cualquier duda o mensaje y te responderé."
    )

# ---------------------------
# Mensaje del usuario → reenviar al admin + reacción temporal
# ---------------------------
async def recibir_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # No reenviar si es el admin
    if user_id == ADMIN_ID:
        return

    # Reenviar al admin
    reenviado = await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=user_id,
        message_id=update.message.message_id
    )

    # Guardar relación
    link[reenviado.message_id] = user_id

    # Reacción temporal al mensaje del usuario
    try:
        # Agregar reacción 👍
        await context.bot._post(
            "setMessageReaction",
            data={
                "chat_id": update.effective_chat.id,
                "message_id": update.message.message_id,
                "reaction": [{"type": "emoji", "emoji": "👍"}]
            }
        )
        # Esperar
        await asyncio.sleep(3.5)
        # Quitar reacción
        await context.bot._post(
            "setMessageReaction",
            data={
                "chat_id": update.effective_chat.id,
                "message_id": update.message.message_id,
                "reaction": []
            }
        )
    except Exception as e:
        print("Error reacción temporal usuario:", e)

# ---------------------------
# Admin responde → enviar mensaje al usuario + reacción temporal
# ---------------------------
async def admin_respuesta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Si NO es el admin, tratar como usuario normal
    if user_id != ADMIN_ID:
        return await recibir_usuario(update, context)

    # Debe ser respuesta a un mensaje reenviado
    if update.message.reply_to_message is None:
        return

    msg_id = update.message.reply_to_message.message_id

    if msg_id not in link:
        return

    destinatario = link[msg_id]

    # Enviar respuesta al usuario
    await context.bot.send_message(chat_id=destinatario, text=update.message.text)

    # Reacción temporal al mensaje del admin
    try:
        # Agregar reacción 👍
        await context.bot._post(
            "setMessageReaction",
            data={
                "chat_id": update.effective_chat.id,
                "message_id": update.message.message_id,
                "reaction": [{"type": "emoji", "emoji": "👍"}]
            }
        )
        # Esperar
        await asyncio.sleep(3.5)
        # Quitar reacción
        await context.bot._post(
            "setMessageReaction",
            data={
                "chat_id": update.effective_chat.id,
                "message_id": update.message.message_id,
                "reaction": []
            }
        )
    except Exception as e:
        print("Error reacción temporal admin:", e)

# ---------------------------
# Admin reacciona a un mensaje reenviado
# ---------------------------
async def admin_reaccion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    msg_id = update.message.message_id
    if msg_id not in link:
        return

    destinatario = link[msg_id]
    reaction = update.message.reactions[0].emoji

    respuestas = {
        "👍": "✌️ ¡Perfecto!",
        "❤️": "❤️ ¡Gracias por tu mensaje!",
        "😂": "😂 jajaja!",
        "❗": "❗ En un momento te respondo.",
        "❓": "❓ ¿Podrías explicar un poco más?"
    }

    texto = respuestas.get(reaction, f"Reacción: {reaction}")
    await context.bot.send_message(chat_id=destinatario, text=texto)

# ---------------------------
# MAIN
# ---------------------------
async def main():
    app = Application.builder().token(TOKEN).build()

    # Comando /start
    app.add_handler(CommandHandler("start", start_cmd))

    # Mensajes y respuestas
    app.add_handler(MessageHandler(filters.TEXT, admin_respuesta))

    # Reacciones del admin
    app.add_handler(MessageReactionHandler(admin_reaccion))

    print("BOT INICIADO, ESPERANDO MENSAJES...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

asyncio.run(main())