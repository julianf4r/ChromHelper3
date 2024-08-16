# coding: utf8
from PySide6.QtCore import (
    QSize, Qt, QAbstractListModel,
    QModelIndex,
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QLineEdit, QDialog, QToolButton,
)

from jnp3.gui import CardsArea
from chromy import get_browser_exec_path, get_browser_data_path

from core.utils import get_icon_path, SUPPORTED_BROWSERS


class IconListModel(QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon_names = SUPPORTED_BROWSERS.copy()

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.icon_names)

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        if role == Qt.ItemDataRole.DisplayRole:
            return self.icon_names[row]
        if role == Qt.ItemDataRole.DecorationRole:
            return QIcon(get_icon_path(self.icon_names[row]))


class DaUserDataEdit(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vly_m = QVBoxLayout()
        self.setLayout(self.vly_m)

        self.hly_icon = QHBoxLayout()
        self.hly_name = QHBoxLayout()
        self.hly_exec = QHBoxLayout()
        self.hly_data = QHBoxLayout()
        self.vly_m.addLayout(self.hly_icon)
        self.vly_m.addLayout(self.hly_name)
        self.vly_m.addLayout(self.hly_exec)
        self.vly_m.addLayout(self.hly_data)

        self.lb_icon = QLabel("图标：　　　　", self)
        self.cmbx_icons = QComboBox(self)
        self.icon_model = IconListModel(self)
        self.cmbx_icons.setModel(self.icon_model)

        self.hly_icon.addWidget(self.lb_icon)
        self.hly_icon.addWidget(self.cmbx_icons)

        self.hly_icon.addStretch(1)

        self.lb_name = QLabel("名称：　　　　", self)
        self.lne_name = QLineEdit(self)
        self.hly_name.addWidget(self.lb_name)
        self.hly_name.addWidget(self.lne_name)
        self.hly_name.addStretch(1)

        self.lb_exec = QLabel("执行文件路径：", self)
        self.lne_exec = QLineEdit(self)
        self.tbn_exec = QToolButton(self)
        self.tbn_exec.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.tbn_exec.setText("...")
        self.hly_exec.addWidget(self.lb_exec)
        self.hly_exec.addWidget(self.lne_exec)
        self.hly_exec.addWidget(self.tbn_exec)

        self.lb_data = QLabel("用户数据路径：", self)
        self.lne_data = QLineEdit(self)
        self.tbn_data = QToolButton(self)
        self.tbn_data.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.tbn_data.setText("...")
        self.hly_data.addWidget(self.lb_data)
        self.hly_data.addWidget(self.lne_data)
        self.hly_data.addWidget(self.tbn_data)

        self.hly_bot = QHBoxLayout()
        self.vly_m.addLayout(self.hly_bot)
        self.pbn_save = QPushButton("保存", self)
        self.pbn_cancel = QPushButton("取消", self)
        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_save)
        self.hly_bot.addWidget(self.pbn_cancel)

        self.vly_m.addStretch(1)

        self.pbn_save.clicked.connect(self.on_pbn_save_clicked)
        self.pbn_cancel.clicked.connect(self.on_pbn_cancel_clicked)
        self.cmbx_icons.currentIndexChanged.connect(self.on_cmbx_icons_current_index_changed)

        # 手动触发一次
        self.on_cmbx_icons_current_index_changed(0)

    def on_cmbx_icons_current_index_changed(self, index: int):
        browser = self.icon_model.icon_names[index]
        browser_path = get_browser_exec_path(browser)
        if browser_path is not None:
            self.lne_exec.setText(browser_path)
        else:
            self.lne_exec.clear()
        data_path = get_browser_data_path(browser)
        if data_path is not None:
            self.lne_data.setText(data_path)
        else:
            self.lne_data.clear()

    def sizeHint(self):
        return QSize(640, 120)

    def on_pbn_cancel_clicked(self):
        self.reject()

    def on_pbn_save_clicked(self):
        self.accept()


class WgUserDataDisplay(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vly_m = QVBoxLayout()
        self.setLayout(self.vly_m)

        self.hly_exec = QHBoxLayout()
        self.hly_data = QHBoxLayout()
        self.vly_m.addLayout(self.hly_exec)
        self.vly_m.addLayout(self.hly_data)

        self.lb_exec_title = QLabel("执行文件路径：", self)
        self.lne_exec_path = QLineEdit(self)
        self.lne_exec_path.setReadOnly(True)
        self.hly_exec.addWidget(self.lb_exec_title)
        self.hly_exec.addWidget(self.lne_exec_path)

        self.lb_data_title = QLabel("用户数据路径：", self)
        self.lne_data_path = QLineEdit(self)
        self.lne_data_path.setReadOnly(True)
        self.hly_data.addWidget(self.lb_data_title)
        self.hly_data.addWidget(self.lne_data_path)

    def set_exec_path(self, exec_path: str):
        self.lne_exec_path.setText(exec_path)

    def set_data_path(self, data_path: str):
        self.lne_data_path.setText(data_path)


class TabConfig(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.vly_m = QVBoxLayout()
        self.setLayout(self.vly_m)

        self.hly_top = QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)
        self.pbn_add = QPushButton("添加", self)
        self.hly_top.addWidget(self.pbn_add)
        self.hly_top.addStretch(1)

        self.ca_m = CardsArea(self)
        self.vly_m.addWidget(self.ca_m)

        self.pbn_add.clicked.connect(self.on_pbn_add_clicked)

    def on_pbn_add_clicked(self):
        de = DaUserDataEdit(self)
        de.setWindowTitle("添加用户数据")
        state = de.exec()
        if state == QDialog.DialogCode.Accepted:
            wg_ud = WgUserDataDisplay(self)
            wg_ud.set_exec_path(de.lne_exec.text())
            wg_ud.set_data_path(de.lne_data.text())

            self.ca_m.add_card(
                widget=wg_ud,
                title=de.lne_name.text(),
                icon=de.cmbx_icons.currentData(Qt.ItemDataRole.DecorationRole),
            )



