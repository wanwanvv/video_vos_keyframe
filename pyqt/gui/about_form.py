# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about_form.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class AboutForm(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(800, 680)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setContentsMargins(50, 50, 50, 110)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_0 = QtWidgets.QFrame(Form)
        self.frame_0.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_0.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_0.setObjectName("frame_0")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_0_1 = QtWidgets.QFrame(self.frame_0)
        self.frame_0_1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_0_1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_0_1.setObjectName("frame_0_1")
        self.horizontalLayout.addWidget(self.frame_0_1)
        self.frame_0_2 = QtWidgets.QFrame(self.frame_0)
        self.frame_0_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_0_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_0_2.setObjectName("frame_0_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_0_2)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_icon0 = QtWidgets.QFrame(self.frame_0_2)
        self.frame_icon0.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_icon0.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_icon0.setObjectName("frame_icon0")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_icon0)
        self.horizontalLayout_3.setContentsMargins(90, 0, 50, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_icon = QtWidgets.QLabel(self.frame_icon0)
        self.label_icon.setText("")
        self.label_icon.setObjectName("label_icon")
        self.horizontalLayout_3.addWidget(self.label_icon)
        self.verticalLayout.addWidget(self.frame_icon0)
        self.frame_icon_1 = QtWidgets.QFrame(self.frame_0_2)
        self.frame_icon_1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_icon_1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_icon_1.setObjectName("frame_icon_1")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_icon_1)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_title = QtWidgets.QLabel(self.frame_icon_1)
        self.label_title.setTextFormat(QtCore.Qt.AutoText)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.verticalLayout_3.addWidget(self.label_title)
        self.verticalLayout.addWidget(self.frame_icon_1)
        self.verticalLayout.setStretch(0, 3)
        self.verticalLayout.setStretch(1, 1)
        self.horizontalLayout.addWidget(self.frame_0_2)
        self.frame_0_3 = QtWidgets.QFrame(self.frame_0)
        self.frame_0_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_0_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_0_3.setObjectName("frame_0_3")
        self.horizontalLayout.addWidget(self.frame_0_3)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(2, 1)
        self.verticalLayout_2.addWidget(self.frame_0)
        self.frame_1 = QtWidgets.QFrame(Form)
        self.frame_1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_1.setObjectName("frame_1")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_1)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.frame_1_0 = QtWidgets.QFrame(self.frame_1)
        self.frame_1_0.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_1_0.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_1_0.setObjectName("frame_1_0")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame_1_0)
        self.verticalLayout_5.setContentsMargins(80, 0, 80, 20)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.textBrowser = QtWidgets.QTextBrowser(self.frame_1_0)
        self.textBrowser.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textBrowser.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_5.addWidget(self.textBrowser)
        self.verticalLayout_4.addWidget(self.frame_1_0)
        self.frame_1_1 = QtWidgets.QFrame(self.frame_1)
        self.frame_1_1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_1_1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_1_1.setObjectName("frame_1_1")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_1_1)
        self.horizontalLayout_4.setContentsMargins(100, 0, 60, 0)
        self.horizontalLayout_4.setSpacing(80)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame_1_1_0 = QtWidgets.QFrame(self.frame_1_1)
        self.frame_1_1_0.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_1_1_0.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_1_1_0.setObjectName("frame_1_1_0")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame_1_1_0)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_version = QtWidgets.QLabel(self.frame_1_1_0)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_version.sizePolicy().hasHeightForWidth())
        self.label_version.setSizePolicy(sizePolicy)
        self.label_version.setMinimumSize(QtCore.QSize(0, 0))
        self.label_version.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_version.setObjectName("label_version")
        self.verticalLayout_6.addWidget(self.label_version)
        self.label_programmer = QtWidgets.QLabel(self.frame_1_1_0)
        self.label_programmer.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_programmer.setObjectName("label_programmer")
        self.verticalLayout_6.addWidget(self.label_programmer)
        self.label_github = QtWidgets.QLabel(self.frame_1_1_0)
        self.label_github.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_github.setObjectName("label_github")
        self.verticalLayout_6.addWidget(self.label_github)
        self.label_connect = QtWidgets.QLabel(self.frame_1_1_0)
        self.label_connect.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_connect.setObjectName("label_connect")
        self.verticalLayout_6.addWidget(self.label_connect)
        self.horizontalLayout_4.addWidget(self.frame_1_1_0)
        self.frame_1_1_1 = QtWidgets.QFrame(self.frame_1_1)
        self.frame_1_1_1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_1_1_1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_1_1_1.setObjectName("frame_1_1_1")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_1_1_1)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_version_value = QtWidgets.QLabel(self.frame_1_1_1)
        self.label_version_value.setObjectName("label_version_value")
        self.verticalLayout_7.addWidget(self.label_version_value)
        self.label_programmer_value = QtWidgets.QLabel(self.frame_1_1_1)
        self.label_programmer_value.setObjectName("label_programmer_value")
        self.verticalLayout_7.addWidget(self.label_programmer_value)
        self.label_github_value = QtWidgets.QLabel(self.frame_1_1_1)
        self.label_github_value.setObjectName("label_github_value")
        self.verticalLayout_7.addWidget(self.label_github_value)
        self.label_connect_value = QtWidgets.QLabel(self.frame_1_1_1)
        self.label_connect_value.setObjectName("label_connect_value")
        self.verticalLayout_7.addWidget(self.label_connect_value)
        self.horizontalLayout_4.addWidget(self.frame_1_1_1)
        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 5)
        self.verticalLayout_4.addWidget(self.frame_1_1)
        self.verticalLayout_4.setStretch(0, 2)
        self.verticalLayout_4.setStretch(1, 5)
        self.verticalLayout_2.addWidget(self.frame_1)
        self.frame_2 = QtWidgets.QFrame(Form)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frame_2_1 = QtWidgets.QFrame(self.frame_2)
        self.frame_2_1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2_1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2_1.setObjectName("frame_2_1")
        self.horizontalLayout_2.addWidget(self.frame_2_1)
        self.horizontalLayout_2.setContentsMargins(0, 0, 85, 0)
        self.pushButton_update = QtWidgets.QPushButton(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_update.sizePolicy().hasHeightForWidth())
        self.pushButton_update.setSizePolicy(sizePolicy)
        self.pushButton_update.setMinimumSize(QtCore.QSize(170, 40))
        self.pushButton_update.setObjectName("pushButton_update")
        self.horizontalLayout_2.addWidget(self.pushButton_update)
        self.verticalLayout_2.addWidget(self.frame_2)
        self.verticalLayout_2.setStretch(0, 6)
        self.verticalLayout_2.setStretch(1, 7)
        self.verticalLayout_2.setStretch(2, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_title.setText(_translate("Form", "KFaVos 智能视频编辑系统"))
        self.textBrowser.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">Kfa-vos是一款利用人工智能技术来对视频进行智能处理的基于Ｐyqt5开发的桌面端．采用基于关键帧物体标注的视频目标分割方法可以让用户快速地对视频进行关键帧抽取，前景分割，目标移除等处理．</span></p></body></html>"))
        self.label_version.setText(_translate("Form", "版本信息"))
        self.label_programmer.setText(_translate("Form", "开发作者"))
        self.label_github.setText(_translate("Form", "Github地址"))
        self.label_connect.setText(_translate("Form", "联系方式"))
        self.label_version_value.setText(_translate("Form", "version 1.0"))
        self.label_programmer_value.setText(_translate("Form", "万静意"))
        self.label_github_value.setText(_translate("Form", "https://github.com/wanwanvv/projects"))
        self.label_connect_value.setText(_translate("Form", "ijingyiwan@gmail.com"))
        self.pushButton_update.setText(_translate("Form", "检查更新"))
