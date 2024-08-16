# coding: utf8
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

from jnp3.path import get_log_dir

from widgets.mw_chromhelper import MwChromHelper
import rc_chromhelper3


__version__ = '0.1.0'
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

    win = MwChromHelper(get_app_dir())
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
