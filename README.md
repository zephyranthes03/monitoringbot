# Monitoring Bot

A Python prototype for managing monitored TCP endpoints through Telegram. A background loop attempts the checks, and MongoDB stores endpoint, chat, and scheduling data.

## Local setup

Docker Compose builds the Python 3.12 bot and starts MongoDB. Provide `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in your local environment. The token variable name matches the bot code and [Compose configuration](docker-compose.yml).

~~~sh
docker compose up --build
~~~

The Compose file uses development credentials and publishes the MongoDB port on the host. Run the prototype in a local development environment.

## Telegram commands

| Command | Purpose |
| --- | --- |
| `/start` | Open the bot menu. |
| `/chat_id` | Show the current chat ID. |
| `/add` | Add an endpoint by host and port. |
| `/list` | List the chat's monitored endpoints. |
| `/remove` | Remove an endpoint from monitoring. |

See the [Telegram handlers](bot/telegram_event_handler.py), [TCP checks](bot/socket_test.py), and [MongoDB access layer](bot/database/database.py).

The scheduled check loop currently records scheduling state. Automatic outage notifications are future work.

## License

[GNU GPL v3](LICENSE)
