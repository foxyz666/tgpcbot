from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import restricted
from utils.keyboards import get_persistent_keyboard, get_update_menu
from utils.i18n import t
from utils.updater import check_for_updates

@restricted
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отправляем закрепленную клавиатуру вниз
    await update.message.reply_text(
        text="🚀 " + t("menu_main"), 
        reply_markup=get_persistent_keyboard(),
        parse_mode="Markdown"
    )

@restricted
async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Checking for updates... ⏳")
    has_update, update_info = check_for_updates()
    
    if has_update:
        text = f"🌟 **New Update Available!**\n\n**Version:** {update_info.get('tag_name')}\n**Details:**\n{update_info.get('body', 'No details provided.')}\n\nDo you want to update now?"
        await msg.edit_text(text, reply_markup=get_update_menu(), parse_mode="Markdown")
    else:
        await msg.edit_text("✅ You are using the latest version of the bot.")

