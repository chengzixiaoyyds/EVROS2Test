# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LightControl.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QSlider, QStatusBar,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(896, 667)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.openButton = QPushButton(self.centralwidget)
        self.openButton.setObjectName(u"openButton")
        self.openButton.setGeometry(QRect(120, 180, 141, 51))
        font = QFont()
        font.setPointSize(15)
        self.openButton.setFont(font)
        self.closeButton = QPushButton(self.centralwidget)
        self.closeButton.setObjectName(u"closeButton")
        self.closeButton.setGeometry(QRect(120, 250, 141, 51))
        self.closeButton.setFont(font)
        self.transmitButton = QPushButton(self.centralwidget)
        self.transmitButton.setObjectName(u"transmitButton")
        self.transmitButton.setGeometry(QRect(120, 320, 141, 51))
        self.transmitButton.setFont(font)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(240, 30, 421, 111))
        font1 = QFont()
        font1.setPointSize(25)
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignCenter)
        self.lightSlider = QSlider(self.centralwidget)
        self.lightSlider.setObjectName(u"lightSlider")
        self.lightSlider.setGeometry(QRect(340, 190, 351, 31))
        self.lightSlider.setMaximum(100)
        self.lightSlider.setOrientation(Qt.Horizontal)
        self.gpioLabel = QLabel(self.centralwidget)
        self.gpioLabel.setObjectName(u"gpioLabel")
        self.gpioLabel.setGeometry(QRect(340, 250, 321, 61))
        self.gpioLabel.setFont(font)
        self.sliderLabel = QLabel(self.centralwidget)
        self.sliderLabel.setObjectName(u"sliderLabel")
        self.sliderLabel.setGeometry(QRect(710, 190, 121, 31))
        self.sliderLabel.setFont(font)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 896, 28))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.openButton.setText(QCoreApplication.translate("MainWindow", u"\u5f00", None))
        self.closeButton.setText(QCoreApplication.translate("MainWindow", u"\u5173", None))
        self.transmitButton.setText(QCoreApplication.translate("MainWindow", u"\u53cd\u8f6c", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u5c0f\u706f\u63a7\u5236\u4e0e\u5f15\u811a\u4fe1\u606f\u663e\u793a", None))
        self.gpioLabel.setText(QCoreApplication.translate("MainWindow", u"\u5f15\u811a\u7535\u5e73\uff1a", None))
        self.sliderLabel.setText(QCoreApplication.translate("MainWindow", u"0", None))
    # retranslateUi

