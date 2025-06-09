import re
import pytz

from nonebot import require
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Tuple
from urllib.parse import urlparse

from mengluo_vrc_bot.services.log import logger
from mengluo_vrc_bot.config.path import TEMPLATE_PATH

from .vrchat_utils import VRChatAPI

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import template_to_pic

# 常量定义
FILE_ID_PATTERN = re.compile(r"file_[a-zA-Z0-9-]+")
AUTHOR_TAG_PATTERN = re.compile(r'author_tag_')
LOCATION_PATTERN = r'wrld_([0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}):(\d+)(?:.*?~(group|hidden|friends)\()?'
DEFAULT_AVATAR_FILE_ID = "file_0e8c4e32-7444-44ea-ade4-313c010d4bae"
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

vrchat = VRChatAPI()

# 平台映射
class Platform(Enum):
    PC = "standalonewindows"
    ANDROID = "android"
    IOS = "ios"


PLATFORM_DISPLAY_MAP = {
    Platform.PC.value: "PC",
    Platform.ANDROID.value: "Android",
    Platform.IOS.value: "iOS"
}

# 信任等级配置
TRUST_LEVELS = [
    ("system_trust_veteran", "x-tag-veteran", "Trusted User", "rgb(177, 143, 255)"),
    ("system_trust_trusted", "x-tag-trusted", "Known User", "rgb(255, 123, 66)"),
    ("system_trust_known", "x-tag-known", "User", "rgb(43, 207, 92)"),
    ("system_trust_basic", "x-tag-basic", "New User", "rgb(23, 120, 255)")
]

# 内容标签映射
CONTENT_TAG_MAP = {
    "content_sex": "性暗示",
    "content_adult": "成人内容"
}

STATUS_MAP = {
    'active': 'online',
    'join me': 'joinme',
    'ask me': 'askme',
    'busy': 'busy'
}

LANGUAGE_MAP = {
    "language_eng": 'us',
    "language_kor": 'kr',
    "language_rus": 'ru',
    "language_spa": 'es',
    "language_por": 'pt',
    "language_zho": 'cn',
    "language_deu": 'de',
    "language_jpn": 'jp',
    "language_fra": 'fr',
    "language_swe": 'se',
    "language_nld": 'nl',
    "language_pol": 'pl',
    "language_dan": 'da',
    "language_nor": 'no',
    "language_ita": 'it',
    "language_thai": 'th',
    "language_fin": 'fi',
    "language_hun": 'hu',
    "language_ces": 'cz',
    "language_tur": 'tr',
    "language_ara": 'ar',
    "language_ron": 'ro',
    "language_vie": 'vn',
    "language_ase": 'as',
    "language_bfi": 'bf',
    "language_dse": 'ds',
    "language_fsl": 'fr',
    "language_kvk": 'kr',
}

@dataclass
class AvatarInfo:
    """头像信息数据类"""
    avatar_name: str = "default"
    avatar_status: bool = False
    avatar_is_owned: bool = False


@dataclass
class GroupData:
    """用户组数据类"""
    group_image: str = ""
    group_memberCount: str = ""
    group_name: str = ""
    group_is_owned: bool = False


@dataclass
class PlatformStatus:
    """平台状态数据类"""
    pc: Union[str, float] = ""
    android: Union[str, float] = ""
    ios: Union[str, float] = ""


def format_date_sync(date_str: str) -> str:
    """同步版本的日期格式化函数"""
    if date_str == "none":
        return "-"
    try:
        utc_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(BEIJING_TZ)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.error(f"无效的日期格式: {date_str}")
        return "-"


async def format_date(date_str: str) -> str:
    """异步版本的日期格式化函数（保持向后兼容）"""
    return format_date_sync(date_str)


def extract_file_id(url: str) -> Optional[str]:
    """从URL中提取文件ID"""
    match = FILE_ID_PATTERN.search(url)
    return match.group(0) if match else None


