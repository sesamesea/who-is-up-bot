import observer
from bot import start_bot
from listener import BotListener, YeelightListener


def main() -> None:
    BotListener().setup_handlers()
    YeelightListener().setup_handlers()

    observer.load_from_config()
    observer.start_daemon()

    start_bot()


if __name__ == '__main__':
    main()
