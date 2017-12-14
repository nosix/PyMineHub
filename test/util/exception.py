import sys
import traceback
from typing import Callable, Optional, Any


def interrupt_for_pycharm(exc: Exception, called: Optional[str], packet_info: str=None) -> None:
    if type(exc).__name__ == 'EqualsAssertionError':
        attrs = exc.__dict__
        if called is not None:
            if 'called' not in attrs:
                attrs['called'] = called
            if 'stack' not in attrs:
                attrs['stack'] = []
            if packet_info is not None:
                attrs['stack'].append(packet_info)
        elif 'called' in attrs:
            messages = ['AssertionError occurred while testing', attrs['called'][:-1]]  # remove \n
            messages.extend(attrs['stack'])
            messages.append(attrs['msg'])
            attrs['msg'] = '\n'.join(messages)
        raise exc


class _WrappedException(Exception):

    def __init__(self, exc: Exception, tb: traceback, message: str) -> None:
        super().__init__(message)
        self.exc = exc
        self.tb = tb


def try_action(
        action_of_raising_exception: Callable[[], None],
        called_line: Optional[str]=None,
        packet_info: Optional[str]=None,
        exception_factory: Optional[Callable[..., Exception]]=None
) -> Any:
    """Call when doing exception handling.

    :param action_of_raising_exception: you need to call this function
    :param called_line: line where PacketAnalyzer's constructor is called
    :param packet_info: information of the packet
        Example:
            Batch BATCH(id=254, payloads=(bytearray(b'4\x00\x00\xfd\x07\x02\x06\x06\n\x82\xfc...
    :param exception_factory: raise exception that create by factory if _WrappedException is raised
    """
    try:
        return action_of_raising_exception()
    except _WrappedException as e:
        message = '{}'.format(e.args[0])
        if exception_factory is None:
            raise _WrappedException(e.exc, e.tb, message) from None
        else:
            raise exception_factory(message).with_traceback(e.tb) from None
    except Exception as e:
        interrupt_for_pycharm(e, called_line, packet_info)
        if called_line is not None:
            message = '{} occurred while testing\n{}{}'.format(
                repr(e), called_line, packet_info if packet_info is not None else '')
            raise _WrappedException(e, sys.exc_info()[2], message) from None
        else:
            raise e
