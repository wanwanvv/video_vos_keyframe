import os,sys
import shutil
import cv2
from time import sleep
from threading import Timer
from PyQt5 import QtCore
from PyQt5.QtCore import QThread,Qt
from PyQt5.QtGui import QImage, QPixmap, QCursor
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pynput
import math
from PyQt5.QtWidgets import QDesktopWidget, QWidget, QApplication

root_folder14 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder14=os.path.dirname(root_folder14 )
resources_folder14=os.path.join(parent_folder14,'resources')
sys.path.append(parent_folder14)
sys.path.append(os.path.join(parent_folder14,'gui'))
sys.path.append(os.path.join(parent_folder14,'direct'))
sys.path.append(os.path.join(parent_folder14,'Removal'))
default_workdir='/home/wanwanvv/workspace/osvos/car-shadow'

from remove_window import Remove_Form
from propagate_thread import VosIvs_thread
from CPNet_thread import InpaintingCPNet_thread
from video_output import VideoOutForm
from MgrHelper import MgrHelper
#************************实用类****************************
#改变图片尺寸
def changeImageSize(src_path,dst_path,width,height,scale=1.0):
    imgs = sorted(os.listdir(src_path))
    scale_width = int(width * scale)
    scale_height = int(height * scale)
    frames_num = len(imgs)
    for i in range(frames_num):
        img=os.path.join(src_path, imgs[i])
        img_array=cv2.imread(img)
        img_resize=cv2.resize(img_array,(scale_width,scale_height),interpolation=cv2.INTER_LINEAR)
        img_output=os.path.join(dst_path,imgs[i])
        cv2.imwrite(img_output,img_resize)

#将图片转为视频
def frames_to_video(fps,save_path,frames_path,type='mp4'):
    if type=='mp4':
        fourcc=cv2.VideoWriter_fourcc(*'mp4v')
    elif type=='avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #videoWriter=cv2.VideoWriter(save_path,fourcc,fps,(966,540))
    imgs=sorted(os.listdir(frames_path))
    image1= os.path.join(frames_path,imgs[0])
    [height,width,pix]=cv2.imread(image1).shape
    print('h:{} w:{} pix:{}'.format(height,width,pix))
    print('value--save_path:{} fourcc:{} fps:{} width:{} height:{}'.format(save_path,fourcc,fps,width,height))
    videoWriter = cv2.VideoWriter(save_path, fourcc, fps, (width, height))
    frames_num=len(imgs)
    for i in range(frames_num):
        image=os.path.join(frames_path,imgs[i])
        frame=cv2.imread(image)
        videoWriter.write(frame)
    videoWriter.release()
    return

#将视频默认抽帧
def video_to_frames(result_path,video_path):
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    capture = cv2.VideoCapture(video_path)
    length=int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps=capture.get(cv2.CAP_PROP_FPS)
    num = 0
    while True:
        ret, img = capture.read()
        if not ret:
            break
        picname = '{:05d}.jpg'.format(num)
        cv2.imwrite(os.path.join(result_path, picname), img)
        num += 1
    capture.release()
    return (fps,length)

def getResultsMaskImages(path):
    results_images=[]
    images=sorted(os.listdir(path))
    img_num=len(images)
    for i in range(img_num):
        img=os.path.join(path,images[i])
        results_images.append(img)
    return results_images

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

def getImages(path):
    results_images=[]
    images=sorted(os.listdir(path))
    img_num=len(images)
    for i in range(img_num):
        img=os.path.join(path,images[i])
        results_images.append(img)
    return results_images

#************************实用类×××××××××××××××××××××××××

#*************************播放视频帧的类××××××××××××××××××××××
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
                if self.mw.frameID>self.mw.length-1:
                    # self.mw.ui.pushButton_left6.setEnabled(False)
                    # self.mw.ui.pushButton_left5.setEnabled(True)
                    self.mw.isPlay=True
                    self.mw.ui.pushButton_play.setText('Play')
                    self.mw.isthreadActive=False
                    if not self.mw.timer is None:
                        self.mw.timer.cancel()
                    self.mw.isthreadActive=False
                    self.mw.isbusy=False
                    continue
                self.mw.currentID = self.mw.frameID
                # if self.mw.isInit==True:
                #     self.mw.on_zoomfit_clicked()
                #     self.mw.isInit=False
                if self.mw.resizegoing==False:
                    self.mw.on_zoomfit_clicked()
                    #print('wthread self.resizegoing:{}'.format(self.mw.resizegoing))
                    if not self.mw.sliderbusy and not self.mw.sliderbusy2:
                        self.updatedM.emit(self.mw.frameID)
                    QApplication.processEvents()
                self.mw.isbusy=False
            else:
                if self.mw.isthreadActive and self.mw.timer is None:
                    self.mw.frameID+=1
                sleep(1.0/50)
