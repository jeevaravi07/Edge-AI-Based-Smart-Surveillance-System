<div align="center">

# 🛡️ Edge AI-Based Smart Warehouse Surveillance System

**Real-Time Intrusion Detection & Event-Triggered Video Archiving on Edge Devices**

[![Python](https://img.shields.io/badge/Python-3.8%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8n-Ultralytics-00FFFF?style=for-the-badge&logo=yolo&logoColor=black)](https://ultralytics.com/)
[![Flask](https://img.shields.io/badge/Flask-Web%20Backend-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind%20CSS-3D%20Glassmorphism-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Raspberry Pi](https://img.shields.io/badge/Edge%20Hardware-Raspberry%20Pi%204-A22846?style=for-the-badge&logo=raspberry-pi&logoColor=white)](https://www.raspberrypi.com/)

<p align="center">
  An intelligent, offline-capable surveillance platform that transforms passive cameras into active edge sentinels. Powered by <b>YOLOv8n</b> and <b>Flask</b>, it detects humans and animals in real time, records 5-second event clips locally, and provides a 3D glassmorphic web dashboard for archive management.
</p>

</div>

---

## 📌 Project Metadata (For GitHub About Section)

* **Repository Title:** `edge-ai-warehouse-surveillance`
* **Project Full Title:** Edge AI-Based Smart Warehouse Surveillance and Event Recording System Using YOLOv8n
* **Short Description (250 chars):** An Edge AI smart warehouse surveillance system running YOLOv8n locally on Raspberry Pi 4. It detects humans and animals (dogs, cats, cows) in real time, records 5-second event clips offline, and manages video archives via a secure Flask dashboard.

---

## ✨ Key Features

* 🧠 **On-Device Edge AI Inference:** Runs `YOLOv8n` locally on CPU (optimized for Raspberry Pi 4 and standard desktop/laptop environments) with zero cloud dependency.
* 🎯 **Smart Target Filtering:** Strictly monitors and triggers on specific COCO classes—**Person (`0`)**, **Cat (`15`)**, **Dog (`16`)**, and **Cow (`19`)**—ignoring background clutter and false alarms.
* 🎬 **Event-Triggered Video Recording:** Saves disk space by discarding empty frames and automatically recording 5-second `.webm` (`VP80`) video clips only when an intrusion occurs.
* 🌐 **Native Browser Playback & Hover Zoom:** Encodes clips in browser-native WebM format with calibrated real-time FPS (`6 FPS`). Hover over any clip in the database to smoothly zoom and preview, or click to launch the full-screen modal player.
* 🔐 **Role-Protected Access Control:** Secures the `/cam` live stream and `/database` archive behind SQLite user authentication and `@login_required` session decorators.
* 🎨 **3D Glassmorphism Dark UI:** Built with Tailwind CSS and FontAwesome 6, featuring deep slate aesthetics, glowing cyan/emerald accents, and elevated 3D cards.

---

## 🏗️ System Architecture

```text
+-----------------------------------------------------------------------+
|                        1. SENSING LAYER                               |
|        Pi Camera Module (CSI) / USB Webcam  --->  OpenCV Capture      |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                      2. INTELLIGENCE LAYER                            |
|      YOLOv8n CPU Inference  --->  Class Filter [0, 15, 16, 19]        |
|                   (Person, Cat, Dog, Cow @ conf >= 0.5)               |
+-----------------------------------------------------------------------+
                                   |
            +----------------------+----------------------+
            | (Live MJPEG Stream)                         | (Target Detected)
            v                                             v
+-----------------------+                     +-------------------------+
|   3A. LIVE STREAMING  |                     |   3B. EVENT ARCHIVING   |
|  Flask /video_feed    |                     |  5s .webm Clip Writer   |
|  Real-time Bounding   |                     |  (VP80 @ 6 FPS) +       |
|  Boxes & Status UI    |                     |  SQLite Metadata Log    |
+-----------------------+                     +-------------------------+
```

---

## 🛠️ Tech Stack & Hardware Specifications

### Software Stack
| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **AI / Vision Model** | Ultralytics YOLOv8n (`yolov8n.pt`) | Real-time multi-target object detection |
| **Video Processing** | OpenCV (`cv2`) | Frame capture, annotation, & `VP80` `.webm` encoding |
| **Backend Framework** | Python Flask | Web server, MJPEG streaming, & REST routing |
| **Database** | SQLite3 (`surveillance.db`) | User credentials & recorded video metadata tracking |
| **Frontend UI** | HTML5, Jinja2, Tailwind CSS, JS | 3D Glassmorphic dark-mode responsive interface |

### Edge Hardware Target
* **Compute Unit:** Raspberry Pi 4 Model B (4GB/8GB RAM) or Windows/Linux PC
* **Camera Interface:** Pi Camera Module (CSI) or USB 2.0/3.0 Webcam
* **Storage:** 32GB+ Class 10 MicroSD Card / Local SSD
* **Alert Module (Optional):** Active GPIO Buzzer for immediate physical deterrence

---

## 📂 Project Directory Structure

```text
ware-house/
├── app.py                   # Main Flask application, YOLOv8 worker & routes
├── yolov8n.pt               # Pre-trained YOLOv8 Nano weights
├── surveillance.db          # Auto-generated SQLite database (Users & Videos)
├── recorded_events/         # Auto-generated folder storing .webm event clips
├── static/                  # Static assets directory
├── templates/               # Jinja2 HTML Templates (3D Glassmorphic UI)
│   ├── base.html            # Master layout, glass navbar & Tailwind config
│   ├── index.html           # Landing hero page & system capability cards
│   ├── auth.html            # Unified single-page Register & Login switcher
│   ├── cam_stream.html      # Protected live stream viewport & camera toggle
│   ├── database.html        # Protected video gallery with hover-zoom & modal
│   └── about.html           # System architecture & hardware documentation
└── README.md                # Project documentation
```

---

## 🚀 Getting Started & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/edge-ai-warehouse-surveillance.git
cd edge-ai-warehouse-surveillance
```

### 2. Install Dependencies
Make sure you have Python 3.8+ (or Python 3.11) installed, then install the required packages:
```bash
pip install flask opencv-python ultralytics
```

### 3. Run the Application
```bash
python app.py
# Or on Windows with Python 3.11 launcher:
py -3.11 app.py
```
*(On first launch, Ultralytics will automatically load or download `yolov8n.pt` and initialize `surveillance.db`.)*

### 4. Access the Web Dashboard
Open your browser and navigate to:
```text
http://localhost:8000
```

---

## 🖥️ Usage Workflow

1. **Create an Account:** Click **Register** on the navigation bar (`/register`). Fill in your name, email, and password. Upon submission, the interface automatically switches to the **Login** tab with your email pre-filled.
2. **Authenticate:** Log in to unlock the protected **Live Stream** and **Database** routes.
3. **Start Surveillance:** Navigate to **Live Stream** (`/cam`) and click **Start Camera**. The system initializes the webcam and begins real-time YOLOv8n inference.
4. **Automatic Event Recording:** Whenever a **Person, Dog, Cat, or Cow** enters the frame, a red `RECORDING EVENT...` indicator appears on the feed and a 5-second `.webm` clip is saved to `recorded_events/`.
5. **Review & Manage Clips:** Visit the **Database** page (`/database`):
   * **Hover** over any video card to smoothly zoom and preview the footage.
   * **Click** any video card to open the enlarged modal player with playback controls.
   * **Delete** unwanted clips from both disk storage and SQLite with a single click.

---

## 🔒 Security & Privacy Advantages

* **100% Offline Operation:** Continues detecting intrusions and recording evidence even during internet outages.
* **Zero Cloud Leakage:** Raw camera feeds never leave your local network or edge device.
* **Minimal Storage Footprint:** Only stores 5-second actionable intrusion events rather than 24/7 empty warehouse footage.

---

## 👤 Author

**Jeeva R**  
*Machine Learning Engineer & IoT Systems Developer*  
📍 Bengaluru, India

---

<div align="center">
  <i>Built with ❤️ using Python, YOLOv8, OpenCV, Flask, and Tailwind CSS.</i>
</div>