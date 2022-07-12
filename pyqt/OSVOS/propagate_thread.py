import os,sys
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication

from propagate_utils import load_frames
from propagate_model import model

root_folder = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder=os.path.dirname(root_folder )
sys.path.append(parent_folder)

class VosIvs_thread(QObject):#执行交互式图像分割的ivs子线程类
    finishVos_signal = QtCore.pyqtSignal(str)

    def __init__(self,scribbles_tmp):
        super(VosIvs_thread,self).__init__()
        self.scribbles = scribbles_tmp
        #self.maskinfo= maskinfo_tmp

    def VosIvs_work(self):
        self.frame_file_list=self.scribbles['frames']
        self.frames = load_frames(self.frame_file_list)
        self.model = model(self.frames)
        target=self.scribbles['annotated_frame']
        QApplication.processEvents()
        self.model.Run_interaction(self.scribbles)
        QApplication.processEvents()
        self.model.Run_propagation(target,mode='linear', at_least=-1)
        tmp_dir=self.scribbles['tmp_dir']
        self.model.get_result_pics(tmp_dir)
        self.finishVos_signal.emit(tmp_dir)