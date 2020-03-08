#!/usr/bin/env python3
"""
Demonstration of all the ANSI colors.
"""
from prompt_toolkit import print_formatted_text as pft
from prompt_toolkit import HTML
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles.named_colors import NAMED_COLORS


def main():
    tokens = FormattedText(
        [('fg:' + name, name + '  ') for name in NAMED_COLORS]
    )
    pft(HTML('\n<u>Named colors, hex codes.</u>'))
    print(", ".join([f"{k}: {v}" for k, v in NAMED_COLORS.items()]))

    pft(HTML('\n<u>Named colors, using 16 color output.</u>'))
    pft('(Note that it doesn\'t really make sense to use named colors ')
    pft('with only 16 color output.)')
    pft(tokens, color_depth=ColorDepth.DEPTH_4_BIT)

    pft(HTML('\n<u>Named colors, use 256 colors.</u>'))
    pft(tokens)

    pft(HTML('\n<u>Named colors, using True color output.</u>'))
    pft(tokens, color_depth=ColorDepth.TRUE_COLOR)


if __name__ == '__main__':
    main()