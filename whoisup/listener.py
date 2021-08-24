import bot
import config
import yee
from observer import Subject


def handle_subject_update(subject: Subject) -> None:
    bot.notify(subject.id_)


def handle_notification(notification_pair: tuple) -> None:
    recipient, subject = notification_pair
    if config.YEELIGHT_ENABLED and recipient.id == config.OWNER_ID:
        _handle_yeelight(notification_pair)


def _handle_yeelight(notification_pair) -> None:
    subject = notification_pair[1]
    yee.notify(subject.color)
