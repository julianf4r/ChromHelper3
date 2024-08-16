# coding: utf8
from PySide6.QtCore import (
    QSize, QAbstractTableModel,
    QModelIndex, Qt,
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout,
    QTabWidget, QPushButton,
    QTreeView,
)

from jnp3.gui import StyleComboBox
from chromy.chromi import ChromInstance

from .tab_profiles import TabProfiles
from .tab_extensions import TabExtensions
from .tab_bookmarks import TabBookmarks


class UserDataListModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.userdata_info = [
            [QIcon(":/assets/icons/chrome_32.png"), "Chrome", r"C:\Users\Julian\AppData\Local\Google\Chrome\User Data"],
            [QIcon(":/assets/icons/edge_32.png"), "Edge", r"C:\Users\Julian\AppData\Local\Microsoft\Edge\User Data"],
            [QIcon(":/assets/icons/brave_32.png"), "Brave", r"C:\Users\Julian\AppData\Local\BraveSoftware\Brave-Browser\User Data"],
        ]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.userdata_info)

    def columnCount(self, parent: QModelIndex = ...):
        return 1

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        if role == Qt.ItemDataRole.DisplayRole:
            return self.userdata_info[row][1]
        if role == Qt.ItemDataRole.DecorationRole:
            return self.userdata_info[row][0]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return "浏览器"
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignCenter


class MwChromHelper(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        chrome = ChromInstance(r"C:\Users\Julian\AppData\Local\Google\Chrome\User Data")
        # chrome = ChromInstance(r"F:\Chrome\RecycleAccounts\User Data")
        chrome.fetch_all_profiles()
        chrome.fetch_extensions_from_all_profiles()
        chrome.fetch_bookmarks_from_all_profiles()

        # =================== UI =========================
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)

        self.vly_cw = QVBoxLayout()
        self.cw.setLayout(self.vly_cw)

        self.hly_top = QHBoxLayout()
        self.vly_cw.addLayout(self.hly_top)

        self.cmbx_styles = StyleComboBox(self)
        self.cmbx_styles.setMinimumWidth(100)

        self.pbn_settings = QPushButton("设置", self)
        self.pbn_about = QPushButton("关于", self)

        self.hly_top.addWidget(self.cmbx_styles)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.pbn_settings)
        self.hly_top.addWidget(self.pbn_about)

        self.hly_main = QHBoxLayout()
        self.vly_cw.addLayout(self.hly_main)

        self.trv_left = QTreeView(self)
        self.trv_left.setMinimumWidth(100)
        self.trv_left.setIndentation(0)

        self.tw_right = QTabWidget(self)

        self.hly_main.addWidget(self.trv_left)
        self.hly_main.addWidget(self.tw_right)
        self.hly_main.setStretchFactor(self.trv_left, 1)
        self.hly_main.setStretchFactor(self.tw_right, 5)

        self.tab_profiles = TabProfiles(chrome.profiles, self)
        self.tab_extensions = TabExtensions(chrome, self)
        self.tab_bookmarks = TabBookmarks(chrome, self)
        self.tw_right.addTab(self.tab_profiles, QIcon(":/assets/icons/profile_32.png"), "用户页")
        self.tw_right.addTab(self.tab_extensions, QIcon(":/assets/icons/extension_32.png"), "插件页")
        self.tw_right.addTab(self.tab_bookmarks, QIcon(":/assets/icons/bookmark_32.png"), "书签页")

        # ================== END UI =====================

        model = UserDataListModel(self)
        self.trv_left.setModel(model)

    def sizeHint(self):
        return QSize(860, 640)
