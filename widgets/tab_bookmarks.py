# coding: utf8
from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex, Qt, QSortFilterProxyModel
)
from PySide6.QtGui import (
    QFont,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView
)

from chromy.structs import Bookmark
from chromy.chromi import ChromInstance
from core.utils import sort_profiles_id_func, ProfileSortFilterProxyModel
from .da_show_profiles import DaShowProfiles, ShowProfilesModel


class BookmarksModel(QAbstractTableModel):

    def __init__(self, bookmarks: dict[str, Bookmark], parent=None):
        super().__init__(parent)
        self.bookmarks = bookmarks
        self.bookmark_urls = list(self.bookmarks.keys())

        self.headers = ["名称", "URL"]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.bookmark_urls)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        col = index.column()
        bmk = self.bookmarks[self.bookmark_urls[row]]
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return bmk.name
            if col == 1:
                return bmk.url
        elif role == Qt.ItemDataRole.UserRole:
            return bmk.url

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[section]
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font


class TabBookmarks(QWidget):

    def __init__(self, chrom_ins: ChromInstance, parent=None):
        super().__init__(parent)
        self.chrom_ins = chrom_ins
        self.bookmarks = self.chrom_ins.bookmarks
        self.profiles = self.chrom_ins.profiles

        self.vly_m = QVBoxLayout()
        self.setLayout(self.vly_m)

        self.trv_m = QTreeView(self)
        self.trv_m.setIndentation(0)
        self.trv_m.setSortingEnabled(True)
        self.trv_m.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.vly_m.addWidget(self.trv_m)

        model = BookmarksModel(self.bookmarks, self)
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(model)

        self.trv_m.setModel(proxy_model)

        self.trv_m.doubleClicked.connect(self.on_trv_m_double_clicked)

    def on_trv_m_double_clicked(self):
        index = self.trv_m.selectedIndexes()[0]
        url: str = index.data(Qt.ItemDataRole.UserRole)
        bmk = self.bookmarks[url]

        show_profile_ids = list(bmk.profiles.keys())
        show_profile_ids.sort(key=sort_profiles_id_func)
        show_profiles: list[list[str]] = []
        for profile_id in show_profile_ids:
            profile = self.profiles[profile_id]
            show_profiles.append([profile.id, profile.name, bmk.profiles[profile_id]])

        model = ShowProfilesModel(show_profiles, self)
        proxy_model = ProfileSortFilterProxyModel(self)
        proxy_model.setSourceModel(model)

        ds = DaShowProfiles(self.chrom_ins.userdata_dir, self)
        ds.setWindowTitle(bmk.name)
        ds.lne_mark.setText(bmk.url)
        ds.trv_p.setModel(proxy_model)
        ds.exec()
