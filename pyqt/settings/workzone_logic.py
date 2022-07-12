from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QWidget
import os,sys

#引入本地库
root_folder35 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder35 = os.path.dirname(root_folder35 )
resources_folder35 = os.path.join(parent_folder35,'resources')
sys.path.append(parent_folder35)
sys.path.append(os.path.join(parent_folder35,'gui'))
sys.path.append(os.path.join(parent_folder35,'settings'))
from workzone_form import Ui_workzone_form

class WorkzoneForm(QWidget, Ui_workzone_form):
    def __init__(self):
        super(WorkzoneForm, self).__init__()

        # 子窗口初始化时实现子窗口布局
        self.ui = Ui_workzone_form()
        self.ui.setupUi(self)
        self.initConstant()
        self.initUI()
        # 设置子窗体最小尺寸
        # self.setMinimumWidth(30)
        # self.setMinimumHeight(30)

    def initConstant(self):
        self.work_num=1
        self.check_img=os.path.join(resources_folder35,'nike_64.png')
        self.check_pix = QPixmap(self.check_img)
        #*****************是否选中打勾******************
        self.hasChecked_static = False
        self.hasChecked_dynamic = False
        self.hasChecked_resize = False
        self.hasChecked_drag = False

    def initUI(self):
        #*********************label信号绑定函数**********************
        self.ui.label_drag.chooseSignal.connect(self.showCheck_drag)
        self.ui.label_drag_icon.chooseSignal.connect(self.showCheck_drag)
        self.ui.label_resize.chooseSignal.connect(self.showCheck_resize)
        self.ui.label_resize_icon.chooseSignal.connect(self.showCheck_resize)
        self.ui.label_dynamic1.chooseSignal.connect(self.showCheck_dynamic)
        self.ui.label_dynamic2.chooseSignal.connect(self.showCheck_dynamic)
        self.ui.label_dynamic_icon.chooseSignal.connect(self.showCheck_dynamic)
        self.ui.label_staitc1.chooseSignal.connect(self.showCheck_staitc)
        self.ui.label_static2.chooseSignal.connect(self.showCheck_staitc)
        self.ui.label_static_icon.chooseSignal.connect(self.showCheck_staitc)
        # ****************spinBox的值改变关联函数******************
        self.ui.spinBox_worknum.valueChanged.connect(self.numValueChanged)
        # *****************qss属性设置**********************
        self.ui.label_set.setFont(QFont("Microsoft Yahei",15,QFont.Bold))
        self.styleSheet = []
        self.ui.label_resize.setProperty('flag', 'big')
        self.ui.label_drag.setProperty('flag', 'big')
        self.ui.label_staitc1.setProperty('flag', 'big')
        self.ui.label_dynamic1.setProperty('flag', 'big')
        self.ui.label_worknum.setProperty('flag', 'num')
        self.ui.label_set.setProperty('flag','midset')
        self.ui.label_static2.setProperty('flag','small')
        self.ui.label_dynamic2.setProperty('flag','small')
        self.ui.label_resize_icon.setProperty('flag','icon')
        self.ui.label_drag_icon.setProperty('flag','icon')
        self.ui.label_static_icon.setProperty('flag','icon')
        self.ui.label_dynamic_icon.setProperty('flag','icon')
        self.styleSheet.append('QLabel[flag="big"]{background:black;color: white;font-family:Microsoft Yahei;font-size:18px;}')
        self.styleSheet.append('QLabel[flag="num"]{color:white;font-family:Microsoft Yahei;font-size:18px;}')
        self.styleSheet.append('QLabel[flag="small"]{background:black;color: #999999;font-family:Microsoft Yahei;font-size:15px;}')
        #self.stylesheet.append('QLabel[flag="midset"]{background:black;font-family:Segoe UI;font-size:18px;font-weight:bold;color:white;}')
        #self.styleSheet.append('QLabel[flag="icon"]{background:black;}')
        self.styleSheet.append('QLabel[flag="big"]:hover{background:#002030;color: white;font-family:Microsoft Yahei;font-size:18px;}')
        self.styleSheet.append('QLabel[flag="small"]:hover{background:#002030;color: #999999;font-family:Microsoft Yahei;font-size:15px;}')  # E5E5E5
        #self.styleSheet.append('QLabel[flag="icon"]:hover{background:#454545;}')
        self.setStyleSheet(''.join(self.styleSheet))

    def numValueChanged(self):
        self.work_num=self.ui.spinBox_worknum.value()
        print('self.work_num={}'.format_map(self.work_num))

    def showCheck_drag(self):
        if self.hasChecked_drag==True:
            self.hasChecked_drag=False
            self.ui.label_drag_icon.setPixmap(QPixmap(""))
        else:
            self.hasChecked_drag = True
            self.ui.label_drag_icon.setPixmap(self.check_pix)

    def showCheck_resize(self):
        if self.hasChecked_resize==True:
            self.hasChecked_resize=False
            self.ui.label_resize_icon.setPixmap(QPixmap(""))
        else:
            self.hasChecked_resize = True
            self.ui.label_resize_icon.setPixmap(self.check_pix)

    def showCheck_dynamic(self):
        if self.hasChecked_dynamic==True:
            self.hasChecked_dynamic = False
            self.ui.label_dynamic_icon.setPixmap(QPixmap(""))
        else:
            self.hasChecked_dynamic = True
            self.ui.label_dynamic_icon.setPixmap(self.check_pix)

    def showCheck_staitc(self):
        if self.hasChecked_static==True:
            self.hasChecked_static=False
            self.ui.label_static_icon.setPixmap(QPixmap(""))
        else:
            self.hasChecked_static = True
            self.ui.label_static_icon.setPixmap(self.check_pix)