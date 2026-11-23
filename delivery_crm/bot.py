from __future__ import annotations

import logging
import re

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, ConversationHandler,
    MessageHandler, filters,
)

from .config import Config
from .storage import DeliveryStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("samurai.delivery")

DETAILS, PHONE, ADDRESS, RECEIPT = range(4)


def is_admin(user_id: int, cfg: Config) -> bool:
    return user_id in cfg.admin_ids


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "SAMURAI Delivery\nДля оформления заказа отправьте /order. "
        "По вопросам оплаты дождитесь ручной проверки администратором."
    )


async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Опишите заказ одним сообщением:")
    return DETAILS


async def order_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["details"] = update.message.text.strip()[:2000]
    await update.message.reply_text("Отправьте номер телефона для связи:")
    return PHONE


async def order_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not re.fullmatch(r"[+0-9() .-]{7,30}", phone):
        await update.message.reply_text("Номер выглядит некорректно. Отправьте номер ещё раз:")
        return PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text("Укажите полный адрес доставки:")
    return ADDRESS


async def order_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cfg: Config = context.application.bot_data["config"]
    store: DeliveryStore = context.application.bot_data["store"]
    address = update.message.text.strip()
    if len(address) < 6:
        await update.message.reply_text("Уточните адрес доставки:")
        return ADDRESS
    user = update.effective_user
    order_id = store.create_order(
        user.id, user.full_name, context.user_data["details"],
        context.user_data["phone"], address,
    )
    context.user_data["order_id"] = order_id
    await update.message.reply_text(
        f"Заказ №{order_id} создан.\nЦена: {cfg.price_text}\n"
        f"Оплата: {cfg.payment_instructions}\n\n"
        "После оплаты отправьте сюда фото чека. Проверка выполняется администратором вручную."
    )
    return RECEIPT


async def receipt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store: DeliveryStore = context.application.bot_data["store"]
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Использование: /receipt ORDER_ID")
        return ConversationHandler.END
    order_id = int(context.args[0])
    order = store.get_order(order_id)
    if not order or order["customer_id"] != update.effective_user.id:
        await update.message.reply_text("Заказ не найден.")
        return ConversationHandler.END
    if order["status"] != "awaiting_details":
        await update.message.reply_text("Для этого заказа чек уже отправлен или статус изменён.")
        return ConversationHandler.END
    context.user_data["order_id"] = order_id
    await update.message.reply_text(f"Отправьте фото чека для заказа №{order_id}.")
    return RECEIPT


async def receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store: DeliveryStore = context.application.bot_data["store"]
    order_id = context.user_data.get("order_id")
    photo = update.message.photo[-1]
    if not order_id or not store.submit_receipt(order_id, update.effective_user.id, photo.file_id):
        await update.message.reply_text("Не удалось привязать чек к заказу. Начните заново командой /order.")
        return ConversationHandler.END
    await update.message.reply_text(f"Фото чека принято. Заказ №{order_id} ожидает ручной проверки.")
    for admin_id in context.application.bot_data["config"].admin_ids:
        try:
            await context.bot.send_photo(
                admin_id, photo.file_id,
                caption=f"Чек заказа №{order_id}. Проверка: /approve {order_id} или /reject {order_id}",
            )
        except Exception:
            log.exception("Failed to notify admin about receipt for order %s", order_id)
    return ConversationHandler.END


async def receipt_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Оформление остановлено. Для нового заказа используйте /order.")
    return ConversationHandler.END


async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cfg: Config = context.application.bot_data["config"]
    if not is_admin(update.effective_user.id, cfg):
        return
    store: DeliveryStore = context.application.bot_data["store"]
    rows = store.list_orders()
    if not rows:
        await update.message.reply_text("Заказов пока нет.")
        return
    lines = [
        f"#{o['id']} | {o['status']} | {o['customer_name']} | {o['phone']} | {o['address']}"
        for o in rows
    ]
    await update.message.reply_text("\n".join(lines)[:3900])


