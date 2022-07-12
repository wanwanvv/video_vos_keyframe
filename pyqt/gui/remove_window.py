# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'remove_form.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel
import time

class MyLabel_ivs(QLabel):
    formAnno = QtCore.pyqtSignal( )  # 信号

    def __init__(self, parent=None):
        super(MyLabel_ivs, self).__init__((parent))
        self.flag = False
        self.isShow = False
        self.point_type=0 #0-左键前景点,1-右键背景点
        self.stroke={}
        self.pos_xy=[]

    def mousePressEvent(self, event):
        QLabel.mousePressEvent(self, event)
        #self.clear()
        self.stroke = {}
        self.pos_xy = []
        self.stroke['path'] = []
        # if event.button() == QtCore.Qt.LeftButton:
        #     self.point_type=1
        # elif event.button() == QtCore.Qt.RightButton:
        #     self.point_type=0
        pos_tmp=(event.x(),event.y())
        self.pos_xy.append(pos_tmp)
        self.stroke['object_id'] = 1
        self.flag=True
        self.stroke['path'].append([event.globalPos().x(), event.globalPos().y()])
        self.stroke['start_time'] = time.time()

    def mouseMoveEvent(self, event):
        QLabel.mouseMoveEvent(self, event)
        if self.flag==True:#鼠标左键按下的同时移动鼠标
            pos_tmp = (event.x(), event.y())
            self.pos_xy.append(pos_tmp)
            self.stroke['path'].append([event.globalPos().x(), event.globalPos().y()])
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        #print("paintEvent self.isShow:{}, self.flag:{}".format(self.isShow,self.flag))
        if self.flag==True:
            painter.setPen(QPen(QColor(255, 0, 0), 7))
            # if self.point_type==1:
            #     #painter.begin(self)
            #     painter.setPen(QPen(QColor(255,0,0), 7))
            # elif self.point_type==0:
            #     #painter.begin(self)
            #     painter.setPen(QPen(QColor(0,255,0), 7))
            #     #painter.end()
        if  self.isShow == True:
            if len(self.pos_xy)>1:
                point_start=self.pos_xy[0]
                for pos_tmp in self.pos_xy:
                    point_end=pos_tmp
                    painter.drawLine(point_start[0],point_start[1],point_end[0],point_end[1])
                    point_start = point_end

    def mouseReleaseEvent(self, event):
        QLabel.mouseReleaseEvent(self, event)
        #self.stroke['path'].append([event.globalPos().x(), event.globalPos().y()])
        self.stroke['end_time'] = time.time()
        if self.isShow == True:
            print("发射信号")
            self.formAnno.emit( )
        self.flag=False

    def getStrokeGlobalPos(self):
        return self.stroke

