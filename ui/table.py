# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'table.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem

from resources import resource_path



class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self):
        """Метод инициализации интерфейса."""
        super().__init__()
        self.setupUi(self)
    
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(900, 500)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.table_zoom = QtWidgets.QGraphicsView(Dialog)
        self.table_zoom.setGeometry(QtCore.QRect(10, 10, 731, 561))
        self.table_zoom.setStyleSheet("    border-style: outset;\n"
"    border-width: 2px;\n"
"    border-radius: 10px;\n"
"    border-color: #828790;")
        self.table_zoom.setObjectName("table_zoom")
        self.gridLayout.addWidget(self.table_zoom, 0, 0, 1, 1)
        
        pixmap = QPixmap()
        pixmap.load(resource_path('img/armature_table.jpg'))
        self.scene_table = QGraphicsScene(self)
        item_table = QGraphicsPixmapItem(pixmap)
        self.scene_table.addItem(item_table)
        self.table_zoom.setScene(self.scene_table)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        
    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        self.table_zoom.fitInView(self.scene_table.itemsBoundingRect(), Qt.KeepAspectRatio)
        return super().resizeEvent(e)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle("Сортамент арматуры")