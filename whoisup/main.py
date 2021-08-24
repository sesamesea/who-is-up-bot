import listener
import observer
from bot import start_bot
from event import EventType, subscribe


def main() -> None:
    subscribe(EventType.SUBJECT_UPDATE, listener.handle_subject_update)
    subscribe(EventType.NOTIFICATION, listener.handle_notification)

    observer.load_from_config()
    observer.start_daemon()

    start_bot()


if __name__ == '__main__':
    main()
