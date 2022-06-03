from unittest import mock

from loguru import logger

from hash2passbot.apps.bot import temp
from hash2passbot.config.config import config
from hash2passbot.db.models import User

fields_nums = {
    "user_id": "1",
    "username": "2",
    "first_name": "3",
    "last_name": "4",
}


async def save_statistics():
    # todo 6/3/2022 1:29 PM taima: обновление и перестройка
    # data = dict(temp.STATS)
    # await temp.STATS.refresh_from_db()
    # temp.STATS.total_requests_count = data["total_requests_count"]
    # temp.STATS.found_local_count = data["found_local_count"]
    # temp.STATS.found_in_saved_count = data["found_in_saved_count"]
    # temp.STATS.found_via_api_count = data["found_via_api_count"]
    # temp.STATS.not_found_count = data["not_found_count"]
    await temp.STATS.save()
    logger.success(f"Статистика сохранена")


async def part_sending(message, answer):
    if len(answer) > 4096:
        for x in range(0, len(answer), 4096):
            y = x + 4096
            await message.answer(answer[x:y])
    else:
        await message.answer(answer)


def parse_user_fields(fields_text: str) -> tuple:
    if "0" in fields_text:
        return ()
    else:
        return tuple(filter(lambda x: fields_nums[x] in fields_text, fields_nums))


async def get_mock_users() -> list:
    user = await User.exclude(user_id__in=config.bot.admins).first()
    users = []
    for i in range(250):
        mock_user = mock.Mock()
        mock_user.user_id = user.user_id
        mock_user.first_name = user.first_name
        users.append(mock_user)
    return users
