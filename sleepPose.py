#该代码为实时睡眠姿势判断，仅用到摄像头，不含机械臂
#可实时展示人体框架，姿势判断在输出框内

import cv2
import time
import os
import sys
from sys import platform
import argparse
import numpy as np
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal

# 可能需要更改的参数 #
sys.path.append('D:/Desktop Files/Vital_Monitor/openpose/')  #添加路径
path = sys.path
model_path = "D:/Desktop Files/Vital_Monitor/openpose/svm.txt"

# 导入SVM分类库
from svm import *
from plattSMO import PlattSMO
from libSVM import LibSVM

# 引入Openpose库（是文件里的）
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
os.environ['PATH'] = os.environ['PATH'] + ';' + dir_path + '/bin;'
import pyopenpose as op
print(op)
print("成功引入pyopenpose")


class sleepPoseEst(QThread):
    pose_tag = pyqtSignal(int)
    def __init__(self, image):
        super().__init__()
        # setup keypoints frame
        self.columns = ['Xnose', 'Ynose',
                   'Xmidshoulder', 'Ymidshoulder',
                   'Xrshoulder', 'Yrshoulder',
                   'Xlshoulder', 'Ylshoulder',
                   'Xrelbow', 'Yelbow',
                   'Xlelbow', 'Ylelbow',
                   'Xrhand', 'Yrhand',
                   'Xlhand', 'Ylhand',
                   'Xmidhip', 'Ymidhip',
                   'Xrhip', 'Yrhip',
                   'Xlhip', 'Ylhip',
                   'Xrknee', 'Yrknee',
                   'Xlknee', 'Ylknee',
                   'Xrankle', 'Yrankle',
                   'Xlankle', 'Ylankle',
                   'Xreye', 'Yreye',
                   'Xleye', 'Yleye',
                   'Xrear', 'Yrear',
                   'Xlear', 'Ylear',
                   'pose']
        self.keypoints_df = pd.DataFrame(columns=self.columns)
        # 初始化openpose
        # Custom Params (refer to include/openpose/flags.hpp for more parameters)
        self.params = dict()
        self.params["model_folder"] = "D:/Desktop Files/Vital_Monitor/openpose/models"
        # 修改参数
        # 修改分辨率，可以降低对显存的占用 （16的倍数）
        self.params["net_resolution"] = "368x256"
        # Starting OpenPose
        self.opWrapper = op.WrapperPython()
        self.opWrapper.configure(self.params)
        self.opWrapper.start()
        self.pose = 0
        self.image = image
        self.svmModel = LibSVM.load(model_path)  # 引入训练好的SVM
        self.running = True

    def run(self):
        # try:
        #     while self.running:
        #         self.skeletonImage = self.poseEstimate()
        #         self.poseClassify()
        # except Exception as e:
        #     print(f"Error in PoseEstimateProcess: {e}")
        while self.running:
            self.skeletonImage = self.poseEstimate()
            self.poseClassify()
            # 发送pose识别结果
            self.pose_tag.emit(self.pose)

            time.sleep(5)


    def stop(self):
        self.running = False
        self.wait()

    def readImage(self, image):
        self.image = image

    # 睡姿估计
    def poseEstimate(self):
        # 检测图像大小  Height对应 X, Width对应 Y
        self.Xr, self.Yr, self.channels = self.image.shape
        # Process Image
        self.datum = op.Datum()
        self.datum.cvInputData = self.image
        self.opWrapper.emplaceAndPop(op.VectorDatum([self.datum]))
        skeletonImage = self.datum.cvOutputData
        return skeletonImage

    # 睡姿分类
    def poseClassify(self):
        # 如果识别到关键点，则判断睡姿
        # 数据预处理
        if self.datum.poseKeypoints is not None:
            # Write Keypoint
            self.keypoints_df = pd.DataFrame(self.keypoints_df).append({
                'Xnose': self.datum.poseKeypoints[0][0][0] / self.Xr,
                'Ynose': self.datum.poseKeypoints[0][0][1] / self.Yr,
                'Xmidshoulder': self.datum.poseKeypoints[0][1][0] / self.Xr,
                'Ymidshoulder': self.datum.poseKeypoints[0][1][1] / self.Yr,
                'Xrshoulder': self.datum.poseKeypoints[0][2][0] / self.Xr,
                'Yrshoulder': self.datum.poseKeypoints[0][2][1] / self.Yr,
                'Xlshoulder': self.datum.poseKeypoints[0][5][0] / self.Xr,
                'Ylshoulder': self.datum.poseKeypoints[0][5][1] / self.Yr,
                'Xrelbow': self.datum.poseKeypoints[0][3][0] / self.Xr,
                'Yelbow': self.datum.poseKeypoints[0][3][1] / self.Yr,
                'Xlelbow': self.datum.poseKeypoints[0][6][0] / self.Xr,
                'Ylelbow': self.datum.poseKeypoints[0][6][1] / self.Yr,
                'Xrhand': self.datum.poseKeypoints[0][4][0] / self.Xr,
                'Yrhand': self.datum.poseKeypoints[0][4][1] / self.Yr,
                'Xlhand': self.datum.poseKeypoints[0][7][0] / self.Xr,
                'Ylhand': self.datum.poseKeypoints[0][7][1] / self.Yr,
                'Xmidhip': self.datum.poseKeypoints[0][8][0] / self.Xr,
                'Ymidhip': self.datum.poseKeypoints[0][8][1] / self.Yr,
                'Xrhip': self.datum.poseKeypoints[0][9][0] / self.Xr,
                'Yrhip': self.datum.poseKeypoints[0][9][1] / self.Yr,
                'Xlhip': self.datum.poseKeypoints[0][12][0] / self.Xr,
                'Ylhip': self.datum.poseKeypoints[0][12][1] / self.Yr,
                'Xrknee': self.datum.poseKeypoints[0][10][0] / self.Xr,
                'Yrknee': self.datum.poseKeypoints[0][10][1] / self.Yr,
                'Xlknee': self.datum.poseKeypoints[0][13][0] / self.Xr,
                'Ylknee': self.datum.poseKeypoints[0][13][1] / self.Yr,
                'Xrankle': self.datum.poseKeypoints[0][11][0] / self.Xr,
                'Yrankle': self.datum.poseKeypoints[0][11][1] / self.Yr,
                'Xlankle': self.datum.poseKeypoints[0][14][0] / self.Xr,
                'Ylankle': self.datum.poseKeypoints[0][14][1] / self.Yr,
                'Xreye': self.datum.poseKeypoints[0][15][0] / self.Xr,
                'Yreye': self.datum.poseKeypoints[0][15][1] / self.Yr,
                'Xleye': self.datum.poseKeypoints[0][16][0] / self.Xr,
                'Yleye': self.datum.poseKeypoints[0][16][1] / self.Yr,
                'Xrear': self.datum.poseKeypoints[0][17][0] / self.Xr,
                'Yrear': self.datum.poseKeypoints[0][17][1] / self.Yr,
                'Xlear': self.datum.poseKeypoints[0][18][0] / self.Xr,
                'Ylear': self.datum.poseKeypoints[0][18][1] / self.Yr
            }, ignore_index=True)

        # SVM分类

        if not self.keypoints_df.empty:
            data_df = self.keypoints_df.iloc[-1, :-1]
            keypointsdata = data_df.to_numpy()
            self.pose = self.svmModel.predict_singlePic(keypointsdata)
            self.keypoints_df = self.keypoints_df.append({'pose': self.pose}, ignore_index=True)

            # 打印预测结果
            self.printpose(self.pose)

        else:
            print("DataFrame is empty.")
        # data_df = self.keypoints_df.iloc[-1, :-1]


    # 分类姿态输出
    # pose=1_up-0  2_down-0  3_left-0  4_left+45  5_left-45  6 _right-0  7_right+45  8_right-45
    def printpose(self, pose):
        if pose == 0:
            print("pose: up")
        elif pose == 1:
            print("pose: down")
        elif pose == 2:
            print("pose: right-0")
        elif pose == 3:
            print("pose: right+45")
        elif pose == 4:
            print("pose: right-45")
        elif pose == 5:
            print("pose: left-0")
        elif pose == 6:
            print("pose: left+45")
        elif pose == 7:
            print("pose: left-45")
