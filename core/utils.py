# coding: utf8
import time
import subprocess
from pathlib import Path
from PySide6.QtCore import (
    QModelIndex, QSortFilterProxyModel, Qt,
)
from PySide6.QtGui import (
    QRgba64, QIcon,
)
from PySide6.QtWidgets import QWidget, QMessageBox

from jnp3.path import path_not_exist
from jnp3.dict import get_with_chained_keys
from jnp3.gui import create_round_icon_from_pixmap, create_mono_icon

from chromy import Profile

from .profile_pic import get_profile_pic


SUPPORTED_BROWSERS = ["chrome", "edge", "brave", "vivaldi", "yandex", "chromium"]

icons_map = {
    "chrome": ":/assets/icons/chrome_32.png",
    "edge": ":/assets/icons/edge_32.png",
    "brave": ":/assets/icons/brave_32.png",
    "vivaldi": ":/assets/icons/vivaldi_32.png",
    "yandex": ":/assets/icons/yandex_32.png",
    "chromium": ":/assets/icons/chromium_32.png",
    "profile": ":/assets/icons/profile_32.png",
    "extension": ":/assets/icons/extension_32.png",
    "bookmark": ":/assets/icons/bookmark_32.png",
    "config": ":/assets/icons/config_32.png",
    "none": ":/assets/icons/none_128.png",

    "chrome_avatars": {
        "IDR_PROFILE_AVATAR_27": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_27.png",
        "IDR_PROFILE_AVATAR_28": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_28.png",
        "IDR_PROFILE_AVATAR_29": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_29.png",
        "IDR_PROFILE_AVATAR_30": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_30.png",
        "IDR_PROFILE_AVATAR_31": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_31.png",
        "IDR_PROFILE_AVATAR_32": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_32.png",
        "IDR_PROFILE_AVATAR_33": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_33.png",
        "IDR_PROFILE_AVATAR_34": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_34.png",
        "IDR_PROFILE_AVATAR_35": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_35.png",
        "IDR_PROFILE_AVATAR_36": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_36.png",
        "IDR_PROFILE_AVATAR_37": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_37.png",
        "IDR_PROFILE_AVATAR_38": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_38.png",
        "IDR_PROFILE_AVATAR_39": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_39.png",
        "IDR_PROFILE_AVATAR_40": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_40.png",
        "IDR_PROFILE_AVATAR_41": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_41.png",
        "IDR_PROFILE_AVATAR_42": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_42.png",
        "IDR_PROFILE_AVATAR_43": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_43.png",
        "IDR_PROFILE_AVATAR_44": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_44.png",
        "IDR_PROFILE_AVATAR_45": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_45.png",
        "IDR_PROFILE_AVATAR_46": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_46.png",
        "IDR_PROFILE_AVATAR_47": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_47.png",
        "IDR_PROFILE_AVATAR_48": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_48.png",
        "IDR_PROFILE_AVATAR_49": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_49.png",
        "IDR_PROFILE_AVATAR_50": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_50.png",
        "IDR_PROFILE_AVATAR_51": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_51.png",
        "IDR_PROFILE_AVATAR_52": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_52.png",
        "IDR_PROFILE_AVATAR_53": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_53.png",
        "IDR_PROFILE_AVATAR_54": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_54.png",
        "IDR_PROFILE_AVATAR_55": ":/assets/avatars/chrome/IDR_PROFILE_AVATAR_55.png",
    },
    "brave_avatars": {
        "IDR_PROFILE_AVATAR_26": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_26.png",
        "IDR_PROFILE_AVATAR_56": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_56.png",
        "IDR_PROFILE_AVATAR_57": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_57.png",
        "IDR_PROFILE_AVATAR_58": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_58.png",
        "IDR_PROFILE_AVATAR_59": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_59.png",
        "IDR_PROFILE_AVATAR_60": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_60.png",
        "IDR_PROFILE_AVATAR_61": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_61.png",
        "IDR_PROFILE_AVATAR_62": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_62.png",
        "IDR_PROFILE_AVATAR_63": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_63.png",
        "IDR_PROFILE_AVATAR_64": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_64.png",
        "IDR_PROFILE_AVATAR_65": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_65.png",
        "IDR_PROFILE_AVATAR_66": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_66.png",
        "IDR_PROFILE_AVATAR_67": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_67.png",
        "IDR_PROFILE_AVATAR_68": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_68.png",
        "IDR_PROFILE_AVATAR_69": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_69.png",
        "IDR_PROFILE_AVATAR_70": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_70.png",
        "IDR_PROFILE_AVATAR_71": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_71.png",
        "IDR_PROFILE_AVATAR_72": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_72.png",
        "IDR_PROFILE_AVATAR_73": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_73.png",
        "IDR_PROFILE_AVATAR_74": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_74.png",
        "IDR_PROFILE_AVATAR_75": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_75.png",
        "IDR_PROFILE_AVATAR_76": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_76.png",
        "IDR_PROFILE_AVATAR_77": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_77.png",
        "IDR_PROFILE_AVATAR_78": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_78.png",
        "IDR_PROFILE_AVATAR_79": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_79.png",
        "IDR_PROFILE_AVATAR_80": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_80.png",
        "IDR_PROFILE_AVATAR_81": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_81.png",
        "IDR_PROFILE_AVATAR_82": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_82.png",
        "IDR_PROFILE_AVATAR_83": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_83.png",
        "IDR_PROFILE_AVATAR_84": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_84.png",
        "IDR_PROFILE_AVATAR_85": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_85.png",
        "IDR_PROFILE_AVATAR_86": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_86.png",
        "IDR_PROFILE_AVATAR_87": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_87.png",
        "IDR_PROFILE_AVATAR_88": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_88.png",
        "IDR_PROFILE_AVATAR_89": ":/assets/avatars/brave/IDR_PROFILE_AVATAR_89.png",
    },
    "vivaldi_avatars": {
        "IDR_PROFILE_VIVALDI_AVATAR_0": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_0.png",
        "IDR_PROFILE_VIVALDI_AVATAR_1": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_1.png",
        "IDR_PROFILE_VIVALDI_AVATAR_2": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_2.png",
        "IDR_PROFILE_VIVALDI_AVATAR_3": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_3.png",
        "IDR_PROFILE_VIVALDI_AVATAR_4": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_4.png",
        "IDR_PROFILE_VIVALDI_AVATAR_5": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_5.png",
        "IDR_PROFILE_VIVALDI_AVATAR_6": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_6.png",
        "IDR_PROFILE_VIVALDI_AVATAR_7": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_7.png",
        "IDR_PROFILE_VIVALDI_AVATAR_8": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_8.png",
        "IDR_PROFILE_VIVALDI_AVATAR_9": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_9.png",
        "IDR_PROFILE_VIVALDI_AVATAR_10": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_10.png",
        "IDR_PROFILE_VIVALDI_AVATAR_11": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_11.png",
        "IDR_PROFILE_VIVALDI_AVATAR_12": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_12.png",
        "IDR_PROFILE_VIVALDI_AVATAR_13": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_13.png",
        "IDR_PROFILE_VIVALDI_AVATAR_14": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_14.png",
        "IDR_PROFILE_VIVALDI_AVATAR_15": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_15.png",
        "IDR_PROFILE_VIVALDI_AVATAR_16": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_16.png",
        "IDR_PROFILE_VIVALDI_AVATAR_17": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_17.png",
        "IDR_PROFILE_VIVALDI_AVATAR_18": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_18.png",
        "IDR_PROFILE_VIVALDI_AVATAR_19": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_19.png",
        "IDR_PROFILE_VIVALDI_AVATAR_20": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_20.png",
        "IDR_PROFILE_VIVALDI_AVATAR_21": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_21.png",
        "IDR_PROFILE_VIVALDI_AVATAR_22": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_22.png",
        "IDR_PROFILE_VIVALDI_AVATAR_23": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_23.png",
        "IDR_PROFILE_VIVALDI_AVATAR_24": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_24.png",
        "IDR_PROFILE_VIVALDI_AVATAR_25": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_25.png",
        "IDR_PROFILE_VIVALDI_AVATAR_26": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_26.png",
        "IDR_PROFILE_VIVALDI_AVATAR_27": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_27.png",
        "IDR_PROFILE_VIVALDI_AVATAR_28": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_28.png",
        "IDR_PROFILE_VIVALDI_AVATAR_29": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_29.png",
        "IDR_PROFILE_VIVALDI_AVATAR_30": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_30.png",
        "IDR_PROFILE_VIVALDI_AVATAR_31": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_31.png",
        "IDR_PROFILE_VIVALDI_AVATAR_32": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_32.png",
        "IDR_PROFILE_VIVALDI_AVATAR_33": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_33.png",
        "IDR_PROFILE_VIVALDI_AVATAR_34": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_34.png",
        "IDR_PROFILE_VIVALDI_AVATAR_35": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_35.png",
        "IDR_PROFILE_VIVALDI_AVATAR_36": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_36.png",
        "IDR_PROFILE_VIVALDI_AVATAR_37": ":/assets/avatars/vivaldi/IDR_PROFILE_VIVALDI_AVATAR_37.png",
    },
    "edge_avatars": {
        "IDR_PROFILE_AVATAR_20": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_20.png",
        "IDR_PROFILE_AVATAR_21": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_21.png",
        "IDR_PROFILE_AVATAR_22": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_22.png",
        "IDR_PROFILE_AVATAR_23": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_23.png",
        "IDR_PROFILE_AVATAR_24": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_24.png",
        "IDR_PROFILE_AVATAR_25": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_25.png",
        "IDR_PROFILE_AVATAR_26": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_26.png",
        "IDR_PROFILE_AVATAR_27": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_27.png",
        "IDR_PROFILE_AVATAR_28": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_28.png",
        "IDR_PROFILE_AVATAR_29": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_29.png",
        "IDR_PROFILE_AVATAR_30": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_30.png",
        "IDR_PROFILE_AVATAR_31": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_31.png",
        "IDR_PROFILE_AVATAR_32": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_32.png",
        "IDR_PROFILE_AVATAR_33": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_33.png",
        "IDR_PROFILE_AVATAR_34": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_34.png",
        "IDR_PROFILE_AVATAR_35": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_35.png",
        "IDR_PROFILE_AVATAR_36": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_36.png",
        "IDR_PROFILE_AVATAR_37": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_37.png",
        "IDR_PROFILE_AVATAR_38": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_38.png",
        "IDR_PROFILE_AVATAR_39": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_39.png",
        "IDR_PROFILE_AVATAR_40": ":/assets/avatars/edge/IDR_PROFILE_AVATAR_40.png",
    },
    "yandex_avatars": {
        "IDR_PROFILE_AVATAR_YANDEX_0": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_0.png",
        "IDR_PROFILE_AVATAR_YANDEX_1": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_1.png",
        "IDR_PROFILE_AVATAR_YANDEX_2": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_2.png",
        "IDR_PROFILE_AVATAR_YANDEX_3": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_3.png",
        "IDR_PROFILE_AVATAR_YANDEX_4": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_4.png",
        "IDR_PROFILE_AVATAR_YANDEX_5": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_5.png",
        "IDR_PROFILE_AVATAR_YANDEX_6": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_6.png",
        "IDR_PROFILE_AVATAR_YANDEX_7": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_7.png",
        "IDR_PROFILE_AVATAR_YANDEX_8": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_8.png",
        "IDR_PROFILE_AVATAR_YANDEX_9": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_9.png",
        "IDR_PROFILE_AVATAR_YANDEX_10": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_10.png",
        "IDR_PROFILE_AVATAR_YANDEX_11": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_11.png",
        "IDR_PROFILE_AVATAR_YANDEX_12": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_12.png",
        "IDR_PROFILE_AVATAR_YANDEX_13": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_13.png",
        "IDR_PROFILE_AVATAR_YANDEX_14": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_14.png",
        "IDR_PROFILE_AVATAR_YANDEX_15": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_15.png",
        "IDR_PROFILE_AVATAR_YANDEX_16": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_16.png",
        "IDR_PROFILE_AVATAR_YANDEX_17": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_17.png",
        "IDR_PROFILE_AVATAR_YANDEX_18": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_18.png",
        "IDR_PROFILE_AVATAR_YANDEX_19": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_19.png",
        "IDR_PROFILE_AVATAR_YANDEX_20": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_20.png",
        "IDR_PROFILE_AVATAR_YANDEX_21": ":/assets/avatars/yandex/IDR_PROFILE_AVATAR_YANDEX_21.png",
    },
}


