import json
import os


def load_config():
    default_config = {
    "bot_username": "your_bot",
    "min_top_up_amount": 350,
    "chat_id": -1002863123944,
    "countdown_post_check": 300,
    "countdown": 1800,
    "prices": {
        "link_post_price": 500,
        "no_link_post_price": 350
    },
    "messages": {
        "startup_admin": "💎 Autoposting | Автопостинг в чатах 💎\n\nСтатус обновлен: Онлайн 🟢",
        "start": "👋 Привет!\n\nЭтот бот для автопостинга ❤️\n\nАвтопостинг — это автоматическое размещение ваших рекламных сообщений каждый час! ⏰✨\n\nПочему это работает?\nЧем чаще ваше предложение на виду, тем больше интереса. Постоянные напоминания вызывают привыкание и желание узнать больше.\n\n⭐️ Возможности автопостинга:\n- 🌟 Premium эмодзи\n- 📢 Мгновенные публикации в нескольких чатах\n- 🔘 Добавление интерактивных кнопок\n- 🖋️ Любые шрифты\n- ⚙️ Полная автоматизация\n\nНе упустите шанс увеличить свою аудиторию и интерес к продукту! 🚀",
        "information": "➜ Контакты\n ├ По вопросам: @username\n └ Спам Блок : @username\n\n⭐️ Что предлагает наш автопостинг\n ├ 🌟 Поддержка Premium эмодзи\n ├ 📢 Публикации в множестве чатов\n ├ 🔘 Возможность добавления кнопок\n ├ 🖋️ Любые шрифты на выбор\n └ ⚙️ Полная автоматизация процесса\n\n📖 Важная информация: {ваша_ссылка}\n‼️ Правила: {ваша_ссылка}",
        "profile": "Имя: {name}\nВаш ID: {user_id}\n\nВаш баланс: {balance} 💲\nАктивных автопостингов: {active_posts}\n\nДата регистрации: {registration_date}\nВас пригласил: {invited_by}",
        "ref_system": "Приглашайте пользователей в наш сервис и получайте 25% от их платежей на свой баланс!\n\nВаша статистика:\n👥 Всего рефералов: {total_refs}\n💰 Заработано: ${earned}\n\nВаша реферальная ссылка:\n{ref_link}\n\nПросто отправьте эту ссылку друзьям и знакомым.",
        "no_referrals": "Список ваших рефералов\n\nУ вас пока нет рефералов. Пригласите друзей с помощью своей реферальной ссылки!",
        "referrals_list": "Список ваших рефералов\n\n{referrals_list}",
        "new_referral_inviter": "Ого! Рады сообщить, что ваш друг {username} только что присоединился к нам по вашей реферальной ссылке! 👏",
        "new_referral": "🎉 Приветствуем нового участника!\n\n🌟 Вы были приглашены в наш сервис благодаря реферальной ссылке от {username}!",
        "error_referral": "Вы уже есть в реферальной системе!",
        "top_up_amount": "Введите сумму пополнения в рублях (RUB), на которую хотите пополнить баланс.",
        "invoice": "Пополнение баланса\n\nID пополнения: {invoice_id}\nСумма пополнения: {invoice_amount} RUB\nВремя на оплату: 20 минут\n\nОплатите чек по ссылке: {invoice_link}",
        "invoice_successful": "Пополнение баланса\n\nОплата была произведена, ваш баланс пополнен на {invoice_amount} RUB!",
        "invoice_ref_system": "Реферальная система\n\nВаш рефферал {referral_id} пополнил баланс на {invoice_amount} RUB",
        "invoice_too_small": "Сумма слишком маленькая\n\nМинимальная сумма пополнения {min_top_up_amount} RUB:",
        "invoice_enter_no_digits": "Вводите только цифры:",
        "my_posts": "Список ваших постов:",
        "my_posts_no": "🔍 У вас пока нет активных автопостингов\n\nЧтобы создать автопостинг, нажмите на кнопку «Купить автопостинг».",
        "post_details": "ID поста: {post_id}\n\nТекст:\n<code>{post_text}</code>\n\nЧат ID: {chat_id}\nПериодичность: {add_time} минут\nТип: {type_post}\nДата истечения: {expiry_date}",
        "edit_enter_text": "Введите новый текст:",
        "edit_text_successful": "Текст успешно изменен!",
        "edit_text_error_link": "Вы пытаетесь добавить ссылку в пост, но оплатили за пост без ссылки.",
        "remove_successful": "Пост успешно удален!",
        "remove_error": "Не удалось удалить пост!",
        "autoposting_choose": "❗ Выберите вариант автопостинга, который вам нужен",
        "autoposting_link": "❗ Отлично, использовав этот режим ВЫ можете добавить ссылки на канал или бот ❗\nЦена 500 рублей в месяц",
        "autoposting_no_link": "❗ Отлично, использовав этот режим вы НЕ сможете добавить ссылки на канал или бот\nЦена 350 рублей в месяц",
        "buy_autoposting_successful": "Оплата успешно произведена!",
        "buy_autoposting_error": "На вашем балансе недостаточно средств. Пополните его в меню профиля!",
        "autoposting_add_post_text": "Введите текст вашего поста:",
        "autoposting_post_added": "Ваш пост успешно добавлен!",
        "expire_date_post": "❌ Ваш пост (ID {post_id}) был деактивирован по истечении срока подписки (1 месяц).",
        "renew_post_successful": "Пост теперь активен!",
        "admin_panel":  "АДМИН-ПАНЕЛЬ\n\nКОМАНДЫ\n/admin_add_balance [user_id] [amount] - начисление денег на баланс (отрицательные значения для снятия с баланса)\n/admin_set_interval [time] - установка времени кулдауна между публикациями постов\n/admin_add [user_id] - добавить админа (будет доступна эта панель)\n/admin_remove [user_id] - удаление админа\n/admin_history - получение всей истории публикаций\n/admin_unban [user_id] - снятие бана пользователю\n/admin_ban [user_id] - выдача бана пользователю (не сможет пользоваться ботом)\n/spam - запустить рассылку (текст вводится следующим сообщением)\n\nСТАТИСТИКА - ЗА ВСЕ ВРЕМЯ:\nЛюдей в боте: {all_users_count}\nОпубликовано постов: {all_published_posts}\nЗаработано: {all_earned_amount}\n\nСТАТИСТИКА - ЗА МЕСЯЦ:\nОпубликовано постов: {month_published_posts}\nЗаработано: {month_earned_amount}\n\nСТАТИСТИКА - ЗА ДЕНЬ:\nОпубликовано постов: {day_published_posts}\nЗаработано: {day_earned_amount}"
    },
    "buttons": {
        "start": {
            "1": {
                "text": "🛍️ Купить Автопостинг",
                "callback": "autoposting"
            },
            "2": {
                "text": "📊 Мои посты",
                "callback": "my_posts"
            },
            "3": {
                "text": "ℹ️ Информация",
                "callback": "information"
            },
            "4": {
                "text": "👤 Профиль",
                "callback": "profile"
            }
        },
        "back_start_menu": {
            "text": "◀️ Назад",
            "callback": "back_start_menu"
        },
        "profile": {
            "1": {
                "text": "💳 Пополнить баланс",
                "callback": "top_up"
            },
            "2": {
                "text": "🤝 Реферальная система",
                "callback": "ref_system"
            }
        },
        "my_referrals": {
            "text": "👥 Мои рефералы",
            "callback": "my_referrals"
        },
        "cancel_top_up": {
            "text": "❌ Закрыть",
            "callback": "cancel_top_up"
        },
        "edit_post_opportunity": {
            "1": {
                "text": "Изменить текст",
                "callback": "change-text_{post_id}"
            },
            "2": {
                "text": "⬅️Назад",
                "callback": "back_to_posts_list"
            },
            "3": {
                "text": "Удалить пост",
                "callback": "remove_{post_id}"
            },
            "4": {
                "text": "Возобновить пост",
                "callback": "renew-post_{post_id}"
            }
        },
        "autoposting_types": {
            "1": {
                "text": "📎 С ссылкой",
                "callback": "autoposting_link"
            },
            "2": {
                "text": "🔗 Без ссылки",
                "callback": "autoposting_no_link"
            }
        },
        "autoposting_buy_or_no": {
            "1": {
                "text": "✅ Купить",
                "callback": "post-buy_{post_type}"
            },
            "2": {
                "text": "❌ Отмена",
                "callback": "autoposting"
            }
        }
    }
}

    if not os.path.exists('config.json'):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


config = load_config()
MESSAGES = config['messages']
BUTTONS = config['buttons']
BOT_USERNAME = config['bot_username']
MIN_TOP_UP_AMOUNT = config['min_top_up_amount']
PRICES = config['prices']
CHAT_ID = config['chat_id']
COUNTDOWN_POST_CHECK = config['countdown_post_check']
