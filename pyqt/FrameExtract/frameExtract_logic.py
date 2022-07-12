import shutil

import cv2
import sys,os

from PyQt5.QtGui import QImage, QPixmap, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QFileDialog, QMessageBox, QListWidgetItem, QListView
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import QThread,Qt

#引入本地库
root_folder20 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder20=os.path.dirname(root_folder20 )
resources_folder20=os.path.join(parent_folder20,'resources')
sys.path.append(parent_folder20)
sys.path.append(os.path.join(parent_folder20,'gui'))
sys.path.append(os.path.join(parent_folder20,'FrameExtract'))
sys.path.append(os.path.join(parent_folder20,'direct'))
sys.path.append(os.path.join(parent_folder20,'bubbleNets'))
from frameExtract_window import FrameExtractForm
from video_to_frames import defaultExtract_thread
from difference_video_to_frames import differenceExtract_thread
from cluster_video_to_frames import clusterExtract_thread
from flow_video_to_frames import flowExtract_thread
from MgrHelper import MgrHelper
from bubbleNets_logic import BubbleNetsForm
from osvos_logic import OsvosForm
#************************************主类***********************************
class FrameExtractWindow(QWidget):
    resized = QtCore.pyqtSignal()  # 缩放信号
    def __init__(self,workdir,direct_object):
        super(FrameExtractWindow, self).__init__()  # 继承的所有父类的初始化
        self.ui=FrameExtractForm()
        self.ui.setupUi(self)
        # *************path*******************
        self.path_prefix = workdir  # 工作目录
        self.direct_object=direct_object
        # **************path********************
        # resize关联函数
        self.initConstant()
        self.initUI()
        self.adjustUI()

    def closeEvent(self, event):
        print('执行了closeEvent')
        QWidget.closeEvent(self, event)
        # self.direct_object.close()
        self.close()

    def adjustUI(self):
        helper = MgrHelper.Instance()
        navButtonSize=25
        helper.setFontIcon(self.ui.pushButton_return,0xf015,navButtonSize)
        helper.setFontIcon(self.ui.pushButton_next,0xf061,navButtonSize)
        self.ui.pushButton_return.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.pushButton_next.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.pushButton_next.setStyleSheet("QPushButton{background-color:#4a93ca;"
                                                  #"border-radius:5px"
                                                  "border:none;"
                                                  #"color:#ffffff;"
                                                  #"font-size:12px;"
                                                  "font-family:Microsoft Yahei;}"
                                      "QPushButton:hover{background-color:#ea5e00;}"
                                      "QPushButton:pressed{background-color:#002030;}")
        self.ui.pushButton_return.setStyleSheet("QPushButton{background-color:#4a93ca;"
                                              "border:none;"
                                              # "color:#ffffff;"
                                              # "font-size:12px;"
                                              "font-family:Microsoft Yahei;}"
                                              "QPushButton:hover{background-color:#ea5e00;}"
                                              "QPushButton:pressed{background-color:#002030;}")
        self.ui.label_title.setStyleSheet("QLabel{background-color:#4a93ca;"
                                        "border:none;"
                                        "color:#ffffff;"
                                        "font:bold;"
                                        "font-size:20px;"
                                        "font-family:Meiryo UI;"
                                        "qproperty-alignment:AlignCenter;}")
        #顶部导航栏两个按钮
        self.ui.pushButton_return.clicked.connect(self.returnButtonPressed)
        self.ui.pushButton_next.clicked.connect(self.nextButtonPressed)

    def returnButtonPressed(self):
        print('return按钮被按下')
        self.direct_object.show()
        print('direct_object.show')
        #direct_widget=DirectForm()
        #direct_widget.show()
        self.close()

    def nextButtonPressed(self):
        self.osvos_object=OsvosForm(self.path_prefix,self.direct_object)
        self.bubblenet_widget = BubbleNetsForm(self.path_prefix,self.direct_object,self.osvos_object,2,None)
        self.bubblenet_widget.show()
        self.close()

    # def closeEvent(self, event):
    # 重写resizeEvent事件
    def resizeEvent(self, event):
        self.resized.emit()
        return super(FrameExtractWindow,self).resizeEvent(event)

    def initConstant(self):
        self.video_path=None #源视频文件目录
        self.video_name=None #源视频文件名称
        self.curr_img=None #当前显示的图片全路径
        self.curr_img_index=0 #当前显示的图片index
        self.curr_img_name = 0  # 当前显示的图片名
        self.frameWidth = 0
        self.frameHeight = 0
        self.extract_type=0 #抽取关键帧的方式
        self.result_path=None #默认保存路径
        self.user_result_path=None #自行选择的保存路径
        self.frames_length=0 #帧图片数
        self.frame_names = [] #所有帧的name list
        self.frame_paths = []  #所有帧的路径list
        self.scaleFactor=1.0 #label的缩放比例
        self.scaleFactor1 = 1.0 #listWidget中的缩放比例
        self.iconWidth =0 # icon宽度
        self.iconHeight = 0 #icon高度
        #多线程变量
        self.extractThreadActive = False
        self.extract_threads_pool = [None, None, None, None, None]
        self.extract_thread_cnt=-1

    def reinitConstant(self):
        self.frames_length = 0  # 帧图片数
        self.frame_names = []  # 所有帧的name list
        self.frame_paths = []  # 所有帧的路径list
        self.curr_img = None  # 当前显示的图片全路径
        self.curr_img_index = 0  # 当前显示的图片index
        self.frameWidth = 0
        self.frameHeight = 0

    def initUI(self):
        # 窗体居中显示
        screen_size = QDesktopWidget().screenGeometry()  # 获得屏幕的尺寸
        widget_size = self.geometry()  # 获得窗体的尺寸
        self.move((screen_size.width() - widget_size.width()) / 2,
                  (screen_size.height() - widget_size.height()) / 2)
        self.ui.frame.setProperty('flag', 'nav')
        self.setWindowTitle(u'抽取关键帧')
        self.navBtnWidth = 45  # 上方导航条上按钮宽度
        self.navIconFontSize = 20  # 上方导航条上图标字体的大小

        # 标题栏
        # qss_label_title = []
        # qss_label_title.append('QLabel#label_title{{font:{}px;}}'.format(self.navIconFontSize))
        # # qss_label_title.append('QFrame[flag="nav"]{{background:qlineargradient'
        # # '(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 {},stop:1 {});}}'.format('#FFFFFF','#FFFFFF'))
        # qss_label_title.append('QFrame[flag="nav"] QAbstractButton{{background:none;border:none;'
        #                        'min-width:{0}px;max-width:{0}px;}}'.format(self.navBtnWidth))
        # self.setStyleSheet(''.join(qss_label_title))

        # 播放按钮相关变量和美化
        self.isPlay = True  # True表示显示的是play

        #comboBox
        self.extract_type_list=['帧差法','自适应聚类','光流法']
        self.ui.comboBox_type.addItems(self.extract_type_list)
        self.ui.comboBox_type.setCurrentIndex(0)
        self.ui.comboBox_type.currentIndexChanged.connect(self.typeValueChanged)

        # 初始按键设置
        # 按键关联函数
        self.ui.pushButton_open.clicked.connect(self.openVideoButtonpressed)
        self.ui.pushButton_start.clicked.connect(self.startExtractFrames)

        #　listWidget
        #self.ui.listWidget.itemDoubleClicked.connect(self.item_double_clicked)
        self.ui.listWidget.itemClicked.connect(self.item_clicked)

    #comboBox改变函数
    def typeValueChanged(self):
        self.extract_type=self.ui.comboBox_type.currentIndex()
        print("self.extract_type:{}".format(self.extract_type))

    # 打开视频按钮按下
    def openVideoButtonpressed(self):
        filename_choose,filetype=QFileDialog.getOpenFileName(self,"选取视频",self.path_prefix,'MP4 file(*.mp4);;AVI file(*.avi);;MPEG file(.mpeg*);;RMVB file(＊.rmvb);;WMV file(*.wmv)')
        if filename_choose=="":
            print("选取视频文件为空")
            return
        print(filename_choose)
        self.video_path=filename_choose
        self.ui.lineEdit_video_path.setText(self.video_path)
        #获取视频名字
        self.video_name=self.video_path.split('/')[-1].split('.')[0]
        print('self.video_name:{}'.format(self.video_name))
        result_path_name=self.video_name+"_JPEGImages"
        self.result_path=os.path.join(self.path_prefix,result_path_name)
        if os.path.exists(self.result_path):
            self.removeTmpDir(self.result_path)
        os.makedirs(self.result_path)
        print("self.result_path:{}".format(self.result_path))
        #开始以默认方式裁帧,多线程
        #default_video_to_frames(self.video_path, self.result_path)
        #　按钮设置
        self.ui.pushButton_start.setEnabled(False)
        self.ui.pushButton_open.setEnabled(False)
        self.ui.pushButton_next.setEnabled(False)
        self.ui.pushButton_return.setEnabled(False)

        # 多线程
        self.extractThreadActive = True
        self.extract_thread_cnt += 1
        self.extract_threads_pool[self.extract_thread_cnt % 5] = None
        self.extract_threads_pool[self.extract_thread_cnt % 5] = QThread()
        self.extractWork = defaultExtract_thread(self.video_path,self.result_path)
        self.extractWork.moveToThread(self.extract_threads_pool[self.extract_thread_cnt % 5])
        self.extract_threads_pool[self.extract_thread_cnt % 5].started.connect(self.extractWork.default_ExtractFrames_work)
        self.extractWork.finishExtract_signal.connect(self.finishExtract_default)
        self.extract_threads_pool[self.extract_thread_cnt % 5].start()

    def finishExtract_default(self,frames_length):
        self.reinitConstant()
        print('finishExtract_default')
        self.frames_length=frames_length
        print("self.frames_length:{}".format(self.frames_length))
        self.frame_names = self.getImageNames(self.result_path)
        self.frame_paths=self.getImagePathes(self.result_path)
        self.extractThreadActive = False
        self.extractWork.finishExtract_signal.disconnect(self.finishExtract_default)
        self.extract_threads_pool[self.extract_thread_cnt % 5].quit()
        self.extract_threads_pool[self.extract_thread_cnt % 5].wait()
        self.extract_threads_pool[self.extract_thread_cnt % 5].deleteLater()
        #　显示视频帧路径到label
        self.ui.label.setText("当前视频帧路径为: "+self.result_path)
        #显示图片到label
        self.curr_img_index=0
        self.load_img(self.curr_img_index)
        #显示图片到list
        self.showListImages()
        # 　按钮设置
        self.ui.pushButton_start.setEnabled(True)
        self.ui.pushButton_open.setEnabled(True)
        self.ui.pushButton_next.setEnabled(True)
        self.ui.pushButton_return.setEnabled(True)

    def showListImages(self):
        listwidget_size = self.ui.listWidget.size()
        # 计算缩放比例
        self.scaleFactor1 = self.frameWidth / listwidget_size.width()
        self.iconWidth = listwidget_size.width()
        self.iconHeight = int(self.frameHeight / self.scaleFactor1)
        self.ui.listWidget.clear()
        self.ui.listWidget.setViewMode(QListView.IconMode)
        self.ui.listWidget.setIconSize(QtCore.QSize(self.iconWidth, self.iconHeight))
        self.ui.listWidget.setResizeMode(QListView.Adjust)
        self.ui.listWidget.setMovement(QListView.Static)  # Listview显示状态
        # self.ui.listWidget.setMaximumHeight() #设置最大高宽
        self.ui.listWidget.setSpacing(12)  # 间距大小
        for idx, file_path in enumerate(self.frame_paths):
            item = QListWidgetItem(QtGui.QIcon(file_path), self.frame_names[idx])
            item.setTextAlignment(QtCore.Qt.AlignHCenter)
            item.setFlags(item.flags() ^ Qt.ItemIsUserCheckable)
            # if self._has_label_file(idx):
            #     item.setCheckState(Qt.Checked)
            # else:
            #     item.setCheckState(Qt.Unchecked)
            self.ui.listWidget.addItem(item)

    # listWidget单击关联函数
    def item_clicked(self, item):
        currentRow = self.ui.listWidget.currentRow()
        currentIndex = self.ui.listWidget.currentIndex()
        self.curr_img_index=currentRow
        self.load_img(self.curr_img_index)

    # 开始裁帧
    def startExtractFrames(self):
        if self.video_path=="" or self.video_path==None:
            infoBox = QMessageBox(self)
            infoBox.setText('请先选择要处理的视频!')
            infoBox.setWindowTitle('Warning')
            infoBox.setStandardButtons(QMessageBox.Ok)
            infoBox.button(QMessageBox.Ok).animateClick(1 * 1000)
            infoBox.exec_()
            return
        # if self.extract_type==None:
        #     infoBox = QMessageBox(self)
        #     infoBox.setText('请先选择抽帧的方式extract_type!')
        #     infoBox.setWindowTitle('Warning')
        #     infoBox.setStandardButtons(QMessageBox.Ok)
        #     infoBox.button(QMessageBox.Ok).animateClick(1 * 1000)
        #     infoBox.exec_()
        #     return
        #选择存储路径
        dir_choose=QFileDialog.getExistingDirectory(self,"选择保存文件夹",self.path_prefix)
        if dir_choose=="":
            infoBox = QMessageBox(self)
            infoBox.setText('目录不能为空!')
            infoBox.setWindowTitle('Warning')
            infoBox.setStandardButtons(QMessageBox.Ok)
            infoBox.button(QMessageBox.Ok).animateClick(1 * 3000)
            infoBox.exec_()
            return
        #result_path
        self.result_path=dir_choose
        print("用户选择的self.result_path:{}".format(self.result_path))

        # 　按钮设置
        self.ui.pushButton_start.setEnabled(False)
        self.ui.pushButton_open.setEnabled(False)
        self.ui.pushButton_next.setEnabled(False)
        self.ui.pushButton_return.setEnabled(False)

        if self.extract_type==0:#帧差法
            # 多线程
            self.extractThreadActive = True
            self.extract_thread_cnt += 1
            self.extract_threads_pool[self.extract_thread_cnt % 5] = None
            self.extract_threads_pool[self.extract_thread_cnt % 5] = QThread()
            self.extractWork1 = differenceExtract_thread(self.video_path, self.result_path)
            self.extractWork1.moveToThread(self.extract_threads_pool[self.extract_thread_cnt % 5])
            self.extract_threads_pool[self.extract_thread_cnt % 5].started.connect(self.extractWork1.difference_ExtractFrames_work)
            self.extractWork1.finishDifferenceExtract_signal.connect(self.finishExtract_difference)
            self.extract_threads_pool[self.extract_thread_cnt % 5].start()
        elif self.extract_type==1:#自适应聚类
            # 多线程
            self.extractThreadActive = True
            self.extract_thread_cnt += 1
            self.extract_threads_pool[self.extract_thread_cnt % 5] = None
            self.extract_threads_pool[self.extract_thread_cnt % 5] = QThread()
            self.extractWork2 = clusterExtract_thread(self.video_path, self.result_path)
            self.extractWork2.moveToThread(self.extract_threads_pool[self.extract_thread_cnt % 5])
            self.extract_threads_pool[self.extract_thread_cnt % 5].started.connect(self.extractWork2.cluster_ExtractFrames_work)
            self.extractWork2.finishClusterExtract_signal.connect(self.finishExtract_cluster)
            self.extract_threads_pool[self.extract_thread_cnt % 5].start()
        elif self.extract_type==2:#光流法
            # 多线程
            self.extractThreadActive = True
            self.extract_thread_cnt += 1
            self.extract_threads_pool[self.extract_thread_cnt % 5] = None
            self.extract_threads_pool[self.extract_thread_cnt % 5] = QThread()
            self.extractWork3 = flowExtract_thread(self.video_path, self.result_path)
            self.extractWork3.moveToThread(self.extract_threads_pool[self.extract_thread_cnt % 5])
            self.extract_threads_pool[self.extract_thread_cnt % 5].started.connect(self.extractWork3.flow_ExtractFrames_work)
            self.extractWork3.finishFlowExtract_signal.connect(self.finishExtract_flow)
            self.extract_threads_pool[self.extract_thread_cnt % 5].start()

    def finishExtract_flow(self,result_path):
        self.reinitConstant()
        print('finishExtract_flow')
        print("result_path:{}".format(result_path))
        self.frame_names = self.getImageNames(self.result_path)
        self.frame_paths=self.getImagePathes(self.result_path)
        self.extractThreadActive = False
        self.extractWork3.finishFlowExtract_signal.disconnect(self.finishExtract_flow)
        self.extract_threads_pool[self.extract_thread_cnt % 5].quit()
        self.extract_threads_pool[self.extract_thread_cnt % 5].wait()
        self.extract_threads_pool[self.extract_thread_cnt % 5].deleteLater()
        #　显示视频帧路径到label
        self.ui.label.setText("当前视频帧路径为: "+self.result_path)
        #显示图片到label
        self.curr_img_index=0
        self.load_img(self.curr_img_index)
        #显示图片到list
        self.showListImages()
        # 　按钮设置
        self.ui.pushButton_start.setEnabled(True)
        self.ui.pushButton_open.setEnabled(True)
        self.ui.pushButton_next.setEnabled(True)
        self.ui.pushButton_return.setEnabled(True)

    def finishExtract_difference(self,result_path):
        self.reinitConstant()
        print('finishExtract_difference')
        print("result_path:{}".format(result_path))
        self.frame_names = self.getImageNames(self.result_path)
        self.frame_paths=self.getImagePathes(self.result_path)
        self.extractThreadActive = False
        self.extractWork1.finishDifferenceExtract_signal.disconnect(self.finishExtract_difference)
        self.extract_threads_pool[self.extract_thread_cnt % 5].quit()
        self.extract_threads_pool[self.extract_thread_cnt % 5].wait()
        self.extract_threads_pool[self.extract_thread_cnt % 5].deleteLater()
        #　显示视频帧路径到label
        self.ui.label.setText("当前视频帧路径为: "+self.result_path)
        #显示图片到label
        self.curr_img_index=0
        self.load_img(self.curr_img_index)
        #显示图片到list
        self.showListImages()
        # 　按钮设置
        self.ui.pushButton_start.setEnabled(True)
        self.ui.pushButton_open.setEnabled(True)
        self.ui.pushButton_next.setEnabled(True)
        self.ui.pushButton_return.setEnabled(True)

    def finishExtract_cluster(self,result_path):
        self.reinitConstant()
        print('finishExtract_cluster')
        print("result_path:{}".format(result_path))
        self.frame_names = self.getImageNames(self.result_path)
        self.frame_paths=self.getImagePathes(self.result_path)
        self.extractThreadActive = False
        self.extractWork2.finishClusterExtract_signal.disconnect(self.finishExtract_cluster)
        self.extract_threads_pool[self.extract_thread_cnt % 5].quit()
        self.extract_threads_pool[self.extract_thread_cnt % 5].wait()
        self.extract_threads_pool[self.extract_thread_cnt % 5].deleteLater()
        #　显示视频帧路径到label
        self.ui.label.setText("当前视频帧路径为: "+self.result_path)
        #显示图片到label
        self.curr_img_index=0
        self.load_img(self.curr_img_index)
        #显示图片到list
        self.showListImages()
        # 　按钮设置
        self.ui.pushButton_start.setEnabled(True)
        self.ui.pushButton_open.setEnabled(True)
        self.ui.pushButton_next.setEnabled(True)
        self.ui.pushButton_return.setEnabled(True)


    #*****************工具函数**********************
    def removeTmpDir(self,rootdir):
        filelist = os.listdir(rootdir)
        if filelist:
            for f in filelist:
                filepath = os.path.join(rootdir, f)
            if os.path.isfile(filepath):
                os.remove(filepath)
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath, True)
        shutil.rmtree(rootdir, True)

    # 判断是否是图片
    def _is_img(self, file_name):
        ext = file_name.split('.')[-1]
        return ext in ['jpg', 'jpeg', 'png', 'bmp']

    def getImageNames(self,img_path):
        file_list = sorted([name for name in os.listdir(img_path) if self._is_img(name)])
        return file_list

    def getImagePathes(self,imgs_path):
        file_list = sorted([name for name in os.listdir(imgs_path) if self._is_img(name)])
        full_file_list=[]
        for img_name in file_list:
            img_path=os.path.join(imgs_path,img_name)
            full_file_list.append(img_path)
        return full_file_list

    def load_img(self,img_id):
        try:
            with open(self.frame_paths[img_id], 'rb') as f:
                img_data = f.read()
        except Exception as e:
            QMessageBox.warning(self, 'Warning', str(e))
            return

        img = QImage.fromData(img_data)
        if img.isNull():
            QMessageBox.warning(self, 'Warning', 'Invalid Image')
            return False

        pixmap = QPixmap.fromImage(img)
        self.frameWidth=pixmap.size().width()
        self.frameHeight=pixmap.size().height()
        a=self.ui.label_curr_img.size()
        #计算缩放比例
        if a.width()/self.frameWidth<a.height()/self.frameHeight:
            self.scaleFactor=a.width()/self.frameWidth
            self.startx=0
            self.starty=(a.height()-self.scaleFactor*self.frameHeight)/2
        else:
            self.scaleFactor=a.height()/self.frameHeight
            self.starty=0
            self.startx=(a.width()-self.scaleFactor*self.frameWidth)/2.0

        pixmap=pixmap.scaled(int(self.frameWidth*self.scaleFactor),int(self.frameHeight*self.scaleFactor),Qt.KeepAspectRatio)
        self.ui.label_curr_img.setPixmap(pixmap)
        self.curr_img=self.frame_paths[img_id]
        self.curr_img_name=self.frame_names[img_id]
        #self.ui.dockWidget.setWindowTitle(self.curr_img_name)
        return True


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     #default_workdir = '/home/wanwanvv/workspace/osvos/car-shadow'
#     default_workdir = '/home/wanwanvv/workspace/video_extract_workspace'
#     mainWindow = FrameExtractWindow(default_workdir)
#     mainWindow.show()
#     sys.exit(app.exec_())