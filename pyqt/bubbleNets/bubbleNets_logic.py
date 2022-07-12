import os
import sys
import shutil
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, QObject
from PyQt5.QtGui import QCursor, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QDesktopWidget, QWidget, \
    QListWidgetItem, QInputDialog
#import tensorflow as tf

root_folder4 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder4=os.path.dirname(root_folder4 )
resources_folder4=os.path.join(parent_folder4,'resources')
sys.path.append(parent_folder4)
sys.path.append(os.path.join(parent_folder4,'gui'))
sys.path.append(os.path.join(parent_folder4,'OSVOS'))
sys.path.append(os.path.join(parent_folder4,'direct'))
sys.path.append(os.path.join(parent_folder4,'bubbleNets'))
sys.path.append(os.path.join(parent_folder4,'InteSeg'))
default_workdir='/home/wanwanvv/workspace/osvos/car-shadow'

from bubbleNets_window import bubbleNets_Form
from bubbleNets_window import MyLabel,MyLabel_inteSeg,MyLabel_ivs,MyLabel_deepGrab
from MgrHelper import MgrHelper
from bubbleNets import computeBestFrameThread
from our_func_inteSeg import our_func
from ivs_utils import load_frames
from ivs_model import model

#信号类用来发射标准输出作为信号
class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self,text):
        self.textWritten.emit(str(text))

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

def preprocessMixImgae(img,mask):
    overlay_color=[255,0,0]
    transparency=0.6
    #img = np.array(Image.open(srcImage))
    #mask = np.array(Image.open(maskImage))
    #mask=cv2.imread(maskImage)
    mask=mask//np.max(mask)
    im_over=np.ndarray(img.shape)
    nchannel = img.shape[2]

    im_over[:, :, 0] = (1 - mask) * img[:, :, 0] + mask * (overlay_color[0] * transparency + (1 - transparency) * img[:, :, 0])
    im_over[:, :, 1] = (1 - mask) * img[:, :, 1] + mask * (overlay_color[1] * transparency + (1 - transparency) * img[:, :, 1])
    im_over[:, :, 2] = (1 - mask) * img[:, :, 2] + mask * (overlay_color[2] * transparency + (1 - transparency) * img[:, :, 2])
    timg=im_over.astype(np.uint8)
    #limage = QtGui.QImage(timg.data, timg.shape[1], timg.shape[0], nchannel * timg.shape[1], QtGui.QImage.Format_RGB888)
    #print("preprocess image over:nchannel is {},width is {},height is {}".format(nchannel, timg.shape[1], timg.shape[0]))
    return timg



#生成自动标注的线程-with latent diversity方法
class annotateThread_inteSeg(QThread):
    finishAnno=QtCore.pyqtSignal(list)#信号,int是信号承载数据的类型

    def __init__(self,bl):
        self.bl=bl
        QThread.__init__(self)

    def run(self):#通过.Start()调用此run()函数
        clk_globalPoses=self.bl.clk_pos
        resize_factor = self.bl.scale_factor
        img_globalPoses = self.bl.imgPt
        datadir=self.bl.path_prefix
        cnt=self.bl.clk_cnt
        print("cnt:{}".format(cnt))
        pn=self.bl.pn_type
        clk_x = int((clk_globalPoses.x() - img_globalPoses[0][0]) / resize_factor + 0.5)
        clk_y = int((clk_globalPoses.y() - img_globalPoses[0][1]) / resize_factor + 0.5)
        # 图片ID帧数
        img_path = self.bl.currImg
        imIdx = img_path.split('/')[-1].split('.')[0].split('_')[0]
        #临时文件夹目录
        tmp_dir = os.path.join(datadir, imIdx + '_inteSegTmp')
        self.bl.tmp_path = tmp_dir
        QApplication.processEvents()
        outfile=our_func(datadir,clk_x,clk_y,imIdx,img_path,cnt,pn)
        QApplication.processEvents()
        self.finishAnno.emit(outfile)

class AnnoInteseg(QObject):#执行交互式图像分割的with latent diversity子线程类
    finishAnno_inteSeg_signal = QtCore.pyqtSignal(list)
    stop_inteSeg_signal = QtCore.pyqtSignal()
    def __init__(self,bl):
        super(AnnoInteseg,self).__init__()
        self.bl = bl

    def inteseg_work(self):
        clk_globalPoses = self.bl[0]
        resize_factor = self.bl[1]
        img_globalPoses = self.bl[2]
        datadir = self.bl[3]
        cnt = self.bl[4]
        print("cnt:{}".format(cnt))
        pn = self.bl[5]
        clk_x = int((clk_globalPoses.x() - img_globalPoses[0][0]) / resize_factor + 0.5)
        clk_y = int((clk_globalPoses.y() - img_globalPoses[0][1]) / resize_factor + 0.5)
        # 图片ID帧数
        img_path = self.bl[6]
        imIdx = img_path.split('/')[-1].split('.')[0].split('_')[0]
        # 临时文件夹目录
        tmp_dir = os.path.join(datadir, imIdx + '_inteSegTmp')

        QApplication.processEvents()
        outfile = our_func(datadir, clk_x, clk_y, imIdx, img_path, cnt, pn)
        QApplication.processEvents()
        self.finishAnno_inteSeg_signal.emit(outfile)
        self.stop_inteSeg_signal.emit()

class AnnoIvs(QObject):#执行交互式图像分割的ivs子线程类
    finishAnno_ivs_signal = QtCore.pyqtSignal(list)

    def __init__(self,scribbles_tmp):
        super(AnnoIvs,self).__init__()
        self.scribbles= scribbles_tmp

    def ivs_work(self):
        self.frame_file_list=self.scribbles['frames']
        self.frames = load_frames(self.frame_file_list)
        self.model = model(self.frames)
        QApplication.processEvents()
        self.model.Run_interaction(self.scribbles)
        #cursur = self.scribbles['annotated_frame']
        #current_mask= self.model.Get_mask_index(cursur)
        # a=1
        # b=0
        # if a in current_mask:
        #     print('yes-1')
        # if b in current_mask:
        #     print('yes-0')
        # print('current_mask:')
        # print(current_mask)
        outfile = self.model.get_result_pics(self.frames ,self.scribbles)
        QApplication.processEvents()
        self.finishAnno_ivs_signal.emit(outfile)