def calculate_ratio(numerator: int, denominator: int, precision: int = 2) -> float:
    """计算比率，安全处理除零情况"""
    return round((numerator / denominator) * 100, precision) if denominator > 0 else 0


def get_trust_level(tags: List[str]) -> Tuple[str, str, str]:
    """获取用户信任等级"""
    for tag, css_class, description, color in TRUST_LEVELS:
        if tag in tags:
            return css_class, description, color
    return "x-tag-untrusted", "Visitor", "rgb(204, 204, 204)"

def get_languages(tags: List[str]) -> Tuple:
    """获取用户语言"""
    languages = []
    for tag, language in LANGUAGE_MAP.items():
        if tag in tags:
            languages.append(language)
    return languages


def process_content_tags(tags: List[str]) -> List[str]:
    """处理内容标签"""
    return [CONTENT_TAG_MAP[tag] for tag in tags if tag in CONTENT_TAG_MAP]


def process_author_tags(tags: List[str]) -> str:
    """处理作者标签"""
    author_tags = []
    for tag in tags:
        if AUTHOR_TAG_PATTERN.search(tag):
            author_tags.append(tag.split("_")[-1].strip())
    return ",".join(author_tags) if author_tags else "-"


async def process_avatar_info(avatar_image_url: str, user_id: str) -> AvatarInfo:
    """处理头像相关信息"""
    avatar_info = AvatarInfo()

    try:
        file_id = extract_file_id(avatar_image_url)
        if file_id and file_id != DEFAULT_AVATAR_FILE_ID:
            avatar_info.avatar_status = True
            file_info = await vrchat.get_file_info(file_id)
            avatar_info.avatar_name = file_info["name"].split("-")[1].strip()
            avatar_info.avatar_is_owned = (file_info["ownerId"] == user_id)
    except Exception as e:
        logger.error(f"处理头像信息失败: {str(e)}")

    return avatar_info


def process_user_groups(groups_info: List[Dict], user_id: str) -> Tuple[int, bool, GroupData]:
    """处理用户组信息"""
    groups_count = len(groups_info)
    representing_group = next((group for group in groups_info if group['isRepresenting']), None)
    group_status = bool(representing_group)

    group_data = GroupData()
    if representing_group:
        iconId = representing_group['iconId']
        if iconId:
            group_data.group_image = f"https://api.vrchat.cloud/api/1/image/{iconId}/1/128"
        else:
            group_data.group_image = representing_group['iconUrl']
        group_data.group_is_owned = True if representing_group['ownerId'] == user_id else False
        group_data.group_memberCount = representing_group.get('memberCount', "")
        group_data.group_name = representing_group.get('name', "")

    return groups_count, group_status, group_data


def calculate_layout_height(text: str, line_threshold: int = 5,
                            short_height: int = 900, long_height: int = 1100) -> Tuple[int, str]:
    """根据文本内容计算布局高度"""
    if text.count('\n') > line_threshold:
        return long_height, "550px"
    return short_height, "350px"


async def process_unity_packages_for_world(unity_packages: List[Dict]) -> Tuple[PlatformStatus, str]:
    """处理世界的Unity包信息"""
    world_status = PlatformStatus()
    platforms = []

    for package in unity_packages:
        file_id = extract_file_id(package['assetUrl'])
        if not file_id:
            continue

        try:
            file_info = await vrchat.get_file_info(file_id)
            file_size_mb = round(file_info['versions'][1]['file']['sizeInBytes'] / (1024 * 1024), 2)
            platform = package['platform']
            unity_version = package['unityVersion']

            platform_display = PLATFORM_DISPLAY_MAP.get(platform, platform)
            platforms.append(f"{platform_display}/{unity_version}")

            if platform == Platform.PC.value:
                world_status.pc = file_size_mb
            elif platform == Platform.ANDROID.value:
                world_status.android = file_size_mb
            elif platform == Platform.IOS.value:
                world_status.ios = file_size_mb
        except Exception as e:
            logger.error(f"处理Unity包信息失败: {str(e)}")

    return world_status, ",".join(platforms)


