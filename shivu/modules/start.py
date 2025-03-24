import random
from html import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from shivu import application, PHOTO_URL, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID
from shivu import pm_users as collection

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username
    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:
        await collection.insert_one({"_id": user_id, "first_name": first_name, "username": username})
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"New user Started The Bot..\n User: <a href='tg://user?id={user_id}'>{escape(first_name)}</a>",
            parse_mode='HTML'
        )
    else:
        if user_data['first_name'] != first_name or user_data['username'] != username:
            await collection.update_one(
                {"_id": user_id}, {"$set": {"first_name": first_name, "username": username}}
            )

    caption = """***Heyyyy...***
***I am An Open Source Character Catcher Bot... Add me in your group, and I will send random characters after every 100 messages in the group. Use /guess to collect characters and check your collection with /Harem. So add me in your groups and collect your harem!***"""

    keyboard = [
        [InlineKeyboardButton("ADD ME", url=f'http://t.me/Waifu_ChanBbot?startgroup=new')],
        [
            InlineKeyboardButton("SUPPORT", url='https://t.me/+ZTeO__YsQoIwNTVl'),
            InlineKeyboardButton("UPDATES", url='https://t.me/Anime_P_F_P')
        ],
        [InlineKeyboardButton("HELP", callback_data='help')],
        [InlineKeyboardButton("SOURCE", url='http://postimg.cc/bsFFs4YF')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    photo_url = random.choice(PHOTO_URL)

    if update.effective_chat.type == "private":
        await context.bot.send_photo(
            chat_id=update.effective_chat.id, 
            photo=photo_url, 
            caption=caption, 
            reply_markup=reply_markup, 
            parse_mode='markdown'
        )
    else:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id, 
            photo=photo_url, 
            caption="🎴 Alive!?... Connect to me in PM for more information.", 
            reply_markup=reply_markup
        )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """***Help Section:***
***/guess*** - To guess a character (works in groups only)
***/fav*** - Add your favorite character
***/trade*** - Trade characters
***/gift*** - Give a character from your collection to another user (works in groups only)
***/collection*** - View your collection
***/topgroups*** - See the top groups where people guess the most
***/top*** - View top users
***/ctop*** - Your chat's top users
***/changetime*** - Change character appearance time (works in groups only)"""

        help_keyboard = [[InlineKeyboardButton("⤾ Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(help_keyboard)

        await context.bot.edit_message_caption(
            chat_id=update.effective_chat.id, 
            message_id=query.message.message_id, 
            caption=help_text, 
            reply_markup=reply_markup, 
            parse_mode='markdown'
        )

    elif query.data == 'back':
        caption = """***Hoyyyy...*** ✨
***I am an open-source character catcher bot. Add me in your group, and I will send random characters after every 100 messages in the group. Use /guess to collect characters and check your collection with /Harem. So add me in your groups and collect your harem!***"""

        keyboard = [
            [InlineKeyboardButton("ADD ME", url=f'http://t.me/Waifu_ChanBbot?startgroup=new')],
            [
                InlineKeyboardButton("SUPPORT", url='https://t.me/+ZTeO__YsQoIwNTVl'),
                InlineKeyboardButton("UPDATES", url='https://t.me/Anime_P_F_P')
            ],
            [InlineKeyboardButton("HELP", callback_data='help')],
            [InlineKeyboardButton("SOURCE", url='http://postimg.cc/bsFFs4YF')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_caption(
            chat_id=update.effective_chat.id, 
            message_id=query.message.message_id, 
            caption=caption, 
            reply_markup=reply_markup, 
            parse_mode='markdown'
        )

application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$', block=False))
start_handler = CommandHandler('start', start, block=False)
application.add_handler(start_handler)
