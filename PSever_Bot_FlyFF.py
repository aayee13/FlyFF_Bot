import sys
import tkinter as tk
from tkinter import ttk
import threading
import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
import mss
import time
import os, keyboard, json
import win32gui, win32api, win32con

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.json')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

SETTINGS_FILE = "settings.json"

monster_templates = {}
selected_monster = None
selected_hwnd = None
searching = False
threshold = 0.50
search_interval = 5.0
start_time = 0
click_delay = 0.10
movement_interval = 5.0
movement_duration = 0.3 # default duration in seconds
click_interval = 0.1

def load_settings():
    global search_interval, click_interval, movement_duration, threshold, movement_interval
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                search_interval = data.get("search_interval", 5.0)
                click_interval = data.get("click_interval", 0.1)
                movement_duration = data.get("movement_duration", 0.3)
                threshold = data.get("threshold", threshold)
                movement_interval = data.get("movement_interval", 5.0)
        except Exception as e:
            print("Failed to load settings:", e)

    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f, indent=4)

def save_settings_to_file():
    data = {
        "search_interval": search_interval,
        "click_interval": click_interval,
        "movement_duration": movement_duration,
        "threshold": threshold,
        "movement_interval": movement_interval
    }
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print("Failed to save settings:", e)

def load_monster_templates():
    global monster_templates
    monster_templates.clear()
    folder = 'assets/names'
    for filename in os.listdir(folder):
        if filename.endswith('.png'):
            name = os.path.splitext(filename)[0]
            path = os.path.join(folder, filename)
            image = cv2.imread(path)
            monster_templates[name] = image

def update_window_list():
    window_combo['values'] = [w.title for w in gw.getWindowsWithTitle('') if w.title.strip()]

def select_window():
    global selected_hwnd
    title = window_var.get()
    if not title:
        log_message("No window selected when trying to assign window.")
        return

    for w in gw.getWindowsWithTitle(title):
        if w.title == title:
            selected_hwnd = w._hWnd
            log_message(f"Selected window: {title}")
            return

    log_message(f"Window not found: {title}")