def get_icon_path(icon_name: str, sub_dir: str = None) -> str:
    if sub_dir is None:
        if icon_name not in icons_map:
            icon_name = "none"
        return icons_map[icon_name]
    else:
        p = get_with_chained_keys(icons_map, [sub_dir, icon_name])
        return icons_map["none"] if p is None else p


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


def open_profiles(
        widget: QWidget,
        indexes: list[QModelIndex],
        exec_path: str,
        userdata_dir: str,
):
    if path_not_exist(exec_path):
        QMessageBox.critical(widget, "错误", "没有找到执行文件路径，请检查配置页。")
        return

    profile_ids = [index.data(Qt.ItemDataRole.DisplayRole) for index in indexes if index.column() == 0]

    cmd = rf'"{exec_path}" --user-data-dir="{userdata_dir}" --profile-directory="{{0}}"'
    for profile_id in profile_ids:
        subprocess.Popen(cmd.format(profile_id), shell=True)
        time.sleep(0.5)


def get_profile_picture(browser: str, profile: Profile) -> QIcon:
    if browser in ["chrome", "chromium"]:
        if len(profile.gaia_picture_file_name) != 0:
            profile_pic = Path(profile.profile_dir, profile.gaia_picture_file_name)
            if profile_pic.exists():
                return create_round_icon_from_pixmap(QIcon(str(profile_pic)).pixmap(96, 96), 96)
        if len(profile.avatar_icon) != 0:
            if profile.avatar_icon != "IDR_PROFILE_AVATAR_26":
                return create_round_icon_from_pixmap(
                    QIcon(get_icon_path(profile.avatar_icon, f"chrome_avatars")).pixmap(96, 96),
                    size=96
                )
        return get_profile_pic(profile.default_avatar_fill_color, profile.default_avatar_stroke_color)

    elif browser == "edge":
        if len(profile.gaia_picture_file_name) != 0:
            profile_pic = Path(profile.profile_dir, profile.gaia_picture_file_name)
            if profile_pic.exists():
                return create_round_icon_from_pixmap(QIcon(str(profile_pic)).pixmap(96, 96), 96)
        if len(profile.avatar_icon) != 0:
            return QIcon(get_icon_path(profile.avatar_icon, f"{browser}_avatars"))

    elif browser in ["brave", "vivaldi"]:
        if len(profile.avatar_icon) != 0:
            return QIcon(get_icon_path(profile.avatar_icon, f"{browser}_avatars"))

    elif browser == "yandex":
        if len(profile.avatar_icon) != 0:
            return QIcon(get_icon_path(profile.avatar_icon, f"{browser}_avatars"))

    return create_mono_icon(QRgba64.fromArgb32(4294967296 + profile.default_avatar_fill_color), "round")


class ProfileSortFilterProxyModel(QSortFilterProxyModel):

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex):
        if source_left.column() == 0 and source_right.column() == 0:
            left = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
            right = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)
            return sort_profiles_id_func(left) < sort_profiles_id_func(right)

        return super().lessThan(source_left, source_right)
