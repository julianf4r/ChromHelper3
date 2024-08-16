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
from .tab_config import TabConfig
from core.db_operations import DBManger
from core.utils import get_icon_path


class UserDataListModel(QAbstractTableModel):

    def __init__(
            self,
            userdata_info: list[list[str]],  # [[name, type, exec, data]]
            parent: QWidget = None,
    ):
        super().__init__(parent)
        self.userdata_info = userdata_info

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.userdata_info)

    def columnCount(self, parent: QModelIndex = ...):
        return 1

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        if role == Qt.ItemDataRole.DisplayRole:
            return self.userdata_info[row][0]
        if role == Qt.ItemDataRole.DecorationRole:
            return QIcon(get_icon_path(self.userdata_info[row][1]))
        if role == Qt.ItemDataRole.UserRole:
            return self.userdata_info[row][2], self.userdata_info[row][3]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return "浏览器"
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignCenter

    def update_model(self, userdata_info: list[list[str]]):
        self.beginResetModel()
        self.userdata_info = userdata_info
        self.endResetModel()


class MwChromHelper(QMainWindow):

    def __init__(self, app_dir: str, parent=None):
        super().__init__(parent)

        self.dbm = DBManger(app_dir)

        self.chrom_ins_map: dict[str, ChromInstance] = {}

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

        self.tab_profiles = TabProfiles(parent=self)
        self.tab_extensions = TabExtensions(parent=self)
        self.tab_bookmarks = TabBookmarks(parent=self)
        self.tab_config = TabConfig(self.dbm, parent=self)
        self.tw_right.addTab(self.tab_profiles, QIcon(get_icon_path("profile")), "用户页")
        self.tw_right.addTab(self.tab_extensions, QIcon(get_icon_path("extension")), "插件页")
        self.tw_right.addTab(self.tab_bookmarks, QIcon(get_icon_path("bookmark")), "书签页")
        self.tw_right.addTab(self.tab_config, QIcon(get_icon_path("config")), "配置页")

        self.trv_left.doubleClicked.connect(self.on_trv_left_double_clicked)
        self.tab_config.userdata_changed.connect(self.on_tab_config_userdata_changed)

        # ================== END UI =====================

        userdata_info = self.dbm.select_all()
        self.userdata_model = UserDataListModel(userdata_info, self)
        self.trv_left.setModel(self.userdata_model)

    def update_all_data(self, chrom_ins: ChromInstance, exec_path: str):
        self.tab_profiles.update_model(chrom_ins.profiles)
        self.tab_extensions.update_model(
            chrom_ins.extensions,
            chrom_ins.profiles,
            chrom_ins.userdata_dir,
            exec_path,
        )
        self.tab_bookmarks.update_model(
            chrom_ins.bookmarks,
            chrom_ins.profiles,
            chrom_ins.userdata_dir,
            exec_path,
        )

    def on_trv_left_double_clicked(self):
        index = self.trv_left.selectedIndexes()[0]
        name = index.data(Qt.ItemDataRole.DisplayRole)
        exec_path, data_path = index.data(Qt.ItemDataRole.UserRole)
        if name not in self.chrom_ins_map:
            chrom_ins = ChromInstance(data_path)
            chrom_ins.fetch_all_profiles()
            chrom_ins.fetch_extensions_from_all_profiles()
            chrom_ins.fetch_bookmarks_from_all_profiles()
            self.chrom_ins_map[name] = chrom_ins

        self.update_all_data(self.chrom_ins_map[name], exec_path)

    def on_tab_config_userdata_changed(self):
        self.userdata_model.update_model(self.dbm.select_all())

    def sizeHint(self):
        return QSize(860, 640)
