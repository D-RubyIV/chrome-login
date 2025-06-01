import asyncio
import json
import os
import signal
import sys
import logging

import requests
import uvicorn
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QSettings, Qt, QThread
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QTableWidgetItem,
    QCheckBox,
    QPushButton,
    QHeaderView,
    QMenu,
    QFrame,
    QHBoxLayout
)

from api.api import api_app
from config.constant import TableHeaderLabel, Constant
from config.style import StyleSheet
from equipment.alchemy import engine, transactional
from equipment.models import BaseModel, ProfileRecord
from service.profile.profileservice import ProfileService
from utils.confirm import show_confirm_dialog
from utils.model import get_instrumented_attribute_name
from utils.string import safe_string
from utils.table import TableUtil
from utils.time import time_relative

ROOTPATH = os.getcwd()
# os.system(
#     f"pyside6-uic {os.path.join(ROOTPATH, 'resources/untitled.ui')} -o {os.path.join(ROOTPATH, 'resources/untitled.py')}"
# )
from resources.untitled import Ui_MainWindow


class ApiServerThread(QThread):
    error_occurred = QtCore.Signal(str)  # Signal to emit errors

    def __init__(self):
        super().__init__()
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        
        # Create a custom logging config for uvicorn
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "access": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr"
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                }
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO"},
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False}
            }
        }
        
        self.config = uvicorn.Config(
            api_app,
            host="localhost",
            port=5000,
            log_level="info",
            log_config=log_config
        )
        self.server = uvicorn.Server(self.config)
        self._is_running = True

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            while self._is_running:
                loop.run_until_complete(self.server.serve())
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._is_running = False
        self.server.should_exit = True
        self.wait()  # Wait for thread to finish


BaseModel.metadata.create_all(engine)


def setup_first_col_tg_table_widget(profile_object: ProfileRecord):
    # Create a QTableWidgetItem and set its name

    chk_box = QCheckBox()
    chk_box.setChecked(profile_object.is_selected)

    # Thêm checkbox vào ô trong bảng

    # Tạo QTableWidgetItem cho tên
    name_item = QTableWidgetItem(profile_object.id)
    name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

    chk_box_item = QTableWidgetItem(profile_object.id)
    chk_box_item.setFlags(
        QtCore.Qt.ItemFlag.ItemIsUserCheckable |
        QtCore.Qt.ItemFlag.ItemIsEnabled |
        QtCore.Qt.ItemFlag.ItemIsSelectable
    )
    # Set the checkbox state based on tg_object's is_selected property
    if profile_object.is_selected:
        chk_box_item.setCheckState(QtCore.Qt.CheckState.Checked)
    else:
        chk_box_item.setCheckState(QtCore.Qt.CheckState.Unchecked)

    # Attach custom data for tg_object
    chk_box_item.setData(256, profile_object)  # 256 is a custom role
    chk_box_item.setData(Qt.ItemDataRole.DisplayRole, profile_object.id)  # Correct DisplayRole value

    return chk_box_item


