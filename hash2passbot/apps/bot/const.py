from hash2passbot.loader import _


class Menu:

    def start(self, locale=None):
        return _("Сервис по поиску строки пароля по соответствующему хешу.", locale=locale)

    def profile(self, locale=None):
        return _("🔑 ID: {}\n"
                 "👤 Логин: @{}\n"
                 "📄 Оставшиеся успешные запросы - {}", locale=locale)

    def description(self, locale=None):
        return _(
            "Отправьте боту имя почтового ящика и получите список паролей от различных аккаунтов, "
            "которые регистрировались с использованием целевого почтового ящика. "
            "Что есть у нас в базе можно посмотреть тут: "
            "https://telegra.ph/Spisok-utechek-zagruzhennyh-v-bazu-dannyh-telegram-bota-MailLeaksBot-01-24",
            locale=locale)

    def support(self, locale=None):
        return _("По всем вопросам писать @chief_MailLeaks!", locale=locale)

    def check_subscribe_find(self, locale=None):
        return _("✅ Подписки найдены, введите /start чтобы продолжить", locale=locale)

    def check_subscribe_not_find(self, locale=None):
        return _("❌ Ты подписался не на все каналы", locale=locale)

    def get_subscriptions_templates(self, locale=None):
        return _(
            "Приобретение запросов.\nПри приобретении от 250 запросов – подписка на безлимитный доступ к @MailLeaksBot.",
            locale=locale)

    def subscription_purchase_method_unpaid_checks(self, locale=None):
        return _("Слишком много неоплаченных чеков, повторите попытку позже", locale=locale)

    def subscription_purchase_method_created_check(self, locale=None):
        return _("✅ Чек на оплату подписки {} Создан!", locale=locale)

    def purchase_check(self, locale=None):
        return _("❗️ Проверка оплаты происходит автоматически в течении 1 минуты для оплаты через QIWI "
                 "и в течении 10 минут через криптовалюту.\n"
                 "После успешной операции вам придет уведомление об успешной оплате.", locale=locale)

    def get_password_hash_wait(self, locale=None):
        return _("Ожидайте завершения предыдущего поиска", locale=locale)

    def get_password_hash_incorrect(self, locale=None):
        return _("Некорректный hash")

    def _password_found_sub_pass(self, locale=None):
        return _("Хеш:\n{}\nсоответствует строке пароля:\n{}", locale=locale)

    def _password_found_sub_requests(self, locale=None):
        return _("{}\n\nКоличество оставшихся запросов: {}", locale=locale)

    def _password_found_unsub_pass(self, locale=None):
        return _("Хеш:\n{}\nсоответствует строке пароля:\n{}", locale=locale)

    def _password_found_unsub_requests(self, locale=None):
        return _("{}\nЧтобы увидеть пароль приобретите запросы через меню.", locale=locale)

    def search_not_found(self, locale=None):
        return _("Не удалось найти пароль по хешу {}", locale=locale)

    def search_unsub_not_found(self, locale=None):
        return _("Пароль для хеша {} не найден в ограниченной базе. "
                 "Для поиска в расширенной базе приобретите запросы через меню бота.", locale=locale)

    def method_list(self):
        return list(filter(
            lambda x: not x.startswith('_') and x not in ["Config", "copy", "dict", "from_orm", "json", "schema",
                                                          "schema_json", "validate", "construct", "method_list",
                                                          "update_forward_refs"], dir(self)))


menu = Menu()

if __name__ == '__main__':
    # print(menu.dict())
    # print(dir(menu))
    # Menu.from_orm()
    method_list = list(filter(
        lambda x: not x.startswith('_') and x not in ["Config", "copy", "dict", "from_orm", "json", "schema",
                                                      "schema_json", "validate", "construct"], dir(menu)))
    print(method_list)
    # method_list = inspect.getmembers(menu, predicate=inspect.ismethod)
    print(getattr(menu, "search_unsub_not_found").__name__)
    # print(setattr(menu, "search_unsub_not_found", lambda x: 1))
    # print(menu)
    # print(menu.search_unsub_not_found)
