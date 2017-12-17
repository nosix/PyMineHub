import json
from binascii import unhexlify as unhex
from collections import namedtuple
from typing import Dict, Callable, Any

from pyminehub.mcpe.value import *

_KEY_CLASS_NAME = '__cls__'


def _convert_to_jsonable(o):
    if isinstance(o, list):
        return list(_convert_to_jsonable(e) for e in o)
    if isinstance(o, dict):
        return dict((k, _convert_to_jsonable(v)) for k, v in o.items())
    if isinstance(o, tuple):
        if hasattr(o, '_asdict'):
            # noinspection PyProtectedMember
            d = o._asdict()
            d[_KEY_CLASS_NAME] = type(o).__name__
            return _convert_to_jsonable(d)
        return tuple(_convert_to_jsonable(e) for e in o)
    if isinstance(o, bytes):
        return {'value': o.hex(), _KEY_CLASS_NAME: 'bytes'}
    if isinstance(o, Enum):
        return {'value': o.value, _KEY_CLASS_NAME: type(o).__name__}
    return o


def dump_recipe(recipe: Tuple[Recipe], file_name: str, indent=None) -> None:
    """For example, recipe-list.json is dumped by this."""
    with open(file_name, 'w') as file:
        json.dump(_convert_to_jsonable(recipe), file, indent=indent)


def _convert_to_namedtuple(o, factory: Dict[str, Callable[..., namedtuple]]) -> Any:
    if isinstance(o, list):
        return list(_convert_to_namedtuple(e, factory) for e in o)
    if isinstance(o, dict):
        o = dict((k, _convert_to_namedtuple(v, factory)) for k, v in o.items())
        try:
            cls = o.pop(_KEY_CLASS_NAME)
            return factory[cls](**o)
        except KeyError:
            return o
    return o


def load_recipe(file_name: str) -> Tuple[Recipe]:
    factory = {
        'Recipe': Recipe,
        'RecipeType': RecipeType,
        'RecipeForNormal': RecipeForNormal,
        'RecipeForFurnace': RecipeForFurnace,
        'RecipeForMulti': RecipeForMulti,
        'Slot': Slot,
        'UUID': UUID,
        'bytes': lambda value: unhex(value)
    }
    with open(file_name, 'r') as file:
        d = json.load(file)
        return _convert_to_namedtuple(d, factory)
