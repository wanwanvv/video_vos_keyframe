# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bubbleNets_form.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!
from PyQt5.QtCore import Qt
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel
import time

class MyLabel_deepGrab(QLabel):
    formAnno = QtCore.pyqtSignal()  # 信号
    def __init__(self, parent=None):
        super(MyLabel_deepGrab, self).__init__((parent))
        self.x0=0
        self.y0=0
        self.x1=0
        self.y1=0
        self.pos0=None
        self.pos1=None
        self.flag=False
        self.isShow=False

    def paintEvent(self, event):
        super().paintEvent(event)
        rect=QRect(self.x0,self.y0,abs(self.x1-self.x0),abs(self.y1-self.y0))
        painter=QPainter(self)
        painter.setPen(QPen(Qt.red,3,Qt.SolidLine))
        if self.isShow==True:
            painter.drawEllipse(rect)

    def mousePressEvent(self, event):
        QLabel.mousePressEvent(self,event)
        self.flag=True
        self.pos0=event.globalPos()
        self.x0=event.x()
        self.y0=event.y()

    def mouseMoveEvent(self, event):
        QLabel.mouseMoveEvent(self,event)
        if self.flag:
            self.pos1 = event.globalPos()
            self.x1=event.x()
            self.y1=event.y()
            self.update()

    def mouseReleaseEvent(self, event):
        QLabel.mouseReleaseEvent(self,event)
        self.flag=False
        self.isShow = False
        self.formAnno.emit()

    def getRectGlobalPos(self):
        #返回绝对坐标
        poses=[(self.pos0.x(),self.pos0.y())]
        poses.append((self.pos1.x(),self.pos1.y()))
        return poses

class MyLabel_ivs(QLabel):
    formAnno = QtCore.pyqtSignal(int)  # 信号

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
        if event.button() == QtCore.Qt.LeftButton:
            self.point_type=1
        elif event.button() == QtCore.Qt.RightButton:
            self.point_type=0
        pos_tmp=(event.x(),event.y())
        self.pos_xy.append(pos_tmp)
        self.stroke['object_id'] = self.point_type
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
            if self.point_type==1:
                #painter.begin(self)
                painter.setPen(QPen(QColor(255,0,0), 7))
            elif self.point_type==0:
                #painter.begin(self)
                painter.setPen(QPen(QColor(0,255,0), 7))
                #painter.end()
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
            self.formAnno.emit(self.point_type)
        self.flag=False

    def getStrokeGlobalPos(self):
        return self.stroke

class MyLabel_inteSeg(QLabel):
    formAnno = QtCore.pyqtSignal(int)  # 信号

    def __init__(self, parent=None):
        super(MyLabel_inteSeg, self).__init__((parent))
        self.flag = False
        self.isShow = False
        self.point_type=0 #0-左键前景点,1-右键背景点
        self.clk_pos=None
        self.x=None
        self.y=None

    def mousePressEvent(self, event):
        QLabel.mousePressEvent(self, event)
        #self.clear()
        if event.buttons() == QtCore.Qt.LeftButton:
            print("左键按下")
            self.point_type=0
        elif event.buttons() == QtCore.Qt.RightButton:
            print("右键按下")
            self.point_type=1
        self.clk_pos = event.globalPos()
        self.x = event.x()
        self.y = event.y()
        if self.isShow==True:
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter()
        print("paintEvent self.isShow:{}".format(self.isShow))
        if self.isShow==True:
            if self.point_type==0:
                painter.begin(self)
                painter.setPen(QPen(QColor(255,0,0), 7))
                painter.drawPoint(self.x,self.y)
                painter.end()
            elif self.point_type==1:
                painter.begin(self)
                painter.setPen(QPen(QColor(0,255,0), 7))
                painter.drawPoint(self.x,self.y)
                painter.end()

    def mouseReleaseEvent(self, event):
        QLabel.mouseReleaseEvent(self, event)
        if self.isShow == True:
            print("发射信号")
            self.formAnno.emit(self.point_type)
        #self.isShow = False

    def getPointGlobalPos(self):
        return self.clk_pos

