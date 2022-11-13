from PySide2 import QtWidgets
from logs import *
import os


class MainWidget(QtWidgets.QWidget):
    """User enter or browse for a .log file, information will be display inside
    QTableWidgets as QLabels"""

    def __init__(self):
        super(MainWidget, self).__init__()

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        #self.setStyleSheet("background-color: #101010")
        self.resize(750, 600)


        # Data
        self.file = ""
        self.nums = []
        self.errors = []
        self.warnings = []

        # Add main sub-widgets
        self.add_main_widgets()

    def add_main_widgets(self):

        # Select log file
        self.fileLayout = QtWidgets.QHBoxLayout()
        self.file_text = QtWidgets.QLineEdit()
        self.file_text.setPlaceholderText("Search or Enter .log file")
        self.file_button = QtWidgets.QPushButton("Browse")
        self.file_button.clicked.connect(self.click_file_button)
        self.fileLayout.addWidget(self.file_text)
        self.fileLayout.addWidget(self.file_button)

        self.mainLayout.addLayout(self.fileLayout)

        self.read_data = QtWidgets.QPushButton("Read Data")
        self.read_data.clicked.connect(self.get_data_from_file)
        self.mainLayout.addWidget(self.read_data)

        self.spacer1 = QtWidgets.QSpacerItem(0,20)
        self.mainLayout.addSpacerItem(self.spacer1)

        # ADD num widgets

        self.numsGroup = QtWidgets.QGroupBox("Time/MEM")
        self.numsLayout = QtWidgets.QVBoxLayout()

        table_len = len(self.nums)
        self.numWidget = QtWidgets.QTableWidget(table_len, 4)
        self.numWidget.setHorizontalHeaderLabels(["Time", "Mem", "WARNING", "Info"])
        self.numWidget.verticalHeader().setVisible(False)
        header = self.numWidget.horizontalHeader()
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

        self.numsLayout.addWidget(self.numWidget)
        self.numsGroup.setLayout(self.numsLayout)
        self.mainLayout.addWidget(self.numsGroup)

        self.spacer2 = QtWidgets.QSpacerItem(0,20)
        self.mainLayout.addSpacerItem(self.spacer2)

        # ADD ERROR WARNINGS

        self.errorsWarningsGroup = QtWidgets.QGroupBox("ERROR/WARNINGS")
        self.errorsWarningsLayout = QtWidgets.QVBoxLayout()

        table_len = len(self.warnings) + len(self.errors)
        self.warningsErrors = QtWidgets.QTableWidget(table_len, 2)
        self.warningsErrors.setHorizontalHeaderLabels(["Type", "Info"])
        self.warningsErrors.verticalHeader().setVisible(False)

        header = self.warningsErrors.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

        self.errorsWarningsLayout.addWidget(self.warningsErrors)
        self.errorsWarningsGroup.setLayout(self.errorsWarningsLayout)
        self.mainLayout.addWidget(self.errorsWarningsGroup)

        self.spacer3 = QtWidgets.QSpacerItem(0, 20)
        self.mainLayout.addSpacerItem(self.spacer3)

        # BOTTOM BUTTONS

        self.bottomLayout = QtWidgets.QHBoxLayout()


        self.closeButton = QtWidgets.QPushButton("Close")
        self.closeButton.clicked.connect(self.close_widget)
        self.bottomLayout.addWidget(self.closeButton)

        self.clearTableButton = QtWidgets.QPushButton("Clear")
        self.clearTableButton.clicked.connect(self.clear_tables)
        self.bottomLayout.addWidget(self.clearTableButton)
        self.mainLayout.addLayout(self.bottomLayout)

    def get_data_from_file(self):
        self.clear_tables()
        self.file = self.file_text.text()

        if os.path.exists(self.file) and self.file.split(".")[-1] == "log":
            lines = readLogFile(self.file)
            nums, errors, warnings = getTimeUsageErrors(lines)
            self.nums = nums; self.errors = errors; self.warnings = warnings
            self.add_data_to_tables()

    def click_file_button(self):
        fileBrowser = QtWidgets.QFileDialog()
        fileBrowser.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        file = fileBrowser.getOpenFileName()
        self.file_text.setText(file[0])

    def add_data_to_tables(self):

        # ADD num widgets
        for i, num in enumerate(self.nums):
            self.numWidget.insertRow(i)
            self.numWidget.setCellWidget(i, 0, QtWidgets.QLabel(" "*10 + num.time))
            self.numWidget.setCellWidget(i, 1, QtWidgets.QLabel(" "*10 + num.mem))
            if num.warning:
                self.numWidget.setCellWidget(i, 2, QtWidgets.QLabel(" " * 10 + "WARNING"))
            else:
                self.numWidget.setCellWidget(i, 2, QtWidgets.QLabel(" " * 10 + ""))
            self.numWidget.setCellWidget(i, 3, QtWidgets.QLabel(" "*10 + num.info))

        # ADD ERROR WARNINGS

        warningErrors = self.warnings + self.errors

        for i, wE in enumerate(warningErrors):
            self.warningsErrors.insertRow(i)
            if isinstance(wE, Warning):
                self.warningsErrors.setCellWidget(i, 0, QtWidgets.QLabel(" "*10 + "WARNING"))
            else:
                self.warningsErrors.setCellWidget(i, 0, QtWidgets.QLabel(" " * 10 + "ERROR"))
            self.warningsErrors.setCellWidget(i, 1, QtWidgets.QLabel(" "*10 + wE.info))

    def clear_tables(self):
        while(self.numWidget.rowCount() > 0):
            self.numWidget.removeRow(0)

        while (self.warningsErrors.rowCount() > 0):
            self.warningsErrors.removeRow(0)
        self.errors = []
        self.warnings = []

    def close_widget(self):
        self.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWidget()
    window.show()
    app.exec_()