def process_unity_packages_for_avatar(unity_packages: List[Dict]) -> Tuple[PlatformStatus, str, str]:
    """处理模型的Unity包信息"""
    avatar_status = PlatformStatus()
    platforms = []
    impostor_version = ""

    for package in unity_packages:
        if package.get('variant') == "impostor":
            impostor_version = package.get('impostorizerVersion', "")
            continue

        platform = package['platform']
        unity_version = package['unityVersion']
        performance_rating = package.get('performanceRating', '')

        platform_display = PLATFORM_DISPLAY_MAP.get(platform, platform)
        platforms.append(f"{platform_display}/{unity_version}")

        if platform == Platform.PC.value:
            avatar_status.pc = performance_rating
        elif platform == Platform.ANDROID.value:
            avatar_status.android = performance_rating
        elif platform == Platform.IOS.value:
            avatar_status.ios = performance_rating

    return avatar_status, ",".join(platforms), impostor_version


async def render_userinfo(user_id: str) -> Union[bytes, str]:
    """渲染用户信息"""
    try:
        user_info = await vrchat.get_user(user_id)
        if type(user_info) == str:
            return user_info

        # 处理用户组信息
        groups_info = await vrchat.get_user_groups(user_id)
        groups_count, group_status, group_data = process_user_groups(groups_info, user_id)

        # 处理信任等级
        known, know_description, _ = get_trust_level(user_info['tags'])

        languages = get_languages(user_info['tags'])

        # 处理头像信息
        avatar_info = await process_avatar_info(user_info['currentAvatarImageUrl'], user_id)

        # 计算布局高度
        height, min_height = calculate_layout_height(user_info['bio'])

        # 准备模板数据
        template_data = {
            "ageVerificationStatus": user_info['ageVerificationStatus'],
            "ageVerified": user_info['ageVerified'],
            "known": known,
            "known_description": know_description,
            "allowAvatarCopying": user_info['allowAvatarCopying'],
            "displayName": user_info['displayName'],
            "date_joined": user_info['date_joined'],
            "userIcon": user_info['userIcon'] or user_info['currentAvatarThumbnailImageUrl'],
            "bio": user_info['bio'],
            "pronouns": user_info['pronouns'],
            "status_description": user_info['statusDescription'],
            "platform": user_info['platform'] or user_info.get('last_platform'),
            "id": user_id,
            "avatar_name": avatar_info.avatar_name,
            "avatar_status": avatar_info.avatar_status,
            "avatar_is_owned": avatar_info.avatar_is_owned,
            "groups_info": groups_info,
            "groups_count": groups_count,
            "group_status": group_status,
            "group_image": group_data.group_image,
            "group_memberCount": group_data.group_memberCount,
            "group_name": group_data.group_name,
            "group_is_owned": group_data.group_is_owned,
            "badges": user_info['badges'],
            "min_height": min_height,
            "languages": languages
        }

        return await template_to_pic(
            template_path=str((TEMPLATE_PATH / "vrchat").absolute()),
            template_name="user.html",
            templates=template_data,
            pages={
                "viewport": {"width": 850, "height": height},
                "base_url": f"file://{TEMPLATE_PATH}"
            },
        )
    except Exception as e:
        logger.error(f"渲染用户信息失败: {str(e)}")
        return "渲染用户信息失败"


