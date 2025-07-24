# 🐉 PSever_Bot_FlyFF – Private FlyFF Farming Bot

A GUI-based automation bot designed for **FlyFF Private Servers**, this Python script automates monster detection and interaction using template matching and simulates keystrokes/mouse actions to farm monsters efficiently.

---

## 🚀 Features

- 🎮 **Window Selection**: Choose from running game windows.
- 🧠 **Monster Detection**: Uses OpenCV for image-based monster recognition.
- 🖱️ **Auto Clicking**: Clicks detected monsters automatically.
- 🧭 **Smart Movement**: Simulates movement if no monster is found.
- 🔄 **Auto View Adjustment**: Adjusts the in-game camera if the view is obstructed.
- 💾 **Persistent Settings**: Save and load bot behavior via `settings.json`.
- 🛠️ **GUI Settings Panel**: Easily change bot behavior through an in-app config window.
- 📜 **Logs & Status Display**: Tracks actions and uptime via logs and status indicators.

---

## 🖼️ Screenshot

<img width="452" height="579" alt="Screenshot 2025-07-24 233713" src="https://github.com/user-attachments/assets/455c9985-40f2-4916-92e9-e54d419f14e0" />
<img width="379" height="312" alt="Screenshot 2025-07-24 233721" src="https://github.com/user-attachments/assets/ca8ebd91-f075-47a5-9e7f-084c2e21a5e4" />

---

## 🗂️ Folder Structure

project/<br>
├── assets/<br>
│ └── names/<br>
│ ├── monster1.png<br>
│ ├── monster2.png<br>
│ └── ...<br>
├── PSever_Bot_FlyFF.py<br>
├── settings.json<br>
└── README.md<br>

---

## ⚙️ Requirements

- Python 3.8+
- Windows OS (requires Win32 API)
- Python packages:
  - `opencv-python`
  - `numpy`
  - `pyautogui`
  - `pygetwindow`
  - `mss`
  - `keyboard`
  - `pillow`
  - `pywin32`

### ✅ Installation

1. Clone the repository or download the `.zip`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

(If requirements.txt doesn't exist, manually run:)

pip install opencv-python numpy pyautogui pygetwindow mss keyboard pillow pywin32

3. Add your monster name screenshots (.png) to assets/names/. File name (without .png) should match the monster name.

## 🕹️ How to Use
Launch the FlyFF private server and log in.

Run PSever_Bot_FlyFF.py.

In the GUI:

Select a monster from the list.

Select the game window.

Press Start.

To stop the bot, either:

Press Stop, or

Press Q on your keyboard.

## 🔧 Settings
Accessible via the Settings button. Configurable options:

Search Interval

Click Delay

Detection Threshold

Movement Duration

Movement Interval

All settings are saved in settings.json.

### 💡 Tips
Use clear, cropped .png images of monster names (nameplates) from FlyFF.

If detection fails, try adjusting the threshold setting.

Keep the game window visible and not minimized for best results.

## ❗ Troubleshooting
FileNotFoundError: 'assets/names'
→ Ensure the folder assets/names/ exists and contains valid .png monster nameplates.

No window detected
→ Click "Refresh Window List" to update available windows.

## 🧠 How It Works
The bot uses template matching (cv2.matchTemplate) to locate monsters by comparing captured screen regions to preloaded monster name images. Once detected, it clicks on the location and waits until the monster disappears from the scene before searching again. If nothing is found for a while, it simulates WASD or Space movements to refresh the view.

## 📄 License
This project is open-source and provided for educational use only. Use responsibly.

### 🧙‍♂️ Author
Ariel Salibay

