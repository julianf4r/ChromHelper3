# coding: utf8
has_pyside6 = False
has_pyside2 = False

try:
    import PySide6

    has_pyside6 = True

    from PySide6.QtCore import (
        qRegisterResourceData,
        Qt,
        QAbstractItemModel,
        QAbstractListModel,
        QAbstractTableModel,
        QModelIndex,
        QObject,
        QPoint,
        QSize,
        QSortFilterProxyModel,
        Signal,
    )
    from PySide6.QtGui import (
        QAction,
        QFont,
        QIcon,
    )
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QApplication,
        QComboBox,
        QDialog,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenu,
        QMessageBox,
        QPushButton,
        QTabWidget,
        QTreeView,
        QVBoxLayout,
        QWidget,
    )
    from PySide6 import __version__ as pyside_version
except ImportError:
    try:
        import PySide2

        has_pyside2 = True

        from PySide2.QtCore import (
            qRegisterResourceData,
            Qt,
            QAbstractItemModel,
            QAbstractListModel,
            QAbstractTableModel,
            QModelIndex,
            QObject,
            QPoint,
            QSize,
            QSortFilterProxyModel,
            Signal,
        )
        from PySide2.QtGui import (
            QFont,
            QIcon,
        )
        from PySide2.QtWidgets import (
            QAbstractItemView,
            QAction,
            QApplication,
            QComboBox,
            QDialog,
            QFileDialog,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QMenu,
            QMessageBox,
            QPushButton,
            QTabWidget,
            QTreeView,
            QVBoxLayout,
            QWidget,
        )
        from PySide2 import __version__ as pyside_version

    except ImportError:
        pyside_version = "0.0.0"

__all__ = ["has_pyside6", "has_pyside2", "pyside_version"]

__all__ += [
    # QtCore
    "qRegisterResourceData",
    "Qt",
    "QAbstractItemModel",
    "QAbstractListModel",
    "QAbstractTableModel",
    "QModelIndex",
    "QObject",
    "QPoint",
    "QSize",
    "QSortFilterProxyModel",
    "Signal",
    # QtGui
    "QFont",
    "QIcon",
    # QtWidgets
    "QAbstractItemView",
    "QApplication",
    "QComboBox",
    "QDialog",
    "QFileDialog",
    "QHBoxLayout",
    "QLabel",
    "QLineEdit",
    "QMainWindow",
    "QMenu",
    "QMessageBox",
    "QPushButton",
    "QTabWidget",
    "QTreeView",
    "QVBoxLayout",
    "QWidget",
    # not compat
    "QAction",
]
