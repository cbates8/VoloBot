"""Discord ANSI Color Codes

ANSI formatting should be done within a ```ansi ``` code block.
Use `\u001b[0m` as as suffix to revert formatting (i.e. you only want to modify a few words/lines).
https://gist.github.com/kkrypt0nn/a02506f3712ff2d1c8ca7c9e0aed7c06
"""

# Text Formatting
NORMAL = "0"
BOLD = "1"
UNDERLINE = "4"

# Text Colors
T_GREY = "30"
T_RED = "31"
T_GREEN = "32"
T_YELLOW = "33"
T_BLUE = "34"
T_PINK = "35"
T_CYAN = "36"
T_WHITE = "37"

# Text Background
B_FIREFLY_DARK_BLUE = "40"
B_ORANGE = "41"
B_MARBLE_BLUE = "42"
B_GREYISH_TURQUOISE = "43"
B_GREY = "44"
B_INDIGO = "45"
B_LIGHT_GREY = "46"
B_WHITE = "47"

# Format start/stop indicators

# Multiple prefixes can be used to stack modifiers OR you can use a single prefix with multiple codes
# "\u001b[44m\u001b[30m" = "\u001b[44;30m" = grey background, green text
FORMAT_PREFIX = "\u001b[{f_type}m"
FORMAT_SUFFIX = FORMAT_PREFIX.format(f_type=NORMAL)

ANSI_WRAPPER = """```ansi
{body}
```
"""

FORMAT_WRAPPER = "\u001b[{f_type}m{body}\u001b[0m"

NORMAL_WRAPPER = "\u001b[0m{body}\u001b[0m"
GREY_WRAPPER = "\u001b[30m{body}\u001b[0m"
RED_WRAPPER = "\u001b[31m{body}\u001b[0m"
BLUE_WRAPPER = "\u001b[34m{body}\u001b[0m"
