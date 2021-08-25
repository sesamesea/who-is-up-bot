from enum import Enum, auto
from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackQueryHandler, CallbackContext,
                          CommandHandler, ConversationHandler, Updater)

import config
import observer
from event import EventType, post_event


_subscribers = dict()


class _State(Enum):
    LAST_SEEN_INIT = auto()
    NOTIFY_SUGGESTION = auto()

    @property
    def pattern(self) -> str:
        return f'^{self.value}:[0-9]+$'


def _restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user = update.effective_user
        if config.WHITELIST_ENABLED and user.id not in config.WHITELIST:
            user.send_message(
                'You have to be whitelisted to use this command.'
            )
            return
        return func(update, context, *args, **kwargs)
    return wrapped


@_restricted
def _last_seen_init(update: Update, context: CallbackContext) -> int:
    msg_text = 'Which host do you want to check?'

    keyboard = []
    for subject in observer.get_all():
        data = f'{_State.LAST_SEEN_INIT.value}:{subject.id_}'
        button = InlineKeyboardButton(subject.name, callback_data=data)
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(msg_text, reply_markup=reply_markup)

    return _State.LAST_SEEN_INIT.value


@_restricted
def _fetch_last_seen(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    subject_id = int(query.data.split(':')[1])
    subject = observer.get_subject(subject_id)

    last_seen = subject.get_last_seen()
    if last_seen:
        msg_text = f'{subject.name} was up at {last_seen}'
    else:
        msg_text = 'No info found.'

    data = f'{_State.NOTIFY_SUGGESTION.value}:{subject_id}'
    button = InlineKeyboardButton('Notify me', callback_data=data)
    keyboard = [[button]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=msg_text, reply_markup=reply_markup)

    return _State.NOTIFY_SUGGESTION.value


@_restricted
def _set_notification(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    subscriber = query.from_user
    subject_id = int(query.data.split(':')[1])
    subject = observer.get_subject(subject_id)

    if subject_id not in _subscribers:
        _subscribers[subject_id] = set()
    _subscribers[subject_id].add(subscriber)

    msg_text = f'You will get a notification when {subject.name} is up.'
    query.edit_message_text(text=msg_text)

    return ConversationHandler.END


def notify(subject_id: int) -> None:
    subject = observer.get_subject(subject_id)
    if subject_id in _subscribers:
        for subscriber in _subscribers[subject_id]:
            msg_text = f'{subject.name} is now up!'
            subscriber.send_message(msg_text)

            notification_pair = tuple([subscriber, subject])
            post_event(EventType.NOTIFICATION, notification_pair)

        del _subscribers[subject_id]


def start_bot() -> None:
    updater = Updater(config.TOKEN)
    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                _fetch_last_seen,
                pattern=_State.LAST_SEEN_INIT.pattern
            )
        ],
        states={
            _State.NOTIFY_SUGGESTION.value: [
                CallbackQueryHandler(
                    _set_notification,
                    pattern=_State.NOTIFY_SUGGESTION.pattern
                )
            ]
        },
        fallbacks=[
            CallbackQueryHandler(
                _fetch_last_seen,
                pattern=_State.LAST_SEEN_INIT.pattern
            )
        ],
        per_message=True
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(CommandHandler('lastseen', _last_seen_init))

    updater.start_polling()
    updater.idle()
