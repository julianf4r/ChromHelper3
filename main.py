# coding: utf8
import sys
import logging
from pathlib import Path

from jnp3.path import get_log_dir
from jnp3.misc import get_excepthook_for

from compat import QApplication
from widgets.mw_chromhelper import MwChromHelper
from core.utils import get_exec
import rc_chromhelper3


__version__ = '1.3.0'
__version_info__ = tuple(map(int, __version__.split('.')))

ORG_NAME = "JnPrograms"
APP_NAME = "ChromHelper3"


def get_app_dir():
    app_dir = Path(get_log_dir(), ORG_NAME, APP_NAME)
    app_dir.mkdir(parents=True, exist_ok=True)
    return str(app_dir)


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.INFO)
    sys.excepthook = get_excepthook_for(logger)

    win = MwChromHelper(APP_NAME, __version__, get_app_dir(), logger)
    win.setWindowTitle(f"{APP_NAME} v{__version__}")
    win.show()
    return get_exec(app)()


if __name__ == '__main__':
    main()
