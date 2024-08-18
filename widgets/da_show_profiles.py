# coding: utf8
from typing import Callable

from PySide6.QtCore import (
    QSize, QAbstractTableModel,
    QModelIndex, Qt, Signal,
)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit,
    QTreeView, QHBoxLayout, QPushButton,
    QAbstractItemView, QWidget, QMessageBox,
)

from jnp3.gui import accept_warning, run_some_task

from core.utils import open_profiles


class ShowProfilesModel(QAbstractTableModel):

    def __init__(self, show_profiles: list[list[str]], parent=None):
        super().__init__(parent)
        self.show_profiles = show_profiles

        self.headers = ["ID", "名称", "位置"]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.show_profiles)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.show_profiles[index.row()][index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[section]


class DaShowProfiles(QDialog):

    deletion_finished = Signal()

    def __init__(
            self,
            userdata_dir: str,
            exec_path: str,
            delete_func: Callable[[list[str], list[str]], None],
            parent: QWidget = None
    ):
        super().__init__(parent)
        self.userdata_dir = userdata_dir
        self.exec_path = exec_path
        self.delete_func = delete_func

        self.vly_m = QVBoxLayout()
        self.setLayout(self.vly_m)

        self.lne_mark = QLineEdit(self)
        self.lne_mark.setReadOnly(True)
        self.vly_m.addWidget(self.lne_mark)

        self.trv_p = QTreeView(self)
        self.trv_p.setIndentation(0)
        self.trv_p.setSortingEnabled(True)
        self.trv_p.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.trv_p.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.vly_m.addWidget(self.trv_p)

        self.hly_bot = QHBoxLayout()
        self.vly_m.addLayout(self.hly_bot)

        self.pbn_delete = QPushButton("删除所选", self)
        self.pbn_open = QPushButton("打开", self)
        self.pbn_cancel = QPushButton("取消", self)
        self.hly_bot.addWidget(self.pbn_delete)
        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_open)
        self.hly_bot.addWidget(self.pbn_cancel)

        self.pbn_cancel.clicked.connect(self.on_pbn_cancel_clicked)
        self.pbn_open.clicked.connect(self.on_pbn_open_clicked)
        self.pbn_delete.clicked.connect(self.on_pbn_delete_clicked)

    def sizeHint(self):
        return QSize(400, 360)

    def on_pbn_cancel_clicked(self):
        self.reject()

    def on_pbn_open_clicked(self):
        open_profiles(self, self.trv_p.selectedIndexes(), self.exec_path, self.userdata_dir)

    def on_pbn_delete_clicked(self):
        profile_ids_to_delete = [index.data(Qt.ItemDataRole.DisplayRole)
                                 for index in self.trv_p.selectedIndexes()
                                 if index.column() == 0]
        if len(profile_ids_to_delete) == 0:
            QMessageBox.warning(self, "警告", "你没有选中任何用户。")
            return
        if accept_warning(self, True, "警告",
                          f"你确定删除这 {len(profile_ids_to_delete)} 个吗？"):
            return

        run_some_task("提示", "正在删除，请稍等……", self,
                      self.delete_func, [self.lne_mark.text()], profile_ids_to_delete)

        self.deletion_finished.emit()
        self.accept()
