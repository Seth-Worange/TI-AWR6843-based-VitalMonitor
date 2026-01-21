# -*- coding = utf-8 -*-
# @Time: 2024-07-21 12:11
# @Author: Orange Wang
# @File: VitalProcess.py
# @Software: PyCharm

from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import struct
from mmVS.com import serialConfig
import os

# 初始化
byteBuffer = np.zeros(2 ** 15, dtype='uint8')
byteBufferLength = 0
numRangeBinProcessed = 33 - 11 + 1


class DataProcessingThread(QThread):
    breath_wave_signal = pyqtSignal(float)
    heart_wave_signal = pyqtSignal(float)
    breath_rate_signal = pyqtSignal(float)
    heart_rate_signal = pyqtSignal(float)
    breath_energy_signal = pyqtSignal(float)
    motion_signal = pyqtSignal(float)

    def __init__(self, CLIport, Dataport):
        super().__init__()
        self.CLIport = CLIport
        self.Dataport = Dataport

        # 配置文件选择
        path = os.path.dirname(__file__)
        self.configFileName = path + '/profiles/xwr6843_profile_VitalSigns_20fps_Front.cfg'
        # 信号空间初始化
        self.Breathsignal = [0] * 250
        self.Heartbeatsignal = [0] * 250
        self.dataOk = 0
        self.vitalsign = {}
        self.frameNumber = 0

        self.running = True

    def run(self):
        try:
            # Configurate the serial port
            serialConfig(self.CLIport, self.configFileName)

            while self.running:  # 解析接收数据
                self.dataOk, self.frameNumber, self.vitalsign = self.readAndParseData68xx(self.Dataport)

                if self.dataOk:
                    self.breath_wave_signal.emit(self.vitalsign["outputFilterBreathOut"])
                    self.heart_wave_signal.emit(self.vitalsign["outputFilterHeartOut"])
                    self.heart_rate_signal.emit(self.vitalsign["heartRateEst_FFT"])
                    self.breath_rate_signal.emit(self.vitalsign["breathingRateEst_FFT"])
                    self.breath_energy_signal.emit(self.vitalsign["sumEnergyBreathWfm"])
                    self.motion_signal.emit(self.vitalsign["motionDetectedFlag"])

        except Exception as e:
            print(f"Error in VitalSignProcess: {e}")

    def stop(self):
        self.running = False
        self.wait()

    def readAndParseData68xx(self, Dataport):
        global byteBuffer, byteBufferLength, numRangeBinProcessed
        OBJ_STRUCT_SIZE_BYTES = 12
        BYTE_VEC_ACC_MAX_SIZE = 2 ** 15
        MMWDEMO_UART_MSG_DETECTED_POINTS = 1
        MMWDEMO_UART_MSG_RANGE_PROFILE = 2
        MMWDEMO_UART_MSG_VITALSIGN = 6
        maxBufferSize = 2 ** 15
        tlvHeaderLengthInBytes = 8
        pointLengthInBytes = 16
        magicWord = [2, 1, 4, 3, 6, 5, 8, 7]

        magicOK = 0
        dataOK = 0
        frameNumber = 0
        vitalsign = {}

        readBuffer = Dataport.read(Dataport.in_waiting)
        byteVec = np.frombuffer(readBuffer, dtype='uint8')
        byteCount = len(byteVec)

        if (byteBufferLength + byteCount) < maxBufferSize:
            byteBuffer[byteBufferLength:(byteBufferLength + byteCount)] = byteVec[0:byteCount]
            byteBufferLength = byteBufferLength + byteCount

        if byteBufferLength > 16:

            possibleLocs = np.where(byteBuffer == magicWord[0])[0]
            startIdx = []
            for loc in possibleLocs:
                check = byteBuffer[loc:loc + 8]
                if np.all(check == magicWord):
                    startIdx.append(loc)

            if startIdx:
                if 0 < startIdx[0] < byteBufferLength:
                    byteBuffer[:byteBufferLength - startIdx[0]] = byteBuffer[startIdx[0]:byteBufferLength]
                    byteBuffer[byteBufferLength - startIdx[0]:] = np.zeros(
                        len(byteBuffer[byteBufferLength - startIdx[0]:]),
                        dtype='uint8')
                    byteBufferLength = byteBufferLength - startIdx[0]

                if byteBufferLength < 0:
                    byteBufferLength = 0
                if byteBufferLength < 16:
                    return dataOK, None, None
                totalPacketLen = int.from_bytes(byteBuffer[12:12 + 4], byteorder='little')
                if (byteBufferLength >= totalPacketLen) and (byteBufferLength != 0):
                    magicOK = 1

        if magicOK:
            idX = 0
            magicNumber = byteBuffer[idX:idX + 8]
            idX += 8
            version = format(int.from_bytes(byteBuffer[idX:idX + 4], byteorder='little'), 'x')
            idX += 4
            totalPacketLen = int.from_bytes(byteBuffer[idX:idX + 4], byteorder='little')
            idX += 4
            platform = format(int.from_bytes(byteBuffer[idX:idX + 4], byteorder='little'), 'x')
            idX += 4
            frameNumber = int.from_bytes(byteBuffer[idX:idX + 4], byteorder='little')
            idX += 4
            timeCpuCycles = int.from_bytes(byteBuffer[idX:idX + 4], byteorder='little')
            idX += 4
            vitalsign["numDetectedObj"] = numDetectedObj = int.from_bytes(byteBuffer[idX:idX + 4], byteorder='little')
            idX += 4
            numTLVs = int.from_bytes(byteBuffer[idX:idX + 4], byteorder='little')
            idX += 4
            subFrameNumber = int.from_bytes(byteBuffer[idX:idX + 4], byteorder='little')
            idX += 4
            for tlvIdx in range(numTLVs):
                tlv_type = int.from_bytes(byteBuffer[idX:idX + 4], byteorder='little')
                idX += 4
                tlv_length = int.from_bytes(byteBuffer[idX:idX + 4], byteorder='little')
                idX += 4
                if tlv_type == MMWDEMO_UART_MSG_VITALSIGN:
                    vitalsign["rangeBinIndexMax"] = int.from_bytes(byteBuffer[idX:idX + 2], byteorder='little')
                    idX += 2
                    vitalsign["rangeBinIndexPhase"] = int.from_bytes(byteBuffer[idX:idX + 2], byteorder='little')
                    idX += 2
                    vitalsign["maxVal"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["processingCyclesOut"] = int.from_bytes(byteBuffer[idX:idX + 4], byteorder='little')
                    idX += 4
                    vitalsign["rangeBinStartIndex"] = int.from_bytes(byteBuffer[idX:idX + 2], byteorder='little')
                    idX += 2
                    vitalsign["rangeBinEndIndex"] = int.from_bytes(byteBuffer[idX:idX + 2], byteorder='little')
                    idX += 2
                    vitalsign["unwrapPhasePeak_mm"] = byteBuffer[idX:idX + 4].view(dtype=np.float32)[0]
                    idX += 4
                    vitalsign["outputFilterBreathOut"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["outputFilterHeartOut"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["heartRateEst_FFT"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["heartRateEst_FFT_4Hz"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0] / 2
                    idX += 4
                    vitalsign["heartRateEst_xCorr"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["heartRateEst_peakCount"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]  # zero always
                    idX += 4
                    vitalsign["breathingRateEst_FFT"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["breathingRateEst_xCorr"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["breathingRateEst_peakCount"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["confidenceMetricBreathOut"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["confidenceMetricBreathOut_xCorr"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["confidenceMetricHeartOut"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["confidenceMetricHeartOut_4Hz"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["confidenceMetricHeartOut_xCorr"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["sumEnergyBreathWfm"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["sumEnergyHeartWfm"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    vitalsign["motionDetectedFlag"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    idX += 4
                    idX += 40
                    vitalsign["RPlength"] = struct.unpack('<f', byteBuffer[idX:idX + 4])[0]
                    dataOK = 1

                if tlv_type == MMWDEMO_UART_MSG_RANGE_PROFILE:
                    if vitalsign.__contains__("rangeBinEndIndex"):
                        numRangeBinProcessed = vitalsign["rangeBinEndIndex"] - vitalsign["rangeBinStartIndex"] + 1
                    vitalsign["RangeProfile"] = []
                    for i in range(numRangeBinProcessed):
                        RPrealpart = int.from_bytes(byteBuffer[idX:idX + 2], byteorder='little')
                        idX += 2
                        RPimagelpart = int.from_bytes(byteBuffer[idX:idX + 2], byteorder='little')
                        idX += 2
                        vitalsign["RangeProfile"].append(
                            pow(RPrealpart * RPrealpart + RPimagelpart * RPimagelpart, 0.5))
            if 0 < idX < byteBufferLength:
                shiftSize = totalPacketLen

                byteBuffer[:byteBufferLength - shiftSize] = byteBuffer[shiftSize:byteBufferLength]
                byteBuffer[byteBufferLength - shiftSize:] = np.zeros(len(byteBuffer[byteBufferLength - shiftSize:]),
                                                                     dtype='uint8')
                byteBufferLength = byteBufferLength - shiftSize
                if byteBufferLength < 0:
                    byteBufferLength = 0

        return dataOK, frameNumber, vitalsign
