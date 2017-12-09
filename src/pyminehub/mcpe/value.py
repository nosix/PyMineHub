from typing import NamedTuple, Tuple, Union, Optional

from pyminehub.mcpe.const import *
from pyminehub.mcpe.geometry import Vector3

ConnectionRequest = NamedTuple('ConnectionRequest', [
    ('chain', Tuple[dict, ...]),  # NOTE: dict is mutable
    ('client', dict)  # NOTE: dict is mutable
])

PackEntry = NamedTuple('PackEntry', [
    ('id', str),
    ('version', str),
    ('size', int),
    ('unknown1', str),
    ('unknown2', str)
])

PackStack = NamedTuple('PackStack', [
    ('id', str),
    ('version', str),
    ('unknown1', str)
])

GameRule = NamedTuple('GameRule', [
    ('name', str),
    ('type', int),
    ('value', Union[bool, int, float])
])

Attribute = NamedTuple('Attribute', [
    ('min', float),
    ('max', float),
    ('current', float),
    ('default', float),
    ('name', str)
])

CommandEnum = NamedTuple('CommandEnum', [
    ('name', str),
    ('index', Tuple[int, ...])
])

CommandParameter = NamedTuple('CommandParameter', [
    ('name', str),
    ('type', int),
    ('is_optional', bool)
])

CommandData = NamedTuple('CommandData', [
    ('name', str),
    ('description', str),
    ('flags', int),
    ('permission', int),
    ('aliases', int),
    ('overloads', Tuple[Tuple[CommandParameter], ...])
])

Slot = NamedTuple('Slot', [
    ('id', int),
    ('aux_value', Optional[int]),
    ('nbt', Optional[bytes]),
    ('place_on', Optional[str]),
    ('destroy', Optional[str])
])

MetaDataValue = Union[int, float, str, Vector3, Slot]

EntityMetaData = NamedTuple('EntityMetaData', [
    ('key', int),
    ('type', MetaDataType),
    ('value', MetaDataValue)
])

UUID = NamedTuple('UUID', [
    ('part1', int),
    ('part0', int),
    ('part3', int),
    ('part2', int)
])

Skin = NamedTuple('Skin', [
    ('id', str),
    ('data', bytes),
    ('cape', str),
    ('geometry_name', str),
    ('geometry_data', str)
])

PlayerListEntry = NamedTuple('PlayerListEntry', [
    ('uuid', UUID),
    ('entity_unique_id', Optional[int]),
    ('user_name', Optional[str]),
    ('skin', Optional[Skin]),
    ('xbox_user_id', Optional[str])
])

RecipeForNormal = NamedTuple('RecipeForNormal', [
    ('width', Optional[int]),
    ('height', Optional[int]),
    ('input', Tuple[Slot, ...]),
    ('output', Tuple[Slot, ...]),
    ('uuid', UUID)
])

RecipeForFurnace = NamedTuple('RecipeForFurnace', [
    ('input_id', int),
    ('input_damage', Optional[int]),
    ('output', Slot)
])

RecipeForMulti = NamedTuple('RecipeForMulti', [
    ('uuid', UUID)
])

RecipeData = Union[RecipeForNormal, RecipeForFurnace, RecipeForMulti]

Recipe = NamedTuple('Recipe', [
    ('type', RecipeType),
    ('data', RecipeData)
])
