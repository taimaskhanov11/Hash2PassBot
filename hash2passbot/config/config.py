import argparse
import datetime
import os
from pathlib import Path
from typing import Optional

import yaml
from glQiwiApi import QiwiP2PClient
from loguru import logger
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
MEDIA_DIR = BASE_DIR / 'media'

LOG_DIR.mkdir(exist_ok=True)
MEDIA_DIR.mkdir(exist_ok=True)


def load_yaml(file) -> dict | list:
    with open(Path(BASE_DIR, file), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_config():
    parser = argparse.ArgumentParser(description="config_file")
    parser.add_argument("-f", type=str)
    args = parser.parse_args()
    if args.f:
        logger.success(f"Выгрузка конфига из файла {args.f}")
    return args.f


class Bot(BaseModel):
    token: str
    admins: Optional[list[int]]
    default_limit: int = 0


class Database(BaseModel):
    username: str
    password: str
    host: str
    port: int
    db_name: str

    @property
    def postgres_url(self):
        return f"postgres://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class CryptoCloud(BaseModel):
    shop_id: str
    api_key: str
    create_url: str
    status_url: str


class Qiwi(BaseModel):
    token: str


class Payment(BaseModel):
    cryptocloud: CryptoCloud | None
    qiwi: Qiwi | None


class HashApi(BaseModel):
    url: str
    email: str
    code: str

    @property
    def params(self) -> dict:
        return {"email": self.email,
                "code": self.code}


class Config(BaseModel):
    bot: Bot
    db: Database
    payment: Payment | None
    hash_api: HashApi
    main_api_token: str


I18N_DOMAIN = "hash2passbot"
LOCALES_DIR = BASE_DIR / "hash2passbot/apps/bot/locales"
TZ = datetime.timezone(datetime.timedelta(hours=3))
# config_file = parse_config()
config_file = "config_dev.yml" if os.getenv("DEBUG") else "config.yml"
# config_file = "config_dev.yml"
config = Config(**load_yaml(config_file))
QIWI_CLIENT = QiwiP2PClient(secret_p2p=config.payment.qiwi.token)
