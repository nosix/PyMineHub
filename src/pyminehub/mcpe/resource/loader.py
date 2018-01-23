from pkgutil import get_data


__all__ = [
    'CRAFTING_DATA_RECIPE',
    'INVENTORY_CONTENT_ITEMS121'
]


CRAFTING_DATA_RECIPE = get_data(__package__, 'crafting-data-recipe.dat')

INVENTORY_CONTENT_ITEMS121 = get_data(__package__, 'inventory-content-items121.dat')