#生成自动标注的线程-grabCut方法
class annotateThread_grabCut(QThread):
    finishAnno=QtCore.pyqtSignal(list)#信号,int是信号承载数据的类型

    def __init__(self,ml):
        self.ml=ml
        QThread.__init__(self)

    def run(self):#通过.Start()调用此run()函数
        img_globalPoses=self.ml.imgPt
        rect_globalPoses=self.ml.rectPos
        resize_factor=self.ml.scale_factor
        #保存矩形相对于图像的坐标[(x0,y0),(x1,y1)]
        refPt=[(int((rect_globalPoses[0][0]-img_globalPoses[0][0])/resize_factor+0.5),int((rect_globalPoses[0][1]-img_globalPoses[0][1])/resize_factor+0.5))]
        refPt.append((int((rect_globalPoses[1][0]-img_globalPoses[0][0])/resize_factor+0.5),int((rect_globalPoses[1][1]-img_globalPoses[0][1])/resize_factor+0.5)))
        print(refPt)
        # 保存矩形的顶点坐标[min(x),min(y),max(x),max(y)]
        roiPt = (min(refPt[0][0], refPt[1][0]), min(refPt[0][1], refPt[1][1]),
                 max(refPt[0][0], refPt[1][0]), max(refPt[0][1], refPt[1][1]))
        img_path=self.ml.currImg
        img=cv2.imread(img_path)
        QApplication.processEvents()
        initialIterations=5
        mask = np.zeros(img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mask, roiPt, bgdModel, fgdModel, initialIterations,cv2.GC_INIT_WITH_RECT)
        mask[:, :roiPt[0]] = 0
        mask[:roiPt[1], :] = 0
        mask[:, roiPt[2]:] = 0
        mask[roiPt[3]:, :] = 0
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        grabCutImg0 = img // 4
        grabCutImg0[mask2 == 1] = img[mask2 == 1]
        QApplication.processEvents()
        #保存中间文件路径
        log_path = os.path.join(self.ml.path_prefix, 'logFiles')
        self.ml.log_path=log_path
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        # test绘制矩形
        draw1=cv2.rectangle(img,refPt[0],refPt[1],(0,255,0),2)
        draw2=cv2.circle(draw1,(int((self.ml.central_x-img_globalPoses[0][0])/resize_factor+0.5),int((self.ml.central_y-img_globalPoses[0][1])/resize_factor+0.5)),2,(0,0,255),3)
        outfile0 = os.path.join(log_path, 'rect.png')
        #命名-四种图片[二值图,混合标注图,加了矩形框和中点的原图,加了矩形框的混合标注图]
        idx=img_path.split('/')[-1].split('.')[0]
        filename0 = idx+'_mix.png'
        filename1 = idx+'_anno.png'
        filename2 = idx + '_rect.png'
        filename3 = idx + '_rect_mix.png'
        outfile=[os.path.join(log_path,filename0)]
        outfile.append(os.path.join(log_path,filename1))
        outfile.append(os.path.join(log_path, filename2))
        outfile.append(os.path.join(log_path, filename3))
        #保存grabCutImg0
        #outfile1 = os.path.join(log_path, 'grabCutImg0.png')
        cv2.imwrite(outfile[1], grabCutImg0)
        # 将mask的单通道变为3通道
        mask3=cv2.cvtColor(mask2,cv2.COLOR_GRAY2RGB)
        cv2.imwrite(outfile[0], mask3 * 255)
        # 生成Mix图片
        mixImage=preprocessMixImgae(img,mask)
        #draw3 = cv2.rectangle(mixImage, refPt[0], refPt[1], (0, 255, 0), 2)
        # 保存图片
        cv2.imwrite(outfile[2], draw2)
        cv2.imwrite(outfile[3], mixImage)
        #cv2.imwrite(outfile[3], draw3)
        self.finishAnno.emit(outfile)


