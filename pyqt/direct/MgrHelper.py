import os
from PyQt5.QtCore import  QObject, Qt, QEvent
from PyQt5.QtGui import QFont, QColor, QFontDatabase, QPixmap, QPainter
from PyQt5.QtWidgets import QApplication
root_folder2 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder2=os.path.dirname(root_folder2 )
resources_folder=os.path.join(parent_folder2,'resources')

class MgrHelper(QObject):
    self=0#静态变量self,在主类中调用时未定义该类的实例直接使用该类的函数所以定义该变量
    def __init__(self):
        super(MgrHelper, self).__init__()
        fontFile=resources_folder+'/fontawesome-webfont.ttf'
        #fontFile='fontawesome-webfont.ttf'
        fontId=QFontDatabase.addApplicationFont(fontFile)
        fontName=QFontDatabase.applicationFontFamilies(fontId)
        self.iconFont=QFont(fontName[0])#图形字体
        self.mousePressed=False
        #给QApplication安装事件过滤器，所有对象的每个事件在被送到其它事件过滤器前都要送到eventFilter
        QApplication.instance().installEventFilter(self)

    #类的静态函数，返回当前实例对象
    @staticmethod#和@classmethod可以直接类名.方法名()来调用，静态方法类似于全局函数，没有参数,classmethod有参数cls
    def Instance():
        if not MgrHelper.self:
            MgrHelper.self=MgrHelper()
        return MgrHelper.self

    def setFontIcon(self,btn,charCode,size=12):#对控件设置字体图标
        self.iconFont.setPointSize(size)
        btn.setFont(self.iconFont)
        btn.setText(chr(charCode))#chr将unicode数值转化为字符

    def setBottomIconFont(self,btn,label,textEdit,size):
        self.iconFont.setPointSize(size)
        btn.setFont(self.iconFont)
        btn.setText('浏览')
        #self.iconFont.setPointSize(size)
        label.setFont(self.iconFont)
        label.setText('选择工作空间')
        textEdit.setFont(self.iconFont)

    #对某个字体图标返回它的图像
    def getPixmapFromFont(self,color,charCode,size=12,pixWidth=20,pixHeight=20):
        pix=QPixmap(pixWidth,pixHeight)
        pix.fill(Qt.transparent) #背景为透明
        painter=QPainter(pix)
        painter.setPen(QColor(color))#s设置用于绘制的笔的颜色大小样式
        self.iconFont.setPointSize(size)
        painter.setFont(self.iconFont)#设置字体
        painter.drawText(pix.rect(),Qt.AlignCenter,chr(charCode))#绘制文字,rect(0,y0,w,h)
        return pix

    #globelPos是鼠标相对于屏幕坐标，pos是相对控件的坐标
    def eventFilter(self,obj,evt):#事件过滤函数实现窗口的拖动功能
        #print('eventFilter')
        if obj.property('canMove')==True:
            if evt.type()==QEvent.MouseButtonPress:
                if evt.button()==Qt.LeftButton:
                    #print('mousePressed')
                    self.mousePressed=True
                    self.mousePt=evt.globalPos()-obj.pos()#pos()是x和y的组合
            elif evt.type()==QEvent.MouseButtonRelease:
                #print('mouseRealesed')
                self.mousePressed=False
            elif evt.type()==QEvent.MouseMove:
                if self.mousePressed:
                    #print('mouseMove and mousePressed')
                    obj.move(evt.globalPos()-self.mousePt)
        return QObject.eventFilter(self,obj,evt)

    #设置当鼠标移到按钮时改变控件的颜色和鼠标样式
    # def focusBtnChange(self,btn,type,color):
    #     btn.setCursor(QCursor(Qt.PointingHandCursor))
    #     styleSheet_btnExit = []
    #     styleSheet_btnExit.append('QToolButton:hover{{font:{};}}'.format('#737A97'))
    #     btn.setStyleSheet(''.join(styleSheet))
