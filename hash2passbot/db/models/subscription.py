import typing
from typing import List

from tortoise import models, fields
from tortoise.functions import Sum

from hash2passbot.config.config import config

if typing.TYPE_CHECKING:
    from hash2passbot.db.models.base import User


class AbstractSubscription(models.Model):
    pass


# todo 5/31/2022 12:38 PM taima: сделать дневной лимит
class SubscriptionTemplate(models.Model):
    """Шаблоны для создания подписок"""
    title = fields.CharField(255, default="Базовая подписка")
    price = fields.IntField(default=0)
    limit = fields.IntField(null=True, default=config.bot.default_limit)

    # duration = fields.IntField(default=0)

    def __str__(self):
        return self.title

    # class Meta:
    #     table = "subscriptions_templates"

    @property
    def view(self):
        return (f"Название: {self.title}\n"
                f"Цена: {self.price}\n"
                # f"Длительность подписки: {self.duration}\n"
                f"Лимит: {self.limit or 'Безлимит'}")

    @classmethod
    async def create_from_dict(cls, data: list | dict) -> List | "SubscriptionTemplate":
        if isinstance(data, list):
            return [await SubscriptionTemplate.create(**obj) for obj in data]
        else:
            return await SubscriptionTemplate.create(**data)


class Subscription(SubscriptionTemplate):
    """Подписки с привязкой к пользователю"""
    connected_at = fields.DatetimeField(auto_now_add=True)
    user: "User" = fields.OneToOneField("models.User")

    # class Meta:
    #     table = "subscriptions"

    async def set_limit(self, limit: int | str):
        self.limit = limit
        await self.save(update_fields=["limit"])

    @classmethod
    async def all_limits(cls) -> int:
        return (await cls.all().annotate(count=Sum("limit")).values("count"))[0].get("count")

    @property
    def view(self):
        return (f"Название: {self.title}\n"
                # f"Цена {self.price}\n"
                # f"Длительность подписки: {self.duration}\n"
                f"Лимит: {self.limit or 'Безлимит'}")

    async def decr(self):
        self.limit -= 1
        await self.save(update_fields=["limit"])
