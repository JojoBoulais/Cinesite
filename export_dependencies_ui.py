from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Qt
import export_dependencies
import nukescripts
import nuke

class seperator(QtWidgets.QWidget):
    """Use to seperate images sequences and geo inside the dependencie container"""
    def __init__(self, title):
        super(seperator, self).__init__()
        self.setFixedSize(QtCore.QSize(1150, 45))
        self.master_layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(self.master_layout)
        self.setStyleSheet("border: 0.5px double black;" "border-radius: 6px;" "background-color:;")
        self.label = QtWidgets.QLabel(title)
        self.label.setFixedSize(QtCore.QSize(400, 30))
        self.label.setFont(QtGui.QFont("Arial", 20))
        self.master_layout.addWidget(self.label)

class dependencie_rec(QtWidgets.QWidget):
    """Dependencie rectangle inside the dependencie container"""

    def __init__(self, dependencie, parent):
        #super(dependencie_rec, self).__init__()
        QtWidgets.QWidget.__init__(self)
        self.setFixedSize(QtCore.QSize(1150, 45))
        self.master_layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(self.master_layout)
        self.setStyleSheet("border: 0.5px double black;" "border-radius: 6px;" "background-color:;")
        self.parent = parent
        self.dependencie = dependencie

        self.populate()

    def populate(self):
        """Will add labels and button to dependence rec"""
        self.node_name_label = QtWidgets.QLabel(self.dependencie.node_name)
        self.node_name_label.setFixedSize(QtCore.QSize(100, 30))
        self.node_name_label.setFont(QtGui.QFont("Arial", 10))
        self.node_name_label.setStyleSheet("border: 0px double black;" "background-color:;")

        self.path_label = QtWidgets.QLabel(self.dependencie.dependend_path)
        self.path_label.setFixedSize(QtCore.QSize(600, 30))
        #self.path_label.setFont(QtGui.QFont("Arial", 8))
        self.path_label.setStyleSheet("border: 0px double black;" "background-color:;")
        self.image_sequence_label = QtWidgets.QLabel(self.dependencie.short_file)
        self.image_sequence_label.setFixedSize(QtCore.QSize(300, 30))
        self.image_sequence_label.setStyleSheet("border: 0px double black;" "background-color:;")
        self.erase_button = QtWidgets.QPushButton("x")
        self.erase_button.setFixedSize(QtCore.QSize(30, 30))
        self.erase_button.clicked.connect(self.click_remove)
        self.erase_button.setStyleSheet("border: 0px double black;" "background-color:;")
        self.erase_button.parent = self

        self.spacer = QtWidgets.QSpacerItem(25, 0)

        self.master_layout.addWidget(self.node_name_label)
        self.master_layout.addWidget(self.path_label)
        self.master_layout.addSpacerItem(self.spacer)
        self.master_layout.addWidget(self.image_sequence_label)
        self.master_layout.addWidget(self.erase_button)

    def click_remove(self):
        """Will remove dependencies rec from parent grid widget"""
        self.close()
        self.parent.row = self.parent.row - 1
        self.parent.grid.removeWidget(self)
        self.parent.dependencies_recs.remove(self)
        self.parent.check_for_copies()

    def mousePressEvent(self, event):
        """When the dependencies rec is being click, nuke node graph will zoom on the node associated with it.

        :param event: event
        :type event: mousePressEvent
        """
        nuke.zoom(1, (self.dependencie.node['xpos'].value(), self.dependencie.node['ypos'].value()))
        self.dependencie.node.showControlPanel()


class get_dependencies_buttons(QtWidgets.QWidget):
    """Buttons from wich to get dependencie inside of nuke"""
    def __init__(self, parent):
        super(get_dependencies_buttons, self).__init__()
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.parent = parent

        self.get_all_from_script_button = QtWidgets.QPushButton("Get All From Script")
        self.get_all_from_script_button.clicked.connect(self.get_from_script)
        self.get_from_selected_button = QtWidgets.QPushButton("Get From Selected Nodes")
        self.get_from_selected_button.clicked.connect(self.get_from_selected)

        self.layout.addWidget(self.get_all_from_script_button)
        self.layout.addWidget(self.get_from_selected_button)

    def get_from_script(self):
        """Get all dependencie from current nuke script"""
        deps = export_dependencies.get_current_script_dependencies()
        self.parent.add_dependencies_to_grid(deps)

    def get_from_selected(self):
        """Will get dependencies from selected nodes (Read, ReadGeo, Camera)"""
        deps = export_dependencies.get_selected_nodes_dependencies()
        self.parent.add_dependencies_to_grid(deps)


