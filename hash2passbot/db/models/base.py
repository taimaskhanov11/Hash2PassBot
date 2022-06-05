import datetime
import typing
from unittest.mock import Mock

import aiohttp
import asyncpg
from aiogram.types import BufferedInputFile
from loguru import logger
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_queryset_creator, PydanticListModel
from tortoise.models import MODEL
from tortoise.transactions import in_transaction

from hash2passbot.config.config import config
from hash2passbot.db import init_hash_db
from hash2passbot.db.models.invoice import InvoiceQiwi, InvoiceCrypto
from hash2passbot.db.models.subscription import Subscription


class Statistic(models.Model):
    total_requests_count = fields.IntField(default=0)
    found_local_count = fields.IntField(default=0)
    found_in_saved_count = fields.IntField(default=0)
    found_via_api_count = fields.IntField(default=0)
    not_found_count = fields.IntField(default=0)


class ApiPassword(models.Model):
    """Пароль и хеши полученные через api"""
    password = fields.CharField(512, source_field="pass")
    algorithm = fields.CharField(255, index=True)
    hash = fields.CharField(255, index=True)

    @classmethod
    async def search_in_saved(cls, _hash, hash_type) -> typing.Optional["ApiPassword"]:
        logger.debug(f"Поиск хеша в сохраненной базе {_hash}[{hash_type}]")
        return await ApiPassword.get_or_none(hash=_hash, algorithm=hash_type)


class Password:
    password = fields.CharField(512, source_field="pass")
    hash_md5 = fields.CharField(40, index=True)
    hash_md25 = fields.CharField(40, index=True)
    hash_sh1 = fields.CharField(40, index=True)
    connection: asyncpg.Connection | None = None

    class Meta:
        table = "passwords"

    @classmethod
    async def search_in_local(cls, _hash: str, hash_type) -> typing.Optional["Password"]:
        logger.debug(f"Поиск хеша в локальной базе {_hash} [{hash_type}]")
        found_password: asyncpg.Record | None = None
        if not cls.connection:
            cls.connection = await init_hash_db()
        if cls.connection.is_closed():
            cls.connection = await init_hash_db()

        if len(_hash) == 40:
            expression = f"""
                select pass from passwords where hash_sha1 = '{_hash}'
                """
            found_password = await cls.connection.fetchrow(expression)
        elif len(_hash) == 32:
            expression = f"""
                            select pass from passwords where hash_md5 ='{_hash}'
                            """
            found_password = await cls.connection.fetchrow(expression)
            if not found_password:
                expression = f"""
                    select pass from passwords where hash_md25 = '{_hash}'
                    """
                found_password: asyncpg.Record = await cls.connection.fetchrow(expression)
        if found_password:
            mock = Mock()
            mock.password = found_password.get("pass")
            found_password = mock
        logger.trace(found_password)
        return found_password

    # todo 6/1/2022 2:49 PM taima: поймать ошибку
    @classmethod
    async def search_in_api(cls, _hash: str, hash_type) -> typing.Optional[ApiPassword]:
        logger.debug(f"Поиск хеша через API {_hash}[{hash_type}]")
        async with aiohttp.ClientSession() as session:
            async with session.get(config.hash_api.url, params=config.hash_api.params | {"hash": _hash,
                                                                                         "hash_type": hash_type}) as res:
                password = await res.text()
                logger.debug(password)
                if "ERROR CODE" not in password:
                    if password.strip():
                        password = await ApiPassword.create(
                            password=password,
                            hash=_hash,
                            algorithm=hash_type
                        )
                        return password
                # return password


