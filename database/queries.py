USERS_INFO_TABLE_PATH = "user_personal_info"
STATES_TABLE_PATH = "states"

get_user_state = f"""
    DECLARE $user_id AS Uint64;

    SELECT state
    FROM `{STATES_TABLE_PATH}`
    WHERE user_id == $user_id;
"""

set_user_state = f"""
    DECLARE $user_id AS Uint64;
    DECLARE $state AS Utf8?;

    UPSERT INTO `{STATES_TABLE_PATH}` (`user_id`, `state`)
    VALUES ($user_id, $state);
"""

set_user_email = f"""
    DECLARE $user_id AS Uint64;
    DECLARE $email AS Utf8?;
    
    UPSERT INTO `{USERS_INFO_TABLE_PATH}` (`user_id`, `email`)
    VALUES ($user_id, $email);
"""

set_user_subscribe = f"""
    DECLARE $user_id AS Uint64;
    DECLARE $subscribe AS Bool;

    UPSERT INTO `{USERS_INFO_TABLE_PATH}` (`user_id`, `subscribe`)
    VALUES ($user_id, $subscribe);
"""

get_user_info = f"""
    DECLARE $user_id AS Int64;
    
    SELECT
        user_id,
        username,
        first_name,
        last_name,
        email
    FROM `{USERS_INFO_TABLE_PATH}`
    WHERE user_id == $user_id;
"""

get_user_info_by_username = f"""
    DECLARE $username AS Utf8;

    SELECT
        *
    FROM `{USERS_INFO_TABLE_PATH}`
    WHERE username == $username;
"""

get_chat_id = f"""
    DECLARE $user_id AS Int64;
    
    SELECT
        chat_id
    FROM `{USERS_INFO_TABLE_PATH}`
    WHERE user_id == $user_id;    
"""

add_primary_user_info = f"""
    DECLARE $user_id AS Uint64;
    DECLARE $chat_id AS Uint64;
    DECLARE $username AS Utf8;
    DECLARE $first_name AS Utf8;
    DECLARE $last_name AS Utf8;
    $now = CurrentUtcDatetime();

    INSERT INTO `{USERS_INFO_TABLE_PATH}` (`user_id`, `chat_id`, `username`, `first_name`, `last_name`, 
    `registration_date`) VALUES ($user_id, $chat_id, $username, $first_name, $last_name, $now);
"""

upsert_user_info = f"""
    DECLARE $user_id AS Uint64;
    DECLARE $description AS Utf8;
    DECLARE $email AS Utf8;
    DECLARE $exp AS Float;
    

    UPSERT INTO `{USERS_INFO_TABLE_PATH}` (`user_id`, `description`, `exp`, `email`)
    VALUES ($user_id, $description, $exp, $email);
"""

delete_user_info = f"""
    DECLARE $user_id AS Uint64;

    DELETE FROM `{USERS_INFO_TABLE_PATH}`
    WHERE user_id == $user_id;

    DELETE FROM `{STATES_TABLE_PATH}`
    WHERE user_id == $user_id;
"""

get_random_user = f"""
    SELECT `{USERS_INFO_TABLE_PATH}`.*, Random(username) as random
    FROM `{USERS_INFO_TABLE_PATH}`
    WHERE email IS NOT NULL
    ORDER BY random
    LIMIT 1
"""