class dependencies_container(QtWidgets.QWidget):
    """Contains dependencie recs that have been found inside specified nuke script"""
    def __init__(self, parent=None):
        super(dependencies_container, self).__init__()

        #self.setFixedSize(QtCore.QSize(500, 150))
        self.QV = QtWidgets.QVBoxLayout()
        self.setLayout(self.QV)
        self.dependencies_recs = []
        self.parent = parent
        # Legend
        self.legend_layout = QtWidgets.QHBoxLayout()
        self.legend_arrow = QtWidgets.QLabel(">")
        self.legend_arrow.setFixedSize(QtCore.QSize(50, 20))
        self.legend_arrow.state = False
        self.legend_arrow.mousePressEvent = self.click_legend_arrow
        self.green_bar = QtWidgets.QLabel("Dependencies that will be export in same subfolder as other dependencies")
        self.green_bar.setStyleSheet('background-color:green;')
        self.green_bar.setFixedSize(QtCore.QSize(500, 20))
        self.yellow_bar = QtWidgets.QLabel(
            "Dependencies that have same file as other dependencie (Will copy it only 1 time)")
        self.yellow_bar.setFixedSize(QtCore.QSize(500, 20))
        self.yellow_bar.setStyleSheet('background-color:yellow;')
        self.legend_layout.addWidget(self.legend_arrow)
        self.legend_layout.addWidget(self.green_bar)
        self.legend_layout.addWidget(self.yellow_bar)
        self.QV.addWidget(self.legend_arrow)
        self.QV.addLayout(self.legend_layout)
        self.yellow_bar.close()
        self.green_bar.close()

        #GRID AND SCROLL AREA
        self.gridFrame = QtWidgets.QFrame(self)
        self.gridFrame.setStyleSheet("border-left: 0px double black;")
        self.grid = QtWidgets.QGridLayout(self.gridFrame)
        self.grid.setHorizontalSpacing(0)
        self.grid.setVerticalSpacing(10)
        self.gridFrame.setLayout(self.grid)
        self.scrollA = QtWidgets.QScrollArea(objectName="scrollTab")
        self.scrollA.setWidget(self.gridFrame)

        self.scrollA.horizontalScrollBar().hide()
        self.scrollA.setMaximumHeight(250)
        self.scrollA.setStyleSheet('{border: 1px double black;' 'background-color:#101010;}')
        self.scrollA.setFixedSize(QtCore.QSize(1200, 500))
        self.scrollA.setWidgetResizable(True)

        self.row = 0

        self.QV.addWidget(self.scrollA)

        # CLEAR ALL BUTTON
        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.clear_all_button = QtWidgets.QPushButton("Clear All", clicked=self.clear_dependencies)
        self.clear_all_button.setFixedSize(250, 40)
        self.bottom_layout.addWidget(self.clear_all_button)
        self.spacer = QtWidgets.QSpacerItem(950, 0)
        self.bottom_layout.addSpacerItem(self.spacer)
        self.QV.addLayout(self.bottom_layout)

    def get_dependencies(self):
        """Will return dependencies recs

        :return: list of dependencies recs
        :rtype:  list
        """
        # self.dependencies.extend([dep for dep in deps if dep not in self.dependencies])
        return self.dependencies_recs

    def add_dependencies_to_grid(self, deps):
        """Will create dependencies rec out of a list of dependencies and add dependencies recs to to grid widget.

        :param deps: list of dependencies
        :type deps: list
        """
        for dep in deps:
            d = dependencie_rec(dep, self)
            self.dependencies_recs.append(d)
            self.grid.addWidget(d, self.row, 0)
            self.row += 1

            self.check_for_copies()

    def check_for_copies(self):
        """Will check if dependencies container contains dependencies that share the same location or the same file.
        If so, it will put in green those that share the same location and in yellow those that have the same file"""
        for rec in self.dependencies_recs:
            for recc in [other for other in self.dependencies_recs if other != rec]:
                if recc.dependencie.dependend_path == rec.dependencie.dependend_path:
                    rec.path_label.setStyleSheet("border: 0px double black;" "background-color:green;")
                    break
                else:
                    rec.path_label.setStyleSheet("border: 0px double black;")

            for recc in [other for other in self.dependencies_recs if other != rec]:
                if recc.dependencie.short_file == rec.dependencie.short_file:
                    rec.image_sequence_label.setStyleSheet("border: 0px double black;" "background-color:yellow;")
                    break
                else:
                    rec.image_sequence_label.setStyleSheet("border: 0px double black;")

    def remove_same_files(self):
        """Will remove from dependencies recs list those that share the same files and copy 1 of them
        (This function is not being used)"""
        for rec in self.dependencies_recs:
            for recc in [other for other in self.dependencies_recs if other != rec]:
                if recc.dependencie.short_file == rec.dependencie.short_file:
                    rec.click_remove()
                    break

    def click_legend_arrow(self, event):
        if self.legend_arrow.state == False:
            self.yellow_bar.show()
            self.green_bar.show()
            self.legend_arrow.state = True
        else:
            self.yellow_bar.close()
            self.green_bar.close()
            self.legend_arrow.state = False

    def clear_dependencies(self):
        """Will remove all dependences present in the grid"""
        for rec in self.dependencies_recs[:]:
            rec.click_remove()
        self.dependencies_recs = []
        pass

