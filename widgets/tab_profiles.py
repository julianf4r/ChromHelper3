# coding: utf8
from PySide6.QtCore import (
    QAbstractTableModel, QModelIndex, Qt, QPoint, QSize
)
from PySide6.QtGui import (
    QFont, QAction,
)
from PySide6.QtWidgets import (
    QWidget, QTreeView,
    QVBoxLayout, QMenu,
)

from chromy.structs import Profile

from core.utils import (
    sort_profiles_id_func,
    ProfileSortFilterProxyModel,
    open_profiles,
    get_profile_picture,
)


class ProfilesModel(QAbstractTableModel):

    def __init__(self, browser: str, profiles: dict[str, Profile], parent=None):
        super().__init__(parent)
        self.browser = browser
        self.profiles = profiles
        self.profile_ids = list(profiles.keys())
        self.profile_ids.sort(key=sort_profiles_id_func)

        self.headers = ["ID", "名称", "邮箱"]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.profile_ids)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = ...):
        profile_id = self.profile_ids[index.row()]
        profile = self.profiles[profile_id]
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            col_map = {
                0: profile.id,
                1: profile.name,
                2: profile.user_name,
            }
            return col_map[col]
        elif role == Qt.ItemDataRole.DecorationRole:
            if col == 1:
                return get_profile_picture(self.browser, profile)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[section]
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font

    def update_data(self, browser: str, profiles: dict[str, Profile]):
        self.beginResetModel()

        self.browser = browser
        self.profiles = profiles
        self.profile_ids = list(profiles.keys())
        self.profile_ids.sort(key=sort_profiles_id_func)

        self.endResetModel()


class TabProfiles(QWidget):

    def __init__(
            self,
            browser: str = "",
            profiles: dict[str, Profile] = None,
            userdata_dir: str = "",
            exec_path: str = "",
            parent: QWidget = None
    ):
        super().__init__(parent)
        self.browser = browser
        self.profiles = profiles or {}
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path

        self.menu_ctx = QMenu(self)
        self.act_open = QAction("打开", self)
        self.menu_ctx.addAction(self.act_open)

        self.vly_m = QVBoxLayout()
        self.setLayout(self.vly_m)

        self.trv_m = QTreeView(self)
        self.trv_m.setIndentation(0)
        self.trv_m.setSortingEnabled(True)
        self.trv_m.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.trv_m.setUniformRowHeights(True)
        self.trv_m.setStyleSheet("QTreeView::item { height: 40px; }")
        self.trv_m.setIconSize(QSize(32, 32))

        self.vly_m.addWidget(self.trv_m)

        self.profiles_model = ProfilesModel(browser, self.profiles, self)

        proxy_model = ProfileSortFilterProxyModel(self)
        proxy_model.setSourceModel(self.profiles_model)

        self.trv_m.setModel(proxy_model)

        self.trv_m.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.trv_m.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.act_open.triggered.connect(self.on_act_open_triggered)
        self.trv_m.customContextMenuRequested.connect(self.on_trv_m_custom_context_menu_requested)

    def on_act_open_triggered(self):
        open_profiles(self, self.trv_m.selectedIndexes(), self.exec_path, self.userdata_dir)

    def on_trv_m_custom_context_menu_requested(self, pos: QPoint):
        self.menu_ctx.exec(self.trv_m.viewport().mapToGlobal(pos))

    def update_model(
            self,
            browser: str,
            profiles: dict[str, Profile],
            userdata_dir: str,
            exec_path: str,
    ):
        self.browser = browser
        self.profiles = profiles
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.profiles_model.update_data(browser, profiles)

        self.trv_m.setColumnWidth(1, 200)
