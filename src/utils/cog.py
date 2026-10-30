"""Discord Cog Utils"""

import importlib
import os
import sys

from constants.paths import COG_DOTPATH, CONSTANTS_DIR, UTILS_DIR

MODULES_TO_RELOAD = [UTILS_DIR, CONSTANTS_DIR]


def get_cog_path(cog: str) -> str:
    """Get dot path of a cog
    e.g. `spell` -> `commands.spell`

    Args:
        cog (`str`): Name of a cog

    Returns:
        `str`: Dot path of a cog
    """
    return COG_DOTPATH.format(cog=cog.lower())


def get_modules() -> list[str]:
    """Get custom Python modules we want to reload, ignores __init__.py and non-Python files.

    Calling this when reloading a Cog allows us to abstract logic away from Cog classes.

    Right now this gets all files from utils and constants direcories.
    Ideally, we want this to only get the modules imported by the Cog we are reloading
    (e.g. If we are reloading the Crit Cog, we only want to reload `utils.crit` and `constants.paths` instead of everything)

    Returns:
        `list[str]`: List of our custom Python modules
    """
    modules: list[str] = list()
    for module in MODULES_TO_RELOAD:
        for dirpath, _, filenames in os.walk(module):
            for file in filenames:
                if file.endswith(".py") and "__" not in file:
                    module_path = f"{dirpath.replace('/', '.')}.{file.split('.')[0]}"
                    modules.append(module_path)
    return modules


def reload_modules() -> None:
    """Reload Python modules
    https://github.com/Rapptz/discord.py/discussions/9051#discussioncomment-4076913
    """
    for module in get_modules():
        sys.modules[module] = importlib.reload(sys.modules[module])
