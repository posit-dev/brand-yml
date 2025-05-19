#!/usr/bin/env python

import subprocess
import sys

examples = [
    "_resources/examples/home",
    "inspiration/brand-guidelines/dell/_brand",
    "_resources/examples/inspiration/home-depot",
    "_resources/examples/inspiration/indeed",
    "_resources/examples/inspiration/nhsr-community",
    "_resources/examples/inspiration/posit",
    "_resources/examples/inspiration/slack",
    "_resources/examples/inspiration/walmart",
]

for example in examples:
    print(f"Checking example: {example}", file=sys.stderr)

    try:
        subprocess.run(
            ["quarto", "render", example, "--quiet"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error processing {example}: {e}", file=sys.stderr)
    else:
        print(f"Successfully processed {example}", file=sys.stderr)
