class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "7885908019"
    sudo_users = ("7756901810", "8043832960")  # Tuple me proper format
    GROUP_ID = -1002372914024
    TOKEN = "7689391231:AAEHXLz_uEv4Kpd-pZHQqVjkPujA7-ObJZw"
    mongo_url = "mongodb+srv://Sunnydeol:TGDARK0987@cluster0.fsb3s.mongodb.net/?retryWrites=true&w=majority"
    PHOTO_URL = ["https://telegra.ph/file/b925c3985f0f325e62e17.jpg", "https://telegra.ph/file/4211fb191383d895dab9d.jpg"]
    SUPPORT_CHAT = "https://t.me/+ZTeO__YsQoIwNTVl"
    UPDATE_CHAT = "https://t.me/Anime_P_F_P"
    BOT_USERNAME = "Waifu_ChanBbot"
    CHARA_CHANNEL_ID = "-1002640379822"
    api_id = 28159105
    api_hash = "a0936ddf210a7e091e19947c7dc70c91"

    
class Production(Config):
    LOGGER = True


class Development(Config):  # ✅ Colon laga diya
    LOGGER = True
