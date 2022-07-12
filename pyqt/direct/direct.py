import os
import sys
from PyQt5.QtCore import Qt, QSize,pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolButton, QMessageBox, QFileDialog,QDesktopWidget

root_folder1 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder1=os.path.dirname(root_folder1 )
resources_folder=os.path.join(parent_folder1,'resources')
sys.path.append(parent_folder1)
sys.path.append(os.path.join(parent_folder1,'gui'))
sys.path.append(os.path.join(parent_folder1,'OSVOS'))
sys.path.append(os.path.join(parent_folder1,'direct'))
sys.path.append(os.path.join(parent_folder1,'bubbleNets'))
sys.path.append(os.path.join(parent_folder1,'FrameExtract'))
sys.path.append(os.path.join(parent_folder1,'Removal'))
sys.path.append(os.path.join(parent_folder1,'settings'))
default_path = '/home/wanwanvv/workspace/osvos'

#引入的自定义库
from gui import direct_Mainwindow
from direct_Mainwindow import Direct_MainWindow
from MgrHelper import MgrHelper
from osvos_logic import OsvosForm
from frameExtract_logic import FrameExtractWindow
from bubbleNets_logic import BubbleNetsForm
from remove_logic import RemoveObjectForm
from settings_logic import SettingsWindow
from about_logic import aboutWidget
# class LoadDataWorker(QObject):
#     finished = pyqtSignal()
#     message_signal = pyqtSignal(str)
#
#     def __init__(self):
#         super(LoadDataWorker, self).__init__()
#
#     def run(self):
#         for i in range(10):
#             self.message_signal.emit(f'Loading...{str(i)}%')
#         self.finished.emit()
#
# class MySplashScreen(QSplashScreen):
#     def __init__(self):
#         super(MySplashScreen, self).__init__()
#         # 新建动画
#         # self.setAttribute(Qt.WA_TranslucentBackground,True)#设置背景透明
#         # self.setWindowFlags(Qt.FramelessWindowHint)#设置无边框
#         # #　移到正中间显示
#         # cp = QDesktopWidget().availableGeometry().center()
#         # qr = self.frameGeometry()
#         # qr.moveCenter(cp)
#         # self.move(qr.topLeft())
#
#     def mousePressEvent(self, QMouseEvent):
#         super(MySplashScreen, self).mousePressEvent()
#         pass
#
#     def paintEvent(self, event):
#         super(MySplashScreen, self).paintEvent(event)
#         self.painter = QPainter(self)
#         self.painter.begin(self)
#         self.painter.setRenderHint(QPainter.Antialiasing)
#         # painter.drawImage(QRectF(0, 0, self.width(), self.height()), QImage(self.picture))
#         self.painter.save()
#         self.painter.setPen(QColor(255, 255, 255))
#         self.painter.drawText(QPoint(5, self.height() - 8), self.text)
#         self.painter.restore()
#         # painter.fillRect(self.rect(), Qt.black)
#         self.animate(self.painter)
#         self.painter.end()