def detect_loop():
    global searching, start_time
    start_time = time.time()
    last_found_time = time.time()
    last_adjusted_time = 0

    while searching:
        if selected_monster and selected_hwnd:
            try:
                rect = win32gui.GetWindowRect(selected_hwnd)
                if not win32gui.IsWindowVisible(selected_hwnd):
                    time.sleep(1)
                    continue
                bbox = (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
            except:
                time.sleep(1)
                continue

            with mss.mss() as sct:
                monitor = {"top": bbox[1], "left": bbox[0], "width": bbox[2], "height": bbox[3]}
                sct_img = sct.grab(monitor)
                frame = np.array(sct_img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            template = monster_templates.get(selected_monster)
            if template is None:
                continue

            result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                h, w = template.shape[:2]
                center_x = bbox[0] + max_loc[0] + w // 2
                center_y = bbox[1] + max_loc[1] + h + 10

                pyautogui.moveTo(center_x, center_y, duration=0.05)
                log_message(f"Clicked on {selected_monster} at ({center_x}, {center_y})")
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(click_interval)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                status_var.set("Status: Attacking")

                # Wait until monster disappears or timeout
                wait_start = time.time()
                while True:
                    with mss.mss() as sct:
                        sct_img = sct.grab(monitor)
                        frame = np.array(sct_img)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
                    _, val, _, _ = cv2.minMaxLoc(result)

                    if val < threshold or time.time() - wait_start > 5:
                        break
                    time.sleep(0.2)

                last_found_time = time.time()  # update on success
            else:
                # No monster detected
                status_var.set("Status: Searching...")

                # Adjust view if enough time has passed without detection
                if time.time() - last_found_time > 3 and time.time() - last_adjusted_time > 5:
                    status_var.set("Adjusting View...")
                    pyautogui.moveTo(bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                    pyautogui.moveRel(100, 0, duration=0.90)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                    last_adjusted_time = time.time()

                # Movement simulation if idle too long
                if time.time() - last_found_time > movement_interval:
                    simulate_movement()
                    last_found_time = time.time()

        # Runtime clock
        elapsed = time.time() - start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        milliseconds = int((elapsed - int(elapsed)) * 1000)
        runtime_var.set(f"{hours:02}.{minutes:02}.{seconds:02}.{milliseconds:03}")

        time.sleep(search_interval)


def start_detection():
    global searching
    if not selected_monster:
        log_message("No monster selected.")
        return
    if not selected_hwnd:
        log_message("No windows selected.")
        return
    searching = True
    threading.Thread(target=detect_loop, daemon=True).start()
    keyboard.add_hotkey('q', stop_detection)
    status_var.set("Started (Press Q to stop)")
    status_var.set("Status: Started")
    log_message("Detection started.")

def stop_detection():
    global searching
    if not searching:
        log_message("Bot is already stopped.")
        return
    searching = False
    status_var.set("Status: Stopped")
    log_message("Detection stopped.")

def set_monster():
    global selected_monster
    selected_monster = monster_var.get()

def simulate_movement():
    directions = ['w', 'a', 's', 'd', 'space']
    key = np.random.choice(directions)
    keyboard.press(key)
    time.sleep(0.2)
    keyboard.release(key)
    log_message(f"No target found. Simulating movement: '{key}'")

def open_settings_window():
    global search_interval, click_interval, movement_duration, movement_interval

    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("380x280")
    settings_window.transient(root)
    settings_window.grab_set()
    settings_window.update_idletasks()
    settings_window.iconbitmap("assets/icons/settings.ico")

    # Center the window
    x = root.winfo_x() + (root.winfo_width() // 2) - (settings_window.winfo_width() // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (settings_window.winfo_height() // 2)
    settings_window.geometry(f"+{x}+{y}")

    # Create a centered frame inside the settings window
    form_frame = ttk.Frame(settings_window)
    form_frame.pack(pady=10)

    # Set uniform column weights for equal width
    form_frame.columnconfigure(0, weight=1, uniform="equal")
    form_frame.columnconfigure(1, weight=1, uniform="equal")

    # Helper to create one row
    def create_setting_row(parent, row, label_text, var):
        ttk.Label(parent, text=label_text, anchor="e").grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        entry = ttk.Entry(parent, textvariable=var, justify="center")
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        return entry

    # Create the variables
    search_interval_var = tk.StringVar(value=str(search_interval))
    click_interval_var = tk.StringVar(value=str(click_interval))
    movement_duration_var = tk.StringVar(value=str(movement_duration))
    threshold_var = tk.StringVar(value=str(threshold))
    movement_interval_var = tk.StringVar(value=str(movement_interval))

    # Create input rows
    create_setting_row(form_frame, 0, "Search Interval (s):", search_interval_var)
    create_setting_row(form_frame, 1, "Click Interval (s):", click_interval_var)
    create_setting_row(form_frame, 2, "Movement Press Duration (s):", movement_duration_var)
    create_setting_row(form_frame, 3, "Detection Threshold (0.0 - 1.0):", threshold_var)
    create_setting_row(form_frame, 4, "Movement Interval (s):", movement_interval_var)

    def save_settings():
        global search_interval, click_interval, movement_duration, movement_interval
        threshold_input = threshold_var.get()
        try:
            search_interval = float(search_interval_var.get())
            click_interval = float(click_interval_var.get())
            movement_duration = float(movement_duration_var.get())
            threshold_input = float(threshold_input)
            movement_interval = float(movement_interval_var.get())
            if 0.0 <= threshold_input <= 1.0:
                threshold = threshold_input
            else:
                raise ValueError("Threshold must be between 0.0 and 1.0")

            save_settings_to_file()
            log_message("Settings updated.")
            settings_window.destroy()
        except ValueError:
            log_message("Invalid settings input.")

    ttk.Button(settings_window, text="Save", command=save_settings, style="Custom.TButton").pack(pady=10)


def log_message(message):
    log_text.configure(state="normal")
    log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} | {message}\n")
    log_text.configure(state="disabled")
    log_text.yview(tk.END)  # Auto scroll


# GUI
load_settings()
root = tk.Tk()
root.title("Private FlyFF Farm Bot")
root.iconbitmap("assets/icons/FlyFF_Icon.ico")
root.geometry("450x550")

style = ttk.Style()
style.theme_use("clam")

#Style for Button
style.configure(
    "Custom.TButton",
    font=("Arial", 12, "bold"),
    foreground ="white",
    background="#4CAF50",
    padding=10,
    relief="raised"
)
style.map(
    "Custom.TButton",
    background=[("active", "#90EE90"),("disabled","#cccccc")]
)

#Style for Label
style = ttk.Style()
style.configure("Custom.TLabel",
                font=("Arial", 12, "bold"),
                foreground="white",
                background="#333333",
                padding=5)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Select Monster:").grid(row=0, column=0, padx=10, sticky="w")
monster_var = tk.StringVar()
monster_combo = ttk.Combobox(frame, textvariable=monster_var, state="readonly")
monster_combo.grid(row=0, column=1, padx=10, sticky="e")
monster_combo.bind("<<ComboboxSelected>>", lambda e: set_monster())

window_frame = tk.Frame(root)
window_frame.pack(pady=5)

ttk.Label(window_frame, text="Select Window:").grid(row=0, column=0, padx=10)
window_var = tk.StringVar()
window_combo = ttk.Combobox(window_frame, textvariable=window_var, state="readonly")
window_combo.grid(row=0, column=1, padx=10)

ttk.Button(root, text="Refresh Window List", command=update_window_list, style="Custom.TButton").pack(pady=5)
ttk.Button(root, text="Select Window", command=select_window, style="Custom.TButton").pack(pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

ttk.Button(button_frame, text="Start", command=start_detection, style="Custom.TButton").pack(side="left", padx=10)
ttk.Button(button_frame, text="Stop", command=stop_detection, style="Custom.TButton").pack(side="left", padx=10)

status_var = tk.StringVar(value="Status: Idle")
ttk.Label(root, textvariable=status_var, style="Custom.TLabel").pack(pady=5)

runtime_var = tk.StringVar(value="Run Time: 0.0s")
ttk.Label(root, textvariable=runtime_var, style="Custom.TLabel").pack(pady=5)

ttk.Button(root, text="Settings", command=open_settings_window, style="Custom.TButton").pack(pady=5)

# Logs Label
ttk.Label(root, text="Logs:").pack(pady=2)

# Log Box
log_text = tk.Text(root, height=10, width=48, state="disabled", bg="black", fg="lime", font=("Consolas", 9))
log_text.pack(padx=10, pady=5)


# Initialize
load_monster_templates()
monster_combo['values'] = list(monster_templates.keys())
update_window_list()

root.mainloop()
