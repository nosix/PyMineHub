import json
from binascii import unhexlify as unhex
from collections import namedtuple
from enum import Enum
from typing import Any, Callable, Dict, Tuple
from uuid import UUID

from pyminehub.binutil.composite import CompositeCodecContext
from pyminehub.mcpe.const import ItemType, RecipeType
# noinspection PyProtectedMember
from pyminehub.mcpe.network.codec.game import _RecipeList, _InventoryContentItems
from pyminehub.mcpe.value import Item, Recipe, RecipeForNormal, RecipeForFurnace, RecipeForMulti

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
    if isinstance(o, UUID):
        return {'value': o.hex, _KEY_CLASS_NAME: 'UUID'}
    if isinstance(o, Enum):
        return {'value': o.value, _KEY_CLASS_NAME: type(o).__name__}
    return o


def _convert_to_namedtuple(o, factory: Dict[str, Callable[..., namedtuple]]) -> Any:
    if isinstance(o, list):
        return tuple(_convert_to_namedtuple(e, factory) for e in o)
    if isinstance(o, dict):
        o = dict((k, _convert_to_namedtuple(v, factory)) for k, v in o.items())
        try:
            cls = o.pop(_KEY_CLASS_NAME)
            return factory[cls](**o)
        except KeyError:
            return o
    return o


def dump_recipe(recipe: Tuple[Recipe, ...], file_name: str, indent=None) -> None:
    """For example, crafting-data-recipe.json is dumped by this."""
    with open(file_name, 'w') as file:
        json.dump(_convert_to_jsonable(recipe), file, indent=indent)


def load_recipe(file_name: str) -> Tuple[Recipe, ...]:
    factory = {
        'Recipe': Recipe,
        'RecipeType': RecipeType,
        'RecipeForNormal': RecipeForNormal,
        'RecipeForFurnace': RecipeForFurnace,
        'RecipeForMulti': RecipeForMulti,
        'Item': Item,
        'ItemType': ItemType,
        'UUID': lambda value: UUID(hex=value),
        'bytes': lambda value: unhex(value)
    }
    with open(file_name, 'r') as file:
        d = json.load(file)
        return _convert_to_namedtuple(d, factory)


def encode_recipe(recipe: Tuple[Recipe, ...], file_name: str) -> None:
    """For example, pyminehub/mcpe/resource/crafting-data-recipe.dat is encoded by this."""
    data = bytearray()
    context = CompositeCodecContext()
    # noinspection PyProtectedMember
    _RecipeList._CODEC.write(data, recipe, context)
    with open(file_name, 'bw') as file:
        file.write(data)


def dump_inventory_content(content: Tuple[Item, ...], file_name: str, indent=None) -> None:
    """For example, inventory-content-items121.json is dumped by this."""
    with open(file_name, 'w') as file:
        json.dump(_convert_to_jsonable(content), file, indent=indent)


def load_inventory_content(file_name: str) -> Tuple[Item, ...]:
    factory = {
        'Item': Item,
        'ItemType': ItemType,
        'bytes': lambda value: unhex(value)
    }
    with open(file_name, 'r') as file:
        d = json.load(file)
        return _convert_to_namedtuple(d, factory)


def encode_inventory_content(content: Tuple[Item, ...], file_name: str) -> None:
    """For example, pyminehub/mcpe/resource/inventory-content-items121.dat is encoded by this."""
    data = bytearray()
    context = CompositeCodecContext()
    # noinspection PyProtectedMember
    _InventoryContentItems._CODEC.write(data, content, context)
    with open(file_name, 'bw') as file:
        file.write(data)