async def render_worldinfo(world_id: str) -> Union[bytes, str]:
    """渲染世界信息"""
    try:
        world_info = await vrchat.get_world(world_id)
        if type(world_info) == str:
            return world_info

        # 处理日期
        created_at = format_date_sync(world_info['created_at'])
        updated_at = format_date_sync(world_info['updated_at'])
        labs_publication_date = format_date_sync(world_info['labsPublicationDate'])
        publication_date = format_date_sync(world_info['publicationDate'])

        # 处理标签
        tags = world_info['tags']
        content_tags = process_content_tags(tags)
        author_tags = process_author_tags(tags)

        # 检查实验室状态
        release_status = "lab" if "system_labs" in tags else world_info['releaseStatus']

        # 处理Unity包
        world_status, world_platforms = await process_unity_packages_for_world(world_info['unityPackages'])

        # 计算统计数据
        visits = world_info['visits']
        favorites = world_info['favorites']
        ratio_favorite = calculate_ratio(favorites, visits)

        heat = world_info['heat']
        popularity = world_info['popularity']
        heat_display = f"{heat}{'🔥' * heat}"
        popularity_display = f"{popularity}{'💖' * popularity}"

        template_data = {
            "id": world_id,
            "authorName": world_info['authorName'],
            "capacity": world_info['capacity'],
            "created_at": created_at,
            "description": world_info['description'],
            "favorites": favorites,
            "heat": heat_display,
            "labsPublicationDate": labs_publication_date,
            "name": world_info['name'],
            "occupants": world_info['occupants'],
            "popularity": popularity_display,
            "publicationDate": publication_date,
            "recommendedCapacity": world_info['recommendedCapacity'],
            "releaseStatus": release_status,
            "thumbnailImageUrl": world_info['thumbnailImageUrl'],
            "updated_at": updated_at,
            "version": world_info['version'],
            "visits": visits,
            "ratio_favorite": ratio_favorite,
            "authorTags": author_tags,
            "contentTags": content_tags,
            "world_pc": world_status.pc,
            "world_android": world_status.android,
            "world_ios": world_status.ios,
            "world_platforms": world_platforms
        }

        return await template_to_pic(
            template_path=str((TEMPLATE_PATH / "vrchat").absolute()),
            template_name="world.html",
            templates=template_data,
            pages={
                "viewport": {"width": 850, "height": 510},
                "base_url": f"file://{TEMPLATE_PATH}"
            }
        )
    except Exception as e:
        logger.error(f"渲染地图信息失败: {str(e)}")
        return "渲染地图信息失败"


async def render_avatarinfo(avatar_id: str) -> Union[bytes, str]:
    """渲染模型信息"""
    try:
        avatar_info = await vrchat.get_avatar(avatar_id)
        if type(avatar_info) == str:
            return avatar_info

        # 处理日期
        created_at = format_date_sync(avatar_info['created_at'])
        updated_at = format_date_sync(avatar_info['updated_at'])

        # 处理Unity包
        avatar_status, avatar_platforms, avatar_impostor = process_unity_packages_for_avatar(
            avatar_info['unityPackages']
        )

        # 根据描述长度调整高度
        description = avatar_info['description']
        height = 420 if len(description) >= 100 else 340

        template_data = {
            "id": avatar_id,
            "authorName": avatar_info['authorName'],
            "created_at": created_at,
            "description": description,
            "name": avatar_info['name'],
            "updated_at": updated_at,
            "version": avatar_info['version'],
            "thumbnailImageUrl": avatar_info['thumbnailImageUrl'],
            "avatar_pc": avatar_status.pc,
            "avatar_android": avatar_status.android,
            "avatar_ios": avatar_status.ios,
            "avatar_platforms": avatar_platforms,
            "avatar_impostor": avatar_impostor
        }

        return await template_to_pic(
            template_path=str((TEMPLATE_PATH / "vrchat").absolute()),
            template_name="avatar.html",
            templates=template_data,
            pages={
                "viewport": {"width": 850, "height": height},
                "base_url": f"file://{TEMPLATE_PATH}"
            }
        )
    except Exception as e:
        logger.error(f"渲染模型信息失败: {str(e)}")
        return "渲染模型信息失败"


