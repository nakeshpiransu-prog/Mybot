import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 Class 10th PDFs", callback_data="class_10")],
        [InlineKeyboardButton("📚 Class 12th (Inter) PDFs", callback_data="class_12")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 नमस्कार! आपका स्वागत है। कृपया अपनी कक्षा चुनें:",
        reply_markup=reply_markup
    )

# Button click handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "class_10":
        keyboard = [
            [InlineKeyboardButton("हिंदी (Hindi)", callback_data="sub_10_hindi")],
            [InlineKeyboardButton("मानव विज्ञान (Human Science)", callback_data="sub_10_human_science")],
            [InlineKeyboardButton("गणित (Math)", callback_data="sub_10_math")],
            [InlineKeyboardButton("विज्ञान (Science)", callback_data="sub_10_science")],
            [InlineKeyboardButton("अंग्रेजी (English)", callback_data="sub_10_english")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        await query.edit_message_text("📖 **Class 10th** के विषय चुनें:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "class_12":
        keyboard = [
            [InlineKeyboardButton("हिंदी (Hindi)", callback_data="sub_12_hindi")],
            [InlineKeyboardButton("अंग्रेजी (English)", callback_data="sub_12_english")],
            [InlineKeyboardButton("इतिहास (History)", callback_data="sub_12_history")],
            [InlineKeyboardButton("गणित (Math)", callback_data="sub_12_math")],
            [InlineKeyboardButton("भौतिक विज्ञान (Physics)", callback_data="sub_12_physics")],
            [InlineKeyboardButton("रसायन विज्ञान (Chemistry)", callback_data="sub_12_chemistry")],
            [InlineKeyboardButton("जीव विज्ञान (Biology)", callback_data="sub_12_biology")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        await query.edit_message_text("📖 **Class 12th** के विषय चुनें:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("📚 Class 10th PDFs", callback_data="class_10")],
            [InlineKeyboardButton("📚 Class 12th (Inter) PDFs", callback_data="class_12")]
        ]
        await query.edit_message_text("👋 मुख्य मेनू में आपका स्वागत है। कृपया अपनी कक्षा चुनें:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("sub_"):
        parts = data.split("_")
        cls = parts[1]
        subject = parts[2]
        
        back_callback = "class_10" if cls == "10" else "class_12"
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data=back_callback)]]
        
        pdf_database = {
            "10_hindi": "BQACAgUAAxkBAANXamn_A6QB4YV3zD6boTT8bTIsnSUAArgnAALVjFFXyXw_lTNFCoY9BA",
            "10_human_science": "BQACAgUAAxkBAANZamn_xYPi2USTt61bnr4abSXfmVkAAronAALVjFFX8oZhcjsw2789BA",
            "10_math": "BQACAgUAAxkBAANbamoAARJXDBXz8BkU3HHmZjkct2t_AAK8JwAC1YxRV6hU-_12kCLVPQQ",
            "10_science": "BQACAgUAAxkBAANeamoAAaL8GI5fXtuC_cFSwaljEob9AAK_JwAC1YxRV-wRSuV2i9bmPQQ",
            "10_english": "BQACAgUAAxkBAANgamoAAd3-JCosEuakTkChqQj1IA0SAALEJwAC1YxRV2PJbeCtrrKCPQQ",
            "12_hindi": "BQACAgUAAxkBAANiamoBMXha1g44rnLa7YJVvYz6xAkAAscnAALVjFFXCn2Ee9wLn-09BA",
            "12_english": "BQACAgUAAxkBAANkamoBXBlSVzgCBsIedjuN9WlM_QsAAsgnAALVjFFXXlvHYceqNHU9BA",
            "12_history": "BQACAgUAAxkBAANmamoBhgKAFYJRO4DmUci4KZ7wtIcAAsknAALVjFFXbn8ZYmCyA3k9BA",
            "12_math": "BQACAgUAAxkBAANoamoBrH5g9uMHAAFuR9OaDViT3SVZAALKJwAC1YxRVxRNqUxua1QxPQQ",
            "12_physics": "BQACAgUAAxkBAANqamoB3lwEHyTE99Tx53Eh8XMf5RYAAssnAALVjFFXDhqUeqyPpjs9BA",
            "12_chemistry": "BQACAgUAAxkBAANsamoCDdCGxib_RvHO4jgp_Cs1xpAAAswnAALVjFFXpNcKo1gIk6M9BA",
            "12_biology": "BQACAgUAAxkBAANuamoCTzmSO02MSFwzAab7ObEtbyMAAs0nAALVjFFXhYR4X55sqNw9BA",
        }
        
        key = f"{cls}_{subject}"
        file_id_to_send = pdf_database.get(key)
        
        if file_id_to_send:
            await query.message.delete()
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=file_id_to_send,
                caption=f"📄 यह रही आपकी Class {cls} की पीडीएफ!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            subject_names = {
                "hindi": "हिंदी", "english": "अंग्रेजी", "math": "गणित", 
                "science": "विज्ञान", "human_science": "मानव विज्ञान",
                "history": "इतिहास", "physics": "भौतिक विज्ञान", 
                "chemistry": "रसायन विज्ञान", "biology": "जीव विज्ञान"
            }
            sub_name = subject_names.get(subject, subject)
            await query.edit_message_text(
                f"⚠️ Class {cls} - {sub_name} की पीडीएफ अभी जोड़ी नहीं गई है।", 
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

def main():
    # यहाँ अपना बोट टोकन (Bot Token) डालें
    TOKEN = "8929664635:AAFmYrJ8GTknw9sIVp8rOIK2lXaW4TY_aSg"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Bot started successfully...")
    app.run_polling()

if __name__ == '__main__':
    main()
