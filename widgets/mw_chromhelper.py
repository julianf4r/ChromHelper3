# coding: utf8
from logging import Logger

from compat import (
    Qt, QAbstractTableModel, QModelIndex, QPoint, QSize,
    QAction, QFont, QIcon,
    QHBoxLayout, QMainWindow, QMenu, QMessageBox, QPushButton, QTabWidget, QTreeView, QVBoxLayout, QWidget
)

from jnp3.gui import (
    StyleComboBox, HorizontalLine, DebugOutputButton,
    run_some_task, CheckUpdateButton,
)
from chromy import ChromInstance

from .tab_profiles import TabProfiles
from .tab_extensions import TabExtensions
from .tab_bookmarks import TabBookmarks
from .tab_config import TabConfig

from core.db_operations import DBManger
from core.utils import get_icon_path, get_exec


class UserDataListModel(QAbstractTableModel):

    def __init__(
            self,
            userdata_info: list[list[str]],  # [[name, type, exec, data]]
            parent: QWidget = None,
    ):
        super().__init__(parent)
        self.userdata_info = userdata_info

        self.active_name: str | None = None

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
            return self.userdata_info[row][1], self.userdata_info[row][2], self.userdata_info[row][3]
        if role == Qt.ItemDataRole.FontRole:
            if self.userdata_info[row][0] == self.active_name:
                font = QFont()
                font.setBold(True)
                return font

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

    def clear_active(self):
        self.active_name = None

    def set_active(self, index: QModelIndex):
        if index.isValid():
            self.active_name = index.data(Qt.ItemDataRole.DisplayRole)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.FontRole])


class MwChromHelper(QMainWindow):

    def __init__(
            self,
            app_name: str,
            current_version: str,
            app_dir: str,
            logger: Logger,
            parent: QWidget = None
    ):
        super().__init__(parent)
        self.logger = logger
        self.dbm = DBManger(app_dir)

        self.chrom_ins_map: dict[str, ChromInstance] = {}
        self.current_userdata_name = ""

        # =================== UI =========================
        self.setWindowIcon(QIcon(":/assets/chrom_helper_64.png"))
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)

        self.hly_main = QHBoxLayout()
        self.cw.setLayout(self.hly_main)

        self.vly_left = QVBoxLayout()
        self.hly_main.addLayout(self.vly_left)

        self.hln_1 = HorizontalLine(self)
        self.vly_left.addWidget(self.hln_1)

        self.cmbx_styles = StyleComboBox(parent=self)
        self.vly_left.addWidget(self.cmbx_styles)

        self.pbn_refresh = QPushButton("刷新当前用户数据", self)
        self.vly_left.addWidget(self.pbn_refresh)

        self.trv_left = QTreeView(self)
        self.trv_left.setMinimumWidth(100)
        self.trv_left.setIndentation(0)
        self.trv_left.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.vly_left.addWidget(self.trv_left)

        self.trv_menu_ctx = QMenu(self)
        self.act_switch = QAction("切换", self)
        self.trv_menu_ctx.addAction(self.act_switch)

        self.pbn_check_update = CheckUpdateButton(
            app_name=app_name,
            current_version=current_version,
            logger=self.logger,
            parent=self
        )
        self.vly_left.addWidget(self.pbn_check_update)

        self.pbn_debug = DebugOutputButton(logger, text="打开输出窗口", parent=self)
        self.vly_left.addWidget(self.pbn_debug)

        self.tw_right = QTabWidget(self)

        self.hly_main.addWidget(self.tw_right)
        self.hly_main.setStretchFactor(self.vly_left, 1)
        self.hly_main.setStretchFactor(self.tw_right, 5)

        # 一开始都是啥数据都没有，需要等第一次双击左侧才会加载数据
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
        self.pbn_refresh.clicked.connect(self.on_pbn_refresh_clicked)
        self.trv_left.customContextMenuRequested.connect(self.on_trv_left_custom_context_menu_requested)
        self.act_switch.triggered.connect(self.on_act_switch_triggered)

        # ================== END UI =====================

        userdata_info = self.dbm.select_all()
        self.userdata_model = UserDataListModel(userdata_info, self)
        self.trv_left.setModel(self.userdata_model)

    def update_all_data(self, chrom_ins: ChromInstance, browser: str, exec_path: str):
        self.tab_profiles.update_model(
            browser,
            chrom_ins.profiles,
            chrom_ins.userdata_dir,
            exec_path,
        )
        self.tab_extensions.update_model(
            chrom_ins.extensions,
            chrom_ins.profiles,
            chrom_ins.userdata_dir,
            exec_path,
            chrom_ins.delete_extensions,
        )
        self.tab_bookmarks.update_model(
            chrom_ins.bookmarks,
            chrom_ins.profiles,
            chrom_ins.userdata_dir,
            exec_path,
            chrom_ins.delete_bookmarks,
        )

    def _update_chrom_ins_map(self, name: str, data_path: str):
        # 这个函数不涉及 UI 操作，避免在子线程运行时出问题
        chrom_ins = ChromInstance(data_path, self.logger)
        chrom_ins.fetch_all_profiles()
        chrom_ins.fetch_extensions_from_all_profiles()
        chrom_ins.fetch_bookmarks_from_all_profiles()
        self.chrom_ins_map[name] = chrom_ins

    def update_by_one_index(self, index: QModelIndex, force: bool):
        name = index.data(Qt.ItemDataRole.DisplayRole)
        type_, exec_path, data_path = index.data(Qt.ItemDataRole.UserRole)
        if force or name not in self.chrom_ins_map:
            run_some_task("提示", "正在获取浏览器数据……", self,
                          self._update_chrom_ins_map,
                          name=name, data_path=data_path)
        self.update_all_data(self.chrom_ins_map[name], type_, exec_path)

    def on_act_switch_triggered(self):
        if len(self.trv_left.selectedIndexes()) == 0:
            QMessageBox.warning(self, "提示", "你没有选中任何浏览器。")
            return
        index = self.trv_left.selectedIndexes()[0]
        self.on_trv_left_double_clicked(index)

    def on_trv_left_custom_context_menu_requested(self, pos: QPoint):
        get_exec(self.trv_menu_ctx)(self.trv_left.viewport().mapToGlobal(pos))

    def on_trv_left_double_clicked(self, index: QModelIndex):
        self.update_by_one_index(index, force=False)

        self.userdata_model.clear_active()
        self.userdata_model.set_active(index)

    def on_tab_config_userdata_changed(self):
        self.userdata_model.update_model(self.dbm.select_all())

    def on_pbn_refresh_clicked(self):
        for r in range(self.userdata_model.rowCount()):
            index = self.userdata_model.index(r, 0)
            if index.data(Qt.ItemDataRole.DisplayRole) == self.userdata_model.active_name:
                self.update_by_one_index(index, force=True)
                return
        else:
            QMessageBox.warning(self, "警告", "没有找到激活的选项。")

    def sizeHint(self):
        return QSize(860, 640)
