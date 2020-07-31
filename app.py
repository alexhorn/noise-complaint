import configparser
from monitor import Monitor
from PIL import Image
import pystray
import sounddevice as sd
import sys
import time

APP_NAME = "noise-complaint"
TRAY_ICON = "resources/birb.ico"
TRAY_MENU_EXIT = "Exit"

# parse config

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

microphone_device = config["microphone"].get("device", None)
headphone_device = config["headphone"].get("device", None)

samplerate = int(config["microphone"]["sample_rate"])
channels = int(config["microphone"]["channels"])

blocksize = int(samplerate * float(config["calculation"]["duration"]))
debounce = float(config["calculation"]["debounce"])
threshold = float(config["calculation"]["threshold"])

warning_file = config["warning"]["file"]

# set up

sd.default.device = (microphone_device, headphone_device)

monitor = Monitor(samplerate, channels, blocksize, debounce, threshold, warning_file)

# tray icon

def setup(icon):
    icon.visible = True

    monitor.start()

def teardown():
    monitor.stop()

    icon.visible = False
    icon.stop()

icon = pystray.Icon(APP_NAME, menu=pystray.Menu(
    pystray.MenuItem(TRAY_MENU_EXIT, teardown)
))
icon.title = APP_NAME
icon.icon = Image.open(TRAY_ICON)
icon.run(setup)
