# -*- coding = utf-8 -*-
# @Time: 2024-07-23 0:20
# @Author: Orange Wang
# @File: cloudconnect.py
# @Software: PyCharm

import time
import hmac
import hashlib
import paho.mqtt.client as mqtt
from PyQt5.QtCore import QThread, pyqtSignal
import json
import sys
import os
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget


class MqttConnect(QThread):

    def __init__(self):
        super().__init__()
        # mqtt配置
        self.host = "2dbd455ad3.st1.iotda-device.cn-north-4.myhuaweicloud.com"
        self.port = 1883

        # 时间戳
        self.timestamp = time.strftime('%Y%m%d%H', time.localtime(time.time()))
        self.Timestamp = self.timestamp.encode('utf-8')
        self.eventTime = time.strftime('%Y%m%dT%H%M%S', time.localtime(time.time()))

        # 注册直连设备的时候返回的设备ID
        self.deviceId = "669e794b5830dc113ecdd3ca_device1"

        # 注册直连设备的时候返回的秘钥
        self.DeviceSecret = "12345678"
        self.deviceSecret = self.DeviceSecret.encode('utf-8')

        # path = os.path.dirname(__file__)
        # ca_certs = path + '/rootcert.pem'
        self.clientId = "".join((self.deviceId, "_0", "_0", "_", self.timestamp))
        self.username = '669e794b5830dc113ecdd3ca_device1'
        self.password = hmac.new(self.Timestamp, self.deviceSecret, digestmod=hashlib.sha256).hexdigest()

        # mqtt连接
        self.mqtt = mqtt.Client(self.clientId, clean_session=True)
        self.mqtt.username_pw_set(self.username, self.password)
        # self.mqtt.tls_set(self.ca_certs, cert_reqs=ssl.CERT_NONE)
        self.mqtt.connect(self.host, self.port, 60)
        self.mqtt.on_connect = self.on_connect
        self.running = True

    def run(self):
        while self.running:
            # self.publish_breathRate()
            # self.publish_heartRate()
            self.mqtt.loop_forever()

    def stop(self):
        self.running = False
        self.mqtt.disconnect()
        self.wait()

    def publish_breathRate(self, breathrate):
        pubTopic = "$oc/devices/" + self.deviceId + "/sys/properties/report"
        payload = {
            "services": [
                {
                    "serviceId": "awr6843",
                    "properties": {
                        "BreathRate": round(breathrate, 1)
                    },
                    "eventTime": self.eventTime
                }
            ]
        }
        message = json.dumps(payload)
        self.mqtt.publish(pubTopic, message, qos=1)

    def publish_heartRate(self, heartrate):
        pubTopic = "$oc/devices/" + self.deviceId + "/sys/properties/report"
        payload = {
            "services": [
                {
                    "serviceId": "awr6843",
                    "properties": {
                        "HeartRate": round(heartrate, 1)
                    },
                    "eventTime": self.eventTime
                }
            ]
        }
        message = json.dumps(payload)
        self.mqtt.publish(pubTopic, message, qos=1)

    def publish_osa(self, apnea):
        pubTopic = "$oc/devices/" + self.deviceId + "/sys/properties/report"
        payload = {
            "services": [
                {
                    "serviceId": "awr6843",
                    "properties": {
                        "OsaCount": apnea
                    },
                    "eventTime": self.eventTime
                }
            ]
        }
        message = json.dumps(payload)
        self.mqtt.publish(pubTopic, message, qos=1)

    def publish_pose(self, pose):
        # if pose == 0:
        #     str = "pose: up"
        # elif pose == 1:
        #     str = "pose: down"
        # elif pose == 2:
        #     str = "pose: right-0"
        # elif pose == 3:
        #     str = "pose: right+45"
        # elif pose == 4:
        #     str = "pose: right-45"
        # elif pose == 5:
        #     str = "pose: left-0"
        # elif pose == 6:
        #     str = "pose: left+45"
        # elif pose == 7:
        #     str = "pose: left-45"
        pubTopic = "$oc/devices/" + self.deviceId + "/sys/properties/report"
        payload = {
            "services": [
                {
                    "serviceId": "awr6843",
                    "properties": {
                        "Pose": pose
                    },
                    "eventTime": self.eventTime
                }
            ]
        }
        message = json.dumps(payload)
        self.mqtt.publish(pubTopic, message, qos=1)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT successfully!")

        else:
            print("Failed to connect, return code {0}".format(rc))


# class MainWindow(QtCore.QObject):
#     def __init__(self, parent=None):
#         super(MainWindow, self).__init__(parent)
#         self.work = MqttConnect()
#
#     def engage(self):
#         print("calling start")
#         self.work.start()
#
# if __name__ == "__main__":
#
#     app = QApplication(sys.argv)
#     main = MainWindow()
#     main.engage()
#     sys.exit(app.exec_())