class MyLabel(QLabel):
    formAnno = QtCore.pyqtSignal()  # 信号
    def __init__(self, parent=None):
        super(MyLabel, self).__init__((parent))
        self.x0=0
        self.y0=0
        self.x1=0
        self.y1=0
        self.pos0=None
        self.pos1=None
        self.flag=False
        self.isShow=False

    def paintEvent(self, event):
        super().paintEvent(event)
        rect=QRect(self.x0,self.y0,abs(self.x1-self.x0),abs(self.y1-self.y0))
        painter=QPainter(self)
        painter.setPen(QPen(Qt.red,3,Qt.SolidLine))
        if self.isShow==True:
            painter.drawRect(rect)
        # qp.begin(self)
        # qp.end()

    def mousePressEvent(self, event):
        QLabel.mousePressEvent(self,event)
        self.flag=True
        self.pos0=event.globalPos()
        self.x0=event.x()
        self.y0=event.y()

    def mouseMoveEvent(self, event):
        QLabel.mouseMoveEvent(self,event)
        if self.flag:
            self.pos1 = event.globalPos()
            self.x1=event.x()
            self.y1=event.y()
            self.update()

    def mouseReleaseEvent(self, event):
        QLabel.mouseReleaseEvent(self,event)
        self.flag=False
        self.isShow = False
        self.formAnno.emit()

    def getRectGlobalPos(self):
        #返回绝对坐标
        poses=[(self.pos0.x(),self.pos0.y())]
        poses.append((self.pos1.x(),self.pos1.y()))
        return poses

