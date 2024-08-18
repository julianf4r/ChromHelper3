# coding: utf8
from typing import Callable

from PySide6.QtCore import (
    QAbstractTableModel, QPoint,
    QModelIndex, Qt, QSortFilterProxyModel
)
from PySide6.QtGui import (
    QFont, QAction,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QMenu, QMessageBox,
)

from jnp3.gui import accept_warning, run_some_task
from chromy import Bookmark, Profile
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

    def update_data(self, bookmarks: dict[str, Bookmark]):
        self.beginResetModel()

        self.bookmarks = bookmarks
        self.bookmark_urls = list(self.bookmarks.keys())

        self.endResetModel()


class TabBookmarks(QWidget):

    def __init__(
            self,
            bookmarks: dict[str, Bookmark] = None,
            profiles: dict[str, Profile] = None,
            userdata_dir: str = "",
            exec_path: str = "",
            delete_func: Callable[[list[str], list[str]], None] = None,
            parent: QWidget = None
    ):
        super().__init__(parent)
        self.bookmarks = bookmarks or {}
        self.profiles = profiles or {}
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.delete_func = delete_func

        self.menu_ctx = QMenu(self)
        self.act_delete = QAction("删除", self)
        self.menu_ctx.addAction(self.act_delete)

        self.vly_m = QVBoxLayout()
        self.setLayout(self.vly_m)

        self.trv_m = QTreeView(self)
        self.trv_m.setIndentation(0)
        self.trv_m.setSortingEnabled(True)
        self.trv_m.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.trv_m.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.trv_m.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.vly_m.addWidget(self.trv_m)

        self.bookmarks_model = BookmarksModel(self.bookmarks, self)
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(self.bookmarks_model)

        self.trv_m.setModel(proxy_model)

        self.trv_m.doubleClicked.connect(self.on_trv_m_double_clicked)
        self.act_delete.triggered.connect(self.on_act_delete_triggered)
        self.trv_m.customContextMenuRequested.connect(self.on_trv_m_custom_context_menu_requested)

    def on_act_delete_triggered(self):
        urls = [index.data(Qt.ItemDataRole.UserRole)
                for index in self.trv_m.selectedIndexes()
                if index.column() == 0]
        if len(urls) == 0:
            QMessageBox.warning(self, "警告", "你没有选中任何书签。")
            return

        profile_ids = set()
        for url in urls:
            profile_ids = profile_ids.union(self.bookmarks[url].profiles.keys())

        if accept_warning(self, True, "警告",
                          f"你确定要删除这 {len(urls)} 个书签吗？"):
            return

        run_some_task("提示", "正在删除，请稍等……", self,
                      self.delete_func, urls, profile_ids)
        self.update_after_deletion()

    def on_trv_m_custom_context_menu_requested(self, pos: QPoint):
        self.menu_ctx.exec(self.trv_m.viewport().mapToGlobal(pos))

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

        ds = DaShowProfiles(self.userdata_dir, self.exec_path, self.delete_func, self)
        ds.setWindowTitle(bmk.name)
        ds.lne_mark.setText(bmk.url)
        ds.trv_p.setModel(proxy_model)

        ds.deletion_finished.connect(self.update_after_deletion)
        ds.exec()

    def update_after_deletion(self):
        self.bookmarks_model.update_data(self.bookmarks)

    def update_model(
            self,
            bookmarks: dict[str, Bookmark],
            profiles: dict[str, Profile],
            userdata_dir: str,
            exec_path: str,
            delete_func: Callable[[list[str], list[str]], None],
    ):
        self.bookmarks = bookmarks
        self.profiles = profiles
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.delete_func = delete_func
        self.bookmarks_model.update_data(bookmarks)

        self.trv_m.setColumnWidth(0, 300)
