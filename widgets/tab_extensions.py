# coding: utf8
from typing import Callable

from PySide6.QtCore import (
    QAbstractTableModel, QPoint,
    QModelIndex, Qt, QSortFilterProxyModel,
    QSize,
)
from PySide6.QtGui import (
    QIcon, QFont, QAction,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QMenu,
    QMessageBox,
)

from jnp3.gui import accept_warning, run_some_task
from jnp3.path import path_not_exist
from chromy import Extension, Profile
from .da_show_profiles import DaShowProfiles, ShowProfilesModel
from core.utils import (
    sort_profiles_id_func,
    ProfileSortFilterProxyModel,
    get_icon_path
)


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
                if path_not_exist(ext.icon):
                    return QIcon(get_icon_path("none"))
                else:
                    return QIcon(ext.icon)
        elif role == Qt.ItemDataRole.UserRole:
            # 任意一列都返回 id
            return ext.id

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[section]
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font

    def update_data(self, extensions: dict[str, Extension]):
        self.beginResetModel()

        self.extensions = extensions
        self.extension_ids = list(self.extensions.keys())

        self.endResetModel()


class TabExtensions(QWidget):

    def __init__(
            self,
            extensions: dict[str, Extension] = None,
            profiles: dict[str, Profile] = None,
            userdata_dir: str = "",
            exec_path: str = "",
            delete_func: Callable[[list[str], list[str]], None] = None,
            parent=None
    ):
        super().__init__(parent)
        self.extensions = extensions or {}
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
        self.trv_m.setUniformRowHeights(True)
        self.trv_m.setStyleSheet("QTreeView::item { height: 40px; }")
        self.trv_m.setIconSize(QSize(32, 32))

        self.vly_m.addWidget(self.trv_m)

        self.extensions_model = ExtensionsModel(self.extensions, self)
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(self.extensions_model)
        self.trv_m.setModel(proxy_model)

        self.trv_m.doubleClicked.connect(self.on_trv_m_double_clicked)
        self.act_delete.triggered.connect(self.on_act_delete_triggered)
        self.trv_m.customContextMenuRequested.connect(self.on_trv_m_custom_context_menu_requested)

    def on_act_delete_triggered(self):
        ext_ids = [index.data(Qt.ItemDataRole.UserRole)
                   for index in self.trv_m.selectedIndexes()
                   if index.column() == 0]
        if len(ext_ids) == 0:
            QMessageBox.warning(self, "警告", "你没有选中任何插件。")
            return

        profile_ids = set()
        for ext_id in ext_ids:
            profile_ids = profile_ids.union(self.extensions[ext_id].profiles)

        if accept_warning(self, True, "警告",
                          f"你确定要删除这 {len(ext_ids)} 个插件吗？"):
            return

        run_some_task("提示", "正在删除，请稍等……", self,
                      self.delete_func, ext_ids, profile_ids)
        self.update_after_deletion()

    def on_trv_m_custom_context_menu_requested(self, pos: QPoint):
        self.menu_ctx.exec(self.trv_m.viewport().mapToGlobal(pos))

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

        ds = DaShowProfiles(self.userdata_dir, self.exec_path, self.delete_func, self)
        ds.setWindowTitle(ext.name)
        ds.setWindowIcon(QIcon(ext.icon))
        ds.lne_mark.setText(ext.id)
        ds.trv_p.setModel(proxy_model)

        ds.deletion_finished.connect(self.update_after_deletion)
        ds.exec()

    def update_after_deletion(self):
        self.extensions_model.update_data(self.extensions)

    def update_model(
            self,
            extensions: dict[str, Extension],
            profiles: dict[str, Profile],
            userdata_dir: str,
            exec_path: str,
            delete_func: Callable[[list[str], list[str]], None]
    ):
        self.profiles = profiles
        self.extensions = extensions
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.delete_func = delete_func
        self.extensions_model.update_data(extensions)

        self.trv_m.setColumnWidth(0, 200)
