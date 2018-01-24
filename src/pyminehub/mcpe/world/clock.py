import asyncio
import time
from typing import Callable

from pyminehub.config import ConfigKey, get_value

__all__ = [
    'Clock'
]


class _ClockLogic:

    @property
    def time(self) -> int:
        raise NotImplementedError()

    def update(self) -> None:
        raise NotImplementedError()


class _StaticClock(_ClockLogic):
    """Watch that always takes the same time"""

    MORNING = 17760
    NOON = 4800
    EVENING = 9600
    NIGHT = 14400

    def __init__(self, mc_time=0):
        self._mc_time = mc_time

    @property
    def time(self) -> int:
        return self._mc_time

    def update(self) -> None:
        pass


class _DynamicClock(_ClockLogic):
    """Watch that keeps one day in 20 minutes"""

    _MC_TIME_PER_DAY = 19200
    _SEC_PER_DAY = 20 * 60  # 20 minutes

    _MC_TIME_PER_SEC = _MC_TIME_PER_DAY // _SEC_PER_DAY  # 16

    def __init__(self):
        self._current_mc_time = 0
        self._origin = time.time()

    @property
    def time(self) -> int:
        return self._current_mc_time

    def update(self) -> None:
        sec = int(time.time() - self._origin) % self._SEC_PER_DAY
        self._current_mc_time = sec * self._MC_TIME_PER_SEC


class Clock:
    """Clock in MineCraft world

    It is configured by clock_time configuration.
    If clock_time is None then time is changed dynamically.
    If clock_time is positive value then time is always specified time.
    In this case, time of clients is synchronized.
    If clock_time is negative value then time is changed dynamically.
    In this case, time of clients is not synchronized.
    The initial time is specified time with the sign reversed.
    """

    def __init__(self, notify_time: Callable[[int], None]) -> None:
        self._notify_time = notify_time
        clock_time = get_value(ConfigKey.CLOCK_TIME)
        if clock_time is None:
            self._logic = _DynamicClock()
        else:
            if clock_time < 0:
                clock_time *= -1
                self._notify_time = None
            self._logic = _StaticClock(clock_time)

    @property
    def time(self) -> int:
        return self._logic.time

    async def run_loop(self) -> None:
        if self._notify_time is None:
            await asyncio.Event().wait()  # wait cancel
            return
        while True:
            start_time = time.time()
            self._logic.update()
            self._notify_time(self._logic.time)
            run_time = time.time() - start_time
            tick_time = get_value(ConfigKey.CLOCK_TICK_TIME)
            if run_time < tick_time:
                await asyncio.sleep(tick_time - run_time)
