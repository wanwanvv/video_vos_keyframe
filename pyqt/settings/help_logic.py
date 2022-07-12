from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QWidget
import os,sys

#引入本地库
root_folder36 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder36 = os.path.dirname(root_folder36 )
resources_folder36 = os.path.join(parent_folder36,'resources')
sys.path.append(parent_folder36)
sys.path.append(os.path.join(parent_folder36,'gui'))
sys.path.append(os.path.join(parent_folder36,'settings'))
from help_form import helpForm
from switch_button import SwitchButton

class HelpFuncForm(QWidget, helpForm):
    def __init__(self):
        super(HelpFuncForm, self).__init__()

        # 子窗口初始化时实现子窗口布局
        self.ui = helpForm()
        self.ui.setupUi(self)
        self.initConstant()
        self.initUI()
        # 设置子窗体最小尺寸
        # self.setMinimumWidth(30)
        # self.setMinimumHeight(30)

    def initConstant(self):
        self.hasOpen_highlight = False
        self.hasOpen_bigtext = False
        self.hasOpen_cursorsize = False
        self.hasOpen_warn = False
        self.hasOpen_type_k = False
        self.hasOpen_type_e = False
        self.hasOpen_type_b = False
        self.hasOpen_type_t = False
        self.hasOpen_point_m = False
        self.hasOpen_point_c = False

    def initUI(self):
        #****************SwitchButton**************
        self.switchButton_highlight=SwitchButton()
        self.switchButton_bigtext=SwitchButton()
        self.switchButton_cursorsize=SwitchButton()
        self.switchButton_warn=SwitchButton()
        self.switchButton_type_k=SwitchButton()
        self.switchButton_type_e=SwitchButton()
        self.switchButton_type_b=SwitchButton()
        self.switchButton_type_t=SwitchButton()
        self.switchButton_point_m=SwitchButton()
        self.switchButton_point_c=SwitchButton()
        # 替换原来的Widget,控件删除旧的控件
        self.ui.verticalLayout_10.replaceWidget(self.ui.switch_widget_4,self.switchButton_type_t)
        self.ui.switch_widget_4.deleteLater()
        self.ui.verticalLayout_10.replaceWidget(self.ui.switch_widget_b, self.switchButton_type_b)
        self.ui.switch_widget_b.deleteLater()
        self.ui.verticalLayout_10.replaceWidget(self.ui.switch_widget_e, self.switchButton_type_e)
        self.ui.switch_widget_e.deleteLater()
        self.ui.verticalLayout_10.replaceWidget(self.ui.switch_widget_k, self.switchButton_type_k)
        self.ui.switch_widget_k.deleteLater()

        self.ui.verticalLayout_13.replaceWidget(self.ui.switch_widget_m, self.switchButton_point_m)
        self.ui.switch_widget_m.deleteLater()
        self.ui.verticalLayout_13.replaceWidget(self.ui.switch_widget_c, self.switchButton_point_c)
        self.ui.switch_widget_c.deleteLater()

        self.ui.horizontalLayout_2.replaceWidget(self.ui.switch_widget_warn, self.switchButton_warn)
        self.ui.switch_widget_warn.deleteLater()

        self.ui.verticalLayout.replaceWidget(self.ui.switch_widget_bigtext, self.switchButton_bigtext)
        self.ui.switch_widget_bigtext.deleteLater()
        self.ui.verticalLayout.replaceWidget(self.ui.switch_widget_highlight, self.switchButton_highlight)
        self.ui.switch_widget_highlight.deleteLater()
        self.ui.verticalLayout.replaceWidget(self.ui.switchwidget_cursorsize, self.switchButton_cursorsize)
        self.ui.switchwidget_cursorsize.deleteLater()
        #**************SwitchButton信号************
        self.switchButton_warn.switchButtonOpenSignal.connect(self.swichButtonOpen_warn)
        self.switchButton_warn.switchButtonCloseSignal.connect(self.swichButtonClose_warn)
        #***************radioButton****************
        self.radioButtonOpen(False)
        self.ui.radioButton_warn_right.toggled.connect(self.radiobutton_right_toggled)
        self.ui.radioButton_warn_left.toggled.connect(self.radiobutton_left_toggled)
        # ***************horizontalSLider****************
        self.ui.horizontalSlider.valueChanged.connect(self.sliderValueChanged)
        # *****************qss属性设置**********************
        self.ui.label_vision.setFont(QFont("Microsoft Yahei", 12, QFont.Bold))
        self.ui.label_warn1.setFont(QFont("Microsoft Yahei", 12, QFont.Bold))
        self.ui.label_type.setFont(QFont("Microsoft Yahei", 12, QFont.Bold))
        self.ui.label_point.setFont(QFont("Microsoft Yahei", 12, QFont.Bold))

        self.ui.label_vision.setProperty('flag','title')
        self.ui.label_warn1.setProperty('flag','title')
        self.ui.label_type.setProperty('flag','title')
        self.ui.label_point.setProperty('flag','title')
        self.ui.label_highlight.setProperty('flag','item')
        self.ui.label_bigtext.setProperty('flag','item')
        self.ui.label_cursorsize.setProperty('flag','item')
        self.ui.label_warn2.setProperty('flag','item')
        self.ui.label_type_b.setProperty('flag','item')
        self.ui.label_type_e.setProperty('flag','item')
        self.ui.label_type_k.setProperty('flag','item')
        self.ui.label_type_t.setProperty('flag','item')
        self.ui.label_point_c.setProperty('flag','item')
        self.ui.label_point_d.setProperty('flag','item')
        self.ui.label_point_m.setProperty('flag','item')
        self.ui.frame_0_1.setProperty('flag','frame')
        self.ui.frame_3.setProperty('flag','frame')
        self.ui.frame_8.setProperty('flag', 'frame')
        self.ui.frame_6.setProperty('flag', 'frame')
        self.styleSheet = []
        #self.stylesheet.append('QLabel[flag="title"]{font-family:Segoe UI;font-size:18px;font-weight:bold;color:white;}')#Segoe UI
        self.styleSheet.append('QLabel[flag="item"]{font-family:Microsoft Yahei;font-size:15px;color:white;}')
        self.styleSheet.append('QFrame[flag="frame"]{background:black;}')
        self.styleSheet.append('QRadioButton{font-family:Microsoft Yahei;font-size:10px;color:white;}')
        self.styleSheet.append('QRadioButton::indicator {background-color: #DEDEDE;color:#DEDEDE;}')
        self.styleSheet.append('QRadioButton::indicator:checked{background-color: #3A5FCD;color:#3A5FCD;}')
        self.styleSheet.append('QRadioButton::indicator:disabled{background-color: #DEDEDE;color:#DEDEDE;}')
        self.setStyleSheet(''.join(self.styleSheet))

    def swichButtonClose_warn(self):
        self.radioButtonOpen(False)
        self.hasOpen_warn=False

    def swichButtonOpen_warn(self):
        self.radioButtonOpen(True)
        self.hasOpen_warn=True

    def sliderValueChanged(self):
        print('Slider Value:{}'.format(self.ui.horizontalSlider.value()))

    def radiobutton_right_toggled(self):
        print('右边radio button被选中')

    def radiobutton_left_toggled(self):
        print('左边radio button被选中')

    def radioButtonOpen(self,status):
        if status==True:
            self.ui.radioButton_warn_left.setEnabled(True)
            self.ui.radioButton_warn_left.setEnabled(True)
            self.ui.radioButton_warn_left.setChecked(True)#默认选中
        else:
            self.ui.radioButton_warn_left.setEnabled(False)
            self.ui.radioButton_warn_left.setEnabled(False)
