from PySide6.QtWidgets import QMessageBox

from config.style import StyleSheet


def show_confirm_dialog(title: str, description: str, parent=None):
    confirm = QMessageBox(parent)
    confirm.setWindowTitle(title)
    confirm.setText(description)
    confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

    yes_button = confirm.button(QMessageBox.StandardButton.Yes)
    no_button = confirm.button(QMessageBox.StandardButton.No)

    if yes_button:
        yes_button.setText("Đồng ý")
    if no_button:
        no_button.setText("Không")

    confirm.setStyleSheet(StyleSheet.Q_DIALOG_CONFIRM_CSS)

    result = confirm.exec()
    if result == QMessageBox.StandardButton.Yes:
        print("Đã chọn YES")
        return True
    else:
        print("Đã chọn NO")
        return False