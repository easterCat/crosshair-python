#!/usr/bin/env python3
"""
PyQt6 FPS Crosshair Tool
200 presets + Windows专用
"""

import sys
import json
from typing import Dict, List, Tuple
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QColorDialog, QSlider, 
                            QLabel, QComboBox, QGroupBox, QGridLayout, QSpinBox,
                            QCheckBox, QSystemTrayIcon, QMenu, QStyle, QFrame)
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal, QThread
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QIcon, QKeySequence, QShortcut
import win32api
import win32con
import win32gui
import ctypes
from ctypes import wintypes
import keyboard
import threading
import time
import math

# 备份当前文件内容
