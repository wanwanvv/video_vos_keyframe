from __future__ import division
import torch
from torch.autograd import Variable
from torch.utils import data

import torch.nn as nn
import torch.nn.functional as F
import cv2
import os,sys
import time
from copy import  deepcopy
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
#
root_folder = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder=os.path.dirname(root_folder )
sys.path.append(parent_folder)
from RGMP_model import RGMP
from RGMP_utils import ToCudaVariable, ToLabel, DAVIS, upsample, downsample


class VosRGMP_thread(QObject):#执行交互式图像分割的ivs子线程类
    finishVosRGMP_signal = QtCore.pyqtSignal(str)

    def __init__(self,maskinfo_tmp):
        super(VosRGMP_thread,self).__init__()
        self.model=None
        self.maskinfo= maskinfo_tmp

    def Encode_MS(self,val_F1, val_P1, scales):
        ref = {}
        for sc in scales:
            if sc != 1.0:
                msv_F1, msv_P1 = downsample([val_F1, val_P1], sc)
                msv_F1, msv_P1 = ToCudaVariable([msv_F1, msv_P1], volatile=True)
                ref[sc] = self.model.module.Encoder(msv_F1, msv_P1)[0]
            else:
                msv_F1, msv_P1 = ToCudaVariable([val_F1, val_P1], volatile=True)
                ref[sc] = self.model.module.Encoder(msv_F1, msv_P1)[0]

        return ref

    def Propagate_MS(self,ref, val_F2, val_P2, scales):
        h, w = val_F2.size()[2], val_F2.size()[3]
        msv_E2 = {}
        for sc in scales:
            if sc != 1.0:
                msv_F2, msv_P2 = downsample([val_F2, val_P2], sc)
                msv_F2, msv_P2 = ToCudaVariable([msv_F2, msv_P2], volatile=True)
                r5, r4, r3, r2 = self.model.module.Encoder(msv_F2, msv_P2)
                e2 = self.model.module.Decoder(r5, ref[sc], r4, r3, r2)
                msv_E2[sc] = upsample(F.softmax(e2[0], dim=1)[:, 1].data.cpu(), (h, w))
            else:
                msv_F2, msv_P2 = ToCudaVariable([val_F2, val_P2], volatile=True)
                r5, r4, r3, r2 = self.model.module.Encoder(msv_F2, msv_P2)
                torch.cuda.empty_cache()
                e2 = self.model.module.Decoder(r5, ref[sc], r4, r3, r2)
                msv_E2[sc] = F.softmax(e2[0], dim=1)[:, 1].data.cpu()

        val_E2 = torch.zeros(val_P2.size())
        for sc in scales:
            val_E2 += msv_E2[sc]
        val_E2 /= len(scales)
        return val_E2

    def Infer_SO(self,all_F, all_M, num_frames, scales=[0.5, 0.75, 1.0]):
        all_E = torch.zeros(all_M.size())
        all_E[:, :, 0] = all_M[:, :, 0]

        ref = self.Encode_MS(all_F[:, :, 0], all_E[:, 0, 0], scales)
        for f in range(0, num_frames - 1):
            torch.cuda.empty_cache()
            all_E[:, 0, f + 1] = self.Propagate_MS(ref, all_F[:, :, f + 1], all_E[:, 0, f], scales)

        return all_E

    def Infer_MO(self,all_F, all_M, num_frames, num_objects, scales=[0.5, 0.75, 1.0]):
        if num_objects == 1:
            obj_E = self.Infer_SO(all_F, all_M, num_frames, scales=scales)  # 1,1,t,h,w
            return torch.cat([1 - obj_E, obj_E], dim=1)

        _, n, t, h, w = all_M.size()
        all_E = torch.zeros((1, n + 1, t, h, w))
        all_E[:, 1:, 0] = all_M[:, :, 0]
        all_E[:, 0, 0] = 1 - torch.sum(all_M[:, :, 0], dim=1)

        ref_bg = self.Encode_MS(all_F[:, :, 0], torch.sum(all_E[:, 1:, 0], dim=1), scales)
        refs = []
        for o in range(num_objects):
            refs.append(self.Encode_MS(all_F[:, :, 0], all_E[:, o + 1, 0], scales))

        for f in range(0, num_frames - 1):
            ### 1 - all
            all_E[:, 0, f + 1] = 1 - self.Propagate_MS(ref_bg, all_F[:, :, f + 1], torch.sum(all_E[:, 1:, f], dim=1), scales)
            for o in range(num_objects):
                all_E[:, o + 1, f + 1] = self.Propagate_MS(refs[o], all_F[:, :, f + 1], all_E[:, o + 1, f], scales)

            # Normalize by softmax
            all_E[:, :, f + 1] = torch.clamp(all_E[:, :, f + 1], 1e-7, 1 - 1e-7)
            all_E[:, :, f + 1] = torch.log((all_E[:, :, f + 1] / (1 - all_E[:, :, f + 1])))
            all_E[:, :, f + 1] = F.softmax(Variable(all_E[:, :, f + 1]), dim=1).data

        return all_E

    def Vosrgmp_work(self):
        self.MO=self.maskinfo['MO']
        self.annotation_path=self.maskinfo['annotation_path']
        self.ImageSets_path=self.maskinfo['ImageSets_path']
        self.frmas_path=self.maskinfo['frmas_path']
        self.mask_img=self.maskinfo['mask_img']
        self.imset=self.maskinfo['imset']
        self.result_dir=self.maskinfo['result_dir']
        self.model_dir=self.maskinfo['model_dir']
        QApplication.processEvents()
        if self.MO==True:
            #DAVIS参数：annotation_path, ImageSets_path,frmas_path, mask_anno,mask_img,imset='2016/val.txt', multi_object=False:
            Testset = DAVIS(self.annotation_path, self.ImageSets_path,self.frmas_path, self.mask_img,self.imset, multi_object=True)
            Testloader = data.DataLoader(Testset, batch_size=1, shuffle=False, num_workers=2, pin_memory=True)
            # num_workers:使用的子进程数,0为不使用多进程
            # pin_memory：是否把tensor数据复制到CUDA pinned memor中
            # drop_last：当数据集中的数据数量不能正处batch_size时，是否把最后的数据丢掉
        else:
            Testset = DAVIS(self.annotation_path, self.ImageSets_path,self.frmas_path, self.mask_img,self.imset, multi_object=False)
            Testloader = data.DataLoader(Testset, batch_size=1, shuffle=False, num_workers=2, pin_memory=True)

        self.model = nn.DataParallel(RGMP())
        if torch.cuda.is_available():
            self.model.cuda()

        self.model.load_state_dict(torch.load(os.path.join(self.model_dir,'weights.pth')))

        self.model.eval()  # turn-off BN
        for seq, (all_F, all_M, info) in enumerate(Testloader):
            all_F, all_M = all_F[0], all_M[0]
            seq_name = info['name'][0]
            num_frames = info['num_frames'][0]
            num_objects = info['num_objects'][0]

            tt = time.time()
            with torch.no_grad():
                all_E = self.Infer_MO(all_F, all_M, num_frames, num_objects, scales=[0.5, 0.75, 1.0])
            print('{} | num_objects: {}, FPS: {}'.format(seq_name, num_objects, num_frames / (time.time() - tt)))

            # Save results for quantitative eval ######################
            # if self.MO:
            #     folder = 'results/MO'
            # else:
            #     folder = 'results/SO'
            test_path = os.path.join(self.result_dir, seq_name)
            if not os.path.exists(test_path):
                os.makedirs(test_path)

            for f in range(num_frames):
                E = all_E[0, :, f].numpy()
                # make hard label
                E = ToLabel(E)

                (lh, uh), (lw, uw) = info['pad']
                E = E[lh[0]:-uh[0], lw[0]:-uw[0]]
                filename = os.path.join(test_path, '{:05d}.png'.format(f))
                E_copy = deepcopy(E)
                E_copy[E != 0] = 255
                print('E.shape:{}'.format(E.shape))
                # print(np.where(E_copy>=1))
                cv2.imwrite(filename, E_copy)

        self.finishVosRGMP_signal.emit(test_path)