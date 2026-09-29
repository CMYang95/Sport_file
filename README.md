# Sport_file

Tennis Analysis & I-Taiwan Sport — 基於電腦視覺的運動分析專案，包含**網球揮拍訓練**、**雙鏡頭網球軌跡／物理參數推估（可串 Unity）**，以及**羽球時速檢測**。

---

## 專案簡介

本倉庫彙整多個與球類運動相關的即時視覺分析模組，主要技術包含：

- **OpenPose** 人體骨架偵測與關節角度分析
- **OpenCV** 影像處理、背景減除、HSV 球色過濾、透視變換
- **雙鏡頭（側視／俯視）** 推估球速、發射角度與 3D 起始位置
- **UDP Socket** 將結果傳送至 Unity 等模擬／互動端
- **Tkinter** 簡易互動介面（姿態訓練、時速顯示）

---

## 主要功能模組

### 1. 網球揮拍訓練（OpenPose）

| 檔案 | 說明 |
|------|------|
| `Main.py` | 主程式：手勢選單 → 選擇慣用手／正反手 → 預備姿勢偵測 → 揮拍軌跡引導與次數統計 |
| `Detector.py` | 圓形／矩形區域、曲線軌跡、角度條件偵測 |
| `Interactor.py` | 從骨架關鍵點取得雙手／膝蓋／手腕位置 |
| `DrawUI.py` | 畫面文字、偵測區、揮拍曲線繪製 |
| `constants.py` | 偵測參數（微蹲角度、目標次數、停留時間等） |
| `utils.py` | 角度、距離、裁切、觸發計時等工具函式 |

**流程概要：**

1. 將手上藍點移入偵測區，選擇左／右撇子
2. 選擇正手拍或反手拍
3. 手置於紅色預備區，並微蹲（可設定膝蓋角度條件）
4. 依畫面曲線揮拍至目標區，系統累計成功次數

相關變體／延伸：`ten_pose.py`、`ten_pose_new.py`、`tennis_pose_recognize.py`、`openpose_python.py`（姿態角度分析與 GUI）。

---

### 2. 網球即時追蹤與 Unity 串接

| 檔案 | 說明 |
|------|------|
| `Tennis_Real-time.py` | 雙 Webcam（側視＋俯視）、KNN 背景減除、HSV 找球、計算速度／角度／3D 座標，UDP 送至 Unity |
| `VirtualTennis_Real-time.py` | 虛擬網球即時分析變體 |
| `DetectTennis-unity-indoor.py` | 室內場地版本（影片／相機 + Unity） |
| `DetectTennis-unity-redclay.py` | 紅土場地版本 |
| `DetectTennis-kmeans-unity.py` | 使用 K-Means 的偵測變體 |
| `LoadWebcam.py` | Webcam 緩衝讀取 |

**輸出參數（範例）：** `[側視角度, 俯視角度, 速度(m/s), startX, startY, startZ]`  
預設透過 UDP 送往 `127.0.0.1:65520`（各腳本 port 可能不同）。

---

### 3. 羽球時速檢測

目錄：`BadmintonSpeedTest/`

| 檔案 | 說明 |
|------|------|
| `main_BufferCam.py` | 主流程：球偵測 → 場地對應 → 計算時速（km/h）並以大字體顯示 |
| `main_InitVer.py` | 初期版本 |
| `court_line_detector/` | 球場線／關鍵點偵測 |
| `mini_court/` | 迷你球場映射與真實尺度換算 |
| `LoadWebcam.py` | 相機讀取 |

可選用 AI 球場線模型，或手動標定四個場角座標。

---

## 目錄結構（精簡）

```text
Sport_file/
├── Main.py                      # 網球揮拍訓練主程式
├── Detector.py / DrawUI.py / Interactor.py / utils.py / constants.py
├── Tennis_Real-time.py           # 雙鏡頭網球物理推估
├── VirtualTennis_Real-time.py
├── DetectTennis-*.py             # Unity 串接／不同場地變體
├── ten_pose*.py / tennis_pose_recognize.py / openpose_python.py
├── LoadWebcam.py
└── BadmintonSpeedTest/           # 羽球時速檢測
    ├── main_BufferCam.py
    ├── court_line_detector/
    └── mini_court/
