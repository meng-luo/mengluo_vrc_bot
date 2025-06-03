from mengluo_vrc_bot.utils.vrchat_utils import get_user

async def get_user_name(user_id):
    user_info = await get_user(user_id)
    if user_info:
        return user_info.get("displayName")
    else:
        return None