from __future__ import division
import torch
import torch.nn as nn

# general libs
import cv2
import numpy as np
import os,sys
from copy import copy, deepcopy
root_folder3 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder3 = os.path.dirname(root_folder3 )
sys.path.append(parent_folder3)
sys.path.append(os.path.join(parent_folder3,'ivs'))

# my libs
from ivs_utils import ToCudaVariable, ToCudaPN, Dilate_mask, load_UnDP, Get_weight, overlay_davis, overlay_checker,overlay_color, overlay_fade,load_frames
from interaction_net import Inet
from propagation_net import Pnet

# davis
from davisinteractive.utils.scribbles import scribbles2mask, annotated_frames

class vos_model():
    def __init__(self, frames_path,model_prefix):
        self.model_I = Inet()
        self.model_P = Pnet()
        self.model_dir_inet = os.path.join(model_prefix, 'I_e290.pth')
        self.model_dir_pnet = os.path.join(model_prefix, 'P_e290.pth')
        if torch.cuda.is_available():
            print('Using GPU')
            self.model_I = nn.DataParallel(self.model_I)  # 单服务器多GPU
            self.model_P = nn.DataParallel(self.model_P)
            self.model_I.cuda()  # 将模型复制到gpu,默认是cuda('0'),即跳转到第一个gpu
            self.model_P.cuda()
            # load_state_dict加载static_dict-字典对象,将每一层与它的对应参数建立映射关系,只有参数可以训练的layer才会被保存
            self.model_I.load_state_dict(torch.load(self.model_dir_inet))
            self.model_P.load_state_dict(torch.load(self.model_dir_pnet))
        else:
            print('Using CPU')
            self.model_I.load_state_dict(load_UnDP(self.model_dir_inet))
            self.model_P.load_state_dict(load_UnDP(self.model_dir_pnet))

        self.model_I.eval()  # turn-off BN
        self.model_P.eval()  # turn-off BN
        self.frames1 = load_frames(frames_path)
        self.frames = self.frames1.copy()
        self.num_frames, self.height, self.width = self.frames.shape[:3]
        print('num_frames:{} height:{} width:{}'.format(self.num_frames, self.height, self.width))
        self.init_variables(self.frames)


    def init_variables(self, frames):
        self.all_F = torch.unsqueeze(torch.from_numpy(np.transpose(frames, (3, 0, 1, 2))).float() / 255.,
                                     dim=0)  # 1,3,t,h,w torch.Size([1, 3, 10, 480, 854])
        self.all_E = torch.zeros(1, self.num_frames, self.height, self.width)  # 1,t,h,w torch.Size([1, 10, 480, 854])
        self.prev_E = torch.zeros(1, self.num_frames, self.height, self.width)  # 1,t,h,w torch.Size([1, 10, 480, 854])
        self.dummy_M = torch.zeros(1, self.height, self.width).long() #long类型 torch.Size([1, 480, 854])
        self.tar_P= torch.zeros(1, self.height, self.width).float()
        self.tar_N = torch.zeros(1, self.height, self.width).float()
        # to cuda
        self.all_F, self.all_E, self.prev_E, self.dummy_M,self.tar_P,self.tar_N = ToCudaVariable([self.all_F, self.all_E, self.prev_E, self.dummy_M,self.tar_P,self.tar_N], volatile=True)

        self.ref = None
        self.a_ref = None
        self.next_a_ref = None
        self.prev_targets = []


    def Prop_forward(self, target, end):
        for n in range(target + 1, end + 1):  # [1,2,...,N-1]

            print('[MODEL: propagation forward network] >>>>>>>>> {} to {}'.format(n - 1, n))
            self.all_E[:, n], _, self.next_a_ref = self.model_P(self.ref, self.a_ref, self.all_F[:, :, n],
                                                                self.prev_E[:, n], torch.round(self.all_E[:, n - 1]),
                                                                self.dummy_M, [1, 0, 0, 0, 0])

    def Prop_backward(self, target, end):
        for n in reversed(range(end, target)):  # [N-2,N-3,...,0]

            print('[MODEL: propagation backward  network] {} to {} <<<<<<<<<'.format(n + 1, n))
            self.all_E[:, n], _, self.next_a_ref = self.model_P(self.ref, self.a_ref, self.all_F[:, :, n],
                                                                self.prev_E[:, n], torch.round(self.all_E[:, n + 1]),
                                                                self.dummy_M, [1, 0, 0, 0, 0])

    def Run_propagation(self, target,mode='linear', at_least=-1, std=None):
        #self.all_E[:, target] = torch.from_numpy(mask.copy()).float()

        # when new round begins
        with torch.no_grad():
            torch.cuda.empty_cache()
            self.a_ref = self.next_a_ref
            self.prev_E = self.all_E

            if mode == 'naive':
                left_end, right_end, weight = 0, self.num_frames - 1, self.num_frames * [1.0]
            elif mode == 'linear':
                left_end, right_end, weight = Get_weight(target, self.prev_targets, self.num_frames, at_least=at_least)
                #left_end: 0 right_end:9 list weight.len:10
            else:
                raise NotImplementedError

            self.Prop_forward(target, right_end)
            self.Prop_backward(target, left_end)

            for f in range(self.num_frames):
                self.all_E[:, :, f] = weight[f] * self.all_E[:, :, f] + (1 - weight[f]) * self.prev_E[:, :, f]

            self.prev_targets.append(target)
            print('[MODEL] Propagation finished.')

    def Run_interaction(self, scribbles):
        target = scribbles['annotated_frame']
        print('height:{} width:{} target:{}'.format(self.height, self.width, target))
        scribble_mask = scribbles2mask(scribbles, (self.height, self.width))[target]  # 图片本来的宽高
        scribble_mask = Dilate_mask(scribble_mask, 1)

        self.tar_P, self.tar_N = ToCudaPN(scribble_mask)
        with torch.no_grad():
            self.all_E[:, target], _, self.ref = self.model_I(self.all_F[:, :, target], self.all_E[:, target],
                                                              self.tar_P,
                                                              self.tar_N, self.dummy_M,
                                                              [1, 0, 0, 0, 0])  # [batch, 256,512,2]

        print('[MODEL: interaction network] User Interaction on {}'.format(target))


    def Get_mask(self):
        return torch.round(self.all_E[0]).data.cpu().numpy().astype(np.uint8) #self.current_mask.shape:(10, 480, 854)

    def Get_mask_range(self, start, end):
        pred_masks = torch.round(self.all_E[0, start:end]).data.cpu().numpy().astype(np.uint8)  # t,h,w
        return torch.round(self.all_E[0, start:end]).data.cpu().numpy().astype(np.uint8)

    def Get_mask_index(self, index):
        return torch.round(self.all_E[0, index]).data.cpu().numpy().astype(np.uint8) #(480, 854)

    def get_vos_mask_pics(self,vos_mask_dir,vos_viz_dir):
        current_masks = self.Get_mask()
        for cursor in range(current_masks.shape[0]):
            current_mask=current_masks[cursor]
            pic_mask = os.path.join(vos_mask_dir, '{:05d}.png'.format(cursor))
            mask = deepcopy(current_mask)
            mask[current_mask != 0] = 255
            cv2.imwrite(pic_mask, mask)
            #合成图片
            pic_viz=os.path.join(vos_viz_dir,'{:05d}.png'.format(cursor))
            viz = overlay_fade(self.frames1[cursor], current_mask)
            cv2.imwrite(pic_viz,viz[..., ::-1])

    def get_result_pics(self,scribbles):
        tmp_dir = scribbles['annotate_frame_dir']
        print("生成标注图片:{}".format(tmp_dir))
        cursor = scribbles['annotated_frame']
        current_mask = self.Get_mask_index(cursor)

        viz = overlay_fade(self.frames1[cursor], current_mask)
        # 命名-四种图片[二值图,混合标注图,加了点的原图,加了点的混合标注图]
        pic_mask=os.path.join(tmp_dir,str(cursor)+'_mask.png')
        pic_viz=os.path.join(tmp_dir,str(cursor)+'_viz.png')
        pic_ol=os.path.join(tmp_dir,str(cursor)+'_ol.png')
        pic_mix=os.path.join(tmp_dir,str(cursor)+'_mix.png')
        pic_paths=[pic_mask]
        pic_paths.append(pic_viz)
        pic_paths.append(pic_ol)
        pic_paths.append(pic_mix)
        #保存mask二值图像

        mask=deepcopy(current_mask)
        mask[current_mask!=0]=255
        cv2.imwrite(pic_mask, mask)
        cv2.imwrite(pic_viz,viz[..., ::-1])
        # 绘制轨迹
        viz_mix = deepcopy(viz)
        ori_image= deepcopy(self.frames1[cursor])

        # ori_image = deepcopy(frames[cursor])[..., ::-1]
        for i in range(len(scribbles['scribbles'][cursor])):
            stroke = scribbles['scribbles'][cursor][i]  # 得到每个stroke
            pos_xy = stroke['line_path']  # 得到每个stroke的path
            print('pos_xy:{}'.format(pos_xy))
            if stroke['object_id'] == 1:
                line_color = (255, 0, 0)
            elif stroke['object_id'] == 0:
                line_color = (0, 255, 0)
            point_start = pos_xy[0]
            for pos_tmp in pos_xy:
                point_end = pos_tmp
                cv2.line(ori_image, (point_start[0], point_start[1]), (point_end[0], point_end[1]), line_color, 7)
                cv2.line(viz_mix, (point_start[0], point_start[1]), (point_end[0], point_end[1]), line_color, 7)
                point_start = point_end
        cv2.imwrite(pic_ol, ori_image[..., ::-1])
        cv2.imwrite(pic_mix, viz_mix[...,::-1])
        #return pic_paths
