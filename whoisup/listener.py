import bot
import config
import yee
from event import EventType, subscribe
from observer import Subject


class BotListener:
    @classmethod
    def setup_handlers(cls) -> None:
        subscribe(EventType.SUBJECT_UPDATE, cls._handle_subject_update)

    @staticmethod
    def _handle_subject_update(subject: Subject) -> None:
        bot.notify(subject.id_)


class YeelightListener:
    @classmethod
    def setup_handlers(cls) -> None:
        subscribe(EventType.NOTIFICATION, cls._handle_notification)

    @staticmethod
    def _handle_notification(notification_pair: tuple) -> None:
        recipient, subject = notification_pair
        if config.YEELIGHT_ENABLED and recipient.id == config.OWNER_ID:
            yee.notify(subject.color)
