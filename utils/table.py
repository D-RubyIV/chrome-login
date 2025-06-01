from typing import List

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class TableUtil:
    def __init__(self, table_object: QTableWidget):
        self.table_object = table_object

    def clear_table(self):
        self.table_object.setRowCount(0)

    def insert_row(self):
        row_count = self.table_object.rowCount()
        self.table_object.insertRow(row_count)

    def init_header_labels(self, header_labels: List[str]):
        self.table_object.setColumnCount(len(header_labels))
        self.table_object.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_object.setHorizontalHeaderLabels(header_labels)
        self.table_object.horizontalHeader().setSectionsMovable(True)
        self.table_object.setRowCount(0)

    def get_list_data(self, column_index):
        column_data = []
        for row in range(self.table_object.rowCount()):
            item = self.table_object.item(row, column_index)
            if item:
                column_data.append(item.text())
        return column_data

    def find_index_tbl(self, column_name):
        count_hor = self.table_object.horizontalHeader().count()
        for index in range(count_hor):
            if str(self.table_object.horizontalHeaderItem(index).data(0)) == column_name:
                return index
        return None

    def update_cell(self, row_position: int, column_name: str, item: QTableWidgetItem):
        self.table_object.setItem(row_position, self.find_index_tbl(column_name), item)