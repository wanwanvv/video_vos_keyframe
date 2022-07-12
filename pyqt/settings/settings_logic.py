import os,sys
from PyQt5.QtGui import QImage, QPixmap, QCursor, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QFileDialog, QMessageBox, QListWidgetItem, QListView, \
    QListWidget
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import QThread, Qt, QSize

#引入本地库
root_folder30 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder30=os.path.dirname(root_folder30 )
resources_folder30=os.path.join(parent_folder30,'resources')
sys.path.append(parent_folder30)
sys.path.append(os.path.join(parent_folder30,'gui'))
sys.path.append(os.path.join(parent_folder30,'direct'))
sys.path.append(os.path.join(parent_folder30,'settings'))
from settings_form import SettingsForm
from log_logic import log_widget
from workzone_logic import WorkzoneForm
from help_logic import HelpFuncForm
from appearance_logic import AppearanceSetForm

class SettingsWindow(QWidget):
    resized = QtCore.pyqtSignal()  # 缩放信号
    def __init__(self,workdir,direct_object):
        super(SettingsWindow, self).__init__()  # 继承的所有父类的初始化
        self.ui=SettingsForm()
        self.ui.setupUi(self)
        # *************path*******************
        self.path_prefix = workdir  # 工作目录
        self.direct_object=direct_object
        # **************path********************
        self.initConstant()
        self.initUI()

    def initConstant(self):
        print('initConstant')
        #******************美化属性******************

    def closeEvent(self, event):
        QWidget.closeEvent(self, event)
        self.direct_object.show()
        self.close()

    def initUI(self):
        # 窗体居中显示
        screen_size = QDesktopWidget().screenGeometry()  # 获得屏幕的尺寸
        widget_size = self.geometry()  # 获得窗体的尺寸
        self.move((screen_size.width() - widget_size.width()) / 2,
                  (screen_size.height() - widget_size.height()) / 2)
        self.setWindowTitle(u'设置界面')
        #左边创建listWidget部件
        self.left_widget = QListWidget()  # 左侧选项列表
        self.left_widget.setObjectName("left_widget")
        self.ui.splitter.addWidget(self.left_widget )
        # 主窗口初始化时实例化子窗口1和子窗口2
        self.form0_usersetting = log_widget()
        self.form1_appearance = AppearanceSetForm()
        self.form2_workzone = WorkzoneForm()
        self.form3_helpfunc = HelpFuncForm()

        #********************splitter分割器设置****************
        # 在主窗口的QSplitter里添加子窗口
        self.ui.splitter.addWidget(self.form0_usersetting)
        # 设置分割器QSplitter初始化时各个子窗体的大小；下面是两个子窗体。
        self.ui.splitter.setSizes([250, 800])
        #  下面一行为设置 QSplitter 分割器伸缩大小因子，但是这样设置全屏后导航栏放大了比较好看；不清楚原因。
        self.ui.splitter.setStretchFactor(0, 0)  # 此函数用于设定：控件是否可伸缩。第一个参数用于指定控件的序号。第二个函数大于0时，表示控件可伸缩，小于0时，表示控件不可伸缩。
        self.ui.splitter.setStretchFactor(1, 1)  # 此函数用于设定：控件是否可伸缩。第一个参数用于指定控件的序号。第二个函数大于0时，表示控件可伸缩，小于0时，表示控件不可伸缩。
        #  设置 QSplitter 分割器各部分最小化时的情况，设置为“False”意味着左右拉动分隔栏时各部分不会消失；此设置也可以在界面设计时在 QtDesigner 里设置。
        self.ui.splitter.setChildrenCollapsible(False)
        #  设置 QSplitter 分割器随主窗口自适应大小变化。此设置也可以在界面设计时在 QtDesigner 里设置。
        self.ui.splitter.setAutoFillBackground(True)

        # *******************listWIdget设置*******************　　　
        #self.left_widget.setFrameShape(QListWidget.NoFrame)  # 去掉边框
        #self.left_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏滚动条
        #self.left_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.menu_list = ['用户设置', '外观', '工作区', '通用辅助功能']
        self.menu_icons_black=['userset_black.png','pearance_black.png','workzone_black.png','language_black.png']
        self.menu_icons_white = ['userset_white.png', 'pearance_white.png', 'workzone_white.png', 'language_white.png']
        self.item_length=len(self.menu_list)
        for i in range(self.item_length):
            self.item=QListWidgetItem(self.menu_list[i],self.left_widget)   #左侧选项的添加
            self.item.setSizeHint(QSize(60, 60))
            #self.item.setTextAlignment(Qt.AlignCenter)
            self.item.setTextAlignment(Qt.AlignLeft)
            self.item.setTextAlignment(Qt.AlignVCenter)  # 居中显示
            # # 设置图标
            icon = QIcon()
            # 节点打开状态
            icon.addPixmap(QPixmap(os.path.join(resources_folder30,self.menu_icons_white[i])), QIcon.Selected)
            # 节点关闭状态　　
            icon.addPixmap(QPixmap(os.path.join(resources_folder30,self.menu_icons_black[i])), QIcon.Normal)
            self.item.setIcon(icon)
            #self.left_widget.addItem(self.item) 直接添加,功能可能不全
        self.left_widget.itemClicked.connect(self.onClick)  # 绑定点击事件

        # QTreeWidget中每个Item的信号与槽的连接；对应的槽函数；输出鼠标选中的item名字和所在列数；其中text(column)表示第 column 列的item名字

        #*****************qss属性设置**********************
        self.left_widget_styleSheet = []
        self.left_widget_styleSheet.append('QListWidget:{background:white;outline:2px;color: Black;}')
        self.left_widget_styleSheet.append('QListWidget::Item:selected {background: lightGray;}')
        self.left_widget_styleSheet.append('QListWidget::Item:hover {background: lightGray;font-size:30px;}')
        self.setStyleSheet(''.join(self.left_widget_styleSheet))

    def onClick(self, item):
        # 控制台输出鼠标选中的item名字和所在列数；其中text(column)表示第 column 列的item名字
        #currentRow = self.ui.listWidget.currentRow()
        #currentIndex = self.ui.listWidget.currentIndex()
        if item.text() == self.menu_list[0]:#用户设置
            # 把QSplitter的指定位置的窗体从QSplitter中剥离
            self.ui.splitter.widget(1).setParent(None)
            # 在QSplitter的指定位置载入新窗体，但要先用上面的“self.ui.splitter.widget(1).setParent(None)”命令。
            self.ui.splitter.insertWidget(1, self.form0_usersetting)
            self.ui.splitter.setStretchFactor(0, 0)  # 此函数用于设定：控件是否可伸缩。第一个参数用于指定控件的序号。第二个函数大于0时，表示控件可伸缩，小于0时，表示控件不可伸缩。
            self.ui.splitter.setStretchFactor(1, 1)  # 此函数用于设定：控件是否可伸缩。第一个参数用于指定控件的序号。第二个函数大于0时，表示控件可伸缩，小于0时，表示控件不可伸缩。
            #  设置 QSplitter 分割器各部分最小化时的情况，设置为“False”意味着左右拉动分隔栏时各部分不会消失；此设置也可以在界面设计时在 QtDesigner 里设置。
            self.ui.splitter.setChildrenCollapsible(False)
            #  设置 QSplitter 分割器随主窗口自适应大小变化。此设置也可以在界面设计时在 QtDesigner 里设置。
            self.ui.splitter.setAutoFillBackground(True)

        elif item.text() == self.menu_list[1]:#外观
            # 把QSplitter的指定位置的窗体从QSplitter中剥离
            self.ui.splitter.widget(1).setParent(None)
            # 在QSplitter的指定位置载入新窗体，但要先用上面的“self.ui.splitter.widget(1).setParent(None)”命令。
            self.ui.splitter.insertWidget(1, self.form1_appearance)
            self.ui.splitter.setStretchFactor(0, 0)  # 此函数用于设定：控件是否可伸缩。第一个参数用于指定控件的序号。第二个函数大于0时，表示控件可伸缩，小于0时，表示控件不可伸缩。
            self.ui.splitter.setStretchFactor(1, 1)  # 此函数用于设定：控件是否可伸缩。第一个参数用于指定控件的序号。第二个函数大于0时，表示控件可伸缩，小于0时，表示控件不可伸缩。
            #  设置 QSplitter 分割器各部分最小化时的情况，设置为“False”意味着左右拉动分隔栏时各部分不会消失；此设置也可以在界面设计时在 QtDesigner 里设置。
            self.ui.splitter.setChildrenCollapsible(False)
            #  设置 QSplitter 分割器随主窗口自适应大小变化。此设置也可以在界面设计时在 QtDesigner 里设置。
            self.ui.splitter.setAutoFillBackground(True)

        elif item.text() == self.menu_list[2]:#工作区
            # 把QSplitter的指定位置的窗体从QSplitter中剥离
            self.ui.splitter.widget(1).setParent(None)
            # 在QSplitter的指定位置载入新窗体，但要先用上面的“self.ui.splitter.widget(1).setParent(None)”命令。
            self.ui.splitter.insertWidget(1, self.form2_workzone)
            self.ui.splitter.setStretchFactor(0, 0)  # 此函数用于设定：控件是否可伸缩。第一个参数用于指定控件的序号。第二个函数大于0时，表示控件可伸缩，小于0时，表示控件不可伸缩。
            self.ui.splitter.setStretchFactor(1, 1)  # 此函数用于设定：控件是否可伸缩。第一个参数用于指定控件的序号。第二个函数大于0时，表示控件可伸缩，小于0时，表示控件不可伸缩。
            #  设置 QSplitter 分割器各部分最小化时的情况，设置为“False”意味着左右拉动分隔栏时各部分不会消失；此设置也可以在界面设计时在 QtDesigner 里设置。
            self.ui.splitter.setChildrenCollapsible(False)
            #  设置 QSplitter 分割器随主窗口自适应大小变化。此设置也可以在界面设计时在 QtDesigner 里设置。
            self.ui.splitter.setAutoFillBackground(True)

        elif item.text() == self.menu_list[3]:#辅助功能
            # 把QSplitter的指定位置的窗体从QSplitter中剥离
            self.ui.splitter.widget(1).setParent(None)
            # 在QSplitter的指定位置载入新窗体，但要先用上面的“self.ui.splitter.widget(1).setParent(None)”命令。
            self.ui.splitter.insertWidget(1, self.form3_helpfunc)
            self.ui.splitter.setStretchFactor(0, 0)  # 此函数用于设定：控件是否可伸缩。第一个参数用于指定控件的序号。第二个函数大于0时，表示控件可伸缩，小于0时，表示控件不可伸缩。
            self.ui.splitter.setStretchFactor(1, 1)  # 此函数用于设定：控件是否可伸缩。第一个参数用于指定控件的序号。第二个函数大于0时，表示控件可伸缩，小于0时，表示控件不可伸缩。
            #  设置 QSplitter 分割器各部分最小化时的情况，设置为“False”意味着左右拉动分隔栏时各部分不会消失；此设置也可以在界面设计时在 QtDesigner 里设置。
            self.ui.splitter.setChildrenCollapsible(False)
            #  设置 QSplitter 分割器随主窗口自适应大小变化。此设置也可以在界面设计时在 QtDesigner 里设置。
            self.ui.splitter.setAutoFillBackground(True)


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     default_workdir = '/home/wanwanvv/workspace/osvos/car-shadow'
#     direct_form=None
#     mainWindow = SettingsWindow(default_workdir,direct_form)
#     mainWindow.show()
#     sys.exit(app.exec_())