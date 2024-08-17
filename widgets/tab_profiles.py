# coding: utf8
from PySide6.QtCore import (
    QAbstractTableModel, QModelIndex, Qt,
    QSortFilterProxyModel,
)
from PySide6.QtGui import (
    QFont,
)
from PySide6.QtWidgets import (
    QWidget, QTreeView,
    QVBoxLayout,
)

from chromy.structs import Profile

from core.utils import sort_profiles_id_func, ProfileSortFilterProxyModel


class ProfilesModel(QAbstractTableModel):

    def __init__(self, profiles: dict[str, Profile], parent=None):
        super().__init__(parent)
        self.profiles = profiles
        self.profile_ids = list(profiles.keys())
        self.profile_ids.sort(key=sort_profiles_id_func)

        self.headers = ["ID", "名称", "邮箱"]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.profile_ids)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            col = index.column()
            profile_id = self.profile_ids[row]
            profile = self.profiles[profile_id]
            col_map = {
                0: profile.id,
                1: profile.name,
                2: profile.user_name,
            }
            return col_map[col]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[section]
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font

    def update_data(self, profiles: dict[str, Profile]):
        self.beginResetModel()

        self.profiles = profiles
        self.profile_ids = list(profiles.keys())
        self.profile_ids.sort(key=sort_profiles_id_func)

        self.endResetModel()


class TabProfiles(QWidget):

    def __init__(
            self,
            profiles: dict[str, Profile] = None,
            parent: QWidget = None
    ):
        super().__init__(parent)
        self.profiles = profiles or {}
        self.vly_m = QVBoxLayout()
        self.setLayout(self.vly_m)

        self.trv_m = QTreeView(self)
        self.trv_m.setIndentation(0)
        self.trv_m.setSortingEnabled(True)
        self.trv_m.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.vly_m.addWidget(self.trv_m)

        self.profiles_model = ProfilesModel(self.profiles, self)

        proxy_model = ProfileSortFilterProxyModel(self)
        proxy_model.setSourceModel(self.profiles_model)

        self.trv_m.setModel(proxy_model)

    def update_model(self, profiles: dict[str, Profile]):
        self.profiles = profiles
        self.profiles_model.update_data(profiles)

        self.trv_m.setColumnWidth(1, 200)
