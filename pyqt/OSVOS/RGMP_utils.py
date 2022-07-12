from __future__ import division
import torch
from torch.autograd import Variable
from torch.utils import data

# general libs
import cv2
# import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import os
import glob

def ToLabel(E):
    fgs = np.argmax(E, axis=0).astype(np.float32)
    return fgs.astype(np.uint8)


def ToCudaVariable(xs, volatile=False):
    if torch.cuda.is_available():
        return [Variable(x.cuda(), volatile=volatile) for x in xs]
    else:
        return [Variable(x, volatile=volatile) for x in xs]


def upsample(x, size):
    x = x.numpy()[0]
    dsize = (size[1], size[0])
    x = cv2.resize(x, dsize=dsize, interpolation=cv2.INTER_LINEAR)
    return torch.unsqueeze(torch.from_numpy(x), dim=0)


def downsample(xs, scale):
    if scale == 1:
        return xs

    # find new size dividable by 32
    h = xs[0].size()[2]
    w = xs[0].size()[3]

    new_h = int(h * scale)
    new_w = int(w * scale)
    new_h = new_h + 32 - new_h % 32
    new_w = new_w + 32 - new_w % 32

    dsize = (new_w, new_h)
    ys = []
    for x in xs:
        x = x.numpy()[0]  # c,h,w
        if x.ndim == 3:
            x = np.transpose(x, [1, 2, 0])
            x = cv2.resize(x, dsize=dsize, interpolation=cv2.INTER_LINEAR)
            x = np.transpose(x, [2, 0, 1])
        else:
            x = cv2.resize(x, dsize=dsize, interpolation=cv2.INTER_LINEAR)

        ys.append(torch.unsqueeze(torch.from_numpy(x), dim=0))

    return ys


class DAVIS(data.Dataset):  # data.Dataset为抽象类,所有数据集子集应继承这个类,overrride:__len__和__getitem__
    '''
    Dataset for DAVIS
    '''

    def __init__(self, annotation_path, ImageSets_path,frmas_path, mask_img,imset='2016/val.txt', multi_object=False):
        self.mask_dir = annotation_path
        self.image_dir = frmas_path
        self.mask_img=mask_img
        _imset_dir = ImageSets_path
        _imset_f = os.path.join(_imset_dir, imset)
        if not os.listdir(self.mask_dir):
            self.mask_id = self.mask_img.split('.')[0].split('_')[0]
            self.mask_label = self.mask_img.split('.')[0].split('_')[1]

        self.videos = []
        self.num_frames = {}
        self.num_objects = {}
        self.shape = {}
        with open(os.path.join(_imset_f), "r") as lines:
            for line in lines:
                _video = line.rstrip('\n')
                self.videos.append(_video)
                self.num_frames[_video] = len(glob.glob(os.path.join(self.image_dir, '*.jpg')))
                _mask = np.array(Image.open(self.mask_img).convert("P"))
                self.num_objects[_video] = np.max(_mask)
                self.shape[_video] = np.shape(_mask)

        self.MO = multi_object

    def __len__(self):  # 表示样本数量
        return len(self.videos)

    def __getitem__(self, index):  # 每次使用其返回一条数据或一个样本,耗时的如加载图片等操作可以放在这里,多进程并行调用加速
        video = self.videos[index]
        info = {}
        info['name'] = video
        info['num_frames'] = self.num_frames[video]
        if self.MO:
            num_objects = self.num_objects[video]
        else:
            num_objects = 1
        info['num_objects'] = num_objects  # 单目标num_objects为1

        raw_frames = np.empty((self.num_frames[video],) + self.shape[video] + (3,), dtype=np.float32)
        raw_masks = np.empty((self.num_frames[video],) + self.shape[video], dtype=np.uint8)
        for f in range(self.num_frames[video]):
            img_file = os.path.join(self.image_dir, '{:05d}.jpg'.format(f))
            raw_frames[f] = np.array(Image.open(img_file).convert('RGB')) / 255.

            try:
                mask_file = os.path.join(self.mask_dir, '{:05d_*}.png'.format(f))  # allways return first frame mask
                mask_files=sorted(os.listdir(os.path.join(self.mask_dir)))
                if mask_files!=[]:
                    for mask_name in mask_files:
                        id = self.mask_img.split('.')[0].split('_')[0]
                        label = self.mask_img.split('.')[0].split('_')[1]
                        if id==self.mask_id and label==self.mask_label:
                            mask_file=os.path.join(self.mask_dir,mask_name)
                            break

                raw_mask = np.array(Image.open(mask_file).convert('P'), dtype=np.uint8)
                #print('mask_file:{}'.format(mask_file))
            except:
                print('except f:{}'.format(f))
                #mask_file = os.path.join(self.mask_dir, video, '31.png')
                raw_mask = np.array(Image.open(self.mask_img).convert('P'), dtype=np.uint8)

            if self.MO:
                raw_masks[f] = raw_mask
            else:
                raw_masks[f] = (raw_mask != 0).astype(np.uint8)  # 变成0,1矩阵

        # make One-hot channel is object index
        oh_masks = np.zeros((self.num_frames[video],) + self.shape[video] + (num_objects,), dtype=np.uint8)
        for o in range(num_objects):
            oh_masks[:, :, :, o] = (raw_masks == (o + 1)).astype(np.uint8)

        # padding size to be divide by 32
        nf, h, w, _ = oh_masks.shape
        new_h = h + 32 - h % 32
        new_w = w + 32 - w % 32
        print(new_h, new_w)
        lh, uh = (new_h - h) / 2, (new_h - h) / 2 + (new_h - h) % 2
        lw, uw = (new_w - w) / 2, (new_w - w) / 2 + (new_w - w) % 2
        lh, uh, lw, uw = int(lh), int(uh), int(lw), int(uw)
        print('lh:{}, uh:{}, lw:{}, uw:{}'.format(lh, uh, lw, uw))
        pad_masks = np.pad(oh_masks, ((0, 0), (lh, uh), (lw, uw), (0, 0)), mode='constant')
        pad_frames = np.pad(raw_frames, ((0, 0), (lh, uh), (lw, uw), (0, 0)), mode='constant')
        info['pad'] = ((lh, uh), (lw, uw))

        th_frames = torch.unsqueeze(torch.from_numpy(np.transpose(pad_frames, (3, 0, 1, 2)).copy()).float(), 0)
        th_masks = torch.unsqueeze(torch.from_numpy(np.transpose(pad_masks, (3, 0, 1, 2)).copy()).long(), 0)

        return th_frames, th_masks, info