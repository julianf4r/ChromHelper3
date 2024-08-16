# coding: utf8
import sys
from PySide6.QtWidgets import QApplication

from widgets.mw_chromhelper import MwChromHelper
import rc_chromhelper3


__version__ = '0.1.0'
__version_info__ = tuple(map(int, __version__.split('.')))

ORG_NAME = "JnPrograms"
APP_NAME = "ChromHelper3"


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)

    win = MwChromHelper()
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
