import os
import shutil
import sys
import cv2
from time import sleep
from threading import Timer
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import QThread,Qt
from PyQt5.QtGui import QImage, QPixmap, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QDesktopWidget, QInputDialog
import pynput
import numpy as np
from PIL import Image

#************path均最后不带'/'**********
root_folder = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder=os.path.dirname(root_folder )
sys.path.append(parent_folder)
sys.path.append(os.path.join(parent_folder,'gui'))
sys.path.append(os.path.join(parent_folder,'direct'))
sys.path.append(os.path.join(parent_folder,'OSVOS'))
sys.path.append(os.path.join(parent_folder,'bubbleNets'))
sys.path.append(os.path.join(parent_folder,'InteSeg'))
sys.path.append(os.path.join(parent_folder,'Removal'))
#************path**********
from gui import osvos_window
from osvos import finetuneThread
from RGMP_thread import VosRGMP_thread
from osvos_window import osvos_form
from bubbleNets_logic import BubbleNetsForm
from MgrHelper import MgrHelper
from remove_logic import RemoveObjectForm
#********************训练模型的类和函数*********************

#信号类用来发射标准输出作为信号
class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self,text):
        self.textWritten.emit(str(text))

#********************训练模型的类和函数*********************

#********************左边展示分割结果的类和函数*********************
def removeTmpDir(rootdir):
    filelist=os.listdir(rootdir)
    if filelist:
        for f in filelist:
            filepath=os.path.join(rootdir,f)
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath,True)
    shutil.rmtree(rootdir,True)

def getResultsMaskImages(path):
    results_images=[]
    images=sorted(os.listdir(path))
    img_num=len(images)
    for i in range(img_num):
        img=os.path.join(path,images[i])
        results_images.append(img)
    return results_images

def getSrcImages(path):
    results_images=[]
    images=sorted(os.listdir(path))
    img_num=len(images)
    for i in range(img_num):
        img=os.path.join(path,images[i])
        results_images.append(img)
    return results_images

def preprocessShowImgae(srcImage,maskImage,scale):
    overlay_color=[255,0,0]
    transparency=0.6
    img = np.array(Image.open(srcImage))
    mask = np.array(Image.open(maskImage))
    mask=mask//np.max(mask)
    im_over=np.ndarray(img.shape)
    nchannel = cv2.imread(srcImage).shape[2]

    im_over[:, :, 0] = (1 - mask) * img[:, :, 0] + mask * (overlay_color[0] * transparency + (1 - transparency) * img[:, :, 0])
    im_over[:, :, 1] = (1 - mask) * img[:, :, 1] + mask * (overlay_color[1] * transparency + (1 - transparency) * img[:, :, 1])
    im_over[:, :, 2] = (1 - mask) * img[:, :, 2] + mask * (overlay_color[2] * transparency + (1 - transparency) * img[:, :, 2])
    limg2=im_over.astype(np.uint8)

    #limg2 = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    timg = cv2.resize(limg2, (int(scale * limg2.shape[1]), int(scale* limg2.shape[0]))) #cv2.resize(w,h)
    limage = QtGui.QImage(timg.data, timg.shape[1], timg.shape[0], nchannel * timg.shape[1], QtGui.QImage.Format_RGB888)
    #print("preprocess image over:nchannel is {},width is {},height is {}".format(nchannel, timg.shape[1], timg.shape[0]))
    return limage

class workerThread(QThread):
    updatedM=QtCore.pyqtSignal(int)#信号,int是信号承载数据的类型

    def __init__(self,mw):
        self.mw=mw
        QThread.__init__(self)

    def run(self):#通过.Start()调用此run()函数
        itr=0
        #在执行耗时操作的地方添加,使得一边执行耗时程序一边刷新界面，让人感觉界面很流畅
        QApplication.processEvents()
        while self.mw.isRun:
            itr+=1

            if self.mw.isthreadActive and self.mw.isbusy==False and self.mw.frameID!=self.mw.currentID:
                #print(itr)

                if self.mw.timer is None:
                    self.mw.frameID+=1
                self.mw.isbusy=True
                sf=self.mw.scaleFactor
                if sf<=0:
                    self.mw.isbusy=False
                    continue
                #if image is None or mask_image is None:
                if self.mw.frameID>=self.mw.length:
                    self.mw.ui.pushButton_left6.setEnabled(False)
                    self.mw.ui.pushButton_left5.setEnabled(True)
                    if not self.mw.timer is None:
                        self.mw.timer.cancel()
                    self.mw.isthreadActive=False
                    self.mw.isbusy=False
                    continue
                self.mw.currentID = self.mw.frameID
                src_img=self.mw.srcImages[self.mw.currentID]
                mask_img=self.mw.maskImages[self.mw.currentID]
                image=cv2.imread(src_img)
                mask_image=cv2.imread(mask_img)
                #self.maskImages=[]
                self.mw.limg=image
                if self.mw.isInit==True:
                    self.mw.on_zoomfit_clicked()
                    self.mw.isInit=False
                limage=preprocessShowImgae(src_img,mask_img,self.mw.scaleFactor)
                if self.mw.resizegoing==False:
                    self.mw.ui.leftImage.setPixmap(QtGui.QPixmap(limage))
                    if not self.mw.sliderbusy and not self.mw.sliderbusy2:
                        self.updatedM.emit(self.mw.frameID)
                    QApplication.processEvents()
                self.mw.isbusy=False
            else:
                if self.mw.isthreadActive and self.mw.timer is None:
                    self.mw.frameID+=1
                sleep(1.0/50)

#********************左边展示分割结果的类和函数*********************

