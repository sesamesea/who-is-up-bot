import subprocess
from dataclasses import dataclass
from datetime import datetime
from threading import Thread
from time import sleep
from typing import Optional

import config
from event import EventType, post_event
from yee import Color


_subjects = []


@dataclass
class Subject:
    id_: int
    name: str
    hostnames: list[str]
    last_seen: Optional[datetime] = None
    color: Optional[Color] = None

    def get_last_seen(self) -> str:
        if self.last_seen:
            return self.last_seen.strftime('%H:%M, %d.%m.%Y.')

    def ping(self) -> bool:
        is_up = False
        for ip_addr in self.hostnames:
            response = subprocess.call(['ping', '-c', '1', ip_addr],
                                       stdout=subprocess.DEVNULL)
            if response == 0:
                is_up = True
                self.last_seen = datetime.now()
                post_event(EventType.SUBJECT_UPDATE, self)
                break

        return is_up


def load_from_config() -> None:
    for index, subject_record in enumerate(config.HOSTS):
        _subjects.append(
            Subject(id_=index,
                    name=subject_record['name'],
                    hostnames=subject_record['ip_list'])
        )
        if 'color' in subject_record:
            _subjects[index].color = subject_record['color']


def get_subject(id_: int) -> Subject:
    return _subjects[id_]


def get_all() -> list[Subject]:
    return _subjects.copy()


def _update_loop() -> None:
    while True:
        for subject in _subjects:
            subject.ping()
        sleep(config.UPDATE_FREQUENCY)


def start_daemon() -> None:
    thread = Thread(target=_update_loop, daemon=True)
    thread.start()
