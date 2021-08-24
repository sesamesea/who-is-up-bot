from enum import Enum, auto


_subscribers = dict()


class EventType(Enum):
    SUBJECT_UPDATE = auto()
    NOTIFICATION = auto()
    YEELIGHT_NOTIFFICATION = auto()


def subscribe(event_type: EventType, func) -> None:
    if event_type not in _subscribers:
        _subscribers[event_type] = []
    _subscribers[event_type].append(func)


def post_event(event_type: EventType, data) -> None:
    if event_type in _subscribers:
        for func in _subscribers[event_type]:
            func(data)
