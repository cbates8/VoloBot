"""Combat Argument Utils"""

import argparse
import os

from utils.argparse_utils import ArgParseError, CustArgParser, none_or_int, none_or_str
from utils.logging import get_logger

LOGGER = get_logger(os.path.basename(__file__))


# Argument Types
class CombatArgs(argparse.Namespace):
    """Types for Combat arguments"""

    sub_command: str
    combat_id: str
    as_text: bool

    ## Character args ##
    name: str
    id: str
    initiative: str
    cn: str  # Condition name
    cd: str  # Condition duration

    ## PC ##
    chp: int  # Current HP
    mhp: int  # Max HP
    thp: int  # Temp HP
    ac: int  # Armor Class
    tac: int  # Temp Armor Class

    ## NPC ##
    h: bool  # Healthy
    b: bool  # Bloodied
    d: bool  # Dead

    ## Heal/Dmg ##
    amount: int


# Parse `combat` command arguments
def get_combat_args(*args: str) -> CombatArgs:  # noqa: PLR0915
    """Parse arguments for the `combat` command

    Raises:
        `ArgParseError`: Raised if there is an issue parsing args

    Returns:
        `CombatArgs`: Parsed args
    """
    # Create top level `combat` parser
    parser = CustArgParser(prog="combat", exit_on_error=False, add_help=False)
    subparsers = parser.add_subparsers(dest="sub_command", required=True)

    # Create `begin` subcommand
    parser_begin = subparsers.add_parser("begin")
    parser_begin.add_argument("combat_id", type=str)

    # Create `save` subcommand
    parser_save = subparsers.add_parser("save")
    parser_save.add_argument("combat_id", type=str)

    # Create `load` subcommand
    parser_load = subparsers.add_parser("load")
    parser_load.add_argument("combat_id", type=str)

    # Create `clear` subcommand
    _ = subparsers.add_parser("clear")

    # Create `show` subcommand
    parser_show = subparsers.add_parser("show")
    parser_show.add_argument("--as_text", "--t", action="store_true")

    # Create `list` subcommand
    _ = subparsers.add_parser("list")

    # Create `add` subcommand
    parser_add = subparsers.add_parser("add")
    parser_add.add_argument("name", type=str)
    parser_add.add_argument("--id", type=str, default=None)
    parser_add.add_argument("--initiative", "--i", type=int, default=None)
    parser_add.add_argument("--cn", type=str, default=None)
    parser_add.add_argument("--cd", type=str, default=None)
    parser_add.add_argument("--chp", type=int, default=None)
    parser_add.add_argument("--mhp", type=int, default=None)
    parser_add.add_argument("--thp", type=int, default=None)
    parser_add.add_argument("--ac", type=int, default=None)
    parser_add.add_argument("--tac", type=int, default=None)

    # Create `madd` subcommand
    parser_madd = subparsers.add_parser("madd")
    parser_madd.add_argument("name", type=str)
    parser_madd.add_argument("--id", type=str, default=None)
    parser_madd.add_argument("--initiative", "--i", type=int, default=None)
    parser_madd.add_argument("--cn", type=str, default=None)
    parser_madd.add_argument("--cd", type=str, default=None)
    parser_madd.add_argument("--h", action="store_true")
    parser_madd.add_argument("--b", action="store_true")
    parser_madd.add_argument("--d", action="store_true")

    # Create `update` subcommand
    parser_update = subparsers.add_parser("update", argument_default=argparse.SUPPRESS)
    parser_update.add_argument("name", type=str)
    parser_update.add_argument("--id", type=str)
    parser_update.add_argument("--initiative", "--i", type=none_or_int)
    parser_update.add_argument("--cn", type=none_or_str)
    parser_update.add_argument("--crm", type=str)
    parser_update.add_argument("--cd", type=none_or_str)
    parser_update.add_argument("--chp", type=none_or_int)
    parser_update.add_argument("--mhp", type=none_or_int)
    parser_update.add_argument("--thp", type=none_or_int)
    parser_update.add_argument("--ac", type=none_or_int)
    parser_update.add_argument("--tac", type=none_or_int)
    parser_update.add_argument("--h", action="store_true")
    parser_update.add_argument("--b", action="store_true")
    parser_update.add_argument("--d", action="store_true")

    # Create `rm` subcommand
    parser_rm = subparsers.add_parser("rm")
    parser_rm.add_argument("name", type=str)

    # Create `heal` subcommand
    parser_heal = subparsers.add_parser("heal")
    parser_heal.add_argument("name", type=str)
    parser_heal.add_argument("amount", type=int)

    # Create `dmg` subcommand
    parser_dmg = subparsers.add_parser("dmg")
    parser_dmg.add_argument("name", type=str)
    parser_dmg.add_argument("amount", type=int)

    # Parse Args
    # Catch SystemExit because ArgParse keeps trying to kill the program
    try:
        parsed_args = parser.parse_args(args)
    except SystemExit as error:
        LOGGER.exception(error, exc_info=error)
        raise ArgParseError("ArgParse tried to kill Volobot. See log for details.")

    return parsed_args