#********************右边播放视频的类和函数*********************
def video_to_frames(result_path,video_path):
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    capture = cv2.VideoCapture(video_path)
    num = 0
    while True:
        ret, img = capture.read()
        if not ret:
            break
        picname = '{:05d}.jpg'.format(num)
        cv2.imwrite(os.path.join(result_path, picname), img)
        num += 1
    capture.release()

#过一段时间调用一次函数使用定时器
class perpetualTimer():
    def __init__(self,t,hFunction):
        self.t=t
        self.hFunction=hFunction
        self.thread=Timer(self.t,self.handle_function) #每隔t秒执行一次handle_function

    def handle_function(self):
        self.hFunction()
        self.thread=Timer(self.t,self.handle_function)
        self.thread.start()
    def start(self):
        self.thread.start()
    def cancel(self):
        self.thread.cancel()

#将videocapture读取到的帧进行处理以便显示在QLabel上
def preprocessImage(img,scale):
    frame = img
    # self.on_zoomfit_clicked()
    nchannel = frame.shape[2]
    limg2 = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    timg = cv2.resize(limg2, (int(scale * limg2.shape[1]), int(scale* limg2.shape[0])))
    limage = QtGui.QImage(timg.data, timg.shape[1], timg.shape[0], nchannel * timg.shape[1], QtGui.QImage.Format_RGB888)
    #print("preprocess image over:nchannel is {},width is {},height is {}".format(nchannel, timg.shape[1], timg.shape[0]))
    return limage

#根据frameID进行图片的更新 
class workerThread1(QThread):
    updatedM=QtCore.pyqtSignal(int)#信号,int是信号承载数据的类型

    def __init__(self,mw):
        self.mw=mw
        QThread.__init__(self)

    # def __del__(self):#析构器，对象被销毁时调用
    #     self.wait()

    def run(self):#通过.Start()调用此run()函数
        itr=0
        #在执行耗时操作的地方添加,使得一边执行耗时程序一边刷新界面，让人感觉界面很流畅
        QApplication.processEvents()
        while self.mw.isRun1:
            itr+=1

            if self.mw.isthreadActive1 and self.mw.isbusy1==False and self.mw.frameID1!=self.mw.cap1.get(cv2.CAP_PROP_POS_FRAMES):
                #print(itr)
                if np.abs(self.mw.frameID1-self.mw.cap1.get(cv2.CAP_PROP_POS_FRAMES))>1:
                    self.mw.cap1.set(cv2.CAP_PROP_POS_FRAMES,self.mw.frameID1)
                if self.mw.timer1 is None:
                    self.mw.frameID1+=1
                self.mw.isbusy1=True
                sf=self.mw.scaleFactor1
                ret,image=self.mw.cap1.read()
                self.mw.limg1=image
                if sf<=0:
                    self.mw.isbusy1=False
                    continue
                if ret==False:
                    if self.mw.frameID1>=self.mw.length1:
                        self.mw.ui.pushButton_right3.setEnabled(False)
                        self.mw.ui.pushButton_right2.setEnabled(True)
                        if not self.mw.timer1 is None:
                            self.mw.timer1.cancel()
                    self.mw.isthreadActive1=False
                    self.mw.isbusy1=False
                    continue
                limage=preprocessImage(image,self.mw.scaleFactor1)

                if self.mw.resizegoing1==False:
                    self.mw.ui.rightImage.setPixmap(QtGui.QPixmap(limage))
                    if not self.mw.sliderbusy_right and not self.mw.sliderbusy2_right:
                        self.updatedM.emit(self.mw.frameID1)
                    QApplication.processEvents()
                self.mw.isbusy1=False
            else:
                if self.mw.isthreadActive1 and self.mw.timer1 is None:
                    self.mw.frameID1+=1
                sleep(1.0/50)
#********************右边播放视频的类和函数*********************

