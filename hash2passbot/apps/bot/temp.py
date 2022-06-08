import typing

from hash2passbot.db.models import Statistic

if typing.TYPE_CHECKING:
    from hash2passbot.apps.bot.utils import MailSender

SUBSCRIPTION_CHANNELS: list[tuple[str, str]] = []
MAIL_SENDER: typing.Optional["MailSender"] = None
BOT_RUNNING: bool = True
STATS: Statistic | None = None
MENU: dict[str, str] | None = None
