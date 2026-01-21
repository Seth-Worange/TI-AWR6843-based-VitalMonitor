# HoloSleep Monitor: Non-contact Sleep Monitoring System

<div align="center">
  
![Project Banner](./docs/images/banner.png)

**Multi-modal sleep monitoring system combining mmWave radar and computer vision**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)](https://opencv.org/)
[![TI Radar](https://img.shields.io/badge/Radar-TI_AWR6843-red.svg)](https://www.ti.com/product/AWR6843)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## 📖 Overview

HoloSleep Monitor is an innovative non-contact sleep monitoring system that integrates **mmWave radar vital signs detection** with **computer vision-based pose recognition**. The system utilizes Texas Instruments' AWR6843 radar for real-time breathing and heart rate monitoring, combined with camera and OpenPose for sleep posture classification, providing comprehensive sleep health analysis.

## ✨ Key Features

### 🔬 Multi-modal Sensing
- **mmWave Radar Monitoring**: Non-contact detection of respiration rate (8-20 BPM) and heart rate (60-100 BPM)
- **Visual Pose Recognition**: Real-time human pose estimation using OpenPose
- **Sleep Posture Classification**: SVM-based classifier for 7 common sleep positions

### 📊 Intelligent Analytics
- **Real-time Vital Signs Visualization**: Live waveforms for breathing and heart rate
- **Posture Duration Statistics**: Time analysis for each sleep position
- **Anomaly Detection**: Alert system for apnea and arrhythmia
- **Sleep Quality Assessment**: Comprehensive scoring based on multiple parameters

### 🎨 Unified Interface
- **Multi-view Display**: Simultaneous radar data, camera feed, and skeletal overlay
- **Real-time Dashboard**: Key metrics at a glance
- **Historical Review**: Playback and analysis of sleep sessions

## 🏗️ System Architecture

<div align="center">
<img src="./docs/images/system_architecture.png" width="800" alt="System Architecture">
</div>

## 🛠️ Technical Stack

### Hardware Requirements
- **Radar**: Texas Instruments AWR6843ISK-ODS
- **Camera**: USB webcam (1080p recommended) or IP camera
- **Processing Unit**: x86/ARM platform (tested on Jetson Nano, Raspberry Pi 4, PC)

### Software Dependencies
- **Radar Firmware**: TI Vital Signs Demo (vital_signs.bin)
- **Core Framework**: Python 3.8+
- **Computer Vision**: OpenCV 4.5+, OpenPose
- **Machine Learning**: Scikit-learn, NumPy, SciPy
- **Data Visualization**: Matplotlib, PyQt5
- **Communication**: PySerial

## 📦 Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/holosleep-monitor.git
cd holosleep-monitor
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install OpenPose
```bash
# For Ubuntu/Debian systems
git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose.git
cd openpose
sudo bash ./scripts/ubuntu/install_deps.sh
mkdir build && cd build
cmake .. -DBUILD_PYTHON=ON
make -j`nproc`
sudo make install
```

### 4. Flash Radar Firmware
1. Download and install [TI Uniflash](https://www.ti.com/tool/UNIFLASH)
2. Connect AWR6843 via USB
3. Flash `vital_signs.bin` to the board
4. Set baud rate to 921600

### 5. Configure System
```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your hardware settings
```

## 🚀 Quick Start

### Basic Usage
```bash
python main.py
```

### With Custom Configuration
```bash
python main.py --config my_config.yaml
```

### Calibration Mode (First-time setup)
```bash
python main.py --calibrate
```

## 📊 Performance Metrics

| Metric | Performance | Notes |
|--------|-------------|-------|
| Respiration Accuracy | >95% | Under stationary conditions |
| Heart Rate Accuracy | >90% | Compared to medical devices |
| Posture Recognition | >92% | 7 common sleep positions |
| System Latency | <200ms | End-to-end processing |
| Data Update Rate | 10 Hz | Fused radar + vision |

## 📈 Recognized Sleep Positions

The system classifies 7 common sleep positions:

| Position | Icon | Description | Health Impact |
|----------|------|-------------|---------------|
| Supine | 🛌 | Flat on back | May cause snoring |
| Supine Bent Legs | 🤰 | Back with bent knees | Reduces lower back stress |
| Left Lateral | 👈 | On left side | Recommended for digestion |
| Right Lateral | 👉 | On right side | Common position |
| Prone | 🐢 | On stomach | May cause neck strain |
| Fetal | 🧘 | Curled position | Common but may restrict breathing |
| Turning | 🔄 | Transition between positions | Normal during sleep |

## 🧪 Example Output

<div align="center">
<img src="./docs/images/demo_screenshot.png" width="900" alt="System Screenshot">
<p><em>Real-time monitoring interface showing radar data, camera feed, and analytics</em></p>
</div>

## 🔧 Configuration

Edit `config.yaml` to customize system behavior:

```yaml
system:
  mode: "monitor"           # monitor, playback, or calibrate
  data_logging: true
  alert_system: true

radar:
  port: "/dev/ttyUSB0"      # Linux
  # port: "COM3"            # Windows
  baudrate: 921600
  processing_window: 5      # seconds

camera:
  device_id: 0
  resolution: [1280, 720]
  fps: 30

openpose:
  model_directory: "./models"
  net_resolution: "368x368"
  render_threshold: 0.05

classification:
  model_path: "./models/pose_svm.pkl"
  confidence_threshold: 0.7
```

## 📁 Project Structure

```
holosleep-monitor/
├── main.py                 # Main application entry
├── requirements.txt        # Python dependencies
├── config.yaml            # Configuration file
├── LICENSE                # MIT License
│
├── core/                  # Core system modules
│   ├── monitor.py         # Main monitoring loop
│   ├── data_fusion.py     # Radar-vision data fusion
│   └── alert_manager.py   # Anomaly detection
│
├── radar/                 # Radar interface modules
│   ├── awr6843.py        # Radar communication
│   ├── parser.py         # Data packet parsing
│   └── processor.py      # Vital signs extraction
│
├── vision/                # Computer vision modules
│   ├── pose_detector.py  # OpenPose wrapper
│   ├── classifier.py     # SVM posture classifier
│   └── camera.py         # Camera management
│
├── gui/                   # User interface
│   ├── main_window.py    # Main application window
│   ├── radar_panel.py    # Radar data display
│   ├── camera_panel.py   # Camera feed display
│   └── analytics_panel.py# Data analytics display
│
├── models/               # Machine learning models
│   ├── pose_svm.pkl     # Trained SVM classifier
│   ├── label_encoder.pkl# Label encoder
│   └── train_model.py   # Model training script
│
├── utils/                # Utility functions
│   ├── helpers.py       # Helper functions
│   ├── constants.py     # System constants
│   └── logger.py        # Logging configuration
│
├── docs/                 # Documentation
│   ├── hardware_setup.md# Hardware connection guide
│   ├── calibration.md   # System calibration guide
│   └── api_reference.md # API documentation
│
└── tests/               # Test scripts
    ├── test_radar.py    # Radar module tests
    └── test_vision.py   # Vision module tests
```

## 🧠 Algorithm Details

### Radar Signal Processing
1. **Phase Extraction**: Extract chest wall movement from radar signals
2. **Signal Separation**: Separate breathing and heartbeat using bandpass filters
3. **Frequency Analysis**: Apply FFT to obtain respiration and heart rates

### Visual Pose Recognition Pipeline
1. **Keypoint Detection**: OpenPose extracts 18 body keypoints
2. **Feature Engineering**: Calculate angles and distances between keypoints
3. **Classification**: SVM classifies features into 7 sleep positions
4. **Temporal Smoothing**: Apply moving average for stability

## 🔬 Research Applications

This system enables various research applications:
- **Sleep disorder studies**: Apnea, insomnia, restless leg syndrome
- **Post-surgery monitoring**: Non-contact patient observation
- **Infant monitoring**: Safe, non-invasive baby monitoring
- **Elderly care**: Fall detection and sleep pattern analysis




## 🙏 Acknowledgments

- Texas Instruments for AWR6843 radar hardware and SDK
- CMU Perceptual Computing Lab for OpenPose
- All open-source libraries that made this project possible

---

<div align="center">
<sub>Built with ❤️ for better sleep health monitoring</sub>
</div>
