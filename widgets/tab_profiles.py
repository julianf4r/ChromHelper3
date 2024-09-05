# coding: utf8
from compat import (
    Qt, QAbstractTableModel, QModelIndex, QPoint, QSize,
    QAction, QFont, QIcon,
    QMenu, QMessageBox, QTreeView, QVBoxLayout, QWidget,
)

from chromy.structs import Profile

from core.utils import (
    sort_profiles_id_func,
    ProfileSortFilterProxyModel,
    open_profiles,
    get_profile_picture,
    get_exec,
)
from .da_raw_data import DaRawData


class ProfilesModel(QAbstractTableModel):

    def __init__(self, browser: str, profiles: dict[str, Profile], parent=None):
        super().__init__(parent)
        self.browser = browser
        self.profiles = profiles
        self.profile_ids = list(profiles.keys())
        self.profile_ids.sort(key=sort_profiles_id_func)

        self.profile_pic_cache: dict[str, QIcon] = {}

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
                cache_id = f"{self.browser}!{profile_id}"
                if cache_id in self.profile_pic_cache:
                    return self.profile_pic_cache[cache_id]
                else:
                    pic = get_profile_picture(self.browser, profile)
                    self.profile_pic_cache[cache_id] = pic
                    return pic

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

        self.profile_pic_cache.clear()

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
        self.act_show_data = QAction("查看原始数据", self)
        self.menu_ctx.addAction(self.act_open)
        self.menu_ctx.addSeparator()
        self.menu_ctx.addAction(self.act_show_data)

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
        self.act_show_data.triggered.connect(self.on_act_show_data_triggered)
        self.trv_m.customContextMenuRequested.connect(self.on_trv_m_custom_context_menu_requested)

    def on_act_open_triggered(self):
        open_profiles(self, self.trv_m.selectedIndexes(), self.exec_path, self.userdata_dir)

    def on_act_show_data_triggered(self):
        profile_ids = [index.data(Qt.ItemDataRole.DisplayRole)
                       for index in self.trv_m.selectedIndexes()
                       if index.column() == 0]
        if len(profile_ids) == 0:
            QMessageBox.warning(self, "提示", "你没有选中任何用户。")
            return
        # 只取第一个用户的
        profile = self.profiles[profile_ids[0]]
        dr = DaRawData(profile.raw_data, self)
        dr.show()

    def on_trv_m_custom_context_menu_requested(self, pos: QPoint):
        get_exec(self.menu_ctx)(self.trv_m.viewport().mapToGlobal(pos))

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