#*****************************主类×××××××××××××××××××××××××××××××
class BubbleNetsForm(QWidget):

    def __init__(self,workdir,direct_object,osvos_object,flag,callback):
        super(BubbleNetsForm, self).__init__()  # 继承的所有父类的初始化
        self.ui=bubbleNets_Form()
        self.ui.setupUi(self)
        # *************path*******************
        self.model_folder = parent_folder4 + '/models'  # models所在目录
        self.path_prefix = workdir  # 工作目录
        self.direct_object=direct_object
        self.osvos_object=osvos_object
        # **************path********************
        self.initConstant()
        self.initUI()
        self.adjustUI()
        self.imageLabel=self.ui.image
        self.flag = flag
        self.callback=callback
        if self.flag==1:
            frame_dir=os.path.join(self.path_prefix,'JPEGImages')
            self.ui.pushButton_open.setEnabled(False)
            self.openFrameDir(frame_dir)

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
        #self.ui.pushButton_next.clicked.connect(self.nextButtonPressed)
        self.ui.pushButton_next.clicked.connect(self.annoExit)

    def returnButtonPressed(self):
        if self.flag==1:
            return
        self.direct_object.show()
        #direct_widget=DirectForm()
        #direct_widget.show()
        self.close()

    # def nextButtonPressed(self):
    #     if self.flag==1:
    #         return
    #     self.bubblenet_widget = BubbleNetsForm(self.path_prefix,self.direct_object,2,None)
    #     self.bubblenet_widget.show()
    #     self.close()

    def closeEvent(self, event):
        QWidget.closeEvent(self, event)
        if self.flag==0 or self.flag==2:
            # self.direct_object.close()
            self.close()
        else:
            if self.yes==True:
                print('yes')
                self.close()
            self.annoExit()

    def initConstant(self):
        #创建新文件夹存储标注二值图
        self.usrAnno_dir=os.path.join(self.path_prefix, 'usrAnnotate')
        if os.path.exists(self.usrAnno_dir):
            removeTmpDir(self.usrAnno_dir)
        os.makedirs(self.usrAnno_dir)
        self.currImg=None #当前显示的图片
        self.save_anotations=[] #已经保存过的标注图片
        self.file_list=[]
        self.file_list_order=[]
        self.framse_rank=[]
        self.rank_file_list = []
        self.curr_dir_path=None
        self.curr_img_idx = None #file_list当前选中的图片的
        self.navBtnWidth = 45  # 上方导航条上按钮宽度
        self.navIconFontSize = 20  # 上方导航条上图标字体的大小
        self.scale_factor=1.0 #图片缩放大小比例
        self.iter_time=1
        self.model='BN0'#bubbleNets配置的模型
        self.hasCompute=False
        #**********标注的变量***********
        self.threads_pool0 = [None, None, None, None, None]
        self.rect_annothread_cnt=-1 #线程idx
        self.log_path=None #存储grabCut文件的临时文件夹
        self.shape='矩形'
        self.hasAnnotation=False #已经生成完成标注的图片为True
        self.annotationPath=[]
        self.isExisting=False #是否显示的是已有的标注图片
        self.bk_cuurImg=None #备份的当前标注的帧源图片
        self.currAnnotation=None #当前已经生成的标注
        self.rectPos=[]#绘制的矩形框的顶点坐标[(x0,y0),(x1,y1)]
        self.imgPt=[] #图片的顶点全局坐标[(x0,y0),(x1,y1)]
        self.central_x=0 #图像的中心横坐标
        self.central_y=0 #图像的中心纵坐标
        # **************inteSeg的变量**********
        self.threads_pool=[None,None,None,None,None]
        self.clk_cnt=-1
        self.pn_type=0
        self.hasAnnotation_inteSeg=False
        self.clk_pos=None
        self.tmp_path=None
        # **************ivs的变量**********
        self.hasAnnotation_ivs = False
        self.scribbles={}
        self.cursur=0
        self.threads_pool2 = [None,None,None,None,None]
        self.ivs_annothread_cnt = -1
        # **************deepGrab的变量**********
        self.hasAnnotation_deepGrab = False
        self.threads_pool3 = [None, None, None, None, None]
        # ******bubbleNets参数×××××××××

        #********自动加载文件夹*********
        self.flag=0
        # ********自动加载文件夹*********
        # **********两个按键************

        self.yes=False
        # **********两个按键************

    def initUI(self):
        #窗体居中显示
        screen_size=QDesktopWidget().screenGeometry()#获得屏幕的尺寸
        widget_size=self.geometry()#获得窗体的尺寸
        self.move((screen_size.width()-widget_size.width())/2,(screen_size.height()-widget_size.height())/2)
        self.ui.frame.setProperty('flag','nav')
        self.setWindowTitle(u'关键帧标注')
        #标题栏
        qss_label_title=[]
        qss_label_title.append('QLabel#label_title{{font:{}px;}}'.format(self.navIconFontSize))
        #qss_label_title.append('QFrame[flag="nav"]{{background:qlineargradient'
        # '(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 {},stop:1 {});}}'.format('#FFFFFF','#FFFFFF'))
        qss_label_title.append('QFrame[flag="nav"] QAbstractButton{{background:none;border:none;'
        'min-width:{0}px;max-width:{0}px;}}'.format(self.navBtnWidth))
        self.setStyleSheet(''.join(qss_label_title))

        #textBroswer
        self.cursor_text = self.ui.textBrowser.textCursor()
        self.cursor_text.movePosition(QtGui.QTextCursor.End)
        self.ui.textBrowser.setTextCursor(self.cursor_text)
        self.ui.textBrowser.ensureCursorVisible()

        #禁止的按钮
        self.ui.pushButton_showbubble.setEnabled(False)

        #comboBox_shape形状
        self.ui.comboBox_shape.addItem('矩形')
        self.ui.comboBox_shape.addItem('涂鸦')
        #self.ui.comboBox_shape.addItem('圆形')
        self.ui.comboBox_shape.addItem('单击')

        #选择模型combBox
        self.ui.comboBox_model.addItems(['BN0','BNLF'])

        #spinBox的值改变关联函数
        self.ui.doubleSpinBox_resize.valueChanged.connect(self.resizeValueChanged)

        # 选择形状的comboBox的值改变关联函数
        self.ui.comboBox_shape.currentIndexChanged.connect(self.shapeValueChanged)

        #按钮按下关联函数
        self.ui.listWidget_file.itemDoubleClicked.connect(self.file_item_double_clicked)
        self.ui.pushButton_open.clicked.connect(self.openDir)
        self.ui.pushButton_compute.clicked.connect(self.computeButtonPressed)
        self.ui.pushButton_showbubble.clicked.connect(self.showSortImg)
        self.ui.toolButton_exist.clicked.connect(self.existingButtonPressed)
        self.ui.toolButton_save.clicked.connect(self.saveAnnotate)
        self.ui.toolButton_start.clicked.connect(self.startAnnotate)
        self.ui.toolButton_finish.clicked.connect(self.finishAnnotate)
        self.ui.toolButton_restart.clicked.connect(self.restartAnnotate)

        #label用户绘制完毕的信号

    def annoExit(self):
        if self.flag==1:
            if not os.listdir(self.usrAnno_dir):
                reply=QMessageBox.question(self,'Next','还未完成标注，确定退出吗？',QMessageBox.No|QMessageBox.Yes)
                if reply==QMessageBox.Yes:
                    path_list=[]
                    # if self.yes==True:
                    self.callback(path_list)
                    self.yes=True
                    self.close()
                else:
                    pass
            else:
                path_list=[]
                pic_names=os.listdir(self.usrAnno_dir)
                for pic in pic_names:
                    path_list.append(os.path.join(self.usrAnno_dir,pic))
                self.callback(path_list)
                self.close()
        elif self.flag==0: #direct传给它
            self.osvos_object.show()
            self.close()
        elif self.flag==2:#frameExtract传给它
            self.osvos_object.show()
            self.close()
    #**************************标注的类和函数************************

    # 点击开始标注按钮触发的函数
    def startAnnotate(self):
        if self.currImg==None or self.currImg==os.path.join(self.path_prefix,'sort.png'):
            return
        # if self.hasAnnotation==True:
        #     if self.currImg==self.annotationPath[0] or self.currImg==self.annotationPath[1] or self.currImg==self.annotationPath[2] or self.currImg==self.annotationPath[3]:
        #         return
        #如果是打开已有标注
        self.ui.toolButton_exist.setEnabled(False)
        self.ui.toolButton_start.setEnabled(False)
        self.ui.toolButton_save.setEnabled(False)
        self.ui.toolButton_finish.setEnabled(False)
        self.ui.doubleSpinBox_resize.setEnabled(False)
        self.ui.pushButton_showbubble.setEnabled(False)
        self.ui.comboBox_shape.setEnabled(False) #不能再选择标注形状
        #备份当前标注的源图片路径
        self.bk_cuurImg=self.currImg

        if self.shape=='矩形':
            #self.hasAnnotation = False
            self.imageLabel.isShow = True
            self.imageLabel.setCursor(Qt.CrossCursor)
            # 方框绘制完成发射信号
            self.imageLabel.formAnno.connect(self.formAnnotate_grabCut)
        elif self.shape=='单击':
            #self.hasAnnotation_inteSeg=False
            self.imageLabel.isShow = True
            print("self.shape:{}".format(self.shape))
            print("self.imageLabel:{}".format(self.imageLabel))
            print("isShow:{}".format(self.imageLabel.isShow))
            self.imageLabel.formAnno.connect(self.formAnnotate_inteSeg)
        elif self.shape=='圆形':
            #self.hasAnnotation_deepGrab=False
            self.imageLabel.isShow = True
            print("self.shape:{}".format(self.shape))
            print("self.imageLabel:{}".format(self.imageLabel))
            print("isShow:{}".format(self.imageLabel.isShow))
            self.imageLabel.setCursor(Qt.CrossCursor)
            self.imageLabel.formAnno.connect(self.formAnnotate_deepGrab)
        elif self.shape=='涂鸦':
            #self.hasAnnotation_ivs=False
            self.imageLabel.isShow = True
            print("self.shape:{}".format(self.shape))
            print("self.imageLabel:{}".format(self.imageLabel))
            print("isShow:{}".format(self.imageLabel.isShow))
            self.imageLabel.formAnno.connect(self.formAnnotate_ivs)
        #将周围变暗

    # 点击完成标注触发的函数
    def finishAnnotate(self):
        if self.hasAnnotation==False and self.hasAnnotation_inteSeg==False and self.hasAnnotation_ivs==False and self.hasAnnotation_deepGrab==False:
            return
        print("点击完成标注")
        self._load_img(self.annotationPath[0])
        self.ui.toolButton_save.setEnabled(True)

    def formAnnotate_ivs(self,point_type):
        if self.currImg==None or self.currImg==os.path.join(self.path_prefix,'sort.png'):
            return
        self.imageLabel.isShow=False
        if point_type==0:
            print("前景点")
        elif point_type==1:
            print("后景点")
        self.cursur= int(self.currImg.split('/')[-1].split('.')[0].split('_')[0])
        self.scribbles['annotated_frame'] = self.cursur
        pic_list=[]
        for filename in self.file_list_order:
            filename_path = os.path.join(self.curr_dir_path,filename)
            pic_list.append(filename_path)
        self.scribbles['frames']=pic_list
        #frames = load_frames(self.file_list)
        self.scribbles['model_prefix'] = self.model_folder
        stroke = self.imageLabel.getStrokeGlobalPos()
        stroke_poses=stroke['path']
        stroke_poses_global=[]
        # 坐标变换
        label_pos = self.imageLabel.pos()
        global_label_pos = self.imageLabel.mapToGlobal(label_pos)
        label_half_width = int(self.imageLabel.size().width() / 2 + 0.5)
        label_half_height = int(self.imageLabel.size().height() / 2 + 0.5)
        self.central_x = global_label_pos.x() + label_half_width
        self.central_y = global_label_pos.y() + label_half_height
        img_half_width = int((self.curr_img_width * self.scale_factor) / 2 + 0.5)
        img_half_height = int((self.curr_img_height * self.scale_factor) / 2 + 0.5)
        self.imgPt = [(self.central_x - img_half_width, self.central_y - img_half_height)]
        self.imgPt.append((self.central_x + img_half_width, self.central_y + img_half_height))
        lines_path=[]#存储绝对值坐标用来绘制描线
        for stroke_pos in stroke_poses:
            global_x_line=int((stroke_pos[0]- self.imgPt[0][0]) / self.scale_factor + 0.5)
            global_y_line=int((stroke_pos[1]- self.imgPt[0][1]) / self.scale_factor + 0.5)

            global_x = float((stroke_pos[0] - self.imgPt[0][0]) / self.scale_factor)/float(self.curr_img_width)
            global_y = float((stroke_pos[1] - self.imgPt[0][1]) / self.scale_factor)/float(self.curr_img_height)
            lines_path.append([global_x_line,global_y_line])
            stroke_poses_global.append([global_x,global_y])
        stroke['path']=stroke_poses_global
        stroke['line_path']=lines_path
        self.scribbles['scribbles'][self.cursur].append(stroke)

        print('self.cursur:{}'.format(self.cursur))
        print('previous_path:')
        print(stroke_poses)
        print('global_path:')
        print(stroke['path'])
        # 临时存储文件
        tmp_dir = os.path.join(self.path_prefix, str(self.cursur) + '_ivsTmp')
        if os.path.exists(tmp_dir):
            removeTmpDir(tmp_dir)
        self.tmp_path = tmp_dir
        self.scribbles['tmp_dir'] = tmp_dir
        #多线程
        self.ivs_annothread_cnt+=1
        self.threads_pool2[self.ivs_annothread_cnt % 5] = None
        self.threads_pool2[self.ivs_annothread_cnt % 5]=QtCore.QThread()
        self.ivsSeg=AnnoIvs(self.scribbles)
        self.ivsSeg.moveToThread(self.threads_pool2[self.ivs_annothread_cnt % 5])
        self.threads_pool2[self.ivs_annothread_cnt % 5].started.connect(self.ivsSeg.ivs_work)
        self.ivsSeg.finishAnno_ivs_signal.connect(self.finishFormAnno_ivs)
        self.threads_pool2[self.ivs_annothread_cnt % 5].start()

    def formAnnotate_deepGrab(self):
        if self.currImg==None or self.currImg==os.path.join(self.path_prefix,'sort.png'):
            return
        self.imageLabel.isShow=False
        print('信号:formAnnotate_deepGrab')

    def formAnnotate_inteSeg(self,point_type):
        if self.currImg==None or self.currImg==os.path.join(self.path_prefix,'sort.png'):
            return
        print('信号:formAnnotate_inteSeg')
        self.imageLabel.isShow=False
        if point_type==0:
            self.clk_cnt+=1
            self.pn_type=point_type
            print("前景点")
        elif point_type==1:
            self.clk_cnt += 1
            self.pn_type = point_type
            print("后景点")
        self.clk_pos=self.imageLabel.getPointGlobalPos()
        self.imageLabel.isShow = False

        # 坐标变换
        label_pos = self.imageLabel.pos()
        global_label_pos = self.imageLabel.mapToGlobal(label_pos)
        label_half_width = int(self.imageLabel.size().width() / 2 + 0.5)
        label_half_height = int(self.imageLabel.size().height() / 2 + 0.5)
        self.central_x = global_label_pos.x() + label_half_width
        self.central_y = global_label_pos.y() + label_half_height
        img_half_width = int((self.curr_img_width * self.scale_factor) / 2 + 0.5)
        img_half_height = int((self.curr_img_height * self.scale_factor) / 2 + 0.5)
        self.imgPt = [(self.central_x - img_half_width, self.central_y - img_half_height)]
        self.imgPt.append((self.central_x + img_half_width, self.central_y + img_half_height))
        #方法二
        # self.threads_pool[self.clk_cnt%5]=None
        # self.threads_pool[self.clk_cnt%5]=annotateThread_inteSeg(self)
        # self.threads_pool[self.clk_cnt%5].finishAnno.connect(self.finishFormAnno_inteSeg)
        # self.threads_pool[self.clk_cnt%5].start()
        #方法一
        # self.bthread = annotateThread_inteSeg(self)
        # self.bthread.finishAnno.connect(self.finishFormAnno_inteSeg)
        # self.bthread.start()
        #方法三
        args=[self.clk_pos]
        args.append(self.scale_factor)
        args.append(self.imgPt)
        args.append(self.path_prefix)
        args.append(self.clk_cnt)
        args.append(self.pn_type)
        args.append(self.currImg)
        print(args)
        # 临时存储文件
        imIdx = self.currImg.split('/')[-1].split('.')[0].split('_')[0]
        tmp_dir = os.path.join(self.path_prefix, imIdx + '_inteSegTmp')
        self.tmp_path = tmp_dir
        #绑定线程信号

        # self.inteSeg_thread=QtCore.QThread()
        # self.inteSeg=AnnoInteseg(args)
        # self.inteSeg.moveToThread(self.inteSeg_thread)
        # self.inteSeg_thread.started.connect(self.inteSeg.inteseg_work)
        # self.inteSeg.finishAnno_inteSeg_signal.connect(self.finishFormAnno_inteSeg)
        # self.inteSeg_thread.start()
        self.threads_pool[self.clk_cnt % 5] = None
        self.threads_pool[self.clk_cnt % 5]=QtCore.QThread()
        self.inteSeg=AnnoInteseg(args)
        self.inteSeg.moveToThread(self.threads_pool[self.clk_cnt % 5])
        self.threads_pool[self.clk_cnt % 5].started.connect(self.inteSeg.inteseg_work)
        self.inteSeg.finishAnno_inteSeg_signal.connect(self.finishFormAnno_inteSeg)
        self.threads_pool[self.clk_cnt % 5].start()


    def formAnnotate_grabCut(self):
        if self.currImg==None or self.currImg==os.path.join(self.path_prefix,'sort.png'):
            return
        self.rectPos = self.imageLabel.getRectGlobalPos()
        self.imageLabel.isShow = False #不可绘制矩形框
        self.imageLabel.setCursor(Qt.ArrowCursor)
        print('信号:formAnnotate_grabCut')
        #坐标变换
        #print("rectPos:{}".format(self.rectPos))
        label_pos = self.imageLabel.pos()
        #print("label_pos:{}".format(label_pos))
        global_label_pos=self.imageLabel.mapToGlobal(label_pos)
        #print("global_label_pos:{}".format(global_label_pos))
        label_half_width=int(self.imageLabel.size().width()/2+0.5)
        label_half_height=int(self.imageLabel.size().height()/2+0.5)
        #print("label size:{}".format(self.imageLabel.size()))
        self.central_x = global_label_pos.x()+label_half_width
        self.central_y = global_label_pos.y()+label_half_height
        #print("central_x centra_y:({},{})".format(self.central_x,self.central_y))
        #print("scale_factor:{}".format(self.scale_factor))
        #print("image size:({},{})".format(self.curr_img_width,self.curr_img_height))
        img_half_width=int((self.curr_img_width*self.scale_factor)/2+0.5)
        img_half_height=int((self.curr_img_height*self.scale_factor)/2+0.5)
        self.imgPt=[(self.central_x-img_half_width,self.central_y-img_half_height)]
        self.imgPt.append((self.central_x+img_half_width,self.central_y+img_half_height))
        #print("imgPt:{}".format(self.imgPt))
        self.rect_annothread_cnt+=1
        self.threads_pool0[self.rect_annothread_cnt%5]=None
        self.threads_pool0[self.rect_annothread_cnt%5]=annotateThread_grabCut(self)
        self.threads_pool0[self.rect_annothread_cnt%5].finishAnno.connect(self.finishFormAnno)
        self.threads_pool0[self.rect_annothread_cnt%5].start()

        # self.athread = annotateThread_grabCut(self)
        # self.athread.finishAnno.connect(self.finishFormAnno)
        # self.athread.start()

    #生成标注完成信号连接的函数
    def finishFormAnno(self,anno_pics):
        print('完成生成标注！')
        self.annotationPath=anno_pics
        self.imageLabel.isShow = False  # 不可绘制矩形框
        self.imageLabel.setCursor(Qt.ArrowCursor)
        self.hasAnnotation=True
        self.ui.toolButton_exist.setEnabled(True)
        #self.ui.toolButton_start.setEnabled(True)
        #self.ui.toolButton_save.setEnabled(True)
        self.ui.toolButton_finish.setEnabled(True)
        self.ui.doubleSpinBox_resize.setEnabled(True)
        self.ui.pushButton_showbubble.setEnabled(True)
        self.ui.doubleSpinBox_resize.setEnabled(True)
        self._load_img(self.annotationPath[1])
        self.imageLabel.formAnno.disconnect(self.formAnnotate_grabCut)
        self.threads_pool0[self.rect_annothread_cnt%5].quit()
        self.threads_pool0[self.rect_annothread_cnt%5].wait()
        self.threads_pool0[self.rect_annothread_cnt % 5].deleteLater()

    def finishFormAnno_inteSeg(self,anno_pics):
        self.annotationPath = anno_pics
        self.imageLabel.isShow = False  # 不可绘制矩形框
        self.imageLabel.setCursor(Qt.ArrowCursor)
        self.hasAnnotation_inteSeg = True
        self.ui.toolButton_exist.setEnabled(True)
        self.ui.toolButton_start.setEnabled(True)
        self.ui.toolButton_finish.setEnabled(True)
        self.ui.doubleSpinBox_resize.setEnabled(True)
        self.ui.pushButton_showbubble.setEnabled(True)
        self.ui.doubleSpinBox_resize.setEnabled(True)
        self._load_img(self.annotationPath[3])
        # self.threads_pool[self.clk_cnt%5].wait()
        # self.threads_pool[self.clk_cnt%5].quit()
        #self.inteSeg_thread.quit()
        #****************************
        # self.inteSeg_thread.wait()
        # self.inteSeg_thread.quit()
        # self.inteSeg.deleteLater()
        # self.inteSeg_thread.deleteLater()
        # ****************************
        self.imageLabel.formAnno.disconnect(self.formAnnotate_inteSeg)
        self.inteSeg.finishAnno_inteSeg_signal.disconnect(self.finishFormAnno_inteSeg)
        self.threads_pool[self.clk_cnt % 5].quit()
        self.threads_pool[self.clk_cnt % 5].wait()
        self.inteSeg.deleteLater()
        self.threads_pool[self.clk_cnt % 5].deleteLater()

    def finishFormAnno_ivs(self,anno_pics):
        self.annotationPath = anno_pics
        self.imageLabel.isShow = False  # 不可绘制矩形框
        self.imageLabel.setCursor(Qt.ArrowCursor)
        self.hasAnnotation_ivs = True
        self.ui.toolButton_exist.setEnabled(True)
        self.ui.toolButton_start.setEnabled(True)
        self.ui.toolButton_finish.setEnabled(True)
        self.ui.doubleSpinBox_resize.setEnabled(True)
        self.ui.pushButton_showbubble.setEnabled(True)
        self.ui.doubleSpinBox_resize.setEnabled(True)
        self._load_img(self.annotationPath[1])
        self.imageLabel.formAnno.disconnect(self.formAnnotate_ivs)
        self.ivsSeg.finishAnno_ivs_signal.disconnect(self.finishFormAnno_ivs)
        self.threads_pool2[self.ivs_annothread_cnt % 5].quit()
        self.threads_pool2[self.ivs_annothread_cnt % 5].wait()
        self.ivsSeg.deleteLater()
        self.threads_pool2[self.ivs_annothread_cnt % 5].deleteLater()

    # 点击重新开始标注触发的函数
    def restartAnnotate(self):
        if self.currImg==None or self.currImg==os.path.join(self.path_prefix,'sort.png'):
            return
        self._load_img( self.bk_cuurImg)
        self.initAnno()
        #切断信号
        # if self.shape=='矩形':
        #     self.imageLabel.formAnno.disconnect(self.formAnnotate_grabCut)
        # elif self.shape=='单击':
        #     self.imageLabel.formAnno.disconnect(self.formAnnotate_inteSeg)
        # elif self.shape=='圆形':
        #     self.imageLabel.formAnno.disconnect(self.formAnnotate_deepGrab)
        # elif self.shape=='涂鸦':
        #     self.imageLabel.formAnno.disconnect(self.formAnnotate_ivs)


    def initAnno(self):
        self.imageLabel.isShow = False  # 不可绘制矩形框
        self.imageLabel.setCursor(Qt.ArrowCursor)

        self.ui.toolButton_exist.setEnabled(True)
        self.ui.toolButton_start.setEnabled(True)
        self.ui.toolButton_save.setEnabled(True)
        self.ui.toolButton_finish.setEnabled(True)
        self.ui.comboBox_shape.setEnabled(True)
        self.ui.doubleSpinBox_resize.setEnabled(True)
        self.ui.pushButton_showbubble.setEnabled(True)

        # 删除已有标注
        if self.hasAnnotation == True:
            removeTmpDir(self.log_path)
            self.log_path=None
            self.annotationPath = []
            self.hasAnnotation = False
        if self.hasAnnotation_inteSeg==True:
            if os.path.exists(self.tmp_path):
                removeTmpDir(self.tmp_path)
            self.clk_cnt=-1
            self.hasAnnotation_inteSeg=False
        if self.hasAnnotation_ivs==True:
            self.hasAnnotation_ivs = False
            self.scribbles = {}
            if len(self.file_list)>0:
                self.scribbles['scribbles'] = [[] for _ in range(len(self.file_list))]
            if os.path.exists(self.tmp_path):
                removeTmpDir(self.tmp_path)
    # **************************标注的类和函数************************

    #点击保存标注按钮触发的函数
    def saveAnnotate(self):
        if self.currImg == None:
            return
        #保存的是打开的已有标注
        if self.isExisting==True:
            print("isExistingis True")
            if not self.currImg in self.save_anotations:
                label,ok=QInputDialog.getText(self,'保存标注','输入标签label')
                if label and ok:
                    ano_id=self.currImg.split('/')[-1].split('.')[0]
                    anno_name='{:05d}'.format(ano_id)+'_'+label+'.png'
                    #创建保存标注的文件夹
                    # if not os.path.exists(self.anno_save_folder):
                    #     os.makedirs(self.anno_save_folder)
                    #复制文件
                    shutil.copyfile(self.currImg,os.path.join(self.usrAnno_dir,anno_name))
                    self.save_anotations.append(self.currImg)
                    #弹出保存成功对话框
                    infoBox=QMessageBox(self)
                    # QMessageBox.about(self, 'Success', '标注已保存到相应目录!')
                    #infoBox.setIcon(QMessageBox.information)
                    infoBox.setText('标注已保存到相应目录!')
                    infoBox.setWindowTitle('Success')
                    infoBox.setStandardButtons(QMessageBox.Ok)
                    infoBox.button(QMessageBox.Ok).animateClick(1*1000)
                    infoBox.exec_()
            else:
                return
        elif self.hasAnnotation==True or self.hasAnnotation_inteSeg==True or self.hasAnnotation_ivs==True or self.hasAnnotation_deepGrab==True:
            self.ui.toolButton_finish.setEnabled(False)
            print("hasAnnotation==True")
            label, ok = QInputDialog.getText(self, '保存标注', '输入标签label')
            if label and ok:
                ano_id = int(self.currImg.split('/')[-1].split('.')[0].split('_')[0])
                anno_name = '{:05d}'.format(ano_id)+'_'+label+'.png'
                # 创建保存标注的文件夹
                # if not os.path.exists(self.anno_save_folder):
                #     os.makedirs(self.anno_save_folder)
                # 复制文件
                shutil.copyfile(self.currImg, os.path.join(self.usrAnno_dir, anno_name))
                self.save_anotations.append(self.currImg)
                # 弹出保存成功对话框
                infoBox1 = QMessageBox(self)
                infoBox1.setText('标注已保存到相应目录!')
                infoBox1.setWindowTitle('Success')
                infoBox1.setStandardButtons(QMessageBox.Ok)
                infoBox1.button(QMessageBox.Ok).animateClick(1 * 1000)
                infoBox1.exec_()

            self.hasAnnotation = False
            self.hasAnnotation_inteSeg=False
            self.hasAnnotation_ivs = False
            self.hasAnnotation_deepGrab= False


    #点击已有标注按钮触发的函数
    def existingButtonPressed(self):
        filename,filetype=QFileDialog.getOpenFileName(self,"选取标注文件",self.path_prefix)
        if not self._load_img(filename):
            return
        else:
            self.isExisting=True
            self.initAnno()

    #缩放比例改变显示图片随之改变大小
    def resizeValueChanged(self):
        if self.currImg==None:
            return
        self._load_img(self.currImg)

    # 选择标注的形状改变Label对应改变
    def shapeValueChanged(self):
        self.shape = self.ui.comboBox_shape.currentText()
        old_imageLabel=self.imageLabel
        if self.shape=='单击':
            self.imageLabel = MyLabel_inteSeg(self.ui.frame_5)
        elif self.shape=='矩形':
            self.imageLabel = MyLabel(self.ui.frame_5)
        elif self.shape == '圆形':
            self.imageLabel = MyLabel_deepGrab(self.ui.frame_5)
        elif self.shape=='涂鸦':
            self.imageLabel = MyLabel_ivs(self.ui.frame_5)
        self.ui.horizontalLayout_5.replaceWidget(old_imageLabel,self.imageLabel) #替换原来的Label控件
        #删除旧的控件
        old_imageLabel.deleteLater()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageLabel.sizePolicy().hasHeightForWidth())
        self.imageLabel.setSizePolicy(sizePolicy)
        self.imageLabel.setMinimumSize(QtCore.QSize(0, 0))
        self.imageLabel.setText("")
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.imageLabel.setObjectName("image")
        if self.currImg!=None:
            if not self._load_img(self.currImg):
                return
            else:
                print("切换Label为:"+self.shape)

    #将输出重定位到textBroswer
    def outputWritten(self,text):
        self.cursor_text.insertText(text)
        self.ui.textBrowser.setTextCursor(self.cursor_text)
        self.ui.textBrowser.ensureCursorVisible()

    #计算性能最好的帧
    def computeButtonPressed(self):
        if self.curr_dir_path==None:
            QMessageBox.about(self, 'Warning', '请点击打开视频帧文件选择输入的图片文件夹!')
            return
        self.hasCompute=False
        self.ui.pushButton_open.setEnabled(False)
        self.ui.spinBox_iter.setEnabled(False)
        self.ui.comboBox_model.setEnabled(False)
        self.ui.progressBar.setMaximum(0)
        self.model=self.ui.comboBox_model.currentText() #str
        self.iter_time=self.ui.spinBox_iter.value() #int
        self.cthread=computeBestFrameThread(self)
        self.cthread.finishBubble.connect(self.finishCompute)

        self.old_stdout=sys.stdout
        self.old_stderr=sys.stderr
        sys.stdout = EmittingStream(textWritten=self.outputWritten)
        sys.stderr = EmittingStream(textWritten=self.outputWritten)

        self.cthread.start()

    #计算完帧性能触发的函数
    def finishCompute(self,frames_list):
        self.ui.progressBar.setMaximum(1)
        self.hasCompute=True
        #self.ui.progressBar.setProperty("value",1)
        self.ui.pushButton_open.setEnabled(True)
        self.ui.spinBox_iter.setEnabled(True)
        self.ui.comboBox_model.setEnabled(True)
        self.ui.pushButton_showbubble.setEnabled(True)
        self.isExisting = False
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.framse_rank=frames_list
        top_frame = self.file_list_order[self.framse_rank[0]]
        top_id = top_frame.split('.')[0]

        for i in self.framse_rank:
            self.rank_file_list.append(self.file_list_order[i])

        print('rank_file_list:')
        print(self.rank_file_list)

        self.file_list=self.rank_file_list
        self.ui.label_result.setText('最佳性能帧为:{} {}'.format(top_id,top_frame))
        self.ui.listWidget_file.clear()
        for idx, file_path in enumerate(self.file_list):
            item = QListWidgetItem(file_path)
            item.setFlags(item.flags() ^ Qt.ItemIsUserCheckable)
            # if self._has_label_file(idx):
            #     item.setCheckState(Qt.Checked)
            # else:
            #     item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_file.addItem(item)

        init_idx=0
        self._switch_img(init_idx)

    #点击展示排序结果按钮触发的函数
    def showSortImg(self):
        sort_img=os.path.join(self.path_prefix,'sort.png')
        if not self._load_img(sort_img):
            return
        self.isExisting = False

    #打开输入图片文件夹并显示在listWidget中
    def file_item_double_clicked(self,item):
        file_name = item.text()
        img_idx = self.file_list.index(file_name)
        self._switch_img(img_idx)
        self.isExisting = False
        self.initAnno()

    #自动加载视频帧
    def openFrameDir(self,dir_path):
        print('openFrameDir')
        #导入图片到file_list
        if self.curr_dir_path == dir_path:
            return
        self.curr_dir_path = dir_path
        self.curr_img_idx=None
        self.file_list = sorted([name for name in os.listdir(dir_path) if self._is_img(name)])
        self.file_list_order=self.file_list
        #初始化ivs的scribbles大小
        self.scribbles['scribbles'] = [[] for _ in range(len(self.file_list))]
        if not self.file_list:
            QMessageBox.about(self, 'Warning', '输入图片不能为空!')
            return
        self.ui.listWidget_file.clear()
        self.curr_img_idx=None
        for idx, file_path in enumerate(self.file_list):
            item = QListWidgetItem(file_path)
            item.setFlags(item.flags() ^ Qt.ItemIsUserCheckable)
            # if self._has_label_file(idx):
            #     item.setCheckState(Qt.Checked)
            # else:
            #     item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_file.addItem(item)

        init_idx=0
        self._switch_img(init_idx)
        self.isExisting = False
        self.initAnno()

    #点击打开视频帧文件触发的函数
    def openDir(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Open Folder', self.path_prefix)
        if not os.path.isdir(dir_path):
            QMessageBox.about(self, 'Warning', '请选择包含用于训练排序的输入图片文件夹!')
            return
        #导入图片到file_list
        if self.curr_dir_path == dir_path:
            return
        self.curr_dir_path = dir_path
        self.curr_img_idx=None
        self.file_list = sorted([name for name in os.listdir(dir_path) if self._is_img(name)])
        self.file_list_order=self.file_list
        #初始化ivs的scribbles大小
        self.scribbles['scribbles'] = [[] for _ in range(len(self.file_list))]
        if not self.file_list:
            QMessageBox.about(self, 'Warning', '输入图片不能为空!')
            return
        self.ui.listWidget_file.clear()
        self.curr_img_idx=None
        for idx, file_path in enumerate(self.file_list):
            item = QListWidgetItem(file_path)
            item.setFlags(item.flags() ^ Qt.ItemIsUserCheckable)
            # if self._has_label_file(idx):
            #     item.setCheckState(Qt.Checked)
            # else:
            #     item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_file.addItem(item)

        init_idx=0
        self._switch_img(init_idx)
        self.isExisting = False
        self.initAnno()

    #判断是否是图片
    def _is_img(self, file_name):
        ext = file_name.split('.')[-1]
        return ext in ['jpg', 'jpeg', 'png', 'bmp']

    #切换图片
    def _switch_img(self,img_idx):
        if img_idx == self.curr_img_idx and self.hasCompute==False:
            return
        self.hasCompute=True
        img_name=self.file_list[img_idx]
        img_path=os.path.join(self.curr_dir_path,img_name)
        if not self._load_img(img_path):
            return
        self.curr_img_idx = img_idx
        file_widget_item = self.ui.listWidget_file.item(img_idx)
        file_widget_item.setSelected(True)

    #加载图片并显示到label中
    def _load_img(self, img_path):
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
        self.curr_img_width=pixmap.size().width()
        self.curr_img_height=pixmap.size().height()
        self.scale_factor=self.ui.doubleSpinBox_resize.value()
        pixmap=pixmap.scaled(int(self.curr_img_width*self.scale_factor),int(self.curr_img_height*self.scale_factor),Qt.KeepAspectRatio)
        #print(pixmap.size())
        print("load_img")
        print(self.imageLabel)
        self.imageLabel.setPixmap(pixmap)
        self.currImg =img_path

        return True

    def printSizeAndPos(self):
        print('frame_7:')
        pos1=self.ui.frame_7.pos()
        print("pos:{}".format(pos1))
        print("globalPos:{}".format(self.ui.frame_7.mapToGlobal(pos1)))
        print("size:{}".format(self.ui.frame_7.size()))
        print("geometry:{}".format(self.ui.frame_7.geometry()))
        print("frameGeometry:{}".format(self.ui.frame_7.frameGeometry()))
        print("frameSize:{}".format(self.ui.frame_7.frameSize()))
        print('image:')
        pos2 = self.imageLabel.pos()
        print("pos:{}".format(pos2))
        print("globalPos:{}".format(self.imageLabel.mapToGlobal(pos2)))
        print("size:{}".format(self.imageLabel.size()))
        print("geometry:{}".format(self.imageLabel.geometry()))
        print("frameGeometry:{}".format(self.imageLabel.frameGeometry()))
        print("frameSize:{}".format(self.imageLabel.frameSize()))
        print("******")
        print(self.imageLabel.geometry().x())
        print("******")
        print('frame_4:')
        pos3 = self.ui.frame_4.pos()
        print("pos:{}".format(pos3))
        print("globalPos:{}".format(self.ui.frame_4.mapToGlobal(pos3)))
        print("size:{}".format(self.ui.frame_4.size()))
        print("geometry:{}".format(self.ui.frame_4.geometry()))
        print("frameGeometry:{}".format(self.ui.frame_4.frameGeometry()))
        print("frameSize:{}".format(self.ui.frame_4.frameSize()))

#*****************************主类×××××××××××××××××××××××××××××××


#test
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainWindow = BubbleNetsForm(default_workdir)
#     mainWindow.show()
#     sys.exit(app.exec_())