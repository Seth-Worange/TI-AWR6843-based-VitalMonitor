import sys
from numpy import *
from svm import *
from os import listdir
from plattSMO import PlattSMO   #作者写的，采用SMO进行优化，加入了核函数
import pickle   #用于列出目录中的文件
from tqdm import tqdm
import pandas as pd
import dill

class LibSVM:

    def __init__(self,data=[],label=[],C=0,toler=0,maxIter=0,**kernelargs):
        # data and label are the training data and their corresponding labels.
        # C, toler, and maxIter are hyperparameters for the SVM.
        # 'kernelargs' are additional arguments for the kernel function.
        # The 'dataSet' dictionary groups data points by their labels.
        self.classlabel = unique(label)  #该函数期望从label array中获得不重复的元素，label是不重复的标签集
        self.classNum = len(self.classlabel)
        self.classfyNum = (self.classNum * (self.classNum-1))/2 #This represents the number of binary classifiers needed in a one-vs-one (OvO) multi-class SVM approach
        self.classfy = []
        self.dataSet={}
        self.kernelargs = kernelargs
        self.C = C
        self.toler = toler
        self.maxIter = maxIter
        m = shape(data)[0]  #shape returns the dimensions of an array
        for i in range(m):   #this loop iterates迭代重复 over all data points
            if label[i] not in self.dataSet.keys():  #if label[i] is not already a key in the dictionary 'self.dataSet'
                self.dataSet[label[i]] = []  #initialize it with an empty list
                self.dataSet[label[i]].append(data[i][:])
            else:  #无论这个标签是否已经是个key还是刚添加，都把data[i]对应的标签加到self.dataSet的对应位置上去
                self.dataSet[label[i]].append(data[i][:])
        #If label = [0, 1, 0, 1] and data = [[1, 2], [3, 4], [5, 6], [7, 8]], after this loop:
        #self.dataSet would be {0: [[1, 2], [5, 6]], 1: [[3, 4], [7, 8]]}, grouping the data points by their labels.

    def train(self):
        num = self.classNum  #类别数
        #初始化进度条
        total_pairs = num * (num - 1) // 2  #计算总的分类器对数(//是除法后四舍五入为整数)
        progress_bar = tqdm(total=total_pairs, desc='Training SVM', ncols=80)
        for i in range(num):
            for j in range(i+1,num):  #creating pairs of classes，即每俩类别间弄一个分类器
                data = []
                label = [1.0]*shape(self.dataSet[self.classlabel[i]])[0]  #将第i类所有数据的标签设为1
                label.extend([-1.0]*shape(self.dataSet[self.classlabel[j]])[0])  #将第j类所有的数据标签设为-1
                data.extend(self.dataSet[self.classlabel[i]])  #将标签为1的数据放入data
                data.extend(self.dataSet[self.classlabel[j]])  #将标签为-1的数据放入data
                svm = PlattSMO(array(data),array(label),self.C,self.toler,self.maxIter,**self.kernelargs)
                svm.smoP()
                self.classfy.append(svm)
                progress_bar.update(1)  #update the bar
        progress_bar.close()  # 关闭进度条
        self.dataSet = None

    def predict_singlePic(self,data):
        m = shape(data)[0]
        num = self.classNum
        result = [0] * num
        index = -1
        for i in range(num):
            for j in range(i + 1, num):
                index += 1
                s = self.classfy[index]
                t = s.predict_singlePic0([data])[0]
                if t > 0.0:
                    result[i] +=1
                else:
                    result[j] +=1
        classlabel = result.index(max(result))
        return classlabel

    def predict(self,data,label):
        m = shape(data)[0]
        num = self.classNum
        classlabel = []
        count = 0.0
        for n in range(m):
            result = [0] * num
            index = -1
            for i in range(num):
                for j in range(i + 1, num):
                    index += 1
                    s = self.classfy[index]
                    t = s.predict([data[n]])[0]
                    if t > 0.0:
                        result[i] +=1
                    else:
                        result[j] +=1
            classlabel.append(result.index(max(result)))
            if classlabel[-1] != label[n]:
                count += 1
                print(label[n], classlabel[n])
        #print classlabel
        print("error rate:",count / m)
        return classlabel

    def save(self,filename):
        fw = open(filename,'wb')
        pickle.dump(self,fw,2)   # 使用 pickle 模块的 dump 函数，将 self（即当前类的实例）序列化并写入到前面打开的文件中; 2代表协议版本
        fw.close()

    @staticmethod
    def load(filename):
        # for loading a previously saved SVM model from a file
        fr = open(filename, 'rb')
        svm = pickle.load(fr)  # load the serialized SVM object from the file
        fr.close()
        return svm

# def loadImage(dir,maps = None):
#     #Loads image data and their labels from a directory.
#     # Assumes each file's name contains the label.
#     # Converts each pixel in the images to float and stores them in data.
#     dirList = listdir(dir)
#     data = []
#     label = []
#     for file in dirList:
#         label.append(file.split('_')[0])
#         lines = open(dir +'/'+file).readlines()
#         row = len(lines)
#         col = len(lines[0].strip())
#         line = []
#         for i in range(row):
#             for j in range(col):
#                 line.append(float(lines[i][j]))
#         data.append(line)
#         if maps != None:
#             label[-1] = float(maps[label[-1]])
#         else:
#             label[-1] = float(label[-1])
#     return data,label

def load_dataset(filename):
    """
    加载CSV格式的数据集。
    参数:filename: CSV文件的路径。
    返回:
        data: DataFrame，包含所有图片的特征（关键点坐标）。
        label: Series，包含对应图片的标签。
    """
    # 使用pandas读取CSV文件
    df = pd.read_csv(filename)

    # 假设CSV文件的前38列是特征（19个关节点的X和Y坐标）
    # 倒数第二列是标签
    data_df = df.iloc[:, :-1]
    label_df = df.iloc[:, -1]

    data = data_df.to_numpy()
    label = label_df.to_numpy()

    return data, label


def main():
    TrainingFile = 'D:\CodeWarehouse\openposeDEMO\Dataset_doll//train.csv'
    TestingFile='D:\CodeWarehouse\openposeDEMO\Dataset_doll//test.csv'
    data,label = load_dataset(TrainingFile)
    svm = LibSVM(data, label, 200, 0.0001, 10000, name='rbf', theta=20)
    svm.train()
    svm.save("svm_doll.txt")
    svm = LibSVM.load("svm_doll.txt")
    test,testlabel = load_dataset(TestingFile)
    svm.predict(test, testlabel)

if __name__ == "__main__":
    sys.exit(main())


