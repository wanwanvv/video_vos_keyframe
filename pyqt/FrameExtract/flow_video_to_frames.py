import cv2
import os
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
import numpy as np
import time

threshold=2.05

def writeImagePyramid(destPath,seqNumber, image):
    picname = '{:05d}.jpg'.format(seqNumber)
    fullPath = os.path.join(destPath, picname)
    #fullPath = os.path.join(destPath, "full", name + "-" + str(seqNumber) + ".png")
    cv2.imwrite(fullPath, image)
#
# Extract [numCols] domninant colors from an image
# Uses KMeans on the pixels and then returns the centriods
# of the colors
#
def extract_cols(image, numCols):
    # convert to np.float32 matrix that can be clustered
    Z = image.reshape((-1,3))
    Z = np.float32(Z)

    # Set parameters for the clustering
    max_iter = 20
    epsilon = 1.0
    K = numCols
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, max_iter, epsilon)
    labels = np.array([])
    # cluster
    compactness, labels, centers = cv2.kmeans(Z, K, labels, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    clusterCounts = []
    for idx in range(K):
        count = len(Z[labels == idx])
        clusterCounts.append(count)

    #Reverse the cols stored in centers because cols are stored in BGR
    #in opencv.
    rgbCenters = []
    for center in centers:
        bgr = center.tolist()
        bgr.reverse()
        rgbCenters.append(bgr)

    cols = []
    for i in range(K):
        iCol = {
            "count": clusterCounts[i],
            "col": rgbCenters[i]
        }
        cols.append(iCol)

    return cols

def scale(img, xScale, yScale):
    res = cv2.resize(img, None,fx=xScale, fy=yScale, interpolation = cv2.INTER_AREA)
    return res

def resize(img, width, heigth):
    res = cv2.resize(img, (width, heigth), interpolation = cv2.INTER_AREA)
    return res

class flowExtract_thread(QObject):#执行交互式图像分割的ivs子线程类
    finishFlowExtract_signal = QtCore.pyqtSignal(str)

    def __init__(self,video_path,result_path):
        super(flowExtract_thread,self).__init__()
        self.video_path=video_path
        self.result_path=result_path

    def calculateFrameStats(self,verbose=False, after_frame=0):# 提取相邻帧的差别
        cap = cv2.VideoCapture(self.video_path)  # 提取视频
        data = {
            "frame_info": []
        }
        lastFrame = []
        while (cap.isOpened()):
            ret, frame = cap.read()
            if not ret:
                break
            frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES) - 1
            #转化为灰度图,缩放并且模糊
            #使图片之间的差别对噪声更加鲁棒
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 提取灰度信息
            gray = scale(gray, 0.25, 0.25)  # 缩放为原来的四分之一
            gray = cv2.GaussianBlur(gray, (9, 9), 0.0)  # 做高斯模糊
            if frame_number < after_frame:
                lastFrame = gray
                continue
            if lastFrame!=[]:
                diff = cv2.subtract(gray, lastFrame)  # 用当前帧减去上一帧
                diffMag = cv2.countNonZero(diff)  # 计算两帧灰度值不同的像素点个数
                frame_info = {
                    "frame_number": int(frame_number),
                    "diff_count": int(diffMag)
                }
                data["frame_info"].append(frame_info)
                if verbose:
                    cv2.imshow('diff', diff)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            lastFrame = gray
        cap.release()
        cv2.destroyAllWindows()
        # compute some states
        diff_counts = [fi["diff_count"] for fi in data["frame_info"]]
        data["stats"] = {
            "num": len(diff_counts),
            "min": np.min(diff_counts),
            "max": np.max(diff_counts),
            "mean": np.mean(diff_counts),
            "median": np.median(diff_counts),
            "sd": np.std(diff_counts)  # 计算所有帧之间, 像素变化个数的标准差
        }
        greater_than_mean = [fi for fi in data["frame_info"] if fi["diff_count"] > data["stats"]["mean"]]
        greater_than_median = [fi for fi in data["frame_info"] if fi["diff_count"] > data["stats"]["median"]]
        greater_than_one_sd = [fi for fi in data["frame_info"] if
                               fi["diff_count"] > data["stats"]["sd"] + data["stats"]["mean"]]
        greater_than_two_sd = [fi for fi in data["frame_info"] if
                               fi["diff_count"] > (data["stats"]["sd"] * 2) + data["stats"]["mean"]]
        greater_than_three_sd = [fi for fi in data["frame_info"] if
                                 fi["diff_count"] > (data["stats"]["sd"] * 3) + data["stats"]["mean"]]

        # 统计其他信息
        data["stats"]["greater_than_mean"] = len(greater_than_mean)
        data["stats"]["greater_than_median"] = len(greater_than_median)
        data["stats"]["greater_than_one_sd"] = len(greater_than_one_sd)
        data["stats"]["greater_than_three_sd"] = len(greater_than_three_sd)
        data["stats"]["greater_than_two_sd"] = len(greater_than_two_sd)

        return data

    def detectScenes(self, data, verbose=False):
        cap = cv2.VideoCapture(self.video_path)
        diff_threshold = (data["stats"]["sd"] * threshold) + (data["stats"]["mean"])
        print('diff_threshold :{}'.format(diff_threshold ))
        num=0
        for index, fi in enumerate(data["frame_info"]):
            if fi["diff_count"] < diff_threshold:
                continue
            cap.set(cv2.CAP_PROP_POS_FRAMES, fi["frame_number"])
            ret, frame = cap.read()
            num+=1
            # extract dominant color
            #small = resize(frame, 100, 100)
            #cols = extract_cols(small, 5)
            #data["frame_info"][index]["dominant_cols"] = cols
            if ret:
                print('fi["frame_number"]:{}'.format(fi["frame_number"]))
                writeImagePyramid(self.result_path, fi["frame_number"], frame)
                #writeImagePyramid(destDir, name, fi["frame_number"], frame)
                if verbose:
                    cv2.imshow('extract', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        print("num:{}".format(num))
        if num==0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            writeImagePyramid(self.result_path, 0, frame)
        cap.release()
        cv2.destroyAllWindows()
        return data

    def flow_ExtractFrames_work(self):
        QApplication.processEvents()
        # Run the extraction
        start=time.time()
        data = self.calculateFrameStats(False, 0)
        data = self.detectScenes(data,False)
        end=time.time()
        total_time=end-start
        print("total_time:{}".format(total_time))
        #keyframeInfo = [frame_info for frame_info in data["frame_info"] if "dominant_cols" in frame_info]
        QApplication.processEvents()
        self.finishFlowExtract_signal.emit(self.result_path)