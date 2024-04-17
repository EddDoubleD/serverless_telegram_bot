from email_validate import validate

from bot import keyboards, states
from database import model as db_model
from logs import logged_execution
from user_interaction import texts


@logged_execution
def handle_start(message, bot, pool):
    user = db_model.get_user_info(pool, message.from_user.id)
    # user
    if user:
        bot.send_message(message.chat.id, texts.HELLO, reply_markup=keyboards.EMPTY)
    else:
        save_primary(pool, message)
        bot.set_state(
            message.from_user.id,
            states.RegisterState.guest,
            message.chat.id
        )

        bot.send_message(message.chat.id, texts.HELLO, reply_markup=keyboards.EMPTY)


@logged_execution
def handle_start_register(message, bot, pool):
    state = db_model.get_state(pool, message.from_user.id)
    if state == states.RegisterState.guest:
        bot.send_message(message.chat.id, 'Вы уже зерегистрированы', reply_markup=keyboards.EMPTY)
        return
    elif state is None:
        save_primary(pool, message)

    bot.send_message(
        message.chat.id,
        texts.EMAIL_MSG,
        reply_markup=keyboards.get_reply_keyboard(["/cancel"]),
        # reply_markup=keyboards.EMPTY,
    )

    bot.set_state(
        message.from_user.id, states.RegisterState.email, message.chat.id
    )


def save_primary(pool, message):
    db_model.add_primary_user_info(
        pool,
        message.from_user.id,
        message.chat.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )


@logged_execution
def handle_email(message, bot, pool):
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
        data["email"] = message.text

    bot.send_message(
        message.chat.id,
        texts.SUBSCRIBE_MSG,
        reply_markup=keyboards.get_reply_keyboard(texts.YES_NO_OPTIONS),
    )
    bot.set_state(
        message.from_user.id, states.RegisterState.subscribe, message.chat.id
    )


@logged_execution
def handle_finish_register(message, bot, pool):
    if message.text not in texts.YES_NO_OPTIONS:
        bot.send_message(
            message.chat.id,
            texts.DELETE_ACCOUNT_UNKNOWN,
            reply_markup=keyboards.EMPTY,
        )
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        email = data["email"]

    db_model.upsert_user_email(
        pool,
        user_id=message.from_user.id,
        email=email
    )

    subscribe = texts.YES_NO_OPTIONS[message.text]

    # save subscriber status
    db_model.upsert_user_subscribe(
        pool=pool,
        user_id=message.from_user.id,
        subscribe=subscribe
    )

    bot.send_message(
        message.chat.id,
        texts.FINISH_REGISTRATION,
        reply_markup=keyboards.EMPTY,
    )

    bot.set_state(
        message.from_user.id, states.RegisterState.registered, message.chat.id
    )


@logged_execution
def handle_cancel_registration(message, bot, pool):
    bot.set_state(message.from_user.id, states.RegisterState.guest, message.chat.id)
    bot.send_message(
        message.chat.id,
        texts.CANCEL_REGISTER,
        reply_markup=keyboards.EMPTY,
    )


@logged_execution
def handle_show_data(message, bot, pool):
    current_data = db_model.get_user_info(pool, message.from_user.id)

    if not current_data:
        bot.send_message(
            message.chat.id, texts.NOT_REGISTERED, reply_markup=keyboards.EMPTY
        )
        return

    bot.send_message(
        message.chat.id,
        texts.SHOW_DATA_WITH_PREFIX.format(
            current_data["first_name"], current_data["last_name"]
        ),
        reply_markup=keyboards.EMPTY,
    )


@logged_execution
def handle_delete_account(message, bot, pool):
    current_data = db_model.get_user_info(pool, message.from_user.id)
    if not current_data:
        bot.send_message(
            message.chat.id, texts.NOT_REGISTERED, reply_markup=keyboards.EMPTY
        )
        return

    bot.send_message(
        message.chat.id,
        texts.DELETE_ACCOUNT,
        reply_markup=keyboards.get_reply_keyboard(texts.YES_NO_OPTIONS),
    )
    bot.set_state(
        message.from_user.id, states.DeleteAccountState.are_you_sure, message.chat.id
    )


@logged_execution
def handle_finish_delete_account(message, bot, pool):
    bot.delete_state(message.from_user.id, message.chat.id)

    if message.text not in texts.YES_NO_OPTIONS:
        bot.send_message(
            message.chat.id,
            texts.DELETE_ACCOUNT_UNKNOWN,
            reply_markup=keyboards.EMPTY,
        )
        return

    if texts.YES_NO_OPTIONS[message.text]:
        db_model.delete_user_info(pool, message.from_user.id)
        bot.send_message(
            message.chat.id,
            texts.DELETE_ACCOUNT_DONE,
            reply_markup=keyboards.EMPTY,
        )
    else:
        bot.send_message(
            message.chat.id,
            texts.DELETE_ACCOUNT_CANCEL,
            reply_markup=keyboards.EMPTY,
        )


@logged_execution
def handle_about_info(message, bot, pool):
    bot.send_message(
        message.chat.id,
        texts.ABOUT_INFO,
        reply_markup=keyboards.EMPTY,
    )


@logged_execution
def handle_stand_info(message, bot, pool):
    bot.send_message(
        message.chat.id,
        texts.STAND_INFO,
        reply_markup=keyboards.EMPTY,
    )


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