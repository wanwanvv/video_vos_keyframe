import time
import cv2
import os
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication

class differenceExtract_thread(QObject):#执行交互式图像分割的ivs子线程类
    finishDifferenceExtract_signal = QtCore.pyqtSignal(str)

    def __init__(self,video_path,result_path):
        super(differenceExtract_thread,self).__init__()
        self.video_path=video_path
        self.result_path=result_path

    def initConstant(self):
        self.total_frames=[]
        ansl = [1, 94, 132, 154, 162, 177, 222, 236, 252, 268, 286, 310, 322, 255, 373, 401,
                423, 431, 444, 498, 546, 594, 627, 681, 759, 800, 832, 846, 932, 1235, 1369, 1438, 1529, 1581, 1847]
        ansr = [93, 131, 153, 161, 176, 221, 235, 251, 267, 285, 309, 321, 354, 372, 400,
                422, 430, 443, 497, 545, 593, 626, 680, 758, 799, 831, 845, 931, 1234, 1368, 1437,
                1528, 1580, 1846, 2139]  # 关键帧区间
        self.ansl = np.array(ansl)
        self.ansr = np.array(ansr)
        self.capture = cv2.VideoCapture(self.video_path)
        self.Frame_rate = self.capture.get(5)  # 一秒多少帧
        self.Frame_number = self.capture.get(7)  # 帧数
        self.Frame_time = 1000 / self.Frame_rate;  # 一帧多少秒
        if int(self.Frame_number)>50:
            self.len_windows = 50
        else:
            self.len_windows = int(self.Frame_number)
        if int(self.Frame_number)>30:
            self.local_windows=30
        else:
            self.local_windows= int(self.Frame_number)
        print("self.Frame_number:{}".format(self.Frame_number))
        print("self.Frame_time:{}".format(self.Frame_time))
        num = 0
        while True:
            ret, img = self.capture.read()
            if not ret:
                break
            self.total_frames.append(img)
            num += 1
        return num

    def smooth(self,swift_img, windows):
        r = swift_img.shape[1]
        c = swift_img.shape[2]
        for i in range(r):
            for j in range(c):
                L = swift_img[:, i, j]
                L = np.convolve(L, np.ones(windows), 'same')
                # 输入两个一维数组a:(N,)和b:(M,)，same－返回数组长度其中最大的max(M, N)，分别对应相乘移到对应的位置在想加
                # 卷积计算移动平均数
                swift_img[:, i, j] = L
        return swift_img

    def get_block(self,img):
        img = np.array(img)
        return img

    def dif(self,img1, img2):
        diff = img1 - img2
        diff = np.abs(np.array(diff))
        diff = diff.mean()
        return diff

    def get_img(self,now_time,get_number):#get_number=Frame_number
        swift_img=[]
        index=0
        time=now_time
        while(self.capture.isOpened()):
            self.capture.set(cv2.CAP_PROP_POS_MSEC,time)
            ret, img = self.capture.read()  # 获取图像
            if not ret:
                break
            img0 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换成灰度图
            img1 = self.get_block(img0)
            swift_img.append(img1)
            time+=self.Frame_time
            index+=1
            if index>=get_number:
                break
        swift_img = np.array(swift_img)
        print("swift_img.shape:{}".format(swift_img.shape))
        return swift_img

    def get_key_frame(self,swift_img,local_windows):
        L=[]
        L.append(0)
        for i in range(swift_img.shape[0]-1):
            temp = self.dif(swift_img[i], swift_img[i + 1])
            L.append(temp)
            if i==0:
                print("diff shape:{}".format(temp.shape))
        L = np.array(L)
        print("L shape:{}".format(L.shape))
        TL = []
        for i in range(L.shape[0]):
            l = i - local_windows // 2
            r = i + local_windows // 2
            l = max(l, 0)
            r = min(r, L.shape[0])
            if i == l + np.argmax(L[l:r]):
                TL.append(True)
            else:
                TL.append(False)
        TL = np.array(TL)
        print("TL:")
        print(TL)
        print("TL.shape:{}".format(TL.shape))
        return TL

    def preserve(self,L):
        num = 0
        time = 0
        for i in range(L.shape[0]):
            if L[i] == False:
                continue
            #self.capture.set(cv2.CAP_PROP_POS_MSEC, time)
            #ret, img = self.capture.read()  # 获取图像
            picname = '{:05d}.jpg'.format(i)
            cv2.imwrite(os.path.join(self.result_path, picname), self.total_frames[i])
            #cv2.imwrite('./1.1/{0:05d}.jpg'.format(num), img)  # 保存关键帧
            time += self.Frame_time
            num += 1
        print("num:{}".format(num))

    def cal_ans(self,cal_L,l,r):
        rate = []
        add = 0
        right = 0
        for j in range(self.ansl.shape[0]):
            num=0
            if not (l <= j and j <= r):
                continue
            ll = self.ansl[j]
            rr = self.ansr[j]
            for i in range(cal_L.shape[0]):
                if cal_L[i] == False:
                    continue
                if j == 0:
                    print(i)
                if i + self.ansl[l] >= ll and i + self.ansl[l] <= rr:
                    num += 1
            if num == 0:
                rate.append(0.0)
            else:
                right += 1
                if num == 1:
                    rate.append(6.0)
                    continue
                add += num - 1
                rate.append(6.0)
        rate = np.array(rate)
        ret = np.sum(rate) / rate.shape[0]
        print("多余的个数:")
        print(add)
        add = add / (5 * (r - l + 1))
        add = min(add, 1)
        print("多余的占比:")
        print(add)
        print("正确的评分:")
        print(right)
        ret += 4 * (1 - add) * right / (r - l + 1)  # 总共帧数中只有正确的部分才考虑时间因素。
        print("评分是:")
        print(ret)
        return ret

    def study(self):
        window = 1
        local = 2
        mmax = 0
        lindex = 4
        rindex = 10
        for i in range(3):
            tmp = 1 + i
            for j in range(3):
                Tmp = 2 + j
                print("当前参数: " + "卷积窗口" + str(tmp) + "最值窗口" + str(Tmp))
                tmp_img = self.get_img(self.ansl[lindex],self.ansr[rindex])
                tmp_img = self.smooth(tmp_img, tmp)
                tmp_L = self.get_key_frame(tmp_img, Tmp)
                ttmp = self.cal_ans(tmp_L, lindex, rindex)
                if ttmp > mmax:
                    window = tmp
                    local = Tmp
                    mmax = ttmp
                print("分割线--------------------")
        return window, local

    def difference_ExtractFrames_work(self):
        self.initConstant()
        QApplication.processEvents()
        #len_windows, local_windows = self.study()
        print("最终:")
        print("len_windows:{}".format(self.len_windows))
        print("local_windows:{}".format(self.local_windows))
        start=time.time()
        swift_img = self.get_img(0,self.Frame_number)
        swift_img = self.smooth(swift_img, self.len_windows)
        cal_L = self.get_key_frame(swift_img, self.local_windows)
        end=time.time()
        total_time=end-start
        print("total_time:{}".format(total_time))
        #self.cal_ans(cal_L, 0, self.ansl.shape[0] - 1)
        self.preserve(cal_L)
        self.capture.release()
        QApplication.processEvents()
        self.finishDifferenceExtract_signal.emit(self.result_path)