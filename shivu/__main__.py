# ... (imports and initializations remain unchanged)

for module_name in ALL_MODULES:
    importlib.import_module("shivu.modules." + module_name)

def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        message_frequency = chat_frequency.get('message_frequency', 5) if chat_frequency else 5

        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:
                    await update.message.reply_text(f"⚠️ Don't Spam {update.effective_user.first_name}...\nYour Messages Will be ignored for 10 Minutes...")
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        message_counts[chat_id] = message_counts.get(chat_id, 0) + 1
        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)
            message_counts[chat_id] = 0

async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    all_characters = list(await collection.find({}).to_list(length=None))

    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    available_characters = [c for c in all_characters if c['id'] not in sent_characters[chat_id]]
    if not available_characters:
        sent_characters[chat_id] = []
        available_characters = all_characters

    character = random.choice(available_characters)
    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    img_url = character.get('img_url')
    if not img_url or not isinstance(img_url, str) or not img_url.startswith("http"):
        await update.message.reply_text("Image URL is invalid or missing.")
        return

    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=img_url,
            caption=f"""A New {character['rarity']} Character Appeared...\n/guess Character Name and add in Your Harem""",
            parse_mode='Markdown'
        )
    except Exception as e:
        LOGGER.error(f"Error sending image: {e}")
        await update.message.reply_text("Failed to send image. Possibly broken URL or format issue.")

async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in last_characters:
        return

    if chat_id in first_correct_guesses:
        await update.message.reply_text(f'❌ Already Guessed By Someone.. Try Next Time Bruhh ')
        return

    guess_text = ' '.join(context.args).lower() if context.args else ''
    if "()" in guess_text or "&" in guess_text:
        await update.message.reply_text("Nahh You Can't use This Types of words in your guess..❌ ")
        return

    name_parts = last_characters[chat_id]['name'].lower().split()
    if sorted(name_parts) == sorted(guess_text.split()) or any(part == guess_text for part in name_parts):
        first_correct_guesses[chat_id] = user_id

        user = await user_collection.find_one({'id': user_id})
        if user:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await user_collection.update_one({'id': user_id}, {'$set': update_fields})

            await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
        else:
            await user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [last_characters[chat_id]],
            })

        await group_user_totals_collection.update_one(
            {'user_id': user_id, 'group_id': chat_id},
            {'$set': {
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name
            }, '$inc': {'count': 1}}, upsert=True
        )

        await top_global_groups_collection.update_one(
            {'group_id': chat_id},
            {'$set': {'group_name': update.effective_chat.title}, '$inc': {'count': 1}}, upsert=True
        )

        keyboard = [[InlineKeyboardButton("See Harem", switch_inline_query_current_chat=f"collection.{user_id}")]]
        await update.message.reply_text(
            f'<b><a href="tg://user?id={user_id}">{escape(update.effective_user.first_name)}</a></b> You Guessed a New Character ✅  \n\n𝗡𝗔𝗠𝗘: <b>{last_characters[chat_id]["name"]}</b> \n𝗔𝗡𝗜𝗠𝗘: <b>{last_characters[chat_id]["anime"]}</b> \n𝗥𝗔𝗥𝗜𝗧𝗬: <b>{last_characters[chat_id]["rarity"]}</b>\n\nThis Character added in Your harem.. use /harem To see',
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text('Please Write Correct Character Name... ❌ ')

async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text('Please provide Character id...')
        return
    character_id = context.args[0]
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('You have not Guessed any characters yet....')
        return
    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('This Character is Not In your collection')
        return
    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': [character_id]}})
    await update.message.reply_text(f'Character {character["name"]} has been added to your favorite...')

def main() -> None:
    application.add_handler(CommandHandler(["guess", "protecc", "collect", "grab", "hunt"], guess, block=False))
    application.add_handler(CommandHandler("fav", fav, block=False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    shivuu.start()
    LOGGER.info("Bot started")
    main()
