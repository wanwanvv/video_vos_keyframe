from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QMessageBox
import os,sys

#引入本地库
root_folder34 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder34=os.path.dirname(root_folder34 )
resources_folder34=os.path.join(parent_folder34,'resources')
sys.path.append(parent_folder34)
sys.path.append(os.path.join(parent_folder34,'gui'))
sys.path.append(os.path.join(parent_folder34,'settings'))
from about_form import AboutForm

class aboutWidget(QWidget, AboutForm):
    def __init__(self,workdir,direct_object):
        super(aboutWidget, self).__init__()
        # 子窗口初始化时实现子窗口布局
        self.ui = AboutForm()
        self.ui.setupUi(self)
        self.initConstant()
        self.initUI()
        # *************path*******************
        self.path_prefix = workdir  # 工作目录
        self.direct_object = direct_object
        # **************path********************

    def closeEvent(self, event):
        QWidget.closeEvent(self, event)
        self.direct_object.show()
        self.close()

    def initConstant(self):
        self.icon_img=os.path.join(resources_folder34,'ic_icon_144.png')

    def initUI(self):
        #背景颜色
        # palette = QPalette()
        # palette.setColor(QPalette.Background, QColor(255,255,255))
        # 窗体居中显示
        screen_size = QDesktopWidget().screenGeometry()  # 获得屏幕的尺寸
        widget_size = self.geometry()  # 获得窗体的尺寸
        self.move((screen_size.width() - widget_size.width()) / 2,
                  (screen_size.height() - widget_size.height()) / 2)
        self.setWindowTitle(u'关于界面')
        #*********显示图标*************
        head_pix = QPixmap(self.icon_img)
        self.ui.label_icon.setPixmap(head_pix)
        #*********点击更新按钮**********
        self.ui.pushButton_update.clicked.connect(self.version_update)
        #**********qss美化************
        self.ui.label_title.setProperty('flag', 'title')
        self.ui.label_version.setProperty('flag', 'left')
        self.ui.label_connect.setProperty('flag', 'left')
        self.ui.label_programmer.setProperty('flag', 'left')
        self.ui.label_github.setProperty('flag', 'left')
        self.ui.label_version_value.setProperty('flag', 'right')
        self.ui.label_connect_value.setProperty('flag', 'right')
        self.ui.label_programmer_value.setProperty('flag', 'right')
        self.ui.label_github_value.setProperty('flag', 'right')
        self.stylesheet = []
        self.stylesheet.append('QLabel[flag="title"]{font-family:Segoe UI;font-size:25px;font-weight:bold;text-align: center;color:black;}')
        self.stylesheet.append('QLabel[flag="left"]{font-family:Microsoft Yahei;font-size:15px;color:#8B8682;}')
        self.stylesheet.append('QLabel[flag="right"]{font-family:Microsoft Yahei;font-size:18px;color:black;}')
        self.stylesheet.append('QPushButton{border-radius:5px; color:black;font-family:Microsoft Yahei;font-size:15px;font-weight:bold;border:2px solid #8B8682;}')
        self.stylesheet.append('QPushButton:hover{background-color:#8B8682;border-radius:5px; color:white;font-family:Microsoft Yahei;font-size:15px;font-weight:bold;}')
        self.stylesheet.append('QTextBrowser{font-family:Microsoft Yahei;background-color:white;color:balck;font-size:18px;}')
        self.stylesheet.append('#Form{background-color:white;}')
        self.setStyleSheet(''.join(self.stylesheet))

    def version_update(self):
        QMessageBox.information(self, 'Notice', '当前已是最新版本!', QMessageBox.Ok)