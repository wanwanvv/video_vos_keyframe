from __future__ import division
import torch
from torch.utils import data

import torch.nn as nn
# from davisinteractive.utils.visualization import overlay_mask
# general libs
import cv2
import numpy as np
import tqdm
import os
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication

root_folder17 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder17=os.path.dirname(root_folder17 )
sys.path.append(parent_folder17)
sys.path.append(os.path.join(parent_folder17,'Removal'))

from Removal_dataset import DAVIS_Test
from CPNet_model import  CPNet

class InpaintingCPNet_thread(QObject):#执行交互式图像分割的ivs子线程类
    finishInpainting_signal = QtCore.pyqtSignal(str)

    def __init__(self,maskInfo_tmp):
        super(InpaintingCPNet_thread,self).__init__()
        self.maskInfo = maskInfo_tmp

    def InpaintingCPNet_work(self):
        #所需参数变量
        model_folder= self.maskInfo['model_folder']
        annotation_path=self.maskInfo['annotation_path']
        frames_path=self.maskInfo['frames_path']
        result_dir=self.maskInfo['result_dir']
        ImageSets_path=self.maskInfo['ImageSets_path']
        imset=self.maskInfo['imset']
        video_dir =self.maskInfo['video_dir']
        frameWidth=self.maskInfo['width']
        frameHeight=self.maskInfo['height']
        if torch.cuda.is_available():
            print('using Cuda devices, num:', torch.cuda.device_count())
        print(torch.backends.cudnn.version())
        print(torch.version.cuda)
        model = nn.DataParallel(CPNet())
        if torch.cuda.is_available():
            model.cuda()
        Pset = DAVIS_Test(annotation_path,frames_path,ImageSets_path, imset, size='half')
        Trainloader = data.DataLoader(Pset, batch_size=1, shuffle=False, num_workers=2, drop_last=True)
        QApplication.processEvents()
        model.load_state_dict(torch.load(os.path.join(model_folder,'weight.pth')))
        model.eval()  # turn-off BN
        num_length = 120
        for i, V in tqdm.tqdm(enumerate(Trainloader)):
            frames, masks, GTs, info = V  # b,3,t,h,w / b,1,t,h,w

            seq_name = info['name'][0]
            num_frames = frames.size()[2]
            print(seq_name, frames.size())

            with torch.no_grad():
                rfeats = model(frames, masks)
            frames_ = frames.clone()
            masks_ = masks.clone()
            index = [f for f in reversed(range(num_frames))]

            for t in range(2):  # forward : 0, backward : 1
                if t == 1:
                    comp0 = frames.clone()
                    frames = frames_
                    masks = masks_
                    index.reverse()

                for f in index:
                    ridx = []

                    start = f - num_length
                    end = f + num_length

                    if f - num_length < 0:
                        end = (f + num_length) - (f - num_length)
                        if end > num_frames:
                            end = num_frames - 1
                        start = 0

                    elif f + num_length > num_frames:
                        start = (f - num_length) - (f + num_length - num_frames)
                        if start < 0:
                            start = 0
                        end = num_frames - 1

                    # interval: 2
                    for i in range(start, end, 2):
                        if i != f:
                            ridx.append(i)

                    with torch.no_grad():
                        comp = model(rfeats[:, :, ridx], frames[:, :, ridx], masks[:, :, ridx], frames[:, :, f],
                                     masks[:, :, f], GTs[:, :, f])

                        c_s = comp.shape
                        Fs = torch.empty((c_s[0], c_s[1], 1, c_s[2], c_s[3])).float().cuda()
                        Hs = torch.zeros((c_s[0], 1, 1, c_s[2], c_s[3])).float().cuda()
                        Fs[:, :, 0] = comp.detach()
                        frames[:, :, f] = Fs[:, :, 0]
                        masks[:, :, f] = Hs[:, :, 0]
                        rfeats[:, :, f] = model(Fs, Hs)[:, :, 0]

                    save_path = result_dir
                    if t == 1:
                        if not os.path.exists(save_path):
                            os.makedirs(save_path)
                        est = comp0[:, :, f] * (len(index) - f) / len(index) + comp.detach().cpu() * f / len(index)

                        canvas = (est[0].permute(1, 2, 0).numpy() * 255.).astype(np.uint8)

                        if canvas.shape[1] % 2 != 0:
                            canvas = np.pad(canvas, [[0, 0], [0, 1], [0, 0]], mode='constant')

                        canvas_copy=canvas[...,::-1]
                        pic_name=os.path.join(save_path, '{:05d}.jpg'.format(f))
                        cv2.imwrite(pic_name,canvas_copy)
                        # canvas = Image.fromarray(canvas)
                        # canvas.save(os.path.join(save_path, '{:05d}.jpg'.format(f)))

        vid_path = os.path.join(video_dir, '{}_remove.mp4'.format(seq_name))
        frame_path = os.path.join(save_path, 'f%d.jpg')
        #os.system('ffmpeg -framerate 10 -i {} {}  -nostats -loglevel 0 -y'.format(frame_path, vid_path))
        print('----------------------------------------------------------')

        QApplication.processEvents()
        self.finishInpainting_signal.emit(result_dir)
