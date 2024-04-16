import json

from database import queries
from database.utils import execute_select_query, execute_update_query


def get_state(pool, user_id):
    results = execute_select_query(pool, queries.get_user_state, user_id=user_id)
    if len(results) == 0:
        return None
    if results[0]["state"] is None:
        return None
    return json.loads(results[0]["state"])


def set_state(pool, user_id, state):
    execute_update_query(
        pool, queries.set_user_state, user_id=user_id, state=json.dumps(state)
    )


def clear_state(pool, user_id):
    execute_update_query(pool, queries.set_user_state, user_id=user_id, state=None)


def add_primary_user_info(pool, user_id, chat_id, username, first_name, last_name):
    """
    Adds record to database about the user from the telegram stuf
    @param pool: ydb pool
    @param user_id: user id
    @param chat_id: current chat id
    @param username: login from telegram
    @param first_name: name
    @param last_name: surname
    """
    #
    if first_name is None:
        first_name = ""
    if last_name is None:
        first_name = ""
    execute_update_query(
        pool,
        queries.add_primary_user_info,
        user_id=user_id,
        chat_id=chat_id,
        username=username,
        first_name=first_name,
        last_name=last_name
    )


def upsert_user_email(pool, user_id, email):
    """
    Set user email to record by user_id
    @param pool: ydb pool
    @param user_id: user id
    @param email: valid email
    """
    execute_update_query(
        pool,
        queries.set_user_email,
        user_id=user_id,
        email=email
    )


def upsert_user_subscribe(pool, user_id, subscribe):
    execute_update_query(
        pool,
        queries.set_user_subscribe,
        user_id=user_id,
        subscribe=subscribe
    )


def get_user_info(pool, user_id):
    result = execute_select_query(pool, queries.get_user_info, user_id=user_id)

    if len(result) != 1:
        return None
    return result[0]


def delete_user_info(pool, user_id):
    execute_update_query(pool, queries.delete_user_info, user_id=user_id)


def get_random_user(pool):
     result = execute_select_query(pool, queries.get_random_user)

     if len(result) != 1:
         return None
     return result[0]

def get_user_info_by_username(pool, username):
    result = execute_select_query(pool, queries.get_user_info_by_username, username=username)

    if len(result) != 1:
        return None
    return result[0]