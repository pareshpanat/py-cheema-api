"""Import-name alias for `cheema`, matching the `py-cheema-api` PyPI distribution name.

`pip install py-cheema-api` installs the `cheema` package; this module lets
`import py_cheema_api` work too, for anyone who expects the import path to
match the distribution name.
"""
from cheema import *  # noqa: F401,F403
from cheema import __all__, __version__  # noqa: F401
