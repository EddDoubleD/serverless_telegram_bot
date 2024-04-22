 CREATE TABLE `user_personal_info`
  (
    `user_id` Uint64,
    `chat_id` Uint64,
    `username` Utf8,
    `last_name` Utf8,
    `first_name` Utf8,
    `description` Utf8,
    `exp` Int16,
    `email` Utf8,
    `subscribe` Bool,
    `registration_date` Datetime,
    PRIMARY KEY (`user_id`)
  );

  COMMIT;

  CREATE TABLE `states`
  (
    `user_id` Uint64,
    `state` Utf8,
    PRIMARY KEY (`user_id`)
  );