class OsvosForm(QWidget):
    resized=QtCore.pyqtSignal() #缩放信号
    def __init__(self,workdir,direct_object):
        super(OsvosForm, self).__init__()  # 继承的所有父类的初始化
        self.ui=osvos_form()
        self.ui.setupUi(self)
        #窗体居中显示
        screen_size=QDesktopWidget().screenGeometry()#获得屏幕的尺寸
        widget_size=self.geometry()#获得窗体的尺寸
        self.move((screen_size.width()-widget_size.width())/2,(screen_size.height()-widget_size.height())/2)
        self.setWindowTitle(u'视频目标分割')
        #sys.stdout=EmittingStream(textWritten=self.outputWritten)
        #sys.stderr=EmittingStream(textWritten=self.outputWritten)

        #self.setPalette(QPalette(QColor('#FFFFFF')))  # 背景颜色

        #*************path*******************
        self.model_folder = parent_folder + '/models'  # models所在目录
        self.path_prefix = workdir  # 工作目录
        self.direct_object=direct_object
        #**************path********************

        #*************右边播放视频的变量*********
        self.isFirstKey_right=False
        self.stframe1=0
        self.endframe1=0
        self.scaleFactor1 = 1.0  # 缩放比例
        self.length1=1
        self.frameID1 = 0 #第几帧
        self.isRun1 = True #未改变一直未TRUE
        self.resizegoing1 = False #当进行放缩调整时为True
        self.sliderbusy_right = False #进度条被按下时为True，放松时即无操作为False
        self.sliderbusy2_right = False #视频逐帧向前播放反过来让进度条值变化时为True
        self.ui.pushButton_right1.setEnabled(True)
        self.ui.pushButton_right2.setEnabled(False)
        self.ui.pushButton_right3.setEnabled(False)
        self.ui.pushButton_right1.clicked.connect(self.openButtonPressed1)
        self.ui.pushButton_right2.clicked.connect(self.startButtonPressed1)
        self.ui.horizontalSlider_right.sliderPressed.connect(self.horizontalSliderPressed1)
        self.ui.horizontalSlider_right.sliderReleased.connect(self.horizontalSliderReleased1)
        self.ui.horizontalSlider_right.valueChanged.connect(self.slider_value_changed1)
        #self.ui.rightImage.setScaledContents(True)#自适应图片大小
        self.ui.pushButton_right3.clicked.connect(self.pauseButtonPressed1)
        self.resized.connect(self._on_resized1)
        self.videoTIme=0
        self.startx1 = 0
        self.starty1 = 0
        self.isVideo1 = False #capture已经打开视频
        self.isbusy1 = 0
        self.frameHeight1 = 1
        self.frameWidth1 = 1
        self.limg1 = np.zeros((1, 1, 1))
        self.cap1 = None
        self.timer1 = None
        self.isthreadActive1 = False#开始播放视频
        self.wthread1=workerThread1(self)
        self.wthread1.updatedM.connect(self.horizontalSliderSet1)
        self.wthread1.start()
        self.klistener1_right=pynput.keyboard.Listener(on_press=self.on_release1)
        self.klistener2_right = pynput.keyboard.Listener(on_release=self.on_press1)
        self.ui.horizontalSlider_right.setEnabled(False)
        self.ui.pushButton_right2.setEnabled(False)
        # *************右边播放视频的变量*********


        # *************左边展示分割结果的变量*********
        self.isFirstKey_left=False
        #模型快速还是慢速
        self.ui.comboBox_model.addItems(['Fast', 'Slow'])
        # 选择形状的comboBox的值改变关联函数
        self.ui.comboBox_model.currentIndexChanged.connect(self.modelValueChanged)
        self.model='Fast'
        self.stframe=0
        self.endframe=0
        self.fps = 22
        self.scaleFactor = 1.0  # 缩放比例
        self.length = 1
        self.frameID = 0  # 第几帧
        self.currentID = 0  # 显示的第几帧
        self.isRun = True  # 未改变一直为True
        self.resizegoing = False  # 当进行放缩调整时为True
        self.sliderbusy = False  # 进度条被按下时为True，放松时即无操作为False
        self.sliderbusy2 = False  # 视频逐帧向前播放反过来让进度条值变化时为True
        self.ui.pushButton_left1.setEnabled(True)
        #self.ui.pushButton_left2.setEnabled(False)
        # self.ui.pushButton_left3.setEnabled(False)
        # self.ui.pushButton_left4.setEnabled(False)
        self.ui.pushButton_left5.setEnabled(False)
        self.ui.pushButton_left6.setEnabled(False)

        self.ui.pushButton_left5.clicked.connect(self.startButtonPressed)
        self.ui.pushButton_left6.clicked.connect(self.pauseButtonPressed)

        self.ui.horizontalSlider_left.sliderPressed.connect(self.horizontalSliderPressed)
        self.ui.horizontalSlider_left.sliderReleased.connect(self.horizontalSliderReleased)
        self.ui.horizontalSlider_left.valueChanged.connect(self.slider_value_changed)

        self.resized.connect(self._on_resized)

        self.startx = 0
        self.starty = 0
        self.isVideo = False  # 已经显示图片
        self.isbusy = 0
        self.frameHeight = 1
        self.frameWidth = 1
        self.limg = np.zeros((1, 1, 1))
        # self.cap = None
        self.timer = None
        self.ui.textBrowser.setText('Finetune the model first!')
        print('\n')
        self.isthreadActive = False  # 开始播放视频
        self.wthread = workerThread(self)
        self.wthread.updatedM.connect(self.horizontalSliderSet)
        self.wthread.start()

        self.klistener1_left = pynput.keyboard.Listener(on_press=self.on_release)
        self.klistener2_left = pynput.keyboard.Listener(on_release=self.on_press)

        self.srcImages = []
        self.maskImages = []
        #self.initLeftImage()
        #存储分割结果的二值帧图
        self.result_dir = os.path.join(self.path_prefix, 'VosResults')
        self.vos_result_path = None
        self.ui.horizontalSlider_left.setEnabled(False)
        self.ui.pushButton_left5.setEnabled(False)
        # *************左边展示分割结果的变量*********

        # *************选择mask的变量*********
        self.ui.label_mask.openMaskSignal.connect(self.chooseMask) #双击打开文件夹选择mask
        self.resized.connect(self._on_resized2)
        self.curr_mask_img = None
        self.curr_mask_id = None
        self.mask_path=self.path_prefix
        #self.maskinfo = {}
        self.rgmpInfo = {}
        self.osvosInfo = {}
        # *************选择mask的变量*********

        # *************视频帧变量*********
        self.frames_path = os.path.join(self.path_prefix, 'JPEGImages')
        #self.file_list = sorted([name for name in os.listdir(self.frames_path) if self._is_img(name)])
        # *************视频帧变量*********

        #**************两个按键************
        #self.ui.commandLinkButton_next.clicked.connect(self.annoWindowExit)
        # **************两个按键************

        #*************训练模型的变量*********
        self.itertime=50
        self.cursor = self.ui.textBrowser.textCursor()
        self.cursor.movePosition(QtGui.QTextCursor.End)
        self.ui.textBrowser.setTextCursor(self.cursor)
        self.ui.textBrowser.ensureCursorVisible()
        self.ftThreadActive=False
        self.hasModel=False
        self.ui.pushButton_left1.clicked.connect(self.startFinetuneButtonPressed)
        self.ui.pushButton_left0.clicked.connect(self.startAnnotate)
        #self.ui.pushButton_left2.clicked.connect(self.stopFinetuneButtonPressed)
        #ivs
        self.ftThread_cnt=-1
        self.ftThreads_pool = [None, None, None, None, None]
        #ivs
        self.ImageSets_path=os.path.join(self.path_prefix,'ImageSets')
        # *************训练模型的变量*********
        self.adjustUI()

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
        self.direct_object.show()
        #direct_widget=DirectForm()
        #direct_widget.show()
        self.close()

    def nextButtonPressed(self):
        self.removal_widget=RemoveObjectForm(self.path_prefix,self.direct_object)
        self.removal_widget.show()
        self.close()

    def closeEvent(self, event):
        QWidget.closeEvent(self, event)
        # self.direct_object.close()
        self.close()

    #*************globle functions*********
    def resizeEvent(self,event):
        #print('resizeEvent')
        self.resized.emit()
        return super(OsvosForm,self).resizeEvent(event)

    def showCurrentTime(self, cnt, label):
        tsec = cnt / self.fps
        tmin = int(tsec / 60)  # 视频播放到的帧的整数分钟
        ttsec = int(tsec - 60 * tmin)  # 视频播放到的帧的整数秒钟
        ksec = tsec - 60 * tmin - ttsec  # 视频播放到的帧的小数秒钟
        ksec=int (ksec*100)
        # if ksec > 0.5:
        #     ttsec += 1
        label.setText(str(tmin).zfill(2) + ':' + str(ttsec).zfill(2) + ':' + str(ksec).zfill(2))
    #*************globle functions*********

    # *************选择mask的变量*********
    def callback(self,mask_list):
        print(mask_list)
        if mask_list==[]:
            return
        else:
            maskpic0=mask_list[0]
            self.mask_path=os.path.dirname(maskpic0)
            self.load_img(maskpic0)
            print('maskpic0:{}'.format(maskpic0))
            print('mask_path:{}'.format(self.mask_path))

    def _on_resized2(self):
        self.on_zoomfit_clicked2()

    def on_zoomfit_clicked2(self):
        sleep(0.2)
        if self.curr_mask_img!=None:
            self.load_img(self.curr_mask_img)

    # 加载图片并显示到label中
    def load_img(self, img_path):
        try:
            with open(img_path, 'rb') as f:
                img_data = f.read()
        except Exception as e:
            QMessageBox.warning(self, 'Warning', str(e))
            return

        img = QImage.fromData(img_data)
        if img.isNull():
            QMessageBox.warning(self, 'Warning', 'Invalid Image')
            return False

        pixmap = QPixmap.fromImage(img)
        pixmap = pixmap.scaled(int(self.ui.label_mask.width()),int(self.ui.label_mask.height()), Qt.KeepAspectRatio)
        # print(pixmap.size())
        self.ui.label_mask.setPixmap(pixmap)

        #设置mask参数
        self.curr_mask_img = img_path
        self.mask_path=os.path.dirname(self.curr_mask_img)
        picname = img_path.split('/')[-1].split('.')[0]
        if ('_' in picname) == True:
            self.curr_mask_id = int(picname.split('_')[0])
        else:
            self.curr_mask_id = int(picname)
        return True

    def chooseMask(self):
        filename_choose,filetype=QFileDialog.getOpenFileName(self,"选取目标mask",self.mask_path,"Image files(*.jpg *.png *.jpeg)")
        if filename_choose!="":
            self.load_img(filename_choose)
    # *************选择mask的变量*********

    # *************左边展示结果的函数*********
        ########左右按键 #########

    def modelValueChanged(self):
        self.model = self.ui.comboBox_model.currentText()

    def on_release(self, key):
        #if self.isRun:
        if key == pynput.keyboard.Key.left:
            print('按键left')
            self.horizontalSliderIncrease(-1)
        elif key == pynput.keyboard.Key.right:
            print('按键right')
            self.horizontalSliderIncrease(1)

    ########左右按键 #########

    def on_press(self, key):
        if self.isRun:
            if pynput.keyboard.Key.space == key:
                if self.ui.pushButton_left6.isEnabled():
                    self.pauseButtonPressed()
                else:
                    while (self.sliderbusy == True or self.resizegoing == True):
                        sleep(0.1)
                    self.startButtonPressed()

    #进度条值改变为0
    def slider_value_changed(self):
        if not self.isthreadActive:
            #print("slidervalue change")
            self.horizontalSliderIncrease(0)

    def horizontalSliderIncrease(self, val):
        if self.sliderbusy or self.resizegoing or self.stframe + self.ui.horizontalSlider_left.value()+val<0 or self.stframe + self.ui.horizontalSlider_left.value()+val>self.ui.horizontalSlider_left.maximum():
            return
        self.sliderbusy = True
        #print("current horizontalSlider_left value={}".format(self.ui.horizontalSlider_left.value()))
        #print("current left frameId={}".format(self.frameID))
        self.frameID = self.stframe + self.ui.horizontalSlider_left.value()+val
        #print("changed left frameId={}".format(self.frameID))
        if self.ui.pushButton_left5.isEnabled():
            self.currentID=self.frameID
            # src_img = self.srcImages[self.currentID]
            # mask_img = self.maskImages[self.currentID]
            # image = cv2.imread(src_img)
            # self.on_zoomfit_clicked()
            # self.limg = image
            # limage = preprocessShowImgae(src_img, mask_img, self.scaleFactor)
            # self.ui.leftImage.setPixmap(QtGui.QPixmap(limage))
            self.on_zoomfit_clicked()
            self.showCurrentTime(self.currentID, self.ui.label_time1)
            self.ui.horizontalSlider_left.setValue(self.frameID)
        self.sliderbusy = False

    def horizontalSliderSet(self, cnt):
        if cnt-self.stframe>self.ui.horizontalSlider_left.maximum() or self.sliderbusy or self.resizegoing:
            return
        self.sliderbusy2 = True
        self.ui.horizontalSlider_left.setValue(cnt - self.stframe)
        self.showCurrentTime(cnt,self.ui.label_time1)
        self.sliderbusy2 = False

    def horizontalSliderPressed(self):
        if self.ui.horizontalSlider_left.value()==self.ui.horizontalSlider_left.maximum():
            self.isthreadActive=True
        self.sliderbusy=True

    def horizontalSliderReleased(self):
        self.frameID = self.stframe + self.ui.horizontalSlider_left.value()
        if self.ui.pushButton_left5.isEnabled():
            self.currentID = self.frameID
            # src_img = self.srcImages[self.currentID]
            # mask_img = self.maskImages[self.currentID]
            # image = cv2.imread(src_img)
            # self.limg = image
            # limage = preprocessShowImgae(src_img, mask_img, self.scaleFactor)
            # self.ui.leftImage.setPixmap(QtGui.QPixmap(limage))
            self.on_zoomfit_clicked()
            self.showCurrentTime(self.currentID, self.ui.label_time1)
        self.sliderbusy = False

    def updateFrame(self):
        self.frameID += 1

    def on_zoomfit_clicked(self):
        #print('on_zoomfit_clicked')
        self.resizegoing=True
        a=self.ui.leftImage.size()
        if a.width()/self.frameWidth<a.height()/self.frameHeight:
            self.scaleFactor=a.width()/self.frameWidth
            self.startx=0
            self.starty=(a.height()-self.scaleFactor*self.frameHeight)/2
        else:
            self.scaleFactor=a.height()/self.frameHeight
            self.starty=0
            self.startx=(a.width()-self.scaleFactor*self.frameWidth)/2.0

        if self.isVideo==True:
            src_img = self.srcImages[self.currentID]
            mask_img = self.maskImages[self.currentID]
            #print('scaleFactor:{} isInit:{}'.format(self.scaleFactor,self.isInit))
            if self.scaleFactor <= 0.1 and self.isInit == True:
                self.scaleFactor = 0.604167
                self.isInit=False
            limage = preprocessShowImgae(src_img, mask_img, self.scaleFactor)
            self.ui.leftImage.setPixmap(QtGui.QPixmap(limage))
        # sleep(0.2)
        self.resizegoing=False

    def _on_resized(self):
        self.on_zoomfit_clicked()

    def startButtonPressed(self):
        if self.isthreadActive or self.ui.horizontalSlider_left.value()>=self.ui.horizontalSlider_left.maximum():
            return
        self.ui.pushButton_left5.setEnabled(False)
        self.timer=perpetualTimer(1.0/self.fps,self.updateFrame)
        self.timer.start()
        self.ui.pushButton_left6.setEnabled(True)
        self.isthreadActive=True

    def pauseButtonPressed(self):
        if not self.isthreadActive:
            return
        self.ui.pushButton_left5.setEnabled(True)
        self.ui.pushButton_left6.setEnabled(False)
        if not self.timer is None:
            self.timer.cancel()
        self.isthreadActive=False

    def initLeftImage(self):
        #print('初始化左边结果展示...')
        self.isInit=True
        src_img_path=self.frames_path
        result_mask_path=self.vos_result_path
        self.srcImages=getSrcImages(src_img_path)
        self.maskImages=getResultsMaskImages(result_mask_path)
        if len(self.srcImages)==0 or len(self.maskImages)==0 or len(self.srcImages)!=len(self.maskImages):
            QMessageBox.about(self, 'Warning', '处理的结果图像未准备好!')
            return
        else:
            self.isVideo=True
        self.length=len(self.maskImages)
        #print("total frames:{} fps:{}".format(self.length, self.fps))
        self.stframe=0
        self.endframe=self.length-1

        self.ui.horizontalSlider_left.setMaximum(self.endframe - self.stframe)
        #print("horiontalSLider_left maxMiun:{}".format(self.endframe - self.stframe))
        current_img=self.srcImages[self.stframe]
        current_mask=self.maskImages[self.stframe]
        self.currentID=self.stframe
        [height, width, pix] = cv2.imread(current_img).shape
        self.frameWidth=width
        self.frameHeight=height
        #self.on_zoomfit_clicked()
        if self.isInit==True:
            self.scaleFactor=0.604167
        #print('init leftImage-width:{} height:{}'.format(self.ui.leftImage.size().width(),self.ui.leftImage.size().height()))
        #print('init resultImage-frameWidth:{} frameHeight:{} scaleFactor:{}'.format(self.frameWidth,self.frameHeight,self.scaleFactor))
        #print("执行on_zoonfit_clicked,scaleFactor is {}".format(self.scaleFactor))

        limage = preprocessShowImgae(current_img,current_mask,self.scaleFactor)
        #print('第一帧显示成功!')
        #视频总时长
        self.showCurrentTime(self.length-1,self.ui.label_time2)
        #归０
        self.ui.label_time1.setText('00:00:00')
        self.horizontalSliderSet(0)
        self.ui.leftImage.setPixmap(QtGui.QPixmap(limage))
        #self.ui.textBrowser.setText('Ready to play segmentated video!')
        print('\n')
        self.ui.pushButton_left5.setEnabled(True)
        self.ui.pushButton_left6.setEnabled(False)
        self.ui.horizontalSlider_left.setEnabled(True)

    # *************左边展示结果的函数*********

    # *************右边播放视频的函数*********

    ########左右按键——前进后退#########
    def on_release1(self, key):
        #if self.isRun:
        if key == pynput.keyboard.Key.page_up:
            print('page_up')
            self.horizontalSliderIncrease1(1)
        elif key == pynput.keyboard.Key.page_down:
            print('page_down')
            self.horizontalSliderIncrease1(-1)

    ########左右按键-前进后退#########
    ########空格按键-播放暂停#########
    def on_press1(self, key):
        if self.isRun1:
            if pynput.keyboard.Key.enter == key:
                if self.ui.pushButton_right3.isEnabled():
                    self.pauseButtonPressed1()
                else:
                    while (self.sliderbusy_right == True or self.resizegoing1 == True):
                        sleep(0.1)
                    self.startButtonPressed1()
    ########空格按键-播放暂停#########
    # 进度条值改变为0
    def slider_value_changed1(self):
        if not self.isthreadActive1:
            #print("slidervalue change")
            self.horizontalSliderIncrease1(0)

    def horizontalSliderIncrease1(self, val):
        if self.sliderbusy_right or self.resizegoing1 or self.ui.horizontalSlider_right.value()+val+self.stframe1<0 or self.ui.horizontalSlider_right.value()+val+self.stframe1>self.ui.horizontalSlider_right.maximum():
            print('horizontalSliderIncrease1 return')
            return
        self.sliderbusy_right = True
        self.frameID1 = self.stframe1 + self.ui.horizontalSlider_right.value()+val
        #print("changed frameId={}".format(self.frameID1))
        if self.ui.pushButton_right2.isEnabled():
            # self.cap1.set(cv2.CAP_PROP_POS_FRAMES, self.frameID1)
            # ret, frame = self.cap1.read()
            # limage = preprocessImage(frame,self.scaleFactor1)
            # self.ui.rightImage.setPixmap(QtGui.QPixmap(limage))
            self.on_zoomfit_clicked1()
            self.showCurrentTime(self.frameID1,self.ui.label_time3)
            self.ui.horizontalSlider_right.setValue(self.frameID1)
        self.sliderbusy_right = False

    def updateFrame1(self):
        self.frameID1 += 1

    def horizontalSliderSet1(self,cnt):
        if cnt-self.stframe1>self.ui.horizontalSlider_right.maximum() or self.sliderbusy_right or self.resizegoing1:
            return
        self.sliderbusy2_right=True
        self.ui.horizontalSlider_right.setValue(cnt-self.stframe1)
        self.showCurrentTime(cnt,self.ui.label_time3)
        #self.ui.statusbar.showMessage("Frame TIme"+str(tmin).zfill(2)+":"+str(ttsec).zfill(2)+":"+str(int(ksec*100)))
        self.sliderbusy2_right=False

    def horizontalSliderPressed1(self):
        if self.ui.horizontalSlider_right.value()==self.ui.horizontalSlider_right.maximum():
            self.isthreadActive1=True
        self.sliderbusy_right=True

    def horizontalSliderReleased1(self):
        self.frameID1=self.stframe1+self.ui.horizontalSlider_right.value()
        # tsec=self.frameID1/self.fps1
        # self.ui.label_time3.setText(str(tmin).zfill(2)+':'+str(ttsec).zfill(2))
        #如果还没开始播放
        if self.ui.pushButton_right2.isEnabled():
            # self.cap1.set(cv2.CAP_PROP_POS_FRAMES,self.frameID1)
            # ret,frame=self.cap1.read()
            # limage=preprocessImage(frame,self.scaleFactor1)
            # self.ui.rightImage.setPixmap(QtGui.QPixmap(limage))
            self.on_zoomfit_clicked1()
            self.showCurrentTime(self.frameID1, self.ui.label_time3)
        self.sliderbusy_right=False

    def _on_resized1(self):
        self.on_zoomfit_clicked1()

    def openButtonPressed1(self):
        if self.isthreadActive1 or self.isVideo1:
            #print("弹出确认对话框")
            reply=QMessageBox.question(self,'Message','确定要关闭当前视频，打开新的视频吗？',QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
            if reply==QMessageBox.Yes:
                self.curr_mask_id=None
                self.curr_mask_img=None
                if not self.timer1 is None:
                    self.timer1.cancel()
                self.isthreadActive1 = False
                #self.ui.horizontalSlider_right.setValue(0)
                self.sliderbusy_right=False
                self.sliderbusy2_right=False
                self.timer1=None
                # self.ui.label_time3.setText('00:00:00')
                # self.ui.label_time4.setText('00:00:00')
            else:
                return

        #try:
        fileName=QFileDialog.getOpenFileName(None,caption="select video",directory=self.path_prefix)#directory是起始路径
        #getOpenFIleName返回的是(name,type)
        if len(fileName[0])>0:
            self.cap1=cv2.VideoCapture(fileName[0])
            self.isVideo1=True
            self.ui.horizontalSlider_right.setEnabled(True)
            if self.isFirstKey_right==False:
                self.klistener1_right.start()
                self.klistener2_right.start()
                self.isFirstKey_right = True
        else:
            #print("filename {} is empty".format(fileName[0]))
            return
        # 默认逐帧处理
        if not os.path.exists(self.frames_path) or not os.listdir(self.frames_path):
            video_to_frames(self.frames_path,fileName[0])
        self.length1=int(self.cap1.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps1=self.cap1.get(cv2.CAP_PROP_FPS)
        #print("videoName:{} total frames:{} fps:{}".format(fileName[0],self.length1,self.fps1))
        self.stframe1=0
        self.endframe1=self.length1-1
        self.ui.horizontalSlider_right.setMaximum(self.endframe1-self.stframe1)
        #print("horiontalSLider maxMiun:{}".format(self.endframe1-self.stframe1))
        #视频总时长
        self.showCurrentTime(self.length1-1,self.ui.label_time4)
        #归0
        self.ui.horizontalSlider_right.setValue(0)
        self.ui.label_time3.setText('00:00:00')
        # tsec = self.length1 / self.fps1
        # self.ui.label_time4.setText(str(tmin).zfill(2)+':'+str(ttsec).zfill(2))
        self.cap1.set(1,self.stframe1)
        ret,frame=self.cap1.read()
        # if(ret==True):
        #     print("cap read successfully!")
        # else:
        #     print("cap read failed!")
        self.limg1=frame
        self.frameID1=self.stframe1
        self.frameHeight1=frame.shape[0]
        self.frameWidth1=frame.shape[1]
        self.on_zoomfit_clicked1()
        #print("执行on_zoonfit_clicked,scaleFactor1 is {}".format(self.scaleFactor1))
        #print('init rightImage-width:{} height:{}'.format(self.ui.rightImage.size().width(),self.ui.rightImage.size().height()))
        #print('init videoImage-frameWidth1:{} frameHeight1:{} scaleFactor1:{}'.format(self.frameWidth1, self.frameHeight1,self.scaleFactor1))
        limage=preprocessImage(frame,self.scaleFactor1)
        self.ui.rightImage.setPixmap(QtGui.QPixmap(limage))
        #print("打开的第一帧显示成功!")
        #self.ui.textBrowser.setText("Ready to start or redifine video")
        self.ui.textBrowser.clear()
        self.ui.textBrowser.setText('ＥNTER－播放暂停,ＰgUp-前进，ＰgDn-后退')
        print('\n')
        self.ui.pushButton_right2.setEnabled(True)
        self.ui.pushButton_right3.setEnabled(False)
        self.ui.horizontalSlider_right.setEnabled(True)

    def startButtonPressed1(self):
        if self.isthreadActive1 or self.ui.horizontalSlider_right.value()>=self.ui.horizontalSlider_right.maximum():
            return
        self.ui.pushButton_right2.setEnabled(False)
        self.timer1=perpetualTimer(1.0/self.fps1,self.updateFrame1)
        self.timer1.start()

        self.ui.pushButton_right3.setEnabled(True)
        self.isthreadActive1=True

    def pauseButtonPressed1(self):
        if not self.isthreadActive1:
            return
        self.ui.pushButton_right2.setEnabled(True)
        self.ui.pushButton_right3.setEnabled(False)
        if not self.timer1 is None:
            self.timer1.cancel()
        self.isthreadActive1=False

    def on_zoomfit_clicked1(self):
        self.resizegoing1=True
        a=self.ui.rightImage.size()
        if a.width()/self.frameWidth1<a.height()/self.frameHeight1:
            self.scaleFactor1=a.width()/self.frameWidth1
            self.startx1=0
            self.starty1=(a.height()-self.scaleFactor1*self.frameHeight1)/2
        else:
            self.scaleFactor1=a.height()/self.frameHeight1
            self.starty1=0
            self.startx1=(a.width()-self.scaleFactor1*self.frameWidth1)/2.0
        sleep(0.2)
        if self.isVideo1==True:
            self.cap1.set(cv2.CAP_PROP_POS_FRAMES,self.frameID1)
            ret,frame=self.cap1.read()
            #print('resized1-scaleFactor1:{} rightImage width:{}height:{}'.format(self.scaleFactor1,a.width(),a.height()))
            limage=preprocessImage(frame,self.scaleFactor1)
            self.ui.rightImage.setPixmap(QtGui.QPixmap(limage))
        self.resizegoing1=False

    # *************右边播放视频的函数*********

    #***************模型训练的函数************
    def outputWritten(self,text):
        self.cursor.insertText(text)
        self.ui.textBrowser.setTextCursor(self.cursor)
        self.ui.textBrowser.ensureCursorVisible()

    def startAnnotate(self):
        flag=1 #vos
        self.bubbleNets_window= BubbleNetsForm('/home/wanwanvv/workspace/osvos/car-shadow',None,None,flag,self.callback)
        self.bubbleNets_window.show()

    def startFinetuneButtonPressed(self):
        if self.hasModel == True:
            reply = QMessageBox.question(self, 'Message', '已有训练完的模型，确定要重新训练吗？', QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.Yes)
            if reply != QMessageBox.Yes:
                return
        if self.curr_mask_img == None or self.curr_mask_id==None:
            # 弹出保存成功对话框
            infoBox = QMessageBox(self)
            # QMessageBox.about(self, 'Success', '标注已保存到相应目录!')
            # infoBox.setIcon(QMessageBox.information)
            infoBox.setText('请先选择标注目标的mask!')
            infoBox.setWindowTitle('Warning')
            infoBox.setStandardButtons(QMessageBox.Ok)
            infoBox.button(QMessageBox.Ok).animateClick(1 * 3000)
            infoBox.exec_()
            return
        # self.fthread=finetuneThread(self)
        # self.fthread.finishSin.connect(self.finetuneFinish)
        # self.fthread.start()
        self.ui.comboBox_model.setEnabled(False)
        if os.path.exists(self.result_dir):
            removeTmpDir(self.result_dir)
        os.makedirs(self.result_dir)
        if self.model=='Fast':
            self.ui.progressBar.setMaximum(0)
            self.ftThreadActive=True
            self.ui.pushButton_left1.setEnabled(False)
            self.ui.pushButton_left0.setEnabled(True)
            #开启线程
            self.rgmpInfo={}
            self.rgmpInfo['MO']=False
            self.rgmpInfo['annotation_path']=self.mask_path
            self.rgmpInfo['frmas_path'] = self.frames_path
            self.rgmpInfo['mask_img'] = self.curr_mask_img
            self.rgmpInfo['result_dir'] = self.result_dir
            self.rgmpInfo['model_dir']=self.model_folder
            self.rgmpInfo['ImageSets_path'] = self.ImageSets_path
            filename='val.txt'
            self.rgmpInfo['imset'] = filename
            if not os.path.exists(self.ImageSets_path):
                os.makedirs(self.ImageSets_path)
            with open(os.path.join(self.ImageSets_path,filename),'w') as valfile:
                video_name=self.path_prefix.split('/')[-1]
                valfile.write(video_name+'\n')

            #线程池
            self.ftThread_cnt += 1
            self.ftThreads_pool[self.ftThread_cnt % 5] = None
            self.ftThreads_pool[self.ftThread_cnt % 5] = QtCore.QThread()
            self.vosSegRGMP = VosRGMP_thread(self.rgmpInfo)
            self.vosSegRGMP.moveToThread(self.ftThreads_pool[self.ftThread_cnt % 5])
            self.ftThreads_pool[self.ftThread_cnt % 5].started.connect(self.vosSegRGMP.Vosrgmp_work)
            self.vosSegRGMP.finishVosRGMP_signal.connect(self.finetuneFinish_RGMP)
            self.ftThreads_pool[self.ftThread_cnt % 5].start()
            self.ui.textBrowser.clear()
            self.old_stdout = sys.stdout
            self.old_stderr = sys.stderr
            sys.stdout=EmittingStream(textWritten=self.outputWritten)
            sys.stderr=EmittingStream(textWritten=self.outputWritten)
        else:
            itertime, ok = QInputDialog.getInt(self, '开始分割', '输入迭代次数(default:50)',min=1,max=500)
            if itertime and ok:
                self.itertime =itertime
            else:
                return
            print("itertime:{}".format(self.itertime))
            self.fthread=None

            self.osvosInfo={}
            self.osvosInfo['path_prefix']=self.path_prefix
            self.osvosInfo['model_folder']=self.model_folder
            self.osvosInfo['mask_img']=self.curr_mask_img
            self.osvosInfo['mask_id']=self.curr_mask_id
            self.osvosInfo['frames_path']=self.frames_path
            self.osvosInfo['result_path']=self.result_dir
            self.osvosInfo['itertime']=self.itertime

            self.fthread = finetuneThread(self.osvosInfo)
            self.fthread.finishSin.connect(self.finetuneFinish_osvos)
            self.fthread.start()
            self.ui.progressBar.setMaximum(0)
            self.ftThreadActive = True
            self.ui.pushButton_left1.setEnabled(False)
            # self.ui.pushButton_left2.setEnabled(True)
            self.ui.textBrowser.clear()
            self.old_stdout = sys.stdout
            self.old_stderr = sys.stderr
            sys.stdout = EmittingStream(textWritten=self.outputWritten)
            sys.stderr = EmittingStream(textWritten=self.outputWritten)

    def _is_img(self, file_name):
        ext = file_name.split('.')[-1]
        return ext in ['jpg', 'jpeg', 'png', 'bmp']

    def finetuneFinish_RGMP(self,vos_result_path):
        self.ui.pushButton_left0.setEnabled(True)
        self.ui.pushButton_left1.setEnabled(True)
        #self.ui.pushButton_left2.setEnabled(False)
        self.vos_result_path=vos_result_path
        self.hasModel=True
        self.ftThreadActive = False
        self.ui.progressBar.setMaximum(1)
        self.ui.progressBar.setProperty("value",1)
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.ui.textBrowser.clear()
        self.ui.textBrowser.setText('空格键－播放暂停,左右键-前进后退')
        self.vosSegRGMP.finishVosRGMP_signal.disconnect(self.finetuneFinish_RGMP)
        self.ftThreads_pool[self.ftThread_cnt % 5].quit()
        self.ftThreads_pool[self.ftThread_cnt % 5].wait()
        self.vosSegRGMP.deleteLater()
        self.ftThreads_pool[self.ftThread_cnt % 5].deleteLater()
        self.initLeftImage()
        self.ui.horizontalSlider_left.setEnabled(True)
        if self.isFirstKey_left==False:
            self.klistener1_left.start()
            self.klistener2_left.start()
            self.isFirstKey_left = True
        self.ui.pushButton_left5.setEnabled(True)
        self.ui.comboBox_model.setEnabled(True)

    def finetuneFinish_osvos(self,vos_result_path):
        self.ui.pushButton_left1.setEnabled(True)
        self.ui.pushButton_left0.setEnabled(True)
        self.hasModel=True
        self.ftThreadActive = False
        self.vos_result_path = vos_result_path
        self.ui.progressBar.setMaximum(1)
        self.ui.progressBar.setProperty("value",1)
        self.fthread.finishSin.disconnect(self.finetuneFinish_osvos)
        self.ui.comboBox_model.setEnabled(True)
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.ui.textBrowser.clear()
        self.ui.textBrowser.setText('空格键－播放暂停,左右键-前进后退')
        self.initLeftImage()
        self.ui.horizontalSlider_left.setEnabled(True)
        if self.isFirstKey_left == False:
            self.klistener1_left.start()
            self.klistener2_left.start()
            self.isFirstKey_left = True
        self.ui.pushButton_left5.setEnabled(True)
        self.fthread.quit()
        self.fthread.wait()
        self.fthread.deleteLater()

    # ***************模型训练的函数************

#******************test*****************
# if __name__=='__main__':
#     app=QApplication(sys.argv)
#     osvos_widget=OsvosForm('/home/wanwanvv/workspace/osvos/car-shadow')
#     osvos_widget.show()
#     sys.exit(app.exec_())
