import asyncio
import json

from loguru import logger
from dateutil import parser

from hash2passbot.config.config import BASE_DIR
from hash2passbot.db import init_db
from hash2passbot.db.models import User, Subscription, InvoiceQiwi, InvoiceCrypto, SubscriptionTemplate
from hash2passbot.db import models
backup_name = f"db_backup"
BACKUP_DIR = BASE_DIR / "backup"
BACKUP_DIR.mkdir(exist_ok=True)


async def making_import():
    logger.debug("Резервное копирование запущено")
    with open(BACKUP_DIR / f"{backup_name}.json", "r", encoding="utf-8") as f:
        # json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False, default=str)
        data = json.load(f)

    if "User" in data:
        for user_data in data["User"]:
            try:
                user_copy = user_data.copy()
                del user_copy['id']
                user_copy["registered_at"]= parser.parse(user_copy["registered_at"])

                user = await User.create(**user_copy)
                logger.success(f"{user}")
                try:
                    if "Subscription" in data:
                        for sub_data in data["Subscription"]:
                            if sub_data["user_id"] == user_data["id"]:
                                sub_copy = sub_data.copy()
                                del sub_copy['id']
                                del sub_copy['user_id']
                                sub_copy['connected_at'] = parser.parse(sub_copy["connected_at"])

                                await user.subscription.delete()
                                subscription = await Subscription.create(user=user, **sub_copy)

                                logger.success(f"{subscription}")

                    for invoice in ["InvoiceQiwi", "InvoiceCrypto"]:
                        if invoice in data:
                            for qiwi_data in data[invoice]:
                                if qiwi_data["user_id"] == user_data["id"]:
                                    qiwi_copy = qiwi_data.copy()
                                    del qiwi_copy['id']
                                    del qiwi_copy['user_id']
                                    qiwi_copy['created_at'] = parser.parse(qiwi_copy["created_at"])
                                    qiwi_copy['expire_at'] = parser.parse(qiwi_copy["expire_at"])
                                    sub_tem = await SubscriptionTemplate.filter().first()
                                    if not sub_tem:
                                        sub_tem =  await SubscriptionTemplate.create()
                                    Invoice = getattr(models, invoice)
                                    created_invoice = await Invoice.create(**qiwi_copy, user=user)
                                    logger.success(f"{created_invoice}")

                except Exception as e:
                    logger.warning(e)


            except Exception as e:
                logger.warning(e)
    # for model_str in models.__all__:
    for model in [User, Subscription, InvoiceQiwi, InvoiceCrypto]:
        pass

    logger.info(f"Резервное копирование завершено {backup_name}")


async def main():
    await init_db()
    await making_import()


if __name__ == '__main__':
    asyncio.run(main())