class Remove_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1200, 779)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(1, 0, 1, 1)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setTitle("")
        self.groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame = QtWidgets.QFrame(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(0, 45))
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setObjectName("frame")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        # self.commandLinkButton_return = QtWidgets.QCommandLinkButton(self.frame)
        # self.commandLinkButton_return.setFocusPolicy(Qt.NoFocus)
        # self.commandLinkButton_return.setObjectName("commandLinkButton_return")
        # self.horizontalLayout_6.addWidget(self.commandLinkButton_return)

        self.pushButton_return = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_return.sizePolicy().hasHeightForWidth())
        self.pushButton_return.setSizePolicy(sizePolicy)
        self.pushButton_return.setFocusPolicy(Qt.NoFocus)
        self.pushButton_return.setObjectName("pushButton_return")
        self.horizontalLayout_6.addWidget(self.pushButton_return)

        # self.frame_title = QtWidgets.QFrame(self.frame)
        # self.frame_title.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.frame_title.setFrameShadow(QtWidgets.QFrame.Plain)
        # self.frame_title.setObjectName("frame_title")
        # self.horizontalLayout_6.addWidget(self.frame_title)

        self.label_title = QtWidgets.QLabel(self.frame)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.horizontalLayout_6.addWidget(self.label_title)

        # self.commandLinkButton_next = QtWidgets.QCommandLinkButton(self.frame)
        # self.commandLinkButton_next.setFocusPolicy(Qt.NoFocus)
        # self.commandLinkButton_next.setObjectName("commandLinkButton_next")
        # self.horizontalLayout_6.addWidget(self.commandLinkButton_next)

        self.pushButton_next = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_next.sizePolicy().hasHeightForWidth())
        self.pushButton_next.setSizePolicy(sizePolicy)
        self.pushButton_next.setFocusPolicy(Qt.NoFocus)
        self.pushButton_next.setObjectName("pushButton_next")
        self.horizontalLayout_6.addWidget(self.pushButton_next)

        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(1, 5)
        self.horizontalLayout_6.setStretch(2, 1)
        self.verticalLayout_2.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(self.groupBox)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.frame_left = QtWidgets.QFrame(self.frame_2)
        self.frame_left.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_left.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_left.setObjectName("frame_left")
        self.gridLayout.addWidget(self.frame_left, 0, 0, 3, 1)
        self.frame_4 = QtWidgets.QFrame(self.frame_2)
        self.frame_4.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_open = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_open.setFocusPolicy(Qt.NoFocus)
        self.pushButton_open.setObjectName("pushButton_open")
        self.horizontalLayout.addWidget(self.pushButton_open)
        self.pushButton_exist = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_exist.setFocusPolicy(Qt.NoFocus)
        self.pushButton_exist.setObjectName("pushButton_exist")
        self.horizontalLayout.addWidget(self.pushButton_exist)
        self.pushButton_remove = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_remove.setFocusPolicy(Qt.NoFocus)
        self.pushButton_remove.setObjectName("pushButton_remove")
        self.horizontalLayout.addWidget(self.pushButton_remove)
        self.pushButton_out = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_out.setFocusPolicy(Qt.NoFocus)
        self.pushButton_out.setObjectName("pushButton_out")
        self.horizontalLayout.addWidget(self.pushButton_out)
        self.gridLayout.addWidget(self.frame_4, 0, 1, 1, 1)
        self.frame_right = QtWidgets.QFrame(self.frame_2)
        self.frame_right.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_right.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_right.setObjectName("frame_right")
        self.gridLayout.addWidget(self.frame_right, 0, 2, 3, 1)
        self.frame_6 = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_image = MyLabel_ivs(self.frame_6)
        #sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_image.sizePolicy().hasHeightForWidth())
        self.label_image.setSizePolicy(sizePolicy)
        #self.label_image.setMinimumSize(QtCore.QSize(854, 480))
        self.label_image.setText("")
        self.label_image.setAlignment(QtCore.Qt.AlignCenter)
        self.label_image.setObjectName("label_image")
        self.horizontalLayout_3.addWidget(self.label_image)
        self.gridLayout.addWidget(self.frame_6, 1, 1, 1, 1)
        self.frame_8 = QtWidgets.QFrame(self.frame_2)
        self.frame_8.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_8.setObjectName("frame_8")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_8)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_play = QtWidgets.QPushButton(self.frame_8)
        self.pushButton_play.setObjectName("pushButton_play")
        self.horizontalLayout_2.addWidget(self.pushButton_play)
        self.label_curr = QtWidgets.QLabel(self.frame_8)
        self.label_curr.setObjectName("label_curr")
        self.horizontalLayout_2.addWidget(self.label_curr)
        self.horizontalSlider = QtWidgets.QSlider(self.frame_8)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalSlider.sizePolicy().hasHeightForWidth())
        self.horizontalSlider.setSizePolicy(sizePolicy)
        self.horizontalSlider.setToolTipDuration(-1)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalLayout_2.addWidget(self.horizontalSlider)
        self.label_total = QtWidgets.QLabel(self.frame_8)
        self.label_total.setObjectName("label_total")
        self.horizontalLayout_2.addWidget(self.label_total)
        self.gridLayout.addWidget(self.frame_8, 2, 1, 1, 1)
        self.frame_bottom = QtWidgets.QFrame(self.frame_2)
        self.frame_bottom.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_bottom.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_bottom.setObjectName("frame_bottom")
        self.gridLayout.addWidget(self.frame_bottom, 3, 0, 1, 3)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 12)
        self.gridLayout.setColumnStretch(2, 1)
        self.gridLayout.setRowStretch(0, 2)
        self.gridLayout.setRowStretch(1, 8)
        self.gridLayout.setRowStretch(2, 2)
        self.gridLayout.setRowStretch(3, 1)
        self.verticalLayout_2.addWidget(self.frame_2)
        self.frame_3 = QtWidgets.QFrame(self.groupBox)
        self.frame_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.progressBar = QtWidgets.QProgressBar(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setMaximum(1)
        self.progressBar.setMinimum(0)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setFormat("")
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_4.addWidget(self.progressBar)
        self.verticalLayout_2.addWidget(self.frame_3)
        self.verticalLayout.addWidget(self.groupBox)

        self.pushButton_open.setFocusPolicy(Qt.NoFocus)
        self.pushButton_remove.setFocusPolicy(Qt.NoFocus)
        self.pushButton_out.setFocusPolicy(Qt.NoFocus)
        self.pushButton_exist.setFocusPolicy(Qt.NoFocus)
        self.pushButton_play.setFocusPolicy(Qt.NoFocus)
        self.horizontalSlider.setFocusPolicy(Qt.NoFocus)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", " "))
        # self.commandLinkButton_return.setText(_translate("Form", "Return"))
        # self.commandLinkButton_next.setText(_translate("Form", "Next"))
        self.pushButton_return.setText(_translate("Form", "Return"))
        self.pushButton_next.setText(_translate("Form", "Next"))
        self.pushButton_open.setText(_translate("Form", "打开视频文件"))
        self.pushButton_exist.setText(_translate("Form", "已有目标掩膜"))
        self.pushButton_remove.setText(_translate("Form", "移除目标物体"))
        self.pushButton_out.setText(_translate("Form", "导出视频文件"))
        self.pushButton_play.setText(_translate("Form", "Play"))
        self.label_curr.setText(_translate("Form", "00:00:00"))
        self.label_total.setText(_translate("Form", "00:00:00"))
        self.label_title.setText(_translate("Form", "CPNet-Inpainting"))
