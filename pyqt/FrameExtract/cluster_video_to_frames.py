import cv2
import os
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
import multiprocessing
import numpy as np
import time

def video2frame(video_path,ratio):
    total_frames = []
    cap = cv2.VideoCapture(video_path)
    c = 1
    fps = cap.get(cv2.CAP_PROP_FPS) #获得fps
    if ratio == 0:
        gapfps = fps
    else:
        gapfps = fps * ratio
    if cap.isOpened() == False:
        print('Error opening video stream of file')
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == True:
            if c==1:
                total_frames.append(frame)
            elif ratio==0:
                total_frames.append(frame)
            elif ratio!=0:
                if c%(int(gapfps))==0:
                    total_frames.append(frame)
        else:
            break
            print('{} frame read failes!'.format(c))
        c+=1
    cap.release()
    return total_frames

def calc_hist(frame):
    h, w, _ = frame.shape
    temp = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([temp], [0, 1, 2], None, [12, 5, 5], [0, 256, 0, 256, 0, 256])
    hist = hist.flatten()
    hist /= h * w
    return hist

def similarity(a1,a2):
    temp = np.vstack((a1, a2))
    s = temp.min(axis=0) #第一个维度即每一列的最小值
    si = np.sum(s)
    return si

def ekf(total_frames):
    centers_d = {}
    result = []
    for i in range(len(total_frames)):
        temp = 0.0
        if len(centers_d) < 1:
            centers_d[i] = [total_frames[i], i]
        else:
            centers = list(centers_d.keys())
            cen_len = len(centers)
            if cen_len <= 10:
                last_centers = centers
            else:
                last_centers = centers[cen_len - 10:]
            for index, each in enumerate(last_centers):
                ind = -1
                t_si = similarity(total_frames[i], centers_d[each][0])
                # print(t_si)
                if t_si < 0.8:
                    continue
                elif t_si > temp:
                    temp = t_si
                    ind = index
                else:
                    continue
            if temp > 0.8 and ind != -1:
                centers_d[last_centers[ind]].append(i)
                length = len(centers_d[centers[ind]]) - 1
                c_old = centers_d[last_centers[ind]][0] * length
                c_new = (c_old + total_frames[i]) / (length + 1)
                centers_d[last_centers[ind]][0] = c_new
            else:
                centers_d[i] = [total_frames[i], i]
    cks = list(centers_d.keys())
    for index, each in enumerate(cks):
        if len(centers_d[each]) <= 6:
            result.extend(centers_d[each][1:])
        else:
            temp = []
            accordence = {}
            c = centers_d[each][0]
            for jindex, jeach in enumerate(centers_d[each][1:]):
                accordence[jindex] = jeach
                tempsi = similarity(c, total_frames[jeach])
                temp.append(tempsi)
            temp = np.array(temp)
            oktemp = np.argsort(-temp).tolist()
            for i in range(5):
                oktemp[i] = accordence[oktemp[i]]
            result.extend(oktemp[:5])
    return centers_d, sorted(result)

def cluster_video_to_frames(video_path,result_path):
    pool = multiprocessing.Pool(processes=5)
    total_frames = video2frame(video_path, 0)
    h, w, _ = total_frames[0].shape
    hist = pool.map(calc_hist, total_frames)
    start = time.time()
    cents, results = ekf(hist)
    end = time.time()
    ekftime = end - start
    print('cluster time :{}'.format(ekftime))
    # for i in results:
    #     picname = '{:05d}.jpg'.format(i)
    #     cv2.imwrite(os.path.join(result_path,picname), total_frames[i])
    print('clusters length:{}'.format(len(cents.keys())))
    for i in cents.keys():
        picname = '{:05d}.jpg'.format(i)
        cv2.imwrite(os.path.join(result_path,picname), total_frames[i])

class clusterExtract_thread(QObject):#执行交互式图像分割的ivs子线程类
    finishClusterExtract_signal = QtCore.pyqtSignal(str)

    def __init__(self,video_path,result_path):
        super(clusterExtract_thread,self).__init__()
        self.video_path=video_path
        self.result_path=result_path

    def cluster_ExtractFrames_work(self):
        QApplication.processEvents()
        cluster_video_to_frames(self.video_path, self.result_path)
        QApplication.processEvents()
        self.finishClusterExtract_signal.emit(self.result_path)