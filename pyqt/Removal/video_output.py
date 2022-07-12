import os,sys
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QWidget, QDesktopWidget

root_folder18 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder18 = os.path.dirname(root_folder18 )
sys.path.append(parent_folder18)
sys.path.append(os.path.join(parent_folder18,'gui'))

from videoOut_dialog import VideoOut_window

class VideoOutForm(QWidget):
    def __init__(self, workdir,callback):
        super(VideoOutForm, self).__init__()  # 继承的所有父类的初始化
        self.ui = VideoOut_window()
        self.ui.setupUi(self)
        self.path_prefix = workdir
        self.callback=callback
        self.initConstant()

        # 窗体居中显示
        screen_size = QDesktopWidget().screenGeometry()  # 获得屏幕的尺寸
        widget_size = self.geometry()  # 获得窗体的尺寸
        self.move((screen_size.width() - widget_size.width()) / 2, (screen_size.height() - widget_size.height()) / 2)
        self.setWindowTitle(u'设置导出视频参数')
    # def closeEvent(self, event):
    #     QWidget.closeEvent(self, event)
    #     #if self.video_name==None or self.video_saveDir==None:
    #     reply = QMessageBox.question(self, 'Next', '确定放弃导出视频退出吗？', QMessageBox.No | QMessageBox.Yes)
    #     if reply == QMessageBox.Yes:
    #         self.close()
    #     else:
    #         pass

        #self.close()

    def initConstant(self):
        self.video_name=None
        self.video_type='mp4'
        self.video_fps=22
        self.video_scale=1.0
        self.video_saveDir=None
        self.video_info={}

        #buttons绑定的函数
        self.ui.pushButton_accept.clicked.connect(self.accept_return)
        self.ui.pushButton_reject.clicked.connect(self.reject_return)
        self.ui.pushButton_choose.clicked.connect(self.getWorkDirectory)

        self.ui.comboBox.currentIndexChanged.connect(self.typeValueChanged)
        self.ui.comboBox.addItems(['mp4', 'avi'])
        self.ui.doubleSpinBox.valueChanged.connect(self.scaleValueChanged)
        self.ui.spinBox.valueChanged.connect(self.fpsValueChanged)

    def typeValueChanged(self):
        self.video_type=self.ui.comboBox.currentText()
        print('video_type type:{} value:{}'.format(type(self.video_type),self.video_type))

    def scaleValueChanged(self):
        self.video_scale=self.ui.doubleSpinBox.value()
        print('scale type:{} value:{}'.format(type(self.video_scale),self.video_scale))

    def fpsValueChanged(self):
        self.video_fps=self.ui.spinBox.value()
        print('fps type:{} value:{}'.format(type(self.video_fps),self.video_fps))

    # 显示提示框并定时消失
    def showInfoWindow(self,text,title):
        infoBox1 = QMessageBox(self)
        infoBox1.setText(text)
        infoBox1.setWindowTitle(title)
        infoBox1.setStandardButtons(QMessageBox.Ok)
        infoBox1.button(QMessageBox.Ok).animateClick(3 * 1000)
        infoBox1.exec_()

    # 选择存储路径
    def getWorkDirectory(self):
        directory=QFileDialog.getExistingDirectory(None,caption="选取文件夹目录",directory=self.path_prefix)
        self.ui.lineEdit_2.setText(directory)
        self.video_saveDir=directory
        print('dir type:{} value:{}'.format(type(self.video_saveDir), self.video_saveDir))

    def accept_return(self):
        self.video_name=self.ui.lineEdit.text()
        print('name type:{} value:{}'.format(type(self.video_name),self.video_name))
        if self.video_name == None or self.video_saveDir == None:
            if self.video_name == None:
                self.showInfoWindow('文件名不能为空!','Failure')
            elif self.video_saveDir == None:
                self.showInfoWindow('保存路径不能为空!', 'Failure')
        else:
            self.video_info['video_name ']= self.video_name
            self.video_info['video_type ']=self.video_type #str
            self.video_info['video_fps ']=self.video_fps #int
            self.video_info['video_scale']=self.video_scale #float
            self.video_info['video_saveDir']=self.video_saveDir

            print('callback')
            self.callback(self.video_info)
            self.close()

    def reject_return(self):
        #self.closeEvent( )
        reply = QMessageBox.question(self, 'Next', '确定放弃导出视频退出吗？', QMessageBox.No | QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            #self.closeEvent(event=None)
            #self.exec_()
            self.close()
        else:
            pass


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     default_workdir='/home/wanwanvv/workspace/osvos/car-shadow'
#     ex = VideoOutForm(default_workdir)
#     ex.show()
#     sys.exit(app.exec_())
