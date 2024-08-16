# coding: utf8
from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex, Qt, QSortFilterProxyModel
)
from PySide6.QtGui import (
    QIcon, QFont,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView
)

from chromy.structs import Extension
from chromy.chromi import ChromInstance
from .da_show_profiles import DaShowProfiles, ShowProfilesModel
from core.utils import sort_profiles_id_func, ProfileSortFilterProxyModel


class ExtensionsModel(QAbstractTableModel):

    def __init__(self, extensions: dict[str, Extension], parent=None):
        super().__init__(parent)
        self.extensions = extensions
        self.extension_ids = list(self.extensions.keys())
        self.headers = ["名称", "描述"]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.extension_ids)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        col = index.column()
        ext = self.extensions[self.extension_ids[row]]
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return ext.name
            if col == 1:
                return ext.description
        elif role == Qt.ItemDataRole.DecorationRole:
            if col == 0:
                return QIcon(ext.icon)
        elif role == Qt.ItemDataRole.UserRole:
            return ext.id

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[section]
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font


class TabExtensions(QWidget):

    def __init__(self, chrom_ins: ChromInstance, parent=None):
        super().__init__(parent)
        self.chrom_ins = chrom_ins
        self.extensions = self.chrom_ins.extensions
        self.profiles = self.chrom_ins.profiles

        self.vly_m = QVBoxLayout()
        self.setLayout(self.vly_m)

        self.trv_m = QTreeView(self)
        self.trv_m.setIndentation(0)
        self.trv_m.setSortingEnabled(True)
        self.trv_m.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.vly_m.addWidget(self.trv_m)

        model = ExtensionsModel(self.extensions, self)
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(model)

        self.trv_m.setModel(proxy_model)

        self.trv_m.doubleClicked.connect(self.on_trv_m_double_clicked)

    def on_trv_m_double_clicked(self):
        index = self.trv_m.selectedIndexes()[0]
        ext_id: str = index.data(Qt.ItemDataRole.UserRole)
        ext = self.extensions[ext_id]

        show_profile_ids = list(ext.profiles)
        show_profile_ids.sort(key=sort_profiles_id_func)
        show_profiles: list[list[str]] = []
        for profile_id in show_profile_ids:
            profile = self.profiles[profile_id]
            show_profiles.append([profile.id, profile.name, ""])

        model = ShowProfilesModel(show_profiles, self)
        proxy_model = ProfileSortFilterProxyModel(self)
        proxy_model.setSourceModel(model)

        ds = DaShowProfiles(self.chrom_ins.userdata_dir, self)
        ds.setWindowTitle(ext.name)
        ds.setWindowIcon(QIcon(ext.icon))
        ds.lne_mark.setText(ext.id)
        ds.trv_p.setModel(proxy_model)
        ds.exec()