async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cfg: Config = context.application.bot_data["config"]
    if not is_admin(update.effective_user.id, cfg):
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Использование: /approve ORDER_ID")
        return
    order_id = int(context.args[0])
    store: DeliveryStore = context.application.bot_data["store"]
    if not store.approve(order_id):
        await update.message.reply_text("Нельзя подтвердить этот заказ: нет чека или статус уже изменён.")
        return
    order = store.get_order(order_id)
    await context.bot.send_message(order["customer_id"], f"Оплата заказа №{order_id} подтверждена. Ожидайте назначения курьера.")


async def admin_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cfg: Config = context.application.bot_data["config"]
    if not is_admin(update.effective_user.id, cfg):
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Использование: /reject ORDER_ID")
        return
    order_id = int(context.args[0])
    store: DeliveryStore = context.application.bot_data["store"]
    if not store.reject(order_id):
        await update.message.reply_text("Заказ не находится на проверке.")
        return
    order = store.get_order(order_id)
    await context.bot.send_message(order["customer_id"], f"Оплата заказа №{order_id} отклонена. Свяжитесь с администратором.")


async def admin_assign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cfg: Config = context.application.bot_data["config"]
    if not is_admin(update.effective_user.id, cfg):
        return
    if len(context.args) != 2 or not all(x.isdigit() for x in context.args):
        await update.message.reply_text("Использование: /assign ORDER_ID COURIER_TELEGRAM_ID")
        return
    order_id, courier_id = map(int, context.args)
    store: DeliveryStore = context.application.bot_data["store"]
    if not store.assign(order_id, courier_id):
        await update.message.reply_text("Назначение невозможно: заказ должен быть подтверждён.")
        return
    order = store.get_order(order_id)
    await context.bot.send_message(
        courier_id,
        f"Вам назначен заказ №{order_id}.\nДетали: {order['details']}\n"
        f"Телефон клиента: {order['phone']}\nАдрес: {order['address']}\n"
        f"После доставки отправьте фото в этот чат с подписью: done {order_id}",
    )
    await context.bot.send_message(order["customer_id"], f"Заказ №{order_id} передан курьеру.")


async def courier_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store: DeliveryStore = context.application.bot_data["store"]
    caption = update.message.caption or ""
    match = re.fullmatch(r"done\s+(\d+)", caption.strip(), re.IGNORECASE)
    if not match:
        return
    order_id = int(match.group(1))
    delivered = store.mark_delivered(order_id, update.effective_user.id, update.message.photo[-1].file_id)
    if not delivered:
        await update.message.reply_text("Заказ не найден, не назначен вам или уже закрыт.")
        return
    await update.message.reply_text(f"Заказ №{order_id} отмечен доставленным.")
    await context.bot.send_photo(
        delivered["customer_id"], update.message.photo[-1].file_id,
        caption=f"Заказ №{order_id} доставлен. Фото подтверждения от курьера.",
    )


def build_application(cfg: Config) -> Application:
    store = DeliveryStore(cfg.db_path)
    app = Application.builder().token(cfg.token).build()
    app.bot_data["config"] = cfg
    app.bot_data["store"] = store

    conversation = ConversationHandler(
        entry_points=[CommandHandler("order", order_start), CommandHandler("receipt", receipt_start)],
        states={
            DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_details)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_address)],
            RECEIPT: [MessageHandler(filters.PHOTO, receipt_photo)],
        },
        fallbacks=[CommandHandler("cancel", receipt_cancel)],
        allow_reentry=True,
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversation)
    app.add_handler(CommandHandler("orders", admin_orders))
    app.add_handler(CommandHandler("approve", admin_approve))
    app.add_handler(CommandHandler("reject", admin_reject))
    app.add_handler(CommandHandler("assign", admin_assign))
    app.add_handler(MessageHandler(filters.PHOTO, courier_photo))
    return app


def main():
    cfg = Config.from_env()
    app = build_application(cfg)
    log.info("Starting Samurai Delivery CRM polling")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
