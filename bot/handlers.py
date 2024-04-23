import re

from email_validate import validate
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import keyboards, states
from database import model as db_model
from logs import logged_execution
from user_interaction import texts


@logged_execution
def handle_start(message, bot, pool):
    user = db_model.get_user_info(pool, message.from_user.id)
    if not user:
        save_primary(pool, message)
        bot.send_message(
            message.chat.id,
            texts.HELLO,
            reply_markup=keyboards.get_reply_keyboard(["Интересно!"]),
            parse_mode="Markdown"
        )

        bot.set_state(
            message.from_user.id, states.RegisterState.request_interest, message.chat.id
        )
        return

    # routing
    state = db_model.get_state(pool, message.from_user.id)
    if state is None:
        bot.set_state(
            message.from_user.id, states.RegisterState.request_interest, message.chat.id
        )
        return

    if state['state'] == 'RegisterState:request_interest':
        bot.send_message(
            message.chat.id,
            texts.HELLO,
            reply_markup=keyboards.get_reply_keyboard(["Интересно!"]),
            parse_mode="Markdown"
        )
    elif state['state'] == 'RegisterState:request_name':
        bot.send_message(
            message.chat.id,
            texts.INTRODUCE_YOURSELF,
            reply_markup=keyboards.EMPTY
        )
    elif state['state'] == 'RegisterState:request_exp':
        bot.send_message(
            message.chat.id,
            texts.INTRODUCE_YOUR_EXP,
            reply_markup=keyboards.EMPTY
        )
    elif state['state'] == 'RegisterState:request_sub':
        bot.send_message(
            message.chat.id,
            texts.INTRODUCE_SUBSCRIBE,
            reply_markup=keyboards.get_reply_keyboard(texts.YES_NO_OPTIONS),
            parse_mode="Markdown"
        )
    elif state['state'] == 'RegisterState:request_email':
        bot.send_message(
            message.chat.id,
            texts.INTRODUCE_MAIL,
            reply_markup=keyboards.EMPTY
        )
    elif state['state'] == 'GlobalState:guest':
        bot.send_message(
            message.chat.id,
            texts.FINISH_REGISTRATION,
            reply_markup=keyboards.get_reply_keyboard(["Участвую", "Команда", "Стенд"])
        )
    elif state['state'] == 'GlobalState:participate':
        bot.send_message(
            message.chat.id,
            texts.ALREADY_PARTICIPATE,
            reply_markup=keyboards.get_reply_keyboard(
                ["Команда", "Стенд"]
            )
        )


@logged_execution
def handle_register_interest(message, bot, pool):
    if message.text == "Интересно!":
        bot.send_message(
            message.chat.id,
            texts.INTRODUCE_YOURSELF,
            reply_markup=keyboards.EMPTY
        )

        bot.set_state(
            message.from_user.id, states.RegisterState.request_name, message.chat.id
        )


@logged_execution
def handle_register_exp(message, bot, pool):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["DESCRIPTION"] = message.text

    bot.send_message(
        message.chat.id,
        texts.INTRODUCE_YOUR_EXP,
        reply_markup=keyboards.EMPTY
    )

    bot.set_state(
        message.from_user.id, states.RegisterState.request_exp, message.chat.id
    )


@logged_execution
def handle_register_subscribe(message, bot, pool):
    exp = message.text
    if not is_number(exp):
        bot.send_message(
            message.chat.id,
            texts.INVALID_EXP,
            reply_markup=keyboards.EMPTY,
        )
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["EXP"] = float(message.text)

    bot.send_message(
        message.chat.id,
        texts.INTRODUCE_SUBSCRIBE,
        reply_markup=keyboards.get_reply_keyboard(texts.YES_NO_OPTIONS),
        parse_mode="Markdown"
    )

    bot.set_state(
        message.from_user.id, states.RegisterState.request_sub, message.chat.id
    )


@logged_execution
def handle_register_email(message, bot, pool):
    if message.text not in texts.YES_NO_OPTIONS or not texts.YES_NO_OPTIONS[message.text]:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            exp = data["EXP"]
            description = data["DESCRIPTION"]

        db_model.upsert_user_info(
            pool,
            user_id=message.from_user.id,
            description=description,
            email="",
            exp=exp
        )

        bot.send_message(
            message.chat.id,
            texts.FINISH_REGISTRATION,
            reply_markup=keyboards.get_reply_keyboard(["Участвую", "Команда", "Стенд"])
        )

        bot.set_state(
            message.from_user.id, states.GlobalState.guest, message.chat.id
        )
        return

    bot.send_message(
        message.chat.id,
        texts.INTRODUCE_MAIL,
        reply_markup=keyboards.EMPTY
    )

    bot.set_state(
        message.from_user.id, states.RegisterState.request_email, message.chat.id
    )


@logged_execution
def handle_register_validate(message, bot, pool):
    valid = validate(
        email_address=message.text,
        check_format=True,
        check_blacklist=True,
        check_dns=True,
        dns_timeout=10,
        check_smtp=False,
        smtp_debug=False
    )
    if not valid:
        bot.send_message(
            message.chat.id,
            texts.INVALID_EMAIL,
            reply_markup=keyboards.EMPTY,
        )
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        exp = data["EXP"]
        description = data["DESCRIPTION"]

    db_model.upsert_user_info(
        pool,
        user_id=message.from_user.id,
        description=description,
        email=message.text,
        exp=exp
    )
    bot.send_message(
        message.chat.id,
        texts.FINISH_REGISTRATION,
        reply_markup=keyboards.get_reply_keyboard(["Участвую", "Команда", "Стенд"])
    )

    bot.set_state(
        message.from_user.id, states.GlobalState.guest, message.chat.id
    )


