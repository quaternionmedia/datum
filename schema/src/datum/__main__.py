"""Entry point for ``python -m datum``.

The ``datum`` console script is the documented way in, and it needs the package
installed somewhere on ``PATH``. This is the same command line for a caller
that has an interpreter and would rather not depend on that: a subprocess
naming ``sys.executable`` reaches the CLI it is actually running against,
rather than whichever one a shell resolves first.

``python -m datum.cli`` is not that entry point and never was -- it imports the
module, defines the commands, and exits without running any of them.
"""

from datum.cli import cli

if __name__ == "__main__":
    cli()
