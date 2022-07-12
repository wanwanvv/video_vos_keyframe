import os
import sys

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

root_folder5 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder5=os.path.dirname(root_folder5 )
sys.path.append(parent_folder5)
sys.path.append(os.path.join(parent_folder5,'bubbleNets'))
sys.path.append(os.path.join(parent_folder5,'models'))

from ResNet_preprocess import *
from BubbleNets_frame_select import *
from bn_utils import *

class computeBestFrameThread(QThread):
    finishBubble = QtCore.pyqtSignal(list)
    def __init__(self,bn):
        self.bn=bn
        QThread.__init__(self)

    def run(self):
        workDir=self.bn.path_prefix
        dataDir=self.bn.curr_dir_path
        modelDir=self.bn.model_folder
        cmodel=self.bn.model
        iterTime=self.bn.iter_time
        # Preprocess through ResNet.
        QApplication.processEvents()
        resnet_process_data_dir(workDir,dataDir,modelDir)  # 在每个data文件夹下生成经过resnet预处理的pk文件
        QApplication.processEvents()
        frams_rank=BubbleNets_sort(dataDir,workDir, modelDir,iterTime,model=cmodel)  # 输出用BN模型预测的最佳性能帧,放在data目录下的txt文件中
        QApplication.processEvents()
        select_dir=os.path.join(workDir,'frame_selection')
        lines = read_list_file(os.path.join(select_dir, '%s.txt' % cmodel))
        best_frame=lines[2]
        best_id=lines[1]

        self.finishBubble.emit(frams_rank)

