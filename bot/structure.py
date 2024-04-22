from functools import partial

from telebot import TeleBot, custom_filters

from bot import handlers as handlers
from bot import states as bot_states


class Handler:
    def __init__(self, callback, **kwargs):
        self.callback = callback
        self.kwargs = kwargs


def get_start_handlers():
    return [
        Handler(
            callback=handlers.handle_start, commands=["start"]
        ),  # -> description
        Handler(
            callback=handlers.handle_register_exp,
            state=[bot_states.RegisterState.request_name]
        ),  # -> subscribe
        Handler(
            callback=handlers.handle_register_subscribe,
            state=[bot_states.RegisterState.request_exp]
        ),  # -> mail or register
        Handler(
            callback=handlers.handle_register_email,
            state=[bot_states.RegisterState.request_sub]
        ),
        Handler(
            callback=handlers.handle_register_validate,
            state=[bot_states.RegisterState.request_email]
        )  # -> register
    ]


def get_prize_handlers():
    return [
        Handler(
            callback=handlers.handle_prize,
            commands=["prize"],
            state=[bot_states.GlobalState.guest]
        )
    ]


def get_registration_handlers():
    return [
        Handler(callback=handlers.handle_start_register, commands=["register"]),
        Handler(
            callback=handlers.handle_cancel_registration,
            commands=["cancel"],
            state=[
                bot_states.RegisterState.email,
                bot_states.RegisterState.subscribe
            ],
        ),
        Handler(callback=handlers.handle_email, state=bot_states.RegisterState.email),
        Handler(callback=handlers.handle_finish_register, state=bot_states.RegisterState.subscribe)
    ]


def get_show_data_handlers():
    return [
        Handler(callback=handlers.handle_show_data, commands=["show"]),
    ]


def get_delete_account_handlers():
    return [
        Handler(callback=handlers.handle_delete_account, commands=["delete"]),
        Handler(
            callback=handlers.handle_finish_delete_account,
            state=bot_states.DeleteAccountState.are_you_sure,
        ),
    ]


def get_info_handlers():
    return [
        Handler(callback=handlers.handle_about_info, commands=["about"]),
        Handler(callback=handlers.handle_stand_info, commands=["stand"])
    ]


def get_admin_handlers():
    return [
        Handler(callback=handlers.handle_admin_help, commands=["admin_help"]),
        Handler(callback=handlers.handle_admin_roulette, commands=["admin_roulette"]),
        Handler(callback=handlers.handle_admin_gift, commands=["admin_gift"]),
        Handler(callback=handlers.handle_admin_send_message, commands=["admin_send_message"]),
    ]


def create_bot(bot_token, pool):
    state_storage = bot_states.StateYDBStorage(pool)
    bot = TeleBot(bot_token, state_storage=state_storage)

    handlers = []
    handlers.extend(get_start_handlers())
    # handlers.extend(get_registration_handlers())
    # handlers.extend(get_show_data_handlers())
    handlers.extend(get_prize_handlers())
    handlers.extend(get_delete_account_handlers())
    handlers.extend(get_info_handlers())
    handlers.extend(get_admin_handlers())

    for handler in handlers:
        bot.register_message_handler(
            partial(handler.callback, pool=pool), **handler.kwargs, pass_bot=True
        )

    bot.add_custom_filter(custom_filters.StateFilter(bot))
    return bot
