# Hash2PassBot

-----
**Hash2PassBot** - поиску строки пароля по соответствующему хешу.

## Установка
```bash
git clone https://github.com/taimaskhanov11/Hash2PassBot.git
```
После перемещаемся в корень проекта и запускаем скрипт для установки всех базовых зависимостей
```bash
bash download_dep.sh
```
Установка зависимостей проекта
```bash
poetry install 
```
## Запуск
```bash
bash run_bot.bash 
```
Запускает бота и api сервер для взаимодействия с @MailLeaksBot

Запускать только после запуска @MailLeaksBot

Перед перезапуском удалять предыдущий процесс в фоне с помощью команды
```bash
pkill -f hash2passbot/main.py
```

## Основной функционал

Каждый час в папке `backup` создается данные пользователей, лимитов, полученных через api хешей и оплаченных счетов.
Принудительно бекап можно создать через команду `poetry run python hash2passbot/db/utils/backup.py`

Обновления из `backup` через команду  `poetry run python hash2passbot/db/utils/import.py`






[//]: # (- [X] Придумать внешний вид резюме)

[//]: # (- [ ] Написать основные категории)

[//]: # (- [X] Опубликовать)

-----

## 1. Таблицы в БД

`hash2passbot\db\models`

- user
- subscription
- subscriptiontemplate
- password
- apipassword
- invoicecrypto
- invoiceqiwi
- statistic

### ***user***

```python
from tortoise import fields, models

from hash2passbot.db.models.invoice import InvoiceQiwi, InvoiceCrypto
from hash2passbot.db.models.subscription import Subscription


class User(models.Model):
    """Хранит базовые данные пользователя"""
    user_id = fields.BigIntField(index=True, unique=True)
    username = fields.CharField(32, unique=True, index=True, null=True)
    first_name = fields.CharField(255, null=True)
    last_name = fields.CharField(255, null=True)
    locale = fields.CharField(32, default="ru")
    registered_at = fields.DatetimeField(auto_now_add=True)
    is_search = fields.BooleanField(default=False)
    subscription: Subscription
    invoice_cryptos: fields.ReverseRelation[InvoiceCrypto]
    invoice_qiwis: fields.ReverseRelation[InvoiceQiwi]
```

Хранить все основные данные пользователя, а также обратные отношения для связанных таблиц (о них ниже).

- `locale` - выбранный язык
- `is_search` - хранения состояния поиска для защиты от спама

___

### ***subscriptiontemplate*** and ***subscription***

```python
import typing

from tortoise import models, fields

from hash2passbot.config.config import config

if typing.TYPE_CHECKING:
    pass


class SubscriptionTemplate(models.Model):
    """Шаблоны для создания подписок"""
    title = fields.CharField(255, default="Базовая подписка", index=True)
    price = fields.IntField(default=0)
    limit = fields.IntField(null=True, default=config.bot.default_limit)


class Subscription(SubscriptionTemplate):
    """Подписки с привязкой к пользователю"""
    title = fields.CharField(255, default="Базовая подписка")
    connected_at = fields.DatetimeField(auto_now_add=True)
    user: "User" = fields.OneToOneField("models.User")
```

***subscriptiontemplate*** хранить шаблоны подписок созданные админом и на ее основе создается подписка для
пользователя ***subscription***
Данные подписок создаются через конфиг файл `subscriptions.yaml`. Настраиваются через admin панель

___

### ***passwords***

```python
from tortoise import fields


class Password:
    password = fields.CharField(512, source_field="pass")
    hash_md5 = fields.CharField(40, index=True)
    hash_md25 = fields.CharField(40, index=True)
    hash_sh1 = fields.CharField(40, index=True)
```

Хранить хеши, индексация по трех полям
___

### ***apipassword***

```python
from tortoise import fields, models


class ApiPassword(models.Model):
    """Пароль и хеши полученные через api"""
    password = fields.CharField(512, source_field="pass")
    algorithm = fields.CharField(30, index=True)
    hash = fields.CharField(255, index=True)
```

Сохраняет хеши в локальной базе после получения по api
___

### ***invoicecrypto***

```python
import datetime

from tortoise import fields, models

from hash2passbot.config.config import TZ, config
from hash2passbot.db.models.subscription import SubscriptionTemplate


class InvoiceAbstract(models.Model):
    """Абстрактный класс для создания счета"""
    subscription_template: SubscriptionTemplate = fields.ForeignKeyField("models.SubscriptionTemplate",
                                                                         on_delete=fields.CASCADE)
    user: "User" = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)
    currency = fields.CharField(5, default="RUB", description="RUB")
    amount = fields.DecimalField(17, 7)
    invoice_id = fields.CharField(50, index=True)
    created_at = fields.DatetimeField(default=datetime.datetime.now(TZ))
    expire_at = fields.DatetimeField(default=datetime.datetime.now(TZ) + datetime.timedelta(minutes=30))
    email = fields.CharField(20, null=True)
    pay_url = fields.CharField(255)
    is_paid = fields.BooleanField(default=False)

    class Meta:
        abstract = True


class InvoiceCrypto(InvoiceAbstract):
    """
    for create:
        amount
        shop_id
        order_id
        email
        currency

    result:
        {'status': 'success',
        'pay_url': 'https://cryptocloud.plus/pay/4N8RWT',
        'currency': 'BTC',
        'invoice_id': '4N8RWT',
        'amount': 3e-06,
        'amount_usd': 0.1170788818966779}
    check result:
        {'status': 'success', 'status_invoice': 'created'}
        {'status': 'success', 'status_invoice': 'paid'}
    checked time:
        7-10 m
    """
    user: "User" = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, related_name="invoice_cryptos")
    shop_id = fields.CharField(50, default=config.payment.cryptocloud.shop_id)
    currency = fields.CharField(5, default="RUB", description="USD, RUB, EUR, GBP")
    order_id = fields.CharField(50, null=True, description="Custom product ID")


class InvoiceQiwi(InvoiceAbstract):
    """{'amount': {'currency': 'RUB', 'value': 5.0},
         'created_at': datetime.datetime(2022, 5, 22, 21, 24, 17, 186000, tzinfo=datetime.timezone(datetime.timedelta(seconds=10800))),
         'custom_fields': {'pay_sources_filter': 'qw', 'theme_code': 'Yvan-YKaSh'},
         'customer': None,
         'expire_at': datetime.datetime(2022, 5, 22, 21, 54, 7, tzinfo=datetime.timezone(datetime.timedelta(seconds=10800))),
         'id': '397a2a00-19ae-40f6-9ea1-c4e3bccb315f',
         'pay_url': 'https://oplata.qiwi.com/form/?invoice_uid=f8b7366e-3b5d-44e0-9356-50c56eab18d6',
         'recipientPhoneNumber': '79898600122',
         'site_id': '7l0erf-00',
         'status': {'changed_datetime': datetime.datetime(2022, 5, 22, 21, 24, 17, 186000, tzinfo=datetime.timezone(datetime.timedelta(seconds=10800))),
                    'value': 'WAITING'}}
    """
    user: "User" = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, related_name="invoice_qiwis")
    comment = fields.CharField(255, null=True)
```

При отправке запроса на покупку подписки ***invoice*** таблицы создают запись с идентификатором чека и
с привязкой к соответствующему шаблону подписки.

Также эти таблицы хранят данные времени создания `created_at`,
времени просрочки платежа `expire_at`, url для оплаты `pay_url`, статус оплаты `is_paid`.
Время просрочки платежа 30 минут, после чего пользователю придется заново создавать счет для оплаты.

Для проверки платежей при запуске бота в фоновом режиме запускается задача,
которая каждую минуту получает не просроченные и неоплаченные платежи и отправляет запрос в соответствующий сервис
для получения статуса оплаты, пока не будет получен статус `paid` или пока не будет просрочен платеж.
После успешной оплаты, создается или обновляется подписка на указанное в шаблоне `subscriptiontemplate` количество
удачных лимитов.
Так же если в шаблоне подписки в скобках указан безлимит для партнерского бота @MailLeaksBot то создается или
обновляется безлимитная подписка через api для @MailLeaksBot на указанное количество месяцев.

___

### ***statistic***

```python
from tortoise import models, fields


class Statistic(models.Model):
    total_requests_count = fields.IntField(default=0)
    found_local_count = fields.IntField(default=0)
    found_in_saved_count = fields.IntField(default=0)
    found_via_api_count = fields.IntField(default=0)
    not_found_count = fields.IntField(default=0)
```

Хранить статистику запросов для отображения в админ панели
___