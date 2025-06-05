from mengluo_vrc_bot.utils.vrchat_utils import VRChatAPI

async def get_user_name(user_id):
    user_info = await VRChatAPI().get_user(user_id)
    if user_info:
        return user_info.get("displayName")
    else:
        return None