#*************************播放视频帧的类××××××××××××××××××××××

class RemoveObjectForm(QWidget):
    resized = QtCore.pyqtSignal()  # 缩放信号
    def __init__(self,workdir,direct_object):
        super(RemoveObjectForm, self).__init__()  # 继承的所有父类的初始化
        self.ui=Remove_Form()
        self.ui.setupUi(self)
        # *************path*******************
        self.model_folder = parent_folder14 + '/models'  # models所在目录
        self.path_prefix = workdir  # 工作目录
        self.direct_object=direct_object
        # **************path********************
        # resize关联函数
        self.initConstant()
        self.initUI()
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
        self.close()

    def nextButtonPressed(self):
        self.direct_object.show()
        self.close()

    def closeEvent(self, event):
        QWidget.closeEvent(self, event)
        # self.direct_object.close()
        self.close()

    # def closeEvent(self, event):
    # 重写resizeEvent事件
    def resizeEvent(self, event):
        self.resized.emit()
        return super(RemoveObjectForm, self).resizeEvent(event)

    def initConstant(self):

        self.video_output_dir=os.path.join(self.path_prefix,'VideoOutputs') #保存最终视频结果的文件夹
        if os.path.exists(self.video_output_dir):
            removeTmpDir(self.video_output_dir)
        os.makedirs(self.video_output_dir)
        #self.remove_result_dir=os.path.join(self.path_prefix,'RemoveResults') #保存结果的视频图片帧的文件夹,线程清0
        #***************************播放视频帧的变量*******************************
        self.stframe = 0
        self.endframe = 0
        self.fps = 22
        self.default_fps=22
        self.scaleFactor = 1.0  # 缩放比例
        self.length = 1
        self.frameID = 0  # 第几帧
        self.currentID = 0  # 显示的第几帧
        self.isRun = True  # 未改变一直为True
        self.resizegoing = False  # 当进行放缩调整时为True
        self.sliderbusy = False  # 进度条被按下时为True，放松时即无操作为False
        self.sliderbusy2 = False  # 视频逐帧向前播放反过来让进度条值变化时为True

        self.isFirstKey=False #是否第一次开启按键响应
        self.isInit=False
        self.startx = 0
        self.starty = 0
        self.isVideo = False  # 已经显示图片
        #self.isResult=False #已经加载结果图片
        self.isbusy = 0
        self.frameHeight = 1 #当前展示的图片尺寸
        self.frameWidth = 1
        self.src_frameHeight=1 #源图片的图片尺寸
        self.src_frameWidth=1
        self.timer = None
        self.isthreadActive = False  # 开始播放视频
        self.current_img=None #label当前显示的图片

        #存储路径
        self.src_frames_path = os.path.join(self.path_prefix, 'JPEGImages')
        self.mask_frames_path = None
        self.result_frames_path = None

        self.srcImages = []  # 存储源视频帧的文件
        self.showImages = []  # 存储label展示的视频帧的文件
        self.resultImages = []  # 存储结果视频帧的文件
        self.maskImages = []  # 存储mask的文件

        #当前显示的图片类型
        self.isResult = False
        self.isMask = False
        self.isSrc = False

        #播放视频的线程启动
        self.wthread = workerThread(self)
        self.wthread.updatedM.connect(self.horizontalSliderSet)
        self.wthread.start()

        #键盘操作控制视频帧的播放
        self.klistener1_left = pynput.keyboard.Listener(on_press=self.on_release)
        self.klistener2_left = pynput.keyboard.Listener(on_release=self.on_press)

        #控制缩放
        self.resized.connect(self._on_resized)

        #step1-annotate变 step2-vos变量
        self.vosThreadActive=False
        self.vos_threads_pool = [None, None, None, None, None]
        self.scribbles = {}
        self.vos_thread_cnt = -1
        self.rectPos = []  # 绘制的矩形框的顶点坐标[(x0,y0),(x1,y1)]
        self.imgPt = []  # 图片的顶点全局坐标[(x0,y0),(x1,y1)]
        self.central_x = 0  # 图像的中心横坐标
        self.central_y = 0  # 图像的中心纵坐标
        self.video_name=self.path_prefix.split('/')[-1]
        self.last_video_name=None

        #step3-inpainting变量
        self.inpaintingTHreadActive=False
        self.maskInfo={}
        self.ImageSets_path = os.path.join(self.path_prefix, 'ImageSets')
        self.inpainting_threads_pool = [None, None, None, None, None]
        self.inpainting_thread_cnt = -1

        # step4-导出结果变量
        self.hasVideo=False#已有可以导出的视频
        self.video_dialog=None
        self.video_info={}

        # ***************************播放视频帧的变量*******************************


    def initUI(self):
        # 窗体居中显示
        screen_size = QDesktopWidget().screenGeometry()  # 获得屏幕的尺寸
        widget_size = self.geometry()  # 获得窗体的尺寸
        self.move((screen_size.width() - widget_size.width()) / 2,
                  (screen_size.height() - widget_size.height()) / 2)
        self.ui.frame.setProperty('flag', 'nav')
        self.setWindowTitle(u'视频目标移除')
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

        #播放按钮相关变量和美化
        self.isPlay=True #True表示显示的是play

        #初始按键设置
        self.ui.pushButton_open.setEnabled(True)
        self.ui.pushButton_exist.setEnabled(True)
        self.ui.pushButton_play.setEnabled(True)
        self.ui.pushButton_out.setEnabled(False)
        self.ui.pushButton_remove.setEnabled(False)

        #按键关联的函数
        self.ui.pushButton_open.clicked.connect(self.openButtonPressed)
        self.ui.pushButton_exist.clicked.connect(self.existsButtonPressed)
        self.ui.pushButton_remove.clicked.connect(self.removeButtonPressed)
        self.ui.pushButton_out.clicked.connect(self.outButtonPressed)
        self.ui.pushButton_play.clicked.connect(self.playButtonPressed)

        #进度条关联函数
        self.ui.horizontalSlider.setEnabled(False)
        self.ui.horizontalSlider.sliderPressed.connect(self.horizontalSliderPressed)
        self.ui.horizontalSlider.sliderReleased.connect(self.horizontalSliderReleased)
        self.ui.horizontalSlider.valueChanged.connect(self.slider_value_changed)

        #涂鸦关联函数
        self.ui.label_image.formAnno.connect(self.formAnnotate_ivs)

    #清空还原所有变量
    def initImage(self):
        #变量
        if not self.timer is None:
            self.timer.cancel()
        self.timer = None
        self.stframe = 0
        self.endframe = 0
        self.fps = 22
        self.scaleFactor = 1.0  # 缩放比例
        self.length = 1
        self.frameID = 0  # 第几帧
        self.currentID = 0  # 显示的第几帧
        self.isRun = True  # 未改变一直为True
        self.resizegoing = False  # 当进行放缩调整时为True
        self.sliderbusy = False  # 进度条被按下时为True，放松时即无操作为False
        self.sliderbusy2 = False  # 视频逐帧向前播放反过来让进度条值变化时为True

        self.isInit = False
        self.startx = 0
        self.starty = 0
        self.isVideo = False  # 已经显示图片
        # self.isResult=False #已经加载结果图片
        self.isbusy = 0
        self.frameHeight = 1
        self.frameWidth = 1
        self.isthreadActive = False  # 开始播放视频
        self.current_img = None  # label当前显示的图片

        self.isResult = False
        self.isMask = False
        self.isSrc = False
        #清空文件
        if self.result_frames_path!=None and os.path.exists(self.result_frames_path):
            removeTmpDir(self.result_frames_path)
        #ui
        # self.ui.horizontalSlider.setValue(0)
        # self.ui.label_curr.setText('00:00:00')
        # self.ui.label_total.setText('00:00:00')

    #打开视频帧文件
    def openButtonPressed(self):
        print('打开视频文件按钮被按下')
        if self.isthreadActive or self.isVideo :
            reply = QMessageBox.question(self, 'Message', '确定要关闭当前视频，打开新的视频吗？', QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.initImage()
                self.srcImages = []  # 存储源视频帧的文件
                self.showImages = []  # 存储label展示的视频帧的文件
                self.resultImages = []  # 存储结果视频帧的文件
                self.maskImages = []  # 存储mask的文件
            else:
                return
        filename, filetype = QFileDialog.getOpenFileName(self, "选取视频文件", self.path_prefix)
        self.video_name = filename.split('/')[-1].split('.')[0]
        if self.last_video_name != self.video_name:
            if self.src_frames_path != None and os.path.exists(self.src_frames_path):
                removeTmpDir(self.src_frames_path)
        self.last_video_name = self.video_name
        if not os.path.exists(self.src_frames_path) or not os.listdir(self.src_frames_path):
            param=video_to_frames(self.src_frames_path,filename)
            self.length=param[1]
        self.initLeftImage(self.src_frames_path,type='src')
        if len(self.srcImages) > 0:
            self.scribbles['scribbles'] = [[] for _ in range(len(self.srcImages))]
        #self.ui.label_image.flag=True
        self.ui.pushButton_remove.setEnabled(True)

    def load_img(self,img_id):
        try:
            with open(self.showImages[img_id], 'rb') as f:
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
        a=self.ui.label_image.size()
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
        self.ui.label_image.setPixmap(pixmap)
        self.current_img=self.showImages[img_id]
        return True

    def showTime(self,count,label):
        tsec = count / self.fps
        tmin = int(tsec / 60)  # 视频播放到的帧的整数分钟
        ttsec = int(tsec - 60 * tmin)  # 视频播放到的帧的整数秒钟
        ksec = tsec - 60 * tmin - ttsec  # 视频播放到的帧的小数秒钟
        ksec=int (ksec*100)
        label.setText(str(tmin).zfill(2) + ':' + str(ttsec).zfill(2) + ':' + str(ksec).zfill(2))

    def initLeftImage(self,frames_path,type='src'): #type='src'读取的是src,type='result'读取的是结果文件,type='mask'读取的是掩膜图片
        if not frames_path or not os.path.exists(frames_path):
            return
        self.isInit=True
        src_img_path=frames_path
        self.showImages = getImages(src_img_path)
        if type=='src':
            self.srcImages=self.showImages
            self.isSrc=True
            self.isMask = False
            self.isResult = False
            #获取源图片尺寸,用于最后导出
            if self.srcImages!=[]:
                [self.src_frameHeight, self.src_frameWidth, pix] = cv2.imread(self.srcImages[0]).shape

        elif type=='mask':
            self.maskImages=self.showImages
            self.isMask = True
            self.isSrc = False
            self.isResult = False
        elif type == 'result':
            self.resultImages = self.showImages
            self.isResult = True
            self.isSrc = False
            self.isMask = False
        if len(self.showImages)==0:
            QMessageBox.about(self, 'Warning', '处理的结果图像未准备好!')
            return
        else:
            self.isVideo=True
            self.ui.horizontalSlider.setEnabled(True)
            if self.isFirstKey==False:
                self.klistener1_left.start()
                self.klistener2_left.start()
                self.isFirstKey = True
        self.length=len(self.showImages)
        self.stframe=0
        self.endframe=self.length-1
        self.ui.horizontalSlider.setMaximum(self.endframe-self.stframe)
        self.current_img=self.showImages[self.stframe]
        self.currentID = self.stframe
        [height, width, pix] = cv2.imread(self.current_img).shape
        self.frameWidth = width
        self.frameHeight = height
        if self.isInit==True:
            print('isInit=True')
            #self.scaleFactor=0.604167
        #打开图片
        self.load_img(self.currentID)
        # 视频总时长
        self.showTime(self.length-1,self.ui.label_total)
        #归0
        self.ui.label_curr.setText('00:00:00')
        self.ui.horizontalSlider.setValue(0)
        self.isPlay=True
        self.ui.pushButton_play.setText('Play')
        self.ui.pushButton_play.setEnabled(True)
        self.ui.horizontalSlider.setEnabled(True)
        self.isthreadActive=False

    #播放、暂停按钮
    def playButtonPressed(self):
        if self.isVideo==False:
            return
        if self.isPlay==True:
            self.play()
        else:
            self.pause()

    def play(self):
        if self.isthreadActive or self.ui.horizontalSlider.value() >= self.ui.horizontalSlider.maximum():
            print('self.isthreadActive={}'.format(self.isthreadActive))
            print('play_return')
            return
        self.timer = perpetualTimer(1.0 / self.fps, self.updateFrame)
        self.timer.start()
        self.isthreadActive = True
        self.isPlay = False
        self.ui.pushButton_play.setText('Pause')

    def pause(self):
        if not self.isthreadActive:
            return
        if not self.timer is None:
            self.timer.cancel()
        self.isthreadActive = False
        self.isPlay = True
        self.ui.pushButton_play.setText('Play')

    #使用已存在的分割mask
    def existsButtonPressed(self):
        print('existsButtonPressed')
        if self.isthreadActive or self.isVideo :
            reply = QMessageBox.question(self, 'Message', '确定要关闭当前视频，打开标注mask吗？', QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.initImage()
            else:
                return
        self.mask_frames_path = QFileDialog.getExistingDirectory(self, '选择标注mask文件夹', self.path_prefix)
        print('self.mask_frames_path:{}'.format(self.mask_frames_path))
        self.initLeftImage(self.mask_frames_path,type='mask')
        self.ui.pushButton_remove.setEnabled(True)

    #开始移除目标物体
    def removeButtonPressed(self):
        print('removeButtonPressed')
        if self.isMask==True:
            print('isMask==True')
            if self.srcImages==[] or len(self.srcImages)!=len(self.maskImages):
                if self.srcImages == []:
                    print('if self.srcImages==[]')
                if len(self.srcImages)!=len(self.maskImages):
                    print('len(self.srcImages):{}'.format(len(self.srcImages)))
                    print('len(self.maskImages):{}'.format(len(self.maskImages)))
                # 弹出保存成功对话框
                infoBox = QMessageBox(self)
                # QMessageBox.about(self, 'Success', '标注已保存到相应目录!')
                # infoBox.setIcon(QMessageBox.information)
                infoBox.setText('请先选择和视频对应的目标分割!')
                infoBox.setWindowTitle('Warning')
                infoBox.setStandardButtons(QMessageBox.Ok)
                infoBox.button(QMessageBox.Ok).animateClick(1 * 1000)
                infoBox.exec_()
                return
            #ui
            self.ui.progressBar.setMaximum(0)
            self.ui.pushButton_out.setEnabled(False)
            self.ui.pushButton_exist.setEnabled(False)
            self.ui.pushButton_open.setEnabled(False)
            self.startInpainting()
            print('执行完startInpainting')

        elif self.isSrc==True:
            self.ui.label_image.isShow=True
        elif self.isResult==True:
            self.srcImages=self.resultImages
            self.ui.label_image.isShow=True
        self.ui.pushButton_remove.setEnabled(False)

    #step1-annotate***************************
    def initVosConstant(self):
        self.scribbles = {}
        self.hasVideo = False
        self.maskInfo = {}

    def formAnnotate_ivs(self):
        #ui设置
        self.ui.progressBar.setMaximum(0)
        self.ui.pushButton_out.setEnabled(False)
        self.ui.pushButton_exist.setEnabled(False)
        self.ui.pushButton_open.setEnabled(False)
        self.ui.label_image.isShow=False
        self.scribbles['annotated_frame']=self.currentID
        #存储分割结果mask的存储路径
        filename=str(self.video_name)+'_VosResults'
        tmp_dir=os.path.join(self.path_prefix,filename)
        print('formAnnotate_ivs tmp_dir:{}'.format(tmp_dir))
        self.scribbles['tmp_dir'] = tmp_dir
        if os.path.exists(tmp_dir):
            removeTmpDir(tmp_dir)
        os.makedirs(tmp_dir)
        self.scribbles['frames'] = self.srcImages
        self.scribbles['model_prefix'] = self.model_folder
        stroke = self.ui.label_image.getStrokeGlobalPos()
        stroke_poses = stroke['path']
        stroke_poses_global = []
        label_pos = self.ui.label_image.pos()
        global_label_pos = self.ui.label_image.mapToGlobal(label_pos)
        label_half_width = int(self.ui.label_image.size().width() / 2 + 0.5)
        label_half_height = int(self.ui.label_image.size().height() / 2 + 0.5)
        self.central_x = global_label_pos.x() + label_half_width
        self.central_y = global_label_pos.y() + label_half_height
        img_half_width = int((self.frameWidth * self.scaleFactor) / 2 + 0.5)
        img_half_height = int((self.frameHeight * self.scaleFactor) / 2 + 0.5)
        self.imgPt = [(self.central_x - img_half_width, self.central_y - img_half_height)]
        self.imgPt.append((self.central_x + img_half_width, self.central_y + img_half_height))
        lines_path = []  # 存储绝对值坐标用来绘制描线
        for stroke_pos in stroke_poses:
            global_x_line=int((stroke_pos[0]- self.imgPt[0][0]) / self.scaleFactor + 0.5)
            global_y_line=int((stroke_pos[1]- self.imgPt[0][1]) / self.scaleFactor + 0.5)

            global_x = float((stroke_pos[0] - self.imgPt[0][0]) / self.scaleFactor)/float(self.frameWidth)
            global_y = float((stroke_pos[1] - self.imgPt[0][1]) / self.scaleFactor)/float(self.frameHeight)
            lines_path.append([global_x_line,global_y_line])
            stroke_poses_global.append([global_x,global_y])
        stroke['path']=stroke_poses_global
        stroke['line_path']=lines_path
        self.scribbles['scribbles'][self.currentID].append(stroke)
        print("*****************path***********************")
        print("frameWidth:{} frameHeight:{}".format(self.frameWidth,self.frameHeight))
        print(self.scribbles['scribbles'][self.currentID][0])
        print("stroke['line_path']:")
        print(stroke['line_path'])
        print("*****************path***********************")

        #多线程
        self.vosThreadActive = True
        self.vos_thread_cnt+=1
        self.vos_threads_pool[self.vos_thread_cnt%5]=None
        self.vos_threads_pool[self.vos_thread_cnt%5]=QThread()
        self.vosWork=VosIvs_thread(self.scribbles)
        self.vosWork.moveToThread(self.vos_threads_pool[self.vos_thread_cnt%5])
        self.vos_threads_pool[self.vos_thread_cnt%5].started.connect(self.vosWork.VosIvs_work)
        self.vosWork.finishVos_signal.connect(self.finishVos)
        self.vos_threads_pool[self.vos_thread_cnt%5].start()

    def finishVos(self,mask_dir):
        print('finishVos')
        self.initImage()
        self.mask_frames_path = mask_dir
        self.maskImages = getImages(self.mask_frames_path)
        self.isMask=True
        self.vosThreadActive = False
        self.vosWork.finishVos_signal.disconnect(self.finishVos)
        self.vos_threads_pool[self.vos_thread_cnt%5].quit()
        self.vos_threads_pool[self.vos_thread_cnt%5].wait()
        self.vos_threads_pool[self.vos_thread_cnt%5].deleteLater()
        self.startInpainting()

    # step1-annotate***************************

    #step2-vos*********************************
    def startInpainting(self):
        print('startInpainting')
        # 开启线程
        self.maskInfo['model_folder'] = self.model_folder
        self.maskInfo['width'] = self.frameWidth
        print('self.frameWidth:{}'.format(self.frameWidth))
        print('self.frameHeight:{}'.format(self.frameHeight))
        self.maskInfo['height'] = self.frameHeight
        filename = str(self.video_name) + '_InpaintingVideos'
        video_dir=os.path.join(self.path_prefix, filename)
        # print('video_dir:{}'.format(video_dir))
        # if not os.path.exists(video_dir):
        #     os.makedirs(video_dir)
        filename=str(self.video_name)+'_InpaintingResults'
        tmp_dir = os.path.join(self.path_prefix, filename)
        print('result_dir:{}'.format(tmp_dir))
        if os.path.exists(tmp_dir):
            removeTmpDir(tmp_dir)
        os.makedirs(tmp_dir)
        self.maskInfo['video_dir'] = video_dir
        self.maskInfo['annotation_path'] = self.mask_frames_path
        self.maskInfo['frames_path'] = self.src_frames_path
        self.maskInfo['result_dir'] = tmp_dir
        self.maskInfo['ImageSets_path'] = self.ImageSets_path
        filename = 'val.txt'
        self.maskInfo['imset'] = filename
        if not os.path.exists(self.ImageSets_path):
            os.makedirs(self.ImageSets_path)
        val_file_name=os.path.join(self.ImageSets_path, filename)
        if not os.path.exists(val_file_name):
            with open(val_file_name, 'w') as valfile:
                valfile.write(self.video_name + '\n')

        self.inpaintingTHreadActive=True

        # 线程池
        self.inpainting_thread_cnt+=1
        self.inpainting_threads_pool[self.inpainting_thread_cnt % 5] =None
        self.inpainting_threads_pool[self.inpainting_thread_cnt % 5]=QThread()
        self.inpaitingWork=InpaintingCPNet_thread(self.maskInfo)
        self.inpaitingWork.moveToThread(self.inpainting_threads_pool[self.inpainting_thread_cnt % 5])
        self.inpainting_threads_pool[self.inpainting_thread_cnt % 5].started.connect(self.inpaitingWork.InpaintingCPNet_work)
        self.inpaitingWork.finishInpainting_signal.connect(self.finishInpainting)
        self.inpainting_threads_pool[self.inpainting_thread_cnt % 5].start()

    def finishInpainting(self,result_dir):
        #ui
        print('finishiInpainting')
        self.ui.pushButton_open.setEnabled(True)
        self.ui.pushButton_exist.setEnabled(True)
        self.ui.pushButton_out.setEnabled(True)
        self.ui.pushButton_remove.setEnabled(True)
        self.ui.progressBar.setMaximum(1)
        self.ui.progressBar.setProperty("value", 0)

        self.inpaintingTHreadActive=False
        self.hasVideo=True
        self.ui.pushButton_out.setEnabled(True)
        self.inpaitingWork.finishInpainting_signal.disconnect(self.finishInpainting)
        self.inpainting_threads_pool[self.inpainting_thread_cnt % 5].quit()
        self.inpainting_threads_pool[self.inpainting_thread_cnt % 5].wait()
        self.inpainting_threads_pool[self.inpainting_thread_cnt % 5].deleteLater()
        self.result_frames_path=result_dir
        #显示图片帧
        self.initLeftImage(self.result_frames_path, type='result')


    # step2-vos*********************************

    #step3-inpainting
    def getWorkDirectory(self):
        directory=QFileDialog.getExistingDirectory(None,caption="选取保存的文件夹目录",directory=self.path_prefix)
        self.ui.textEdit_root.setText(directory)

    #导出结果视频
    def callback(self, video_info):
        self.video_info={}
        self.video_info=video_info
        video_name=self.video_info['video_name ']
        video_type=self.video_info['video_type ']   # str
        video_fps=self.video_info['video_fps ']   # int
        video_scale=self.video_info['video_scale']   # float
        video_saveDir=self.video_info['video_saveDir']
        video_full_name=video_name+'.'+video_type
        save_path=os.path.join(video_saveDir,video_full_name)
        if math.isclose(1.0,video_scale):
            print('scale==1')
            print('video_fps:{} save_path:{} src_path:{} video_type:{}'.format(video_fps, save_path, self.result_frames_path,video_type))
            frames_to_video(video_fps, save_path, self.result_frames_path,type=video_type)
        else:
            dst_path = os.path.join(self.path_prefix, self.video_name+'_InpaintingResults_Scale')
            if not os.path.exists(dst_path):
                os.makedirs(dst_path)
            print('self.src_frameWidth:{} self.src_frameHeight:{}'.format(self.src_frameWidth,self.src_frameHeight))
            changeImageSize(self.result_frames_path, dst_path, self.src_frameWidth, self.src_frameHeight, scale=video_scale)
            frames_to_video(video_fps, save_path, dst_path, type=video_type)
            # if os.path.exists(dst_path):
            #     removeTmpDir(dst_path)
        # 弹出保存成功对话框
        infoBox = QMessageBox(self)
        # QMessageBox.about(self, 'Success', '标注已保存到相应目录!')
        # infoBox.setIcon(QMessageBox.information)
        infoBox.setText('视频已成功导出到相应目录!')
        infoBox.setWindowTitle('Success')
        infoBox.setStandardButtons(QMessageBox.Ok)
        infoBox.button(QMessageBox.Ok).animateClick(1 * 1000)
        infoBox.exec_()

    def outButtonPressed(self):
        print('outButtonPressed')
        # if self.hasVideo==False or scallbackelf.resultImages==[]:
        #     return
        #弹出dialog
        #self.bubbleNets_window = BubbleNetsForm('/home/wanwanvv/workspace/osvos/car-shadow', flag, self.callback)
        self.video_dialog=VideoOutForm(self.path_prefix,self.callback)
        self.video_dialog.show( )


    # ***********************进度条的函数*****************************
    # 进度条值改变为0
    def slider_value_changed(self):
        if not self.isthreadActive:
            # print("slidervalue change")
            self.horizontalSliderIncrease(0)

    def horizontalSliderIncrease(self, val):
        if self.sliderbusy or self.resizegoing or self.stframe + self.ui.horizontalSlider.value()+val>self.ui.horizontalSlider.maximum() or self.stframe + self.ui.horizontalSlider.value()+val < 0:
            print('horizontalSliderIncrease return:self.sliderbusy=={},self.resizegoing=={}'.format(self.sliderbusy,self.resizegoing))
            return
        self.sliderbusy = True
        self.frameID = self.stframe + self.ui.horizontalSlider.value()+val
        #if self.isPlay==True:
        self.currentID = self.frameID
        # 打开图片
        #self.load_img(self.current_img)
        self.on_zoomfit_clicked()
        self.showTime(self.currentID,self.ui.label_curr)
        self.sliderbusy = False
        self.ui.horizontalSlider.setValue(self.frameID)

    def horizontalSliderSet(self, cnt):
        #print('horizontalSliderSet')
        #print('cnt:{} self.sliderbusy:{} self.resizegoing:{}'.format(cnt,self.sliderbusy,self.resizegoing))
        if cnt-self.stframe>self.ui.horizontalSlider.maximum() or self.sliderbusy or self.resizegoing:
            print('horizontalSliderSet return')
            return
        self.sliderbusy2 = True
        self.ui.horizontalSlider.setValue(cnt - self.stframe)
        self.showTime(cnt,self.ui.label_curr)
        self.sliderbusy2 = False

    def horizontalSliderPressed(self):
        if self.ui.horizontalSlider.value()<=self.ui.horizontalSlider.maximum():
            self.isthreadActive=True
        self.sliderbusy=True

    def horizontalSliderReleased(self):
        self.isthreadActive = False
        if self.isVideo==False:
            return
        self.frameID = self.stframe + self.ui.horizontalSlider.value()
        self.sliderbusy = True
        #if self.isPlay==True:
        self.current_img = self.showImages[self.frameID]
        self.currentID = self.frameID
        self.on_zoomfit_clicked()
        self.showTime(self.currentID,self.ui.label_curr)
        self.sliderbusy = False

    def updateFrame(self):
        self.frameID += 1
    # ***********************进度条的函数*****************************

    #***********************控制缩放的函数*****************************

    def _on_resized(self):
        self.on_zoomfit_clicked()

    def on_zoomfit_clicked(self):
        self.resizegoing=True
        if self.isVideo==True:
            self.load_img(self.currentID)
            print("on_zoomfit_clicked:load_img")
        #sleep(0.2)
        self.resizegoing=False
    # ***********************控制缩放的函数*****************************

    #************************键盘按键控制函数***************************
    def on_press(self, key):
        if self.isRun:
            if pynput.keyboard.Key.space == key:
                if self.isPlay==False:
                    print('按下pause')
                    self.pause()
                else:
                    while (self.sliderbusy == True or self.resizegoing == True):
                        sleep(0.1)
                    print('按下play')
                    self.play()
            # elif key == pynput.keyboard.Key.left:
            #     # print('left')
            #     self.horizontalSliderIncrease(1)
            # elif key == pynput.keyboard.Key.right:
            #     # print('right')
            #     self.horizontalSliderIncrease(-1)

    def on_release(self, key):
        # if self.isRun:
        if key == pynput.keyboard.Key.left:
            print('按键left')
            self.horizontalSliderIncrease(-1)
        elif key == pynput.keyboard.Key.right:
            print('按键right')
            self.horizontalSliderIncrease(+1)
    # ************************键盘按键控制函数***************************

#test
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainWindow = RemoveObjectForm(default_workdir)
#     mainWindow.show()
#     sys.exit(app.exec_())