class DirectForm(QMainWindow):
    resized=pyqtSignal() #缩放信号
    _startPos=None
    _endPos=None
    _isTracking=False
    def __init__(self):
        super(DirectForm,self).__init__()#继承的父类的初始化
        self.ui=Direct_MainWindow()
        self.ui.setupUi(self)
        #mghelper=MgrHelper()
        self.initConstant()
        self.initUI()

    #**********启动动画*************
    #     self.splash = splash
    #     self.load_thread = QThread()
    #     self.load_worker = LoadDataWorker()
    #     self.load_worker.moveToThread(self.load_thread)
    #     self.load_thread.started.connect(self.load_worker.run)
    #     self.load_worker.message_signal.connect(self.set_message)
    #     self.load_worker.finished.connect(self.load_worker_finished)
    #     self.load_thread.start()
    #     while self.load_thread.isRunning():
    #         QtWidgets.qApp.processEvents()  # 不断刷新，保证动画流畅
    #     self.load_thread.deleteLater()
    #
    # def load_worker_finished(self):
    #     self.load_thread.quit()
    #     self.load_thread.wait()
    #
    # def set_message(self, message):
    #     self.splash.showMessage(message, Qt.AlignLeft | Qt.AlignBottom, Qt.white)
    # **********启动动画*************

    def initConstant(self):
        self.iconFontSize=50 #中间按钮上图标字体的大小
        self.iconWidth=100 #中间按钮上图标的宽度
        self.iconHeight=80 #中间按钮上图标的高度
        self.navBtnWidth=45 #上方导航条上按钮宽度
        self.navIconFontSize=20 #上方导航条上图标字体的大小
        self.navSmallFontSize = 44  # 上方导航条上最小化图标字体的大小
        self.bottomIconFontSize=10
        self.workspace=''

    def slotExit(self):
        self.close()

    def initUI(self):
        #self.setMouseTracking(True)
        #窗体居中显示
        cp = QDesktopWidget().availableGeometry().center()
        qr=self.frameGeometry()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle(u'导航界面')
        self.setWindowFlags(Qt.FramelessWindowHint)#窗口属性没有边框的窗口
        self.setProperty('canMove',True) #给一个pyqt对象动态的添加属性setProperty(‘属性名称’,值)
        #self.ui.label_title.setProperty('canMove',True)

        self.ui.frame.setProperty('flag','nav')

        #浏览按钮打开文件夹
        self.ui.pushButton_browse.clicked.connect(self.getWorkDirectory)

        helper=MgrHelper.Instance()
        helper.setFontIcon(self.ui.pushButton_return,0xf00a,self.navIconFontSize) #0xf00a
        helper.setFontIcon(self.ui.pushButton_exit,0xf00d,self.navIconFontSize)#0xf00d
        helper.setFontIcon(self.ui.pushButton_small,0x002D, self.navSmallFontSize)#0x002D
        helper.setBottomIconFont(self.ui.pushButton_browse,self.ui.label_root,self.ui.textEdit_root,self.bottomIconFontSize)
        #关闭按钮
        self.ui.pushButton_exit.setCursor(QCursor(Qt.PointingHandCursor))
        styleSheet_exit = []
        styleSheet_exit.append('QPushButton#pushButton_exit:hover{{color:{};}}'.format('#737A97'))
        self.ui.pushButton_exit.setStyleSheet(''.join(styleSheet_exit))
        self.ui.pushButton_exit.clicked.connect(self.slotExit)
        #最小化按钮
        self.ui.pushButton_small.setCursor(QCursor(Qt.PointingHandCursor))
        styleSheet_small = []
        #styleSheet_small.append('QPushButton#pushButton_small{{text_align:vcenter;}}')
        styleSheet_small.append('QPushButton#pushButton_small:hover{{color:{};}}'.format('#737A97'))
        self.ui.pushButton_small.setStyleSheet(''.join(styleSheet_small))
        self.ui.pushButton_small.clicked.connect(self.showMinimized)#最小化窗口

        #浏览按钮
        self.ui.pushButton_browse.setCursor(QCursor(Qt.PointingHandCursor))

        #设置顶部导航区域样式风格
        #qss语法：#label_title是ID选择器,实际是objectName指定的值;[flag="nav"]匹配所有的属性为这个的实例
        qss=[]
        qss.append('QLabel#label_title{{font:{}px;}}'.format(self.navIconFontSize))
        qss.append('QFrame[flag="nav"]{{background:qlineargradient'
        '(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 {},stop:1 {});}}'.format('#00688B','#093746'))
        qss.append('QFrame[flag="nav"] QAbstractButton{{background:none;border:none;'
        'min-width:{0}px;max-width:{0}px;}}'.format(self.navBtnWidth))

        self.setStyleSheet(''.join(qss))
        allColorBags=['#1570A5','#16A0B5','#C0392B','#047058','#9B59BB','#34495E']
        allColorTexts=['#FEFEFE','#FEFEFE','#FEFEFE','#FEFEFE','#FEFEFE','#FEFEFE']
        #allTexts=[u"抽取关键帧","关键帧标注","视频目标分割",u"视频目标移除",u"敬请期待","..."]
        allTexts = ["视频目标分割",u"抽取关键帧", "关键帧标注", u"视频目标移除", u"设置", "..."]
        allCharCodes=[0xf008,0xf030,0xf012,0xf2C3,0xf013,0xf002]
        btns=self.findChildren(QToolButton) #找到所有的QToolButton,返回结果<PyQt5.QtWidgets.QToolButton object at 0x7f0a2f7efd38>
        for i,btn in enumerate(btns):
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setIconSize(QSize(self.iconWidth,self.iconHeight))

            pix=helper.getPixmapFromFont(allColorTexts[i],allCharCodes[i],
                                         self.iconFontSize,self.iconWidth,self.iconHeight)
            btn.setIcon(QIcon(pix))
            btn.setText(allTexts[i])
            styleSheet=[]
            styleSheet.append('QToolButton{{font:{}pt;background:{};}}'.format(self.iconFontSize/2.5,allColorBags[i]))
            styleSheet.append('QToolButton{border:none;border-radius:8px;padding:30px;}')
            styleSheet.append('QToolButton:pressed{{background:{};}}'.format('#737A97'))
            styleSheet.append('QToolButton:hover{{background:{};}}'.format('#737A97'))
            btn.setStyleSheet(''.join(styleSheet))
            #鼠标移到按钮上变为手型
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(self.slotBtnClicked)

    # def mouseMoveEvent(self, e: QtGui.QMouseEvent):
    #     self._endPos=e.pos()-self._startPos
    #     self.move(self.pos()+self._endPos)
    #
    # def mousePressEvent(self, e: QtGui.QMouseEvent):
    #     if e.button()==Qt.LeftButton:
    #         self._isTracking=True
    #         self._startPos=QPoint(e.x(),e.y())
    #
    # def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
    #     if e.button()==Qt.LeftButton:
    #         self._isTracking=False
    #         self._startPos=None
    #         self._endPos=None

    def slotBtnClicked(self):
        text=str(self.sender().text())#在python2中为unicode,在python3中为str
        #i=[u"抽取关键帧","BubbleNets","OSVOS",u"自动换背景",u"敬请期待","..."].index(text)
        i=["视频目标分割", u"抽取关键帧", "关键帧标注", u"视频目标移除", u"设置", "..."].index(text)
        dir=self.ui.textEdit_root.toPlainText()
        if dir=='' or not os.path.isdir(dir) or not os.path.exists(dir):
            if dir == '':
                QMessageBox.about(self, 'Notice', '工作空间目录不能为空!')
                return
            elif not os.path.exists(dir):
                QMessageBox.about(self, 'Notice', '工作空间目录不存在!')
                return
            elif not os.path.isdir(dir):
                QMessageBox.about(self, 'Notice', '工作空间必须为文件夹目录!')
                return
        if i==0:
            print('OsvosForm')
            osvos_widget = OsvosForm(dir,self)
            osvos_widget.show()
            self.hide()
        elif i==1:
            print('FrameExtractWindow')
            self.extract_widget = FrameExtractWindow(dir, self)
            self.extract_widget.show()
            self.hide()
        elif i==2:
            print('BubbleNetsForm')
            self.osvos_object=OsvosForm(dir,self)
            self.bubblenet_widget = BubbleNetsForm(dir, self,self.osvos_object, 0, None)
            self.bubblenet_widget.show()
            self.hide()
            #osvos_widget.exec_()
        elif i==3:
            print('RemoveObjectForm')
            self.removal_widget=RemoveObjectForm(dir,self)
            self.removal_widget.show()
            self.hide()
        elif i==4:
            print('SettingsForm')
            self.settings_widget=SettingsWindow(dir,self)
            self.settings_widget.show()
            self.hide()
        elif i == 5:
            print('AboutForm')
            self.about_widget = aboutWidget(dir, self)
            self.about_widget.show()
            self.hide()



    def getWorkDirectory(self):
        directory=QFileDialog.getExistingDirectory(None,caption="选取文件夹目录",directory=default_path)
        self.ui.textEdit_root.setText(directory)
    # def slotReturn(self):


if __name__=='__main__':
    app=QApplication(sys.argv)
    app.setFont(QFont('Microsoft Yahei',9))#字体
    app.setPalette(QPalette(QColor('#002030')))#背景颜色
    mainWindow=DirectForm()
    mainWindow.show()
    sys.exit(app.exec_())