@logged_execution
def handle_base_flow(message, bot, pool):
    if message.text in texts.BASE_OPTIONS:
        command = texts.BASE_OPTIONS[message.text]
        if command == 'prize':
            bot.send_message(
                message.chat.id,
                texts.PARTICIPATE,
                reply_markup=keyboards.get_reply_keyboard(
                    ["Команда", "Стенд"]
                )
            )
            bot.set_state(
                message.from_user.id,
                states.GlobalState.participate,
                message.chat.id
            )
        elif command == 'team':
            markup = InlineKeyboardMarkup()
            btn_my_site = InlineKeyboardButton(text=texts.ABOUT_INFO_2_BTN, url=texts.ABOUT_INFO_LINK)
            markup.add(btn_my_site)
            bot.send_photo(
                message.chat.id,
                photo="https://storage.yandexcloud.net/ya360/team.png",
                caption=texts.ABOUT_INFO,
                reply_markup=markup
            )

            bot.send_message(
                message.chat.id,
                texts.WELCOME,
                reply_markup=keyboards.get_reply_keyboard(["Участвую", "Команда", "Стенд"])
            )
        elif command == 'info':
            bot.send_message(
                message.chat.id,
                texts.STAND_INFO,
                reply_markup=keyboards.get_reply_keyboard(["Участвую", "Команда", "Стенд"])
            )
        else:
            bot.send_message(
                message.chat.id,
                "Я тебя не понимаю :(",
                reply_markup=keyboards.get_reply_keyboard(["Участвую", "Команда", "Стенд"])
            )


@logged_execution
def handle_participate_user(message, bot, pool):
    if message.text in texts.BASE_OPTIONS:
        command = texts.BASE_OPTIONS[message.text]
        if command == 'team':
            markup = InlineKeyboardMarkup()
            btn_my_site = InlineKeyboardButton(text=texts.ABOUT_INFO_2_BTN, url=texts.ABOUT_INFO_LINK)
            markup.add(btn_my_site)
            bot.send_photo(
                message.chat.id,
                photo="https://storage.yandexcloud.net/ya360/team.png",
                caption=texts.ABOUT_INFO,
                reply_markup=markup
            )

            bot.send_message(
                message.chat.id,
                texts.WELCOME,
                reply_markup=keyboards.get_reply_keyboard(["Команда", "Стенд"])
            )
        elif command == 'info':
            bot.send_message(
                message.chat.id,
                texts.STAND_INFO,
                reply_markup=keyboards.get_reply_keyboard(["Команда", "Стенд"])
            )


def save_primary(pool, message):
    first_name = message.from_user.first_name
    if first_name is None:
        first_name = ""
    last_name = message.from_user.last_name
    if last_name is None:
        last_name = ""

    db_model.add_primary_user_info(
        pool,
        message.from_user.id,
        message.chat.id,
        message.from_user.username,
        first_name,
        last_name
    )


def is_number(s):
    if re.match('^\d+?\.\d+?$', s) is None:
        return s.isdigit()
    return True


# ============================================= ADMIN ================================================

@logged_execution
def handle_admin_help(message, bot, pool):
    if message.from_user.username not in texts.ADMINS:
        return

    bot.send_message(
        message.chat.id,
        f'''/admin_roulette - розыгрыш
                /admin_gift <login> - отправка приза
                /admin_send_message <login> <message> - отправить сообщение от имени бота
            ''',
        reply_markup=keyboards.EMPTY,
    )


@logged_execution
def handle_admin_roulette(message, bot, pool):
    if message.from_user.username not in texts.ADMINS:
        return

    current_data = db_model.get_random_user(pool)

    bot.send_message(
        message.chat.id,
        f'Победил @{current_data["username"]} чтобы отправить победителю подарок напиши сообщение /admin_gift <login>',
        reply_markup=keyboards.EMPTY,
    )


@logged_execution
def handle_admin_gift(message, bot, pool):
    if message.from_user.username not in texts.ADMINS:
        return

    login = message.text[len('/admin_gift '):]
    current_data = db_model.get_user_info_by_username(pool, login)

    if current_data is None:
        bot.send_message(
            message.chat.id,
            f'Пользователь "{login}" не найден',
            reply_markup=keyboards.EMPTY,
        )
    else:
        bot.send_message(
            current_data["chat_id"],
            f'Поздравляю ты выграл приз. Подходи на стенд Яндекс 360 чтобы забрать его',
            reply_markup=keyboards.EMPTY,
        )


@logged_execution
def handle_admin_send_message(message, bot, pool):
    if message.from_user.username not in texts.ADMINS:
        return

    login, text = message.text[len('/admin_send_message '):].split(" ", 1)
    current_data = db_model.get_user_info_by_username(pool, login)

    if current_data is None:
        bot.send_message(
            message.chat.id,
            f'Пользователь "{login}" не найден',
            reply_markup=keyboards.EMPTY,
        )
    else:
        bot.send_message(
            current_data["chat_id"],
            text,
            reply_markup=keyboards.EMPTY,
        )
