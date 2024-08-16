# coding: utf8
from PySide6.QtCore import (
    QModelIndex, QSortFilterProxyModel, Qt,
)


def sort_profiles_id_func(profile_id: str) -> int:
    if profile_id == "Default":
        return 0
    else:
        # 即便字符串不含空格，split 之后也总能有一个元素，因此索引 -1 总是可以的
        seq = profile_id.split(" ", 1)[-1]
        try:
            return int(seq)
        except ValueError:
            # if the id is weird
            return 999


class ProfileSortFilterProxyModel(QSortFilterProxyModel):

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex):
        if source_left.column() == 0 and source_right.column() == 0:
            left = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
            right = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)
            return sort_profiles_id_func(left) < sort_profiles_id_func(right)

        return super().lessThan(source_left, source_right)
