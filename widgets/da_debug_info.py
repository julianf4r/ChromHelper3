# coding: utf8
# 部分代码来自 ChatGPT
import sys
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QVBoxLayout, QTextEdit, QDialog
)


# 全局的输出缓存，用于存储所有输出信息
output_cache = []


# 自定义类，用于将标准输出重定向到缓存和 QTextEdit
class EmittingStream:
    def __init__(self, text_edit=None):
        self.text_edit = text_edit

    def write(self, text: str):
        global output_cache
        text = text.strip()
        output_cache.append(text)  # 将输出内容存储到缓存中
        if self.text_edit:  # 如果 QTextEdit 存在，则将内容追加到其中
            self.text_edit.append(text)

    def flush(self):
        pass  # 对于文本控件，不需要实现 flush


# 非模态窗口类，用于显示输出信息
class DaDebugInfo(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输出窗口")

        # 创建 QTextEdit 控件用于显示输出
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)

        # 布局
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.text_edit)

        # 将缓存中的内容添加到 QTextEdit 中
        self.load_previous_output()

    def sizeHint(self):
        return QSize(600, 300)

    def load_previous_output(self):
        """将之前缓存的输出加载到 QTextEdit 中"""
        for text in output_cache:
            self.text_edit.append(text)

    # 将输出重定向到窗口的 QTextEdit 控件
    def redirect_output(self):
        sys.stdout = EmittingStream(self.text_edit)
        sys.stderr = EmittingStream(self.text_edit)