class export_dependencies_main_window(QtWidgets.QDialog):
    """Main window of export dependencies feature inside of nuke"""
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.setWindowTitle("Export Dependencies")
        self.export_to_value = ""
        self.clearFocus()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        #EXPORT TO BUTTON
        self.export_layout = QtWidgets.QHBoxLayout()
        self.export_to_line = QtWidgets.QLineEdit()
        self.export_to_button = QtWidgets.QPushButton("Select Destination")
        self.export_to_button.clicked.connect(self.select_destination)
        self.export_layout.addWidget(self.export_to_line)
        self.export_layout.addWidget(self.export_to_button)
        self.main_layout.addLayout(self.export_layout)

        self.spacer1 = QtWidgets.QSpacerItem(0, 50)
        self.main_layout.addSpacerItem(self.spacer1)

        # DEPENDENCIES GRID / GET DEPENDENCIES BUTTONS
        self.dependencies_layout = QtWidgets.QVBoxLayout()
        self.dependencies_container = dependencies_container(self)
        self.dependencies_layout.addWidget(self.dependencies_container)

        self.get_dependencies_buttons = get_dependencies_buttons(self.dependencies_container)
        self.main_layout.addWidget(self.get_dependencies_buttons)
        self.main_layout.addLayout(self.dependencies_layout)

        self.spacer2 = QtWidgets.QSpacerItem(0, 50)
        self.main_layout.addSpacerItem(self.spacer2)

        # EXPORT BUTTON
        self.export_bottom_layout = QtWidgets.QHBoxLayout()
        self.cancel_button = QtWidgets.QPushButton("Cancel", clicked=self.cancel_clicked)
        self.export_bottom_layout.addWidget(self.cancel_button)
        self.spacer3 = QtWidgets.QSpacerItem(600, 0)
        self.export_bottom_layout.addSpacerItem(self.spacer3)
        self.export_bottom_button = QtWidgets.QPushButton("EXPORT", clicked=self.export_clicked)
        self.export_bottom_layout.addWidget(self.export_bottom_button)

        self.main_layout.addLayout(self.export_bottom_layout)

    def select_destination(self):
        """Will open a file browser from wich user will select destination folder"""
        browser = QtWidgets.QFileDialog
        path = browser.getExistingDirectory().encode('ascii', 'ignore')
        self.export_to_line.setText(path)
        self.export_to_value = path

    def cancel_clicked(self):
        """Will close this widget"""
        self.close()

    def export_clicked(self):
        """Will export dependencies from dependencies container to selected destination"""
        deps = [dep.dependencie for dep in self.dependencies_container.dependencies_recs]
        export_dependencies.copie_dependencies(self.export_to_line.text() + "/", deps)
        self.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = export_dependencies_main_window()
    window.show()
    app.exec_()