# legacy
class Password_old:
    password = fields.CharField(512, source_field="pass")
    hash_md5 = fields.CharField(40, index=True)
    hash_md25 = fields.CharField(40, index=True)
    hash_sh1 = fields.CharField(40, index=True)

    class Meta:
        table = "passwords"

    @classmethod
    async def search_in_local(cls, _hash: str, hash_type) -> typing.Optional["Password"]:
        logger.debug(f"Поиск хеша в локальной базе {_hash} [{hash_type}]")
        found_password = None
        if len(_hash) == 40:
            found_password = await cls.get_or_none(hash_sh1=_hash)
        elif len(_hash) == 32:
            found_password = await cls.get_or_none(hash_md5=_hash)
            if not found_password:
                found_password = await cls.get_or_none(hash_md25=_hash)
        return found_password

    # todo 6/1/2022 2:49 PM taima: поймать ошибку
    @classmethod
    async def search_in_api(cls, _hash: str, hash_type) -> typing.Optional[ApiPassword]:
        logger.debug(f"Поиск хеша через API {_hash}[{hash_type}]")
        async with aiohttp.ClientSession() as session:
            async with session.get(config.hash_api.url, params=config.hash_api.params | {"hash": _hash,
                                                                                         "hash_type": hash_type}) as res:
                password = await res.text()
                logger.debug(password)
                if "ERROR CODE" not in password:
                    if password.strip():
                        password = await ApiPassword.create(
                            password=password,
                            hash=_hash,
                            algorithm=hash_type
                        )
                        return password
                # return password


class Channel(models.Model):
    skin = fields.CharField(100, index=True)
    link = fields.CharField(100, index=True)


class User(models.Model):
    """Хранит базовые данные пользователя"""
    user_id = fields.BigIntField(index=True, unique=True)
    username = fields.CharField(32, unique=True, index=True, null=True)
    first_name = fields.CharField(255, null=True)
    last_name = fields.CharField(255, null=True)
    locale = fields.CharField(32, default="ru")
    registered_at = fields.DatetimeField(auto_now_add=True)
    is_search = fields.BooleanField(default=False)
    # subscription: fields.OneToOneRelation[Subscription]
    subscription: Subscription
    invoice_cryptos: fields.ReverseRelation[InvoiceCrypto]
    invoice_qiwis: fields.ReverseRelation[InvoiceQiwi]

    # class Meta:
    #     table = "users"
    # async def create

    async def __aenter__(self):
        # Включение режима блокировки пока запрос не завершиться
        await self.switch_search_to(True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Отключение режима поиска
        await self.switch_search_to(False)
        if exc_type:
            logger.exception(f"{exc_type}, {exc_val}, {exc_tb}")

    # async def get_sub_user(self, user_id:, bot):

    async def switch_search_to(self, status: bool):
        self.is_search = status
        await self.save(update_fields=["is_search"])

    async def get_payments(self) -> list[InvoiceCrypto, InvoiceQiwi]:
        await self.fetch_related("subscription")
        invoice_cryptos = await self.invoice_cryptos.filter(is_paid=True)
        invoice_qiwis = await self.invoice_qiwis.filter(is_paid=True)
        invoice_cryptos.extend(invoice_qiwis)
        invoice_cryptos.sort(key=lambda x: x.created_at)
        return invoice_cryptos

    @classmethod
    async def count_all(cls):
        return await cls.all().count()

    @classmethod
    async def count_new_today(cls) -> int:
        date = datetime.date.today()
        # return await cls.filter(registered_at=).count()
        return await User.filter(
            registered_at__year=date.year,
            registered_at__month=date.month,
            registered_at__day=date.day,
        ).count()


    @classmethod
    async def create(cls: typing.Type[MODEL], using_db=False, **kwargs) -> MODEL:
        async with in_transaction():
            user = await super().create(using_db, **kwargs)
            await Subscription.create(user=user)
            return user

    @classmethod
    async def reset_search(cls):
        count = await cls.filter(is_search=True).update(is_search=False)
        logger.trace(f"Сброс состояния поиска: {count}")

    @classmethod
    async def export_users(cls,
                           _fields: tuple[str],
                           _to: typing.Literal["text", "txt", "json"]) -> BufferedInputFile | str:
        UserPydanticList = pydantic_queryset_creator(User, include=_fields)
        users: PydanticListModel = await UserPydanticList.from_queryset(User.all())
        if _to == "text":
            users_list = list(users.dict()["__root__"])
            user_value_list = list(map(lambda x: str(list(x.values())), users_list))
            result = "\n".join(user_value_list)
        elif _to == "txt":
            users_list = list(users.dict()["__root__"])
            user_value_list = list(map(lambda x: str(list(x.values())), users_list))
            user_txt = "\n".join(user_value_list)
            result = BufferedInputFile(bytes(user_txt, "utf-8"), filename="users.txt")
        else:
            # json.dumps(ensure_ascii=False, default=str)
            result = BufferedInputFile(bytes(users.json(ensure_ascii=False), "utf-8"),
                                       filename="users.json")
        return result
