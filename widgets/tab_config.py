# coding: utf8
import os
import sys
from pathlib import Path

from compat import (
    Qt, QAbstractListModel, QModelIndex, QSize, Signal,
    QIcon,
    QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from jnp3.gui import CardsArea, Card, accept_warning
from jnp3.gui.misc import get_exec
from chromy import get_browser_exec_path, get_browser_data_path

from core.utils import get_icon_path, SUPPORTED_BROWSERS
from core.db_operations import DBManger


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

    def __init__(self, exists_names: list[str], parent: QWidget = None):
        super().__init__(parent)
        self.exists_names = exists_names

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
        self.pbn_exec = QPushButton("选择", self)
        self.hly_exec.addWidget(self.lb_exec)
        self.hly_exec.addWidget(self.lne_exec)
        self.hly_exec.addWidget(self.pbn_exec)

        self.lb_data = QLabel("用户数据路径：", self)
        self.lne_data = QLineEdit(self)
        self.pbn_data = QPushButton("选择", self)
        self.hly_data.addWidget(self.lb_data)
        self.hly_data.addWidget(self.lne_data)
        self.hly_data.addWidget(self.pbn_data)

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
        self.pbn_exec.clicked.connect(self.on_pbn_exec_clicked)
        self.pbn_data.clicked.connect(self.on_pbn_data_clicked)

        # 手动触发一次
        self.on_cmbx_icons_current_index_changed(0)

    def on_cmbx_icons_current_index_changed(self, index: int):
        browser = self.icon_model.icon_names[index]
        browser_path = get_browser_exec_path(browser)
        if browser_path is not None:
            self.lne_exec.setText(browser_path)
        else:
            self.lne_exec.clear()
        # 如果真的要添加，那肯定是除了默认位置之外的，所以这里就不填充了
        # 因为默认的位置可以在初始化时自动填充，如果默认的没了，就重置数据库吧

    def on_pbn_exec_clicked(self):
        browser = self.cmbx_icons.currentData(Qt.ItemDataRole.DisplayRole)
        exec_path = get_browser_exec_path(browser)
        if exec_path is None:
            p = os.path.expanduser("~")
        else:
            p = str(Path(exec_path).parent)
        filename, _ = QFileDialog.getOpenFileName(self, "打开执行文件", p)  # type: (str, str)
        if len(filename) == 0:
            return

        # MacOS 的执行文件只通过 QFileDialog 选不到，所以手动加
        if sys.platform == "darwin":
            filename_p = Path(filename)
            if filename_p.is_dir() and filename.endswith(".app"):
                name = filename_p.stem
                filename = str(filename_p / "Contents" / "MacOS" / name)

        self.lne_exec.setText(filename)

    def on_pbn_data_clicked(self):
        browser = self.cmbx_icons.currentData(Qt.ItemDataRole.DisplayRole)
        data_path = get_browser_data_path(browser)
        if data_path is None:
            d = os.path.expanduser("~")
        else:
            d = str(Path(data_path).parent)
        dirname = QFileDialog.getExistingDirectory(self, "打开用户数据目录", d)
        if len(dirname) == 0:
            return

        self.lne_data.setText(dirname)

    def sizeHint(self):
        return QSize(640, 120)

    def on_pbn_cancel_clicked(self):
        self.reject()

    def on_pbn_save_clicked(self):
        if len(self.lne_name.text()) == 0:
            QMessageBox.critical(self, "错误", "名称不能为空！")
            return
        if len(self.lne_data.text()) == 0:
            QMessageBox.critical(self, "错误", "用户路径不能为空！")
            return
        if accept_warning(self, len(self.lne_exec.text()) == 0, "警告",
                          "如果执行文件路径为空，不影响查看，但无法打开浏览器窗口，要继续吗？"):
            return

        if self.lne_name.text() in self.exists_names:
            QMessageBox.critical(self, "错误", "该名称已存在，请更换一个。")
            return

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

    userdata_changed = Signal()

    def __init__(
            self,
            dbm: DBManger,
            parent: QWidget = None,
    ):
        super().__init__(parent)
        self.dbm = dbm
        # 这里无所谓，后面 reset 的时候会填充这个数据，所以此时为空就行
        self.userdata_info = []  # [[name, type, exec, data]]
        self.vly_m = QVBoxLayout()
        self.setLayout(self.vly_m)

        self.hly_top = QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)
        self.pbn_add = QPushButton("添加", self)
        self.hly_top.addWidget(self.pbn_add)
        self.hly_top.addStretch(1)
        self.pbn_reset = QPushButton("重置", self)
        self.hly_top.addWidget(self.pbn_reset)

        self.ca_m = CardsArea(self)
        self.vly_m.addWidget(self.ca_m)

        self.pbn_add.clicked.connect(self.on_pbn_add_clicked)
        self.pbn_reset.clicked.connect(self.on_pbn_reset_clicked)
        self.ca_m.card_removed.connect(self.on_card_removed)

        # 这个要在最后，第一次填充也相当于重置
        self.reset_cards(is_init=True)

    def on_pbn_add_clicked(self):
        exists_names = [c.title for c in self.ca_m.cards]
        de = DaUserDataEdit(exists_names, self)
        de.setWindowTitle("添加用户数据")
        state = get_exec(de)()
        if state == QDialog.DialogCode.Accepted:
            wg_ud = WgUserDataDisplay(self)
            name = de.lne_name.text()
            type_ = de.cmbx_icons.currentData(Qt.ItemDataRole.DisplayRole)  # 这里跟显示名称一样
            exec_path = de.lne_exec.text()
            data_path = de.lne_data.text()

            wg_ud.set_exec_path(exec_path)
            wg_ud.set_data_path(data_path)

            self.ca_m.add_card(
                widget=wg_ud,
                title=name,
                icon=de.cmbx_icons.currentData(Qt.ItemDataRole.DecorationRole),
            )

            self.dbm.insert_one(name, type_, exec_path, data_path)
            self.userdata_changed.emit()

    def on_pbn_reset_clicked(self):
        # 下面的函数会触发信号，所以这里就不触发了
        self.reset_cards()

    def on_card_removed(self, card: Card):
        self.dbm.delete_one(card.title)
        self.userdata_changed.emit()

    def reset_cards(self, is_init: bool = False):
        # 清空卡片
        while len(self.ca_m.cards) > 0:
            card = self.ca_m.cards[-1]
            # 这里可能每移除一次就会触发一次信号，但是因为总量不会大，就这样吧
            self.ca_m.remove_card(card)

        # 如果是打开软件，就不重置，因为还会想保留上次的路径
        if not is_init:
            self.dbm.reset()
        # 填充数据
        self.userdata_info = self.dbm.select_all()
        # 填充卡片
        for userdata in self.userdata_info:
            wg_ud = WgUserDataDisplay(self)
            wg_ud.set_exec_path(userdata[2])
            wg_ud.set_data_path(userdata[3])

            self.ca_m.add_card(
                widget=wg_ud,
                title=userdata[0],
                icon=QIcon(get_icon_path(userdata[1])),
            )

        self.userdata_changed.emit()