class Application(QtWidgets.QMainWindow, Ui_MainWindow):
    register_threads = {}

    def __init__(self):
        super(Application, self).__init__()
        self.setWindowTitle("Ghost")
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.settings = QSettings("Setting", "MyApp")

        # Initialize UI after window setup
        self.UI = Ui_MainWindow()
        self.UI.setupUi(self)

        self.UI.tableWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.UI.tableWidget.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

        self.UI.btn_create_new_profile.clicked.connect(self.on_create_profile)

        # Start API server in QThread
        self.api_thread = ApiServerThread()
        self.api_thread.error_occurred.connect(self.handle_api_error)
        self.api_thread.start()

        self.profile_service = ProfileService()
        self.load_profiles_to_table()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragPos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            if hasattr(self, 'dragPos'):
                self.move(event.globalPosition().toPoint() - self.dragPos)
                event.accept()

    def on_create_profile(self):
        requests.post(
            url="http://localhost:5000/api/v1/profiles",
            data=json.dumps({
                "raw_proxy": "",
                "profile_name": ""
            })
        )
        self.load_profiles_to_table()

    def load_profiles_to_table(self):
        def open_profile_by_id(uid: str):
            requests.get(f"http://localhost:5000/api/v1/profiles/{uid}")

        tb_object = self.UI.tableWidget
        table_util = TableUtil(
            table_object=tb_object
        )
        table_util.init_header_labels(TableHeaderLabel.header_labels_profile)
        table_util.clear_table()
        list_account_record: list[ProfileRecord] = self.profile_service.get_entities()
        for index, profile_object in enumerate(list_account_record):
            current_row = tb_object.rowCount()
            tb_object.insertRow(current_row)
            # @formatter:off
            fields = [
                (Constant.Profile.lbTableId, setup_first_col_tg_table_widget(profile_object)),
                (Constant.Profile.lbTableName, QTableWidgetItem(safe_string(profile_object.name))),
                (Constant.Profile.lbTableProfilePath, QTableWidgetItem(safe_string(profile_object.profile_path))),
                (Constant.Profile.lbTableProxy,QTableWidgetItem( safe_string(profile_object.raw_proxy))),
                (Constant.Profile.lbTableNote,QTableWidgetItem( safe_string(profile_object.raw_note))),
                (Constant.Profile.lbTableBrowserVersion, QTableWidgetItem(safe_string(profile_object.browser_version))),
                (Constant.Base.lbCreatedAt, QTableWidgetItem(time_relative(safe_string(profile_object.created_time)))),
                (Constant.Base.lbUpdatedAt, QTableWidgetItem(time_relative(safe_string(profile_object.updated_time)))),
            ]
            # @formatter:on
            for label, value in fields:
                tb_object.setItem(current_row, table_util.find_index_tbl(label), value)

            frame = QFrame()
            frame_layout = QHBoxLayout(frame)
            frame_layout.setContentsMargins(0, 0, 0, 0)

            open_push_button = QPushButton("Mở")
            open_push_button.clicked.connect(lambda: open_profile_by_id(profile_object.id))

            edit_push_button = QPushButton("Sửa")
            edit_push_button.clicked.connect(lambda: open_profile_by_id(profile_object.id))

            frame_layout.addWidget(open_push_button)
            frame_layout.addWidget(edit_push_button)

            tb_object.setCellWidget(
                current_row,
                table_util.find_index_tbl(Constant.Profile.lbTableAction),
                frame
            )
        tb_object.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def on_custom_context_menu_requested(self, pos):
        tb_object = self.UI.tableWidget

        @transactional
        def function_1():
            selected_indexes = tb_object.selectedIndexes()
            selected_rows = list(set(i.row() for i in selected_indexes))
            list_tg_object = []
            if selected_rows:
                for row in selected_rows:
                    item = tb_object.item(row, 0)
                    custom_object: ProfileRecord = item.data(256)
                    custom_object.is_selected = True
                    list_tg_object.append(custom_object)
                self.profile_service.upsert_records(
                    records=list_tg_object,
                    unique_columns=[
                        get_instrumented_attribute_name(ProfileRecord, ProfileRecord.id),
                    ],
                    update_columns=[
                        get_instrumented_attribute_name(ProfileRecord, ProfileRecord.is_selected)
                    ]
                )
                self.load_profiles_to_table()

        @transactional
        def function_2():
            selected_indexes = tb_object.selectedIndexes()
            selected_rows = list(set(i.row() for i in selected_indexes))
            list_tg_object = []
            if selected_rows:
                for row in selected_rows:
                    item = tb_object.item(row, 0)
                    custom_object = item.data(256)
                    custom_object.is_selected = False
                    list_tg_object.append(custom_object)
                self.profile_service.upsert_records(
                    records=list_tg_object,
                    unique_columns=[
                        get_instrumented_attribute_name(ProfileRecord, ProfileRecord.id),
                    ],
                    update_columns=[
                        get_instrumented_attribute_name(ProfileRecord, ProfileRecord.is_selected)
                    ]
                )
                self.load_profiles_to_table()

        @transactional
        def function_3():
            account_records: list[ProfileRecord] = self.profile_service.get_entities()
            selected_account_records: list[ProfileRecord] = [i for i in account_records if i.is_selected]

            is_confirm = show_confirm_dialog(
                description=f"Xác nhận xóa {len(selected_account_records)} bản ghi",
                title=f"Xác nhận xóa",
                parent=self
            )
            if is_confirm:
                for record in selected_account_records:
                    self.profile_service.delete_entity_by_id(
                        entity_id=record.id
                    )
                self.load_profiles_to_table()

        index = tb_object.indexAt(pos)
        if index.isValid():
            context_menu = QMenu(self)
            context_menu.setStyleSheet(StyleSheet.Q_MENU_CSS)

            tg_action_select = QAction("[1] - Chọn")
            tg_action_unselect = QAction("[2] - Hủy chọn")
            tg_action_delete = QAction("[3] - Xóa")

            context_menu.addAction(tg_action_select)
            context_menu.addAction(tg_action_unselect)
            context_menu.addAction(tg_action_delete)

            tg_action_select.triggered.connect(function_1)
            tg_action_unselect.triggered.connect(function_2)
            tg_action_delete.triggered.connect(function_3)

            context_menu.exec(tb_object.viewport().mapToGlobal(pos))

    def handle_api_error(self, error_message):
        # Handle API server errors here
        print(f"API Server Error: {error_message}")

    def closeEvent(self, event):
        # Cleanup when application is closing
        if hasattr(self, 'api_thread'):
            self.api_thread.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Initialize QApplication with sys.argv
    screen = app.primaryScreen()
    try:
        window = Application()
        window.show()
        sys.exit(app.exec())
    except SystemExit:
        os.kill(os.getpid(), signal.SIGTERM)