async def render_groupinfo(group_id: str) -> Union[bytes, str]:
    """渲染群组信息"""
    try:
        group_info = await vrchat.get_group(group_id)
        if type(group_info) == str:
            return group_info

        # 处理日期
        created_at = format_date_sync(group_info['createdAt'])

        # 获取群主信息
        owner_info = await vrchat.get_user(group_info['ownerId'])
        owner_name = owner_info["displayName"] if owner_info else "Unknown"

        # 处理链接图标
        links = group_info.get("links", [])
        link_icons = [
            f"https://icons.duckduckgo.com/ip2/{urlparse(link).netloc.split(':')[0]}.ico"
            for link in links
        ]

        # 处理规则
        rules = group_info['rules'] or "-"
        description = group_info['description']

        # 根据内容长度调整高度
        content_is_long = (len(description) > 100 or
                           len(rules) > 100 or
                           rules.count('\n') > 5)
        height = 750 if content_is_long else 570

        # 生成群组代码
        group_code = f"{group_info['shortCode']}.{group_info['discriminator']}"

        template_data = {
            "id": group_id,
            "bannerUrl": group_info['bannerUrl'],
            "createdAt": created_at,
            "description": description,
            "iconUrl": group_info['iconUrl'],
            "joinState": group_info['joinState'],
            "memberCount": group_info['memberCount'],
            "name": group_info['name'],
            "onlineMemberCount": group_info['onlineMemberCount'],
            "owner": owner_name,
            "rules": rules,
            "groupCode": group_code,
            "links": link_icons
        }

        return await template_to_pic(
            template_path=str((TEMPLATE_PATH / "vrchat").absolute()),
            template_name="group.html",
            templates=template_data,
            pages={
                "viewport": {"width": 850, "height": height},
                "base_url": f"file://{TEMPLATE_PATH}"
            }
        )
    except Exception as e:
        logger.error(f"渲染群组信息失败: {str(e)}")
        return "渲染群组信息失败"

async def render_friendsinfo(friends_status: bool, friends_number: int) -> Union[bytes, str]:
    """渲染好友信息"""
    try:
        friends_info = await vrchat.get_friends(friends_status, friends_number)
        if type(friends_info) == str:
            return friends_info
        new_friends_info = []
        web_friends_info = []
        private_friends_info = []
        for friend in friends_info:
            displayName = friend["displayName"]
            user_icon = friend["userIcon"] or friend["currentAvatarThumbnailImageUrl"]
            _, _, color = get_trust_level(friend['tags'])
            status = STATUS_MAP.get(friend["status"], friend["status"])
            location = friend["location"]
            if location == "offline":
                web_friends_info.append({
                    "displayName": displayName,
                    "user_icon": user_icon,
                    "color": color,
                    "status": status
                })
            elif location == "private":
                private_friends_info.append({
                    "displayName": displayName,
                    "user_icon": user_icon,
                    "color": color,
                    "status": status
                })
            else:
                match = re.search(LOCATION_PATTERN, location)
                uuid = "wrld_" + match.group(1)
                room_id = match.group(2)
                access_type = match.group(3) if match.group(3) else "public"
                if access_type == "hidden":
                    access_type = "friend+"
                location = (await vrchat.get_world(uuid))["name"] + " #" + str(room_id) + " " +access_type
                new_friends_info.append({
                    "displayName": displayName,
                    "user_icon": user_icon,
                    "location": location,
                    "color": color,
                    "status": status
                })
        friend_count = len(new_friends_info)
        web_count = len(web_friends_info)
        private_count = len(private_friends_info)
        height = 90 + (friend_count + 1) // 2 * 50 + (
            web_count + 1) // 2 * 50 + (private_count + 1) // 2 * 50
        template_data = {
            "friends_info": new_friends_info,
            "private_friends_info": private_friends_info,
            "web_friends_info": web_friends_info,
            "friend_count": friend_count,
            "web_count": web_count,
            "private_count": private_count,
        }
        return await template_to_pic(
            template_path=str((TEMPLATE_PATH / "vrchat").absolute()),
            template_name="friends.html",
            templates=template_data,
            pages={
                "viewport": {"width": 850, "height": height},
                "base_url": f"file://{TEMPLATE_PATH}"
            }
        )
    except Exception as e:
        logger.error(f"渲染好友信息失败: {str(e)}")
        return "渲染好友信息失败"