class bubbleNets_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1200, 800)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_return = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_return.sizePolicy().hasHeightForWidth())
        self.pushButton_return.setSizePolicy(sizePolicy)
        self.pushButton_return.setObjectName("pushButton_return")
        self.horizontalLayout.addWidget(self.pushButton_return)
        self.label_title = QtWidgets.QLabel(self.frame)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.horizontalLayout.addWidget(self.label_title)
        self.pushButton_next = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_next.sizePolicy().hasHeightForWidth())
        self.pushButton_next.setSizePolicy(sizePolicy)
        self.pushButton_next.setObjectName("pushButton_next")
        self.horizontalLayout.addWidget(self.pushButton_next)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 5)
        self.horizontalLayout.setStretch(2, 1)
        self.verticalLayout.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(Form)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_open = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_open.setObjectName("pushButton_open")
        self.horizontalLayout_2.addWidget(self.pushButton_open)
        self.label_model = QtWidgets.QLabel(self.frame_2)
        self.label_model.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_model.setObjectName("label_model")
        self.horizontalLayout_2.addWidget(self.label_model)
        self.comboBox_model = QtWidgets.QComboBox(self.frame_2)
        self.comboBox_model.setCurrentText("")
        self.comboBox_model.setObjectName("comboBox_model")
        self.horizontalLayout_2.addWidget(self.comboBox_model)
        self.label_iter = QtWidgets.QLabel(self.frame_2)
        self.label_iter.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_iter.setObjectName("label_iter")
        self.horizontalLayout_2.addWidget(self.label_iter)
        self.spinBox_iter = QtWidgets.QSpinBox(self.frame_2)
        self.spinBox_iter.setObjectName("spinBox_iter")
        self.spinBox_iter.setRange(1, 500)
        self.spinBox_iter.setSingleStep(1)
        self.spinBox_iter.setValue(1)
        self.horizontalLayout_2.addWidget(self.spinBox_iter)
        self.pushButton_compute = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_compute.setObjectName("pushButton_compute")
        self.horizontalLayout_2.addWidget(self.pushButton_compute)
        self.pushButton_showbubble = QtWidgets.QPushButton(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_showbubble.sizePolicy().hasHeightForWidth())
        self.pushButton_showbubble.setSizePolicy(sizePolicy)
        self.pushButton_showbubble.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton_showbubble.setObjectName("pushButton_showbubble")
        self.horizontalLayout_2.addWidget(self.pushButton_showbubble)
        self.textBrowser = QtWidgets.QTextBrowser(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setMinimumSize(QtCore.QSize(200, 10))
        self.textBrowser.setObjectName("textBrowser")
        self.horizontalLayout_2.addWidget(self.textBrowser)
        self.horizontalLayout_2.setStretch(0, 3)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 2)
        self.horizontalLayout_2.setStretch(3, 1)
        self.horizontalLayout_2.setStretch(4, 2)
        self.horizontalLayout_2.setStretch(5, 3)
        self.horizontalLayout_2.setStretch(6, 3)
        self.horizontalLayout_2.setStretch(7, 5)
        self.verticalLayout.addWidget(self.frame_2)
        self.frame_3 = QtWidgets.QFrame(Form)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.frame_4 = QtWidgets.QFrame(self.frame_3)
        self.frame_4.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.toolButton_exist = QtWidgets.QToolButton(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_exist.sizePolicy().hasHeightForWidth())
        self.toolButton_exist.setSizePolicy(sizePolicy)
        self.toolButton_exist.setAutoFillBackground(False)
        self.toolButton_exist.setObjectName("toolButton_exist")
        self.verticalLayout_2.addWidget(self.toolButton_exist)
        self.toolButton_start = QtWidgets.QToolButton(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_start.sizePolicy().hasHeightForWidth())
        self.toolButton_start.setSizePolicy(sizePolicy)
        self.toolButton_start.setObjectName("toolButton_start")
        self.verticalLayout_2.addWidget(self.toolButton_start)

        self.toolButton_restart = QtWidgets.QToolButton(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_restart.sizePolicy().hasHeightForWidth())
        self.toolButton_restart.setSizePolicy(sizePolicy)
        self.toolButton_restart.setObjectName("toolButton_restart")
        self.verticalLayout_2.addWidget(self.toolButton_restart)
        self.toolButton_finish = QtWidgets.QToolButton(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_finish.sizePolicy().hasHeightForWidth())
        self.toolButton_finish.setSizePolicy(sizePolicy)
        self.toolButton_finish.setObjectName("toolButton_finish")
        self.verticalLayout_2.addWidget(self.toolButton_finish)
        self.toolButton_save = QtWidgets.QToolButton(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_save.sizePolicy().hasHeightForWidth())
        self.toolButton_save.setSizePolicy(sizePolicy)
        self.toolButton_save.setObjectName("toolButton_save")
        self.verticalLayout_2.addWidget(self.toolButton_save)
        self.horizontalLayout_3.addWidget(self.frame_4)
        self.frame_5 = QtWidgets.QFrame(self.frame_3)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.image = MyLabel(self.frame_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())
        self.image.setSizePolicy(sizePolicy)
        self.image.setMinimumSize(QtCore.QSize(0, 0))
        self.image.setText("")
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.image.setObjectName("image")
        self.horizontalLayout_5.addWidget(self.image)
        self.frame_7 = QtWidgets.QFrame(self.frame_5)
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_7.setObjectName("frame_7")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame_7)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_result = QtWidgets.QLabel(self.frame_7)
        self.label_result.setText("")
        self.label_result.setAlignment(QtCore.Qt.AlignCenter)
        self.label_result.setObjectName("label_result")
        self.verticalLayout_6.addWidget(self.label_result)
        self.groupBox = QtWidgets.QGroupBox(self.frame_7)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.scrollArea = QtWidgets.QScrollArea(self.groupBox)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 170, 181))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setContentsMargins(9, 0, 9, 0)
        self.gridLayout.setHorizontalSpacing(5)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_resize = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_resize.setAlignment(QtCore.Qt.AlignCenter)
        self.label_resize.setObjectName("label_resize")
        self.gridLayout.addWidget(self.label_resize, 0, 0, 1, 1)
        self.doubleSpinBox_resize = QtWidgets.QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox_resize.setObjectName("doubleSpinBox_resize")
        self.doubleSpinBox_resize.setRange(0.1,2)
        self.doubleSpinBox_resize.setSingleStep(0.1)
        self.doubleSpinBox_resize.setValue(1.0)
        self.gridLayout.addWidget(self.doubleSpinBox_resize, 0, 1, 1, 1)
        self.label_shape = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_shape.setAlignment(QtCore.Qt.AlignCenter)
        self.label_shape.setObjectName("label_shape")
        self.gridLayout.addWidget(self.label_shape, 1, 0, 1, 1)
        self.comboBox_shape = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_shape.setObjectName("comboBox_shape")
        self.gridLayout.addWidget(self.comboBox_shape, 1, 1, 1, 1)
        self.pushButton_erase = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_erase.setObjectName("pushButton_erase")
        self.gridLayout.addWidget(self.pushButton_erase, 2, 0, 1, 2)
        self.gridLayout.setColumnMinimumWidth(0, 1)
        self.gridLayout.setColumnMinimumWidth(1, 2)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_4.addWidget(self.scrollArea)
        self.verticalLayout_4.setStretch(0, 1)
        self.verticalLayout_6.addWidget(self.groupBox)
        self.dockWidget = QtWidgets.QDockWidget(self.frame_7)
        self.dockWidget.setMouseTracking(True)
        #self.dockWidget.setFloating(True)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.listWidget_file = QtWidgets.QListWidget(self.dockWidgetContents)
        self.listWidget_file.setObjectName("listWidget_file")
        self.verticalLayout_3.addWidget(self.listWidget_file)
        self.dockWidget.setWidget(self.dockWidgetContents)
        self.verticalLayout_6.addWidget(self.dockWidget)
        self.verticalLayout_6.setStretch(0, 1)
        self.verticalLayout_6.setStretch(1, 5)
        self.verticalLayout_6.setStretch(2, 8)
        self.horizontalLayout_5.addWidget(self.frame_7)
        self.horizontalLayout_5.setStretch(0, 5)
        self.horizontalLayout_5.setStretch(1, 1)
        self.horizontalLayout_3.addWidget(self.frame_5)
        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 17)
        self.frame_5.raise_()
        self.frame_4.raise_()
        self.verticalLayout.addWidget(self.frame_3)
        self.frame_6 = QtWidgets.QFrame(Form)
        self.frame_6.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_4.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.progressBar = QtWidgets.QProgressBar(self.frame_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setMinimumSize(QtCore.QSize(1000, 30))
        self.progressBar.setMaximum(1)
        self.progressBar.setProperty("value", -1)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_4.addWidget(self.progressBar)
        self.verticalLayout.addWidget(self.frame_6)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 9)
        self.verticalLayout.setStretch(3, 1)

        self.retranslateUi(Form)
        self.comboBox_model.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", " "))
        self.pushButton_return.setText(_translate("Form", "Return"))
        self.label_title.setText(_translate("Form", "BubbleNets"))
        self.pushButton_next.setText(_translate("Form", "Next"))
        self.pushButton_open.setText(_translate("Form", " 打开视频帧文件"))
        self.label_model.setText(_translate("Form", "选择配置模型:"))
        self.label_iter.setText(_translate("Form", "选择迭代次数:"))
        self.pushButton_compute.setText(_translate("Form", "开始计算最佳帧"))
        self.pushButton_showbubble.setText(_translate("Form", "展示排序结果"))
        self.toolButton_exist.setText(_translate("Form", "已有标注"))
        self.toolButton_start.setText(_translate("Form", "开始标注"))
        self.toolButton_restart.setText(_translate("Form", "重新标注"))
        self.toolButton_finish.setText(_translate("Form", "完成标注"))
        self.toolButton_save.setText(_translate("Form", "保存标注"))
        self.groupBox.setTitle(_translate("Form", "工具箱"))
        self.label_resize.setText(_translate("Form", "缩放比例"))
        self.label_shape.setText(_translate("Form", "选择形状"))
        self.pushButton_erase.setText(_translate("Form", "橡皮擦"))
        self.dockWidget.setAccessibleName(_translate("Form", "111"))
        self.dockWidget.setWindowTitle(_translate("Form", "FIle List"))
