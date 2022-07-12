from PyQt5.QtCore import QRect,pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QFont
from PyQt5.QtWidgets import QWidget
from PyQt5 import Qt

class SwitchButton(QWidget):
    switchButtonOpenSignal = pyqtSignal()  # 信号
    switchButtonCloseSignal = pyqtSignal()  # 信号
    def __init__(self, parent=None,width=60,height=25):
        super(SwitchButton, self).__init__(parent)

        # 设置无边框和背景透明
        self.setWindowFlags(self.windowFlags() | Qt.Qt.FramelessWindowHint)
        self.setAttribute(Qt.Qt.WA_TranslucentBackground)
        self.resize(width, height)
        self.state = False  # 按钮状态：True表示开，False表示关

    def mousePressEvent(self, event):
        """鼠标点击事件：用于切换按钮状态"""
        super(SwitchButton, self).mousePressEvent(event)
        if self.state == True:
            self.state = False
            self.switchButtonCloseSignal.emit()
        else:
            self.state = True
            self.switchButtonOpenSignal.emit()
        #self.state = False if self.state else True
        self.update()

    def paintEvent(self, event):
        """绘制按钮"""
        super(SwitchButton, self).paintEvent(event)
        # 创建绘制器并设置抗锯齿和图片流畅转换
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        # 定义字体样式
        font = QFont('Microsoft YaHei')
        font.setPixelSize(14)
        painter.setFont(font)

        # 开关为开的状态
        if self.state:
            # 绘制背景
            painter.setPen(Qt.Qt.NoPen)
            brush = QBrush(QColor('#3A5FCD'))
            painter.setBrush(brush)
            painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() // 2, self.height() // 2)

            # 绘制圆圈
            painter.setPen(Qt.Qt.NoPen)
            brush.setColor(QColor('#ffffff'))
            painter.setBrush(brush)
            painter.drawRoundedRect(43, 3, 24, 24, 12, 12)

            # 绘制文本
            painter.setPen(QPen(QColor('#ffffff')))
            painter.setBrush(Qt.Qt.NoBrush)
            painter.drawText(QRect(18, 4, 50, 20), Qt.Qt.AlignLeft, '开')
        # 开关为关的状态　
        else:
            # 绘制背景
            painter.setPen(Qt.Qt.NoPen)
            brush = QBrush(QColor('#FFFFFF'))
            painter.setBrush(brush)
            painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() // 2, self.height() // 2)

            # 绘制圆圈
            pen = QPen(QColor('#999999'))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRoundedRect(3, 3, 24, 24, 12, 12)

            # 绘制文本
            painter.setBrush(Qt.Qt.NoBrush)
            painter.drawText(QRect(38, 4, 50, 20), Qt.Qt.AlignLeft, '关')
