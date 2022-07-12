from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
import os,sys

#引入本地库
root_folder38 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder38 = os.path.dirname(root_folder38 )
resources_folder38 = os.path.join(parent_folder38,'resources')
sys.path.append(parent_folder38)
sys.path.append(os.path.join(parent_folder38,'gui'))
sys.path.append(os.path.join(parent_folder38,'settings'))
from appearance_form import appreanceForm

class AppearanceSetForm(QWidget, appreanceForm):
    def __init__(self):
        super(AppearanceSetForm, self).__init__()

        # 子窗口初始化时实现子窗口布局
        self.ui = appreanceForm()
        self.ui.setupUi(self)
        self.initConstant()
        self.initUI()

    def initConstant(self):
        self.ui.radioButton_font_left0.setChecked(True)
        self.ui.radioButton_font_right0.setChecked(True)
        self.ui.lineEdit_background.setText("#002030")
        #****************comboBox***********************
        self.comboBox_items_theme0 = ['Adwaita（默认）','Adwaita-dark','HighContrast','Radiance','Sweet-Ambar']
        self.comboBox_items_theme1 = ['DMZ-White','Monnlight','Redglass']
        self.comboBox_items_theme2 = ['Ubuntu-mono-dark','Humanity']
        self.comboBox_items_theme3 = ['默认','Flat-Remix','Ant-Nebuia']
        self.comboBox_items_background = ['Zoom','Centered','None','Scaled','Wallpaper','Stretched','Spanned']

    def initUI(self):
        # ****************comboBox***********************
        self.ui.comboBox_theme0.addItems(self.comboBox_items_theme0)
        self.ui.comboBox_theme1.addItems(self.comboBox_items_theme1)
        self.ui.comboBox_theme2.addItems(self.comboBox_items_theme2)
        self.ui.comboBox_theme3.addItems(self.comboBox_items_theme3)
        self.ui.comboBox_background.addItems(self.comboBox_items_background)
        self.ui.comboBox_theme0.setCurrentIndex(0)
        self.ui.comboBox_theme1.setCurrentIndex(0)
        self.ui.comboBox_theme2.setCurrentIndex(0)
        self.ui.comboBox_theme3.setCurrentIndex(0)
        self.ui.comboBox_background.setCurrentIndex(0)
        # *****************qss属性设置**********************
        self.ui.label_font0.setProperty('flag','title')
        self.ui.label_theme0.setProperty('flag','title')
        self.ui.label_background0.setProperty('flag','title')
        self.ui.label_font1.setProperty('flag','item')
        self.ui.label_font2.setProperty('flag', 'item')
        self.ui.label_font3.setProperty('flag', 'item')
        self.ui.label_font4.setProperty('flag', 'item')
        self.ui.label_font5.setProperty('flag', 'item')
        self.ui.label_font6.setProperty('flag', 'item')
        self.ui.label_background1.setProperty('flag', 'item')
        self.ui.label_background2.setProperty('flag', 'item')
        self.ui.label_theme1.setProperty('flag', 'item')
        self.ui.label_theme2.setProperty('flag', 'item')
        self.ui.label_theme3.setProperty('flag', 'item')
        self.ui.label_theme4.setProperty('flag', 'item')
        self.styleSheet = []
        self.styleSheet.append('QLabel[flag="title"]{font-family:Microsoft Yahei;font-size:15px;font-weight:bold;}')
        self.styleSheet.append('QLabel[flag="item"]{font-family:Microsoft Yahei;font-size:15px;}')
        self.setStyleSheet(''.join(self.styleSheet))