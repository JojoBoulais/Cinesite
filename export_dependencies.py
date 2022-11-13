import nuke
import nukescripts
import os
import shutil
import time
import threading
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Qt

class dependencie():
    """is associated to a node that contain a file knob, the class contain the full path, the final sub folder and
    the file name"""
    def __init__(self, node):
        self.node = node
        self.node_name = node.name()

        full_file = node['file'].value()
        dependend_path = full_file.split("/")[0:-1]
        self.dependend_path = "/".join(dependend_path) + "/"
        self.subpath = full_file.split("/")[-2] + "/"
        self.short_file = full_file.split("/")[-1]


def get_current_script_dependencies():
    """Get current script dependencies. Will return a list of dependencie objects

    :return: list of dependencies
    :rtype: list
    """
    d = []
    for i in nuke.allNodes():
        if "file" not in i.knobs() or i.error():
            continue
        if i['file'].value() == "":
            continue
        if i.Class() in ["Read", "Camera2", "ReadGeo2"]:
            curr_dependencie = dependencie(i)
            d.append(curr_dependencie)

    return d


def get_selected_nodes_dependencies():
    """Get dependencies from selected nodes. Will return a list of dependencie objects

        :return: list of dependencies
        :rtype: list
        """
    d = []
    for i in nuke.selectedNodes():
        if "file" not in i.knobs() or i.error():
            continue
        if i['file'].value() == "":
            continue
        if i.Class() in ["Read", "Camera2", "ReadGeo2"]:
            curr_dependencie = dependencie(i)
            d.append(curr_dependencie)

    return d


def copie_dependencies(path_to_export, dependencies):
    """Will copie list of dependencies to the path specified by user. Dependencies that share the same base location
    will be place in the same subfolder. Only 1 copy of dependencies that share the same file will be kept to not copy
    it severals times.

    :param path_to_export: path to export to
    :type path_to_export: string
    :param dependencies: list of dependencies object
    :type dependencies: list
    """

    def copie(dependencies):
        folders_that_already_exist = [x[0] for x in os.walk(path_to_export)]

        progress_bar = nuke.ProgressTask("Copying Dependencies")


        dependencies_c = []

        # FIND MULTIPLE COPIES OF DEPENDENCIES (KEEP ONLY 1)

        for dep in dependencies:
            if dependencies_c != []:
                if dep.short_file not in [depp.short_file for depp in dependencies_c]:
                    dependencies_c.append(dep)
            else:
                dependencies_c.append(dep)

        num_dir = len(dependencies_c)

        ### COPIE
        for i, d in enumerate(dependencies_c):
            if progress_bar.isCancelled():
                break
            progress_bar.setProgress(int(100*float(i) / num_dir))
            progress_bar.setMessage(d.short_file)
            export_dir = path_to_export + d.subpath
            if os.path.exists(export_dir):
                pass
            else:
                os.mkdir(export_dir)
            files = os.listdir(d.dependend_path)
            for file in files:
                if d.short_file.split(".")[0] in file:
                    shutil.copy(d.dependend_path + file, export_dir + file)


    threading.Thread(target=copie, args=(dependencies,)).start()