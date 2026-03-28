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
                            QCheckBox, QSystemTrayIcon, QMenu, QStyle, QFrame,
                            QRadioButton)
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
import os

class ConfigManager:
    """配置管理器，负责保存和加载用户设置"""
    CONFIG_FILE = "config.json"
    
    @classmethod
    def load_config(cls) -> dict:
        """加载配置"""
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
        return {}

    @classmethod
    def save_config(cls, config: dict):
        """保存配置"""
        try:
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")

class HotkeyListener(QThread):
    """全局快捷键监听线程"""
    toggle_signal = pyqtSignal()
    next_signal = pyqtSignal()
    prev_signal = pyqtSignal()
    exit_signal = pyqtSignal()

    def run(self):
        """运行监听循环"""
        keyboard.add_hotkey('f6', self.toggle_signal.emit)
        keyboard.add_hotkey('f7', self.next_signal.emit)
        keyboard.add_hotkey('f8', self.prev_signal.emit)
        keyboard.add_hotkey('ctrl+q', self.exit_signal.emit)
        
        # keyboard 库内部有自己的监听机制，这里只需保持线程存活
        while True:
            time.sleep(1)

class ThemeManager:
    """主题管理器"""
    THEMES = {
        "minimal": {
            "name": "石墨极简",
            "main_window": {
                "background-color": "#121212",
                "color": "#FFFFFF",
                "font-family": "'Segoe UI', Arial, sans-serif",
                "font-size": "11px"
            },
            "groupbox": {
                "background-color": "#1E1E1E",
                "border": "1px solid #2A2A2A",
                "border-radius": "8px",
                "margin-top": "12px",
                "padding-top": "25px",
                "font-weight": "600",
                "color": "#FFFFFF",
                "box-shadow": "0 2px 8px rgba(0,0,0,0.5)",
                "min-height": "80px"
            },
            "groupbox_title": {
                "background-color": "#424242",
                "color": "#FFFFFF",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "12px"
            },
            "button": {
                "background-color": "#424242",
                "color": "#FFFFFF",
                "border": "none",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "11px",
                "padding": "8px 16px"
            },
            "button_hover": {
                "background-color": "#616161"
            },
            "slider": {
                "background-color": "#616161",
                "border-radius": "3px",
                "height": "6px"
            },
            "slider_handle": {
                "background-color": "#424242",
                "border": "2px solid #121212",
                "border-radius": "6px",
                "width": "12px",
                "height": "12px"
            },
            "preview": {
                "background-color": "#1E1E1E",
                "border": "1px solid #2A2A2A",
                "border-radius": "8px",
                "box-shadow": "0 2px 8px rgba(0,0,0,0.5)"
            },
            "combobox": {
                "background-color": "#1E1E1E",
                "border": "1px solid #2A2A2A",
                "border-radius": "4px",
                "padding": "6px 12px",
                "font-size": "11px",
                "color": "#FFFFFF",
                "font-weight": "600"
            },
            "label_title": {
                "font-size": "12px",
                "font-weight": "600",
                "color": "#FFFFFF",
                "margin-bottom": "8px",
                "min-height": "18px"
            },
            "label_value": {
                "font-size": "11px",
                "color": "#B0B0B0",
                "margin-top": "4px"
            }
        },
        "deep_ocean": {
            "name": "深海静谧",
            "main_window": {
                "background-color": "#1A202C",
                "color": "#FFFFFF",
                "font-family": "'Segoe UI', Arial, sans-serif",
                "font-size": "11px"
            },
            "groupbox": {
                "background-color": "#2D3748",
                "border": "1px solid #3A4556",
                "border-radius": "8px",
                "margin-top": "12px",
                "padding-top": "25px",
                "font-weight": "600",
                "color": "#E2E8F0",
                "box-shadow": "0 2px 8px rgba(0,0,0,0.3)",
                "min-height": "80px"
            },
            "groupbox_title": {
                "background-color": "#3182CE",
                "color": "#FFFFFF",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "12px"
            },
            "button": {
                "background-color": "#3182CE",
                "color": "#FFFFFF",
                "border": "none",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "11px",
                "padding": "8px 16px"
            },
            "button_hover": {
                "background-color": "#2970C6"
            },
            "slider": {
                "background-color": "#4A5568",
                "border-radius": "3px",
                "height": "6px"
            },
            "slider_handle": {
                "background-color": "#3182CE",
                "border": "2px solid #1A202C",
                "border-radius": "6px",
                "width": "12px",
                "height": "12px"
            },
            "preview": {
                "background-color": "#2D3748",
                "border": "1px solid #3A4556",
                "border-radius": "8px",
                "box-shadow": "0 2px 8px rgba(42,85,132,0.2)"
            },
            "combobox": {
                "background-color": "#2D3748",
                "border": "1px solid #3A4556",
                "border-radius": "4px",
                "padding": "6px 12px",
                "font-size": "11px",
                "color": "#E2E8F0",
                "font-weight": "600"
            },
            "label_title": {
                "font-size": "12px",
                "font-weight": "600",
                "color": "#E2E8F0",
                "margin-bottom": "8px",
                "min-height": "18px"
            },
            "label_value": {
                "font-size": "11px",
                "color": "#B0C4DE",
                "margin-top": "4px"
            }
        },
        "mint_lemon": {
            "name": "青柠薄荷",
            "main_window": {
                "background-color": "#F7FAFC",
                "color": "#2D3748",
                "font-family": "'Segoe UI', Arial, sans-serif",
                "font-size": "11px"
            },
            "groupbox": {
                "background-color": "#EDF2F7",
                "border": "1px solid #D1E7DD",
                "border-radius": "8px",
                "margin-top": "12px",
                "padding-top": "25px",
                "font-weight": "600",
                "color": "#2D3748",
                "box-shadow": "0 2px 8px rgba(0,0,0,0.1)",
                "min-height": "80px"
            },
            "groupbox_title": {
                "background-color": "#48BB78",
                "color": "#FFFFFF",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "12px"
            },
            "button": {
                "background-color": "#48BB78",
                "color": "#FFFFFF",
                "border": "none",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "11px",
                "padding": "8px 16px"
            },
            "button_hover": {
                "background-color": "#38A862"
            },
            "slider": {
                "background-color": "#9AE6B4",
                "border-radius": "3px",
                "height": "6px"
            },
            "slider_handle": {
                "background-color": "#48BB78",
                "border": "2px solid #F7FAFC",
                "border-radius": "6px",
                "width": "12px",
                "height": "12px"
            },
            "preview": {
                "background-color": "#EDF2F7",
                "border": "1px solid #D1E7DD",
                "border-radius": "8px",
                "box-shadow": "0 2px 8px rgba(154,230,180,0.2)"
            },
            "combobox": {
                "background-color": "#EDF2F7",
                "border": "1px solid #D1E7DD",
                "border-radius": "4px",
                "padding": "6px 12px",
                "font-size": "11px",
                "color": "#2D3748",
                "font-weight": "600"
            },
            "label_title": {
                "font-size": "12px",
                "font-weight": "600",
                "color": "#2D3748",
                "margin-bottom": "8px",
                "min-height": "18px"
            },
            "label_value": {
                "font-size": "11px",
                "color": "#38A169",
                "margin-top": "4px"
            }
        },
        "warm_gray": {
            "name": "暖灰办公",
            "main_window": {
                "background-color": "#F5F5F5",
                "color": "#2D3748",
                "font-family": "'Segoe UI', Arial, sans-serif",
                "font-size": "11px"
            },
            "groupbox": {
                "background-color": "#E0E0E0",
                "border": "1px solid #C5C5C5",
                "border-radius": "8px",
                "margin-top": "12px",
                "padding-top": "25px",
                "font-weight": "600",
                "color": "#2D3748",
                "box-shadow": "0 2px 8px rgba(0,0,0,0.1)",
                "min-height": "80px"
            },
            "groupbox_title": {
                "background-color": "#718096",
                "color": "#FFFFFF",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "12px"
            },
            "button": {
                "background-color": "#718096",
                "color": "#FFFFFF",
                "border": "none",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "11px",
                "padding": "8px 16px"
            },
            "button_hover": {
                "background-color": "#5A6B7B"
            },
            "slider": {
                "background-color": "#A0AEC0",
                "border-radius": "3px",
                "height": "6px"
            },
            "slider_handle": {
                "background-color": "#718096",
                "border": "2px solid #F5F5F5",
                "border-radius": "6px",
                "width": "12px",
                "height": "12px"
            },
            "preview": {
                "background-color": "#E0E0E0",
                "border": "1px solid #C5C5C5",
                "border-radius": "8px",
                "box-shadow": "0 2px 4px rgba(160,174,192,0.2)"
            },
            "combobox": {
                "background-color": "#E0E0E0",
                "border": "1px solid #C5C5C5",
                "border-radius": "4px",
                "padding": "6px 12px",
                "font-size": "11px",
                "color": "#2D3748",
                "font-weight": "600"
            },
            "label_title": {
                "font-size": "12px",
                "font-weight": "600",
                "color": "#2D3748",
                "margin-bottom": "8px",
                "min-height": "18px"
            },
            "label_value": {
                "font-size": "11px",
                "color": "#4A5568",
                "margin-top": "4px"
            }
        },
        "dark_purple": {
            "name": "暗夜紫雾",
            "main_window": {
                "background-color": "#1E1B2E",
                "color": "#E9D8FD",
                "font-family": "'Segoe UI', Arial, sans-serif",
                "font-size": "11px"
            },
            "groupbox": {
                "background-color": "#2D2A3E",
                "border": "1px solid #3A3848",
                "border-radius": "8px",
                "margin-top": "12px",
                "padding-top": "25px",
                "font-weight": "600",
                "color": "#E9D8FD",
                "box-shadow": "0 2px 8px rgba(128,90,213,0.2)",
                "min-height": "80px"
            },
            "groupbox_title": {
                "background-color": "#805AD5",
                "color": "#FFFFFF",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "12px"
            },
            "button": {
                "background-color": "#805AD5",
                "color": "#FFFFFF",
                "border": "none",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "11px",
                "padding": "8px 16px"
            },
            "button_hover": {
                "background-color": "#6B49C3"
            },
            "slider": {
                "background-color": "#9F7AEA",
                "border-radius": "3px",
                "height": "6px"
            },
            "slider_handle": {
                "background-color": "#805AD5",
                "border": "2px solid #1E1B2E",
                "border-radius": "6px",
                "width": "12px",
                "height": "12px"
            },
            "preview": {
                "background-color": "#2D2A3E",
                "border": "1px solid #3A3848",
                "border-radius": "8px",
                "box-shadow": "0 2px 8px rgba(128,90,213,0.2)"
            },
            "combobox": {
                "background-color": "#2D2A3E",
                "border": "1px solid #3A3848",
                "border-radius": "4px",
                "padding": "6px 12px",
                "font-size": "11px",
                "color": "#E9D8FD",
                "font-weight": "600"
            },
            "label_title": {
                "font-size": "12px",
                "font-weight": "600",
                "color": "#E9D8FD",
                "margin-bottom": "8px",
                "min-height": "18px"
            },
            "label_value": {
                "font-size": "11px",
                "color": "#D6BCFA",
                "margin-top": "4px"
            }
        },
        "sky_blue": {
            "name": "晴空淡蓝",
            "main_window": {
                "background-color": "#EBF8FF",
                "color": "#2C5282",
                "font-family": "'Segoe UI', Arial, sans-serif",
                "font-size": "11px"
            },
            "groupbox": {
                "background-color": "#BEE3F8",
                "border": "1px solid #A8D0E8",
                "border-radius": "8px",
                "margin-top": "12px",
                "padding-top": "25px",
                "font-weight": "600",
                "color": "#2C5282",
                "box-shadow": "0 2px 8px rgba(0,0,0,0.1)",
                "min-height": "80px"
            },
            "groupbox_title": {
                "background-color": "#3182CE",
                "color": "#FFFFFF",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "12px"
            },
            "button": {
                "background-color": "#3182CE",
                "color": "#FFFFFF",
                "border": "none",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "11px",
                "padding": "8px 16px"
            },
            "button_hover": {
                "background-color": "#2970C6"
            },
            "slider": {
                "background-color": "#63B3ED",
                "border-radius": "3px",
                "height": "6px"
            },
            "slider_handle": {
                "background-color": "#3182CE",
                "border": "2px solid #EBF8FF",
                "border-radius": "6px",
                "width": "12px",
                "height": "12px"
            },
            "preview": {
                "background-color": "#BEE3F8",
                "border": "1px solid #A8D0E8",
                "border-radius": "8px",
                "box-shadow": "0 2px 8px rgba(99,179,237,0.2)"
            },
            "combobox": {
                "background-color": "#BEE3F8",
                "border": "1px solid #A8D0E8",
                "border-radius": "4px",
                "padding": "6px 12px",
                "font-size": "11px",
                "color": "#2C5282",
                "font-weight": "600"
            },
            "label_title": {
                "font-size": "12px",
                "font-weight": "600",
                "color": "#2C5282",
                "margin-bottom": "8px",
                "min-height": "18px"
            },
            "label_value": {
                "font-size": "11px",
                "color": "#2B6CB0",
                "margin-top": "4px"
            }
        },
        "charcoal_silver": {
            "name": "炭黑银线",
            "main_window": {
                "background-color": "#1A1A1A",
                "color": "#F3F4F6",
                "font-family": "'Segoe UI', Arial, sans-serif",
                "font-size": "11px"
            },
            "groupbox": {
                "background-color": "#252525",
                "border": "1px solid #303030",
                "border-radius": "8px",
                "margin-top": "12px",
                "padding-top": "25px",
                "font-weight": "600",
                "color": "#F3F4F6",
                "box-shadow": "0 2px 8px rgba(0,0,0,0.5)",
                "min-height": "80px"
            },
            "groupbox_title": {
                "background-color": "#D1D5DB",
                "color": "#FFFFFF",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "12px"
            },
            "button": {
                "background-color": "#D1D5DB",
                "color": "#FFFFFF",
                "border": "none",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "11px",
                "padding": "8px 16px"
            },
            "button_hover": {
                "background-color": "#B8C1DB"
            },
            "slider": {
                "background-color": "#9CA3AF",
                "border-radius": "3px",
                "height": "6px"
            },
            "slider_handle": {
                "background-color": "#D1D5DB",
                "border": "2px solid #1A1A1A",
                "border-radius": "6px",
                "width": "12px",
                "height": "12px"
            },
            "preview": {
                "background-color": "#252525",
                "border": "1px solid #303030",
                "border-radius": "8px",
                "box-shadow": "0 2px 8px rgba(156,163,175,0.2)"
            },
            "combobox": {
                "background-color": "#252525",
                "border": "1px solid #303030",
                "border-radius": "4px",
                "padding": "6px 12px",
                "font-size": "11px",
                "color": "#F3F4F6",
                "font-weight": "600"
            },
            "label_title": {
                "font-size": "12px",
                "font-weight": "600",
                "color": "#F3F4F6",
                "margin-bottom": "8px",
                "min-height": "18px"
            },
            "label_value": {
                "font-size": "11px",
                "color": "#D1D5DB",
                "margin-top": "4px"
            }
        },
        "wheat_coffee": {
            "name": "燕麦奶咖",
            "main_window": {
                "background-color": "#FDF6E3",
                "color": "#5C4033",
                "font-family": "'Segoe UI', Arial, sans-serif",
                "font-size": "11px"
            },
            "groupbox": {
                "background-color": "#F4EAD5",
                "border": "1px solid #E8D5C0",
                "border-radius": "8px",
                "margin-top": "12px",
                "padding-top": "25px",
                "font-weight": "600",
                "color": "#5C4033",
                "box-shadow": "0 2px 8px rgba(210,180,140,0.2)",
                "min-height": "80px"
            },
            "groupbox_title": {
                "background-color": "#B08968",
                "color": "#FFFFFF",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "12px"
            },
            "button": {
                "background-color": "#B08968",
                "color": "#FFFFFF",
                "border": "none",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "11px",
                "padding": "8px 16px"
            },
            "button_hover": {
                "background-color": "#9B7659"
            },
            "slider": {
                "background-color": "#D2B48C",
                "border-radius": "3px",
                "height": "6px"
            },
            "slider_handle": {
                "background-color": "#B08968",
                "border": "2px solid #FDF6E3",
                "border-radius": "6px",
                "width": "12px",
                "height": "12px"
            },
            "preview": {
                "background-color": "#F4EAD5",
                "border": "1px solid #E8D5C0",
                "border-radius": "8px",
                "box-shadow": "0 2px 8px rgba(210,180,140,0.2)"
            },
            "combobox": {
                "background-color": "#F4EAD5",
                "border": "1px solid #E8D5C0",
                "border-radius": "4px",
                "padding": "6px 12px",
                "font-size": "11px",
                "color": "#5C4033",
                "font-weight": "600"
            },
            "label_title": {
                "font-size": "12px",
                "font-weight": "600",
                "color": "#5C4033",
                "margin-bottom": "8px",
                "min-height": "18px"
            },
            "label_value": {
                "font-size": "11px",
                "color": "#8B5A3C",
                "margin-top": "4px"
            }
        },
        "fog_blue": {
            "name": "雾蓝冷调",
            "main_window": {
                "background-color": "#2B3A55",
                "color": "#E2E8F0",
                "font-family": "'Segoe UI', Arial, sans-serif",
                "font-size": "11px"
            },
            "groupbox": {
                "background-color": "#3A4D6D",
                "border": "1px solid #4A5B7A",
                "border-radius": "8px",
                "margin-top": "12px",
                "padding-top": "25px",
                "font-weight": "600",
                "color": "#E2E8F0",
                "box-shadow": "0 2px 8px rgba(0,0,0,0.4)",
                "min-height": "80px"
            },
            "groupbox_title": {
                "background-color": "#637394",
                "color": "#FFFFFF",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "12px"
            },
            "button": {
                "background-color": "#637394",
                "color": "#FFFFFF",
                "border": "none",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "11px",
                "padding": "8px 16px"
            },
            "button_hover": {
                "background-color": "#55627F"
            },
            "slider": {
                "background-color": "#8A99B7",
                "border-radius": "3px",
                "height": "6px"
            },
            "slider_handle": {
                "background-color": "#637394",
                "border": "2px solid #2B3A55",
                "border-radius": "6px",
                "width": "12px",
                "height": "12px"
            },
            "preview": {
                "background-color": "#3A4D6D",
                "border": "1px solid #4A5B7A",
                "border-radius": "8px",
                "box-shadow": "0 2px 8px rgba(138,153,183,0.2)"
            },
            "combobox": {
                "background-color": "#3A4D6D",
                "border": "1px solid #4A5B7A",
                "border-radius": "4px",
                "padding": "6px 12px",
                "font-size": "11px",
                "color": "#E2E8F0",
                "font-weight": "600"
            },
            "label_title": {
                "font-size": "12px",
                "font-weight": "600",
                "color": "#E2E8F0",
                "margin-bottom": "8px",
                "min-height": "18px"
            },
            "label_value": {
                "font-size": "11px",
                "color": "#A0B7D4",
                "margin-top": "4px"
            }
        },
        "minimal_white": {
            "name": "极简白灰",
            "main_window": {
                "background-color": "#FFFFFF",
                "color": "#111111",
                "font-family": "'Segoe UI', Arial, sans-serif",
                "font-size": "11px"
            },
            "groupbox": {
                "background-color": "#F7F7F7",
                "border": "1px solid #E0E0E0",
                "border-radius": "8px",
                "margin-top": "12px",
                "padding-top": "25px",
                "font-weight": "600",
                "color": "#111111",
                "box-shadow": "0 2px 8px rgba(0,0,0,0.1)",
                "min-height": "80px"
            },
            "groupbox_title": {
                "background-color": "#333333",
                "color": "#FFFFFF",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "12px"
            },
            "button": {
                "background-color": "#333333",
                "color": "#FFFFFF",
                "border": "none",
                "border-radius": "4px",
                "font-weight": "600",
                "font-size": "11px",
                "padding": "8px 16px"
            },
            "button_hover": {
                "background-color": "#555555"
            },
            "slider": {
                "background-color": "#666666",
                "border-radius": "3px",
                "height": "6px"
            },
            "slider_handle": {
                "background-color": "#333333",
                "border": "2px solid #FFFFFF",
                "border-radius": "6px",
                "width": "12px",
                "height": "12px"
            },
            "preview": {
                "background-color": "#F7F7F7",
                "border": "1px solid #E0E0E0",
                "border-radius": "8px",
                "box-shadow": "0 2px 8px rgba(102,102,102,0.2)"
            },
            "combobox": {
                "background-color": "#F7F7F7",
                "border": "1px solid #E0E0E0",
                "border-radius": "4px",
                "padding": "6px 12px",
                "font-size": "11px",
                "color": "#111111",
                "font-weight": "600"
            },
            "label_title": {
                "font-size": "12px",
                "font-weight": "600",
                "color": "#111111",
                "margin-bottom": "8px",
                "min-height": "18px"
            },
            "label_value": {
                "font-size": "11px",
                "color": "#4A5568",
                "margin-top": "4px"
            }
        }
    }
    
    @classmethod
    def get_theme_stylesheet(cls, theme_name: str) -> str:
        """获取主题样式表"""
        theme = cls.THEMES.get(theme_name, cls.THEMES["minimal"])
        
        return f"""
            /* Material Design 主色调 - {theme['name']} */
            QMainWindow {{
                background-color: {theme['main_window']['background-color']};
                color: {theme['main_window']['color']};
                font-family: {theme['main_window']['font-family']};
                font-size: {theme['main_window']['font-size']};
            }}
            
            /* Material Design 卡片样式 */
            QGroupBox {{
                background-color: {theme['groupbox']['background-color']};
                border: {theme['groupbox']['border']};
                border-radius: {theme['groupbox']['border-radius']};
                margin-top: {theme['groupbox']['margin-top']};
                padding-top: {theme['groupbox']['padding-top']};
                font-weight: {theme['groupbox']['font-weight']};
                color: {theme['groupbox']['color']};
                box-shadow: {theme['groupbox']['box-shadow']};
                min-height: {theme['groupbox']['min-height']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 3px 10px 3px 10px;
                background-color: {theme['groupbox_title']['background-color']};
                color: {theme['groupbox_title']['color']};
                border-radius: {theme['groupbox_title']['border-radius']};
                font-weight: {theme['groupbox_title']['font-weight']};
                font-size: {theme['groupbox_title']['font-size']};
            }}
            
            /* Material Design 按钮样式 */
            QPushButton {{
                background-color: {theme['button']['background-color']};
                color: {theme['button']['color']};
                border: {theme['button']['border']};
                border-radius: {theme['button']['border-radius']};
                font-weight: {theme['button']['font-weight']};
                font-size: {theme['button']['font-size']};
                padding: {theme['button']['padding']};
            }}
            
            QPushButton:hover {{
                background-color: {theme['button_hover']['background-color']};
            }}
            
            QPushButton:pressed {{
                background-color: {theme['button_hover']['background-color']};
            }}
            
            /* 颜色按钮特殊样式 */
            QPushButton#color_button {{
                background-color: {theme['button']['background-color']};
                color: {theme['button']['color']};
                border: {theme['button']['border']};
                border-radius: {theme['button']['border-radius']};
                font-weight: {theme['button']['font-weight']};
                font-size: {theme['button']['font-size']};
                padding: 2px 6px;
                min-width: 50px;
                min-height: 20px;
            }}
            
            QPushButton#color_button:hover {{
                background-color: {theme['button_hover']['background-color']};
            }}
            
            /* Material Design 单选按钮样式 */
            QRadioButton {{
                color: {theme['label_title']['color']};
                font-size: 11px;
                font-weight: 500;
                spacing: 8px;
                min-height: 20px;
                padding: 2px 0px;
            }}
            
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {theme['label_title']['color']};
                border-radius: 8px;
                background-color: {theme['main_window']['background-color']};
            }}
            
            QRadioButton::indicator:hover {{
                border: 2px solid {theme['button']['background-color']};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {theme['button']['background-color']};
                border: 2px solid {theme['button']['background-color']};
                width: 8px;
                height: 8px;
                border-radius: 4px;
                margin: 4px;
            }}
            
            /* Material Design 滑块样式 */
            QSlider::groove:horizontal {{
                background-color: {theme['slider']['background-color']};
                border-radius: {theme['slider']['border-radius']};
                height: {theme['slider']['height']};
            }}
            
            QSlider::handle:horizontal {{
                background-color: {theme['slider_handle']['background-color']};
                border: {theme['slider_handle']['border']};
                border-radius: {theme['slider_handle']['border-radius']};
                width: {theme['slider_handle']['width']};
                height: {theme['slider_handle']['height']};
                margin: -{int(theme['slider_handle']['height'].replace('px', ''))//2}px 0;
            }}
            
            /* Material Design 下拉框样式 */
            QComboBox {{
                background-color: {theme['combobox']['background-color']};
                border: {theme['combobox']['border']};
                border-radius: {theme['combobox']['border-radius']};
                padding: {theme['combobox']['padding']};
                font-size: {theme['combobox']['font-size']};
                color: {theme['combobox']['color']};
                font-weight: {theme['combobox']['font-weight']};
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 0px;
                border-left-color: transparent;
                border-left-style: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid {theme['label_title']['color']};
                margin-right: 8px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {theme['combobox']['background-color']};
                border: {theme['combobox']['border']};
                border-radius: {theme['combobox']['border-radius']};
                {f"color: {theme['combobox']['color']};" if 'color' in theme['combobox'] else ""}
                selection-background-color: {theme['button']['background-color']};
                selection-color: {theme['button']['color']};
            }}
            
            /* Material Design 标签样式 */
            QLabel#title {{
                {f"color: {theme['label_title']['color']};"}
                font-size: {theme['label_title']['font-size']};
                font-weight: {theme['label_title']['font-weight']};
                margin-bottom: {theme['label_title']['margin-bottom']};
                min-height: {theme['label_title']['min-height']};
            }}
            
            QLabel#value {{
                {f"color: {theme['label_value']['color']};"}
                font-size: {theme['label_value']['font-size']};
                margin-top: {theme['label_value']['margin-top']};
            }}
            
            /* Material Design 预览样式 */
            PreviewWidget {{
                background-color: {theme['preview']['background-color']};
                border: {theme['preview']['border']};
                border-radius: {theme['preview']['border-radius']};
                box-shadow: {theme['preview']['box-shadow']};
            }}
            
            /* Material Design 复选框样式 */
            QCheckBox {{
                color: {theme['main_window']['color']};
                font-size: 11px;
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {theme['button']['background-color']};
                border-radius: 3px;
                background-color: transparent;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {theme['button']['background-color']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDRMMy41IDYuNUw5IDEiIHN0cm9rZT0ie2NvbG9yfSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }}
            
            /* Material Design 滚动条样式 */
            QScrollBar:vertical {{
                background-color: transparent;
                width: 8px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {theme['label_value']['color']};
                border-radius: 4px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {theme['button']['background-color']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """
    
    @classmethod
    def get_preview_theme(cls, theme_name: str) -> str:
        """获取预览组件主题"""
        theme = cls.THEMES.get(theme_name, cls.THEMES["minimal"])
        return f"""
            QWidget {{
                background-color: {theme['preview']['background-color']};
                border: {theme['preview']['border']};
                border-radius: {theme['preview']['border-radius']};
                box-shadow: {theme['preview']['box-shadow']};
            }}
        """
    
    @classmethod
    def get_current_theme_color(cls, section: str, key: str) -> str:
        """获取当前主题的颜色值"""
        # 获取当前主题名称
        import sys
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app:
            window = app.activeWindow()
            if window and hasattr(window, 'current_theme'):
                theme_name = window.current_theme
                theme = cls.THEMES.get(theme_name, cls.THEMES["minimal"])
                return theme.get(section, {}).get(key, "#FFFFFF")
        
        # 默认返回白色
        return "#FFFFFF"

class CrosshairPreset:
    """准星预设数据类"""
    def __init__(self, name: str, style: str, color: str = "#00FF00", size: int = 20, thickness: int = 2, opacity: float = 1.0):
        self.name = name
        self.style = style  # cross, dot, circle, plus, x, etc.
        self.color = color
        self.size = size
        self.thickness = thickness
        self.opacity = opacity  # 透明度 0.0-1.0

class PreviewWidget(QWidget):
    """准星预览组件"""
    def __init__(self):
        super().__init__()
        self.preset = CrosshairPreset("Preview", "cross")
        self.setFixedSize(120, 120)
        self.current_theme = "default"
        self.update_theme()
        
    def update_theme(self, theme_name: str = "default"):
        """更新主题"""
        self.current_theme = theme_name
        self.setStyleSheet(ThemeManager.get_preview_theme(theme_name))
        
    def paintEvent(self, event):
        """绘制预览准星"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制浅色背景
        painter.fillRect(self.rect(), QColor("#FAFAFA"))
        
        # 获取预览区域中心
        center = QPoint(self.width() // 2, self.height() // 2)
        
        # 设置画笔和透明度
        color = QColor(self.preset.color)
        color.setAlphaF(self.preset.opacity)  # 设置透明度
        pen = QPen(color, max(1, self.preset.thickness // 2))  # 预览中使用较细的线条
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # 根据样式绘制准星（缩放版本）
        self.draw_crosshair(painter, center, self.preset.style, scale=0.5)  # 减小缩放比例
        
    def draw_crosshair(self, painter: QPainter, center: QPoint, style: str, scale: float = 1.0):
        """根据样式绘制准星"""
        size = int(self.preset.size * scale)
        gap = size // 4
        
        if style == "cross":
            painter.drawLine(center.x() - size, center.y(), center.x() - gap, center.y())
            painter.drawLine(center.x() + gap, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - gap)
            painter.drawLine(center.x(), center.y() + gap, center.x(), center.y() + size)
        elif style == "dot":
            painter.setBrush(QBrush(QColor(self.preset.color)))
            dot_size = max(1, int(self.preset.size * scale))  # 预览中的点大小
            painter.drawEllipse(center, dot_size, dot_size)
        elif style == "circle":
            pen = QPen(QColor(self.preset.color), max(1, int(self.preset.thickness * scale)))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)  # 空心圆
            circle_size = int(self.preset.size * scale)
            painter.drawEllipse(center, circle_size, circle_size)
        elif style == "plus":
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)
        elif style == "x":
            offset = size // 2
            painter.drawLine(center.x() - offset, center.y() - offset, center.x() + offset, center.y() + offset)
            painter.drawLine(center.x() - offset, center.y() + offset, center.x() + offset, center.y() - offset)
        elif style == "cross_dot":
            painter.drawLine(center.x() - size, center.y(), center.x() - gap, center.y())
            painter.drawLine(center.x() + gap, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - gap)
            painter.drawLine(center.x(), center.y() + gap, center.x(), center.y() + size)
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 1, 1)
        elif style == "circle_dot":
            painter.drawEllipse(center, size//2, size//2)
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 1, 1)
        elif style == "bracket":
            bracket_size = size // 3
            painter.drawLine(center.x() - size, center.y() - size, center.x() - size + bracket_size, center.y() - size)
            painter.drawLine(center.x() - size, center.y() - size, center.x() - size, center.y() - size + bracket_size)
            painter.drawLine(center.x() + size - bracket_size, center.y() - size, center.x() + size, center.y() - size)
            painter.drawLine(center.x() + size, center.y() - size, center.x() + size, center.y() - size + bracket_size)
            painter.drawLine(center.x() - size, center.y() + size - bracket_size, center.x() - size, center.y() + size)
            painter.drawLine(center.x() - size, center.y() + size, center.x() - size + bracket_size, center.y() + size)
            painter.drawLine(center.x() + size - bracket_size, center.y() + size, center.x() + size, center.y() + size)
            painter.drawLine(center.x() + size, center.y() + size - bracket_size, center.x() + size, center.y() + size)
        elif style == "line":
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)
        elif style == "double_line":
            offset = size // 3
            painter.drawLine(center.x() - offset, center.y() - size, center.x() - offset, center.y() + size)
            painter.drawLine(center.x() + offset, center.y() - size, center.x() + offset, center.y() + size)
        elif style == "t_shape":
            # T形准星
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y(), center.x(), center.y() + size)
        elif style == "l_shape":
            # L形准星
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y())
            painter.drawLine(center.x(), center.y(), center.x() + size, center.y())
        elif style == "triangle":
            # 三角准星
            triangle_points = [
                QPoint(center.x(), center.y() - size),
                QPoint(center.x() - size, center.y() + size),
                QPoint(center.x() + size, center.y() + size)
            ]
            painter.drawPolygon(triangle_points)
        elif style == "diamond":
            # 菱形准星
            diamond_points = [
                QPoint(center.x(), center.y() - size),
                QPoint(center.x() + size, center.y()),
                QPoint(center.x(), center.y() + size),
                QPoint(center.x() - size, center.y())
            ]
            painter.drawPolygon(diamond_points)
        elif style == "chevron":
            # V形准星
            painter.drawLine(center.x() - size, center.y() - size, center.x(), center.y() + size)
            painter.drawLine(center.x(), center.y() + size, center.x() + size, center.y() - size)
        elif style == "square":
            # 方形准星
            square_size = size // 2
            painter.drawRect(center.x() - square_size, center.y() - square_size, square_size * 2, square_size * 2)
        elif style == "crosshair_circle":
            # 十字圆准星
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)
            painter.drawEllipse(center, size//2, size//2)
        elif style == "dot_circle":
            # 点圆准星
            painter.drawEllipse(center, size//2, size//2)
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 1, 1)
        # 新增独特准星样式（预览版本）
        elif style == "hourglass":
            # 沙漏准星
            gap = size // 3
            painter.drawLine(center.x() - size, center.y() - size, center.x() + size, center.y() + size)
            painter.drawLine(center.x() + size, center.y() - size, center.x() - size, center.y() + size)
            painter.drawLine(center.x() - size, center.y() - gap, center.x() + size, center.y() - gap)
            painter.drawLine(center.x() - size, center.y() + gap, center.x() + size, center.y() + gap)
            
        elif style == "star":
            # 星形准星
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            offset = size // 2
            painter.drawLine(center.x() - offset, center.y() - offset, center.x() + offset, center.y() + offset)
            painter.drawLine(center.x() - offset, center.y() + offset, center.x() + offset, center.y() - offset)
            
        elif style == "hexagon":
            # 六边形准星
            hex_size = size // 2
            points = []
            for i in range(6):
                angle = i * 60
                x = center.x() + hex_size * math.cos(math.radians(angle))
                y = center.y() + hex_size * math.sin(math.radians(angle))
                points.append(QPoint(int(x), int(y)))
            painter.drawPolygon(points)
            
        elif style == "crown":
            # 皇冠准星
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y())
            painter.drawLine(center.x() - size//2, center.y() - size//2, center.x() + size//2, center.y() - size//2)
            
        elif style == "arrow":
            # 箭头准星
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size//2)
            painter.drawLine(center.x(), center.y() - size, center.x() - size//3, center.y() - size//2)
            painter.drawLine(center.x(), center.y() - size, center.x() + size//3, center.y() - size//2)
            
        elif style == "target":
            # 靶心准星
            for i in range(3):
                circle_size = size - i * (size // 3)
                painter.drawEllipse(center, circle_size, circle_size)
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 1, 1)
            
        elif style == "grid":
            # 网格准星
            grid_size = size // 3
            painter.drawLine(center.x() - grid_size, center.y(), center.x() + grid_size, center.y())
            painter.drawLine(center.x(), center.y() - grid_size, center.x(), center.y() + grid_size)
            painter.drawRect(center.x() - grid_size, center.y() - grid_size, grid_size * 2, grid_size * 2)
            
        elif style == "spike":
            # 尖刺准星
            for i in range(8):
                angle = i * 45
                x = center.x() + size * math.cos(math.radians(angle))
                y = center.y() + size * math.sin(math.radians(angle))
                painter.drawLine(center.x(), center.y(), int(x), int(y))
                
        elif style == "compass":
            # 指南针准星
            painter.drawEllipse(center, size//2, size//2)
            painter.drawLine(center.x(), center.y() - size//2, center.x(), center.y() + size//2)
            painter.drawLine(center.x() - size//2, center.y(), center.x() + size//2, center.y())
            # 北方向标记
            painter.drawLine(center.x(), center.y() - size//2, center.x(), center.y() - size//2 - size//4)
            
        elif style == "scope":
            # 瞄准镜准星
            painter.drawEllipse(center, size//3, size//3)
            painter.drawLine(center.x() - size, center.y(), center.x() - size//3, center.y())
            painter.drawLine(center.x() + size//3, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - size//3)
            painter.drawLine(center.x(), center.y() + size//3, center.x(), center.y() + size)
            
        elif style == "reticle":
            # 分划线准星
            gap = size // 4
            # 水平线
            painter.drawLine(center.x() - size, center.y(), center.x() - gap, center.y())
            painter.drawLine(center.x() + gap, center.y(), center.x() + size, center.y())
            # 垂直线
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - gap)
            painter.drawLine(center.x(), center.y() + gap, center.x(), center.y() + size)
            # 中心点
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 1, 1)
            
        elif style == "horseshoe":
            # 马蹄铁准星
            painter.drawArc(center.x() - size, center.y() - size, size * 2, size * 2, 30, 300)
            painter.drawLine(center.x(), center.y() + size, center.x(), center.y() + size//2)
            
        elif style == "crosshair_plus":
            # 十字加号准星
            gap = size // 4
            painter.drawLine(center.x() - size, center.y(), center.x() - gap, center.y())
            painter.drawLine(center.x() + gap, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - gap)
            painter.drawLine(center.x(), center.y() + gap, center.x(), center.y() + size)
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 1, 1)
            
        elif style == "dotted_circle":
            # 点线圆准星
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, size//2, size//2)
            # 添加点标记
            for i in range(8):
                angle = i * 45
                x = center.x() + (size//2) * math.cos(math.radians(angle))
                y = center.y() + (size//2) * math.sin(math.radians(angle))
                painter.setBrush(QBrush(QColor(self.preset.color)))
                painter.drawEllipse(int(x), int(y), 1, 1)
                
        elif style == "segmented":
            # 分段准星
            segment_length = size // 3
            gap = size // 6
            # 水平分段
            painter.drawLine(center.x() - size, center.y(), center.x() - size + segment_length, center.y())
            painter.drawLine(center.x() + size - segment_length, center.y(), center.x() + size, center.y())
            # 垂直分段
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - size + segment_length)
            painter.drawLine(center.x(), center.y() + size - segment_length, center.x(), center.y() + size)
            
        elif style == "mil_dot":
            # 军用点准星
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 2, 2)
            # 外圈
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, size//2, size//2)
            # 刻度线
            for i in range(4):
                angle = i * 90
                x1 = center.x() + (size//2 - 2) * math.cos(math.radians(angle))
                y1 = center.y() + (size//2 - 2) * math.sin(math.radians(angle))
                x2 = center.x() + size//2 * math.cos(math.radians(angle))
                y2 = center.y() + size//2 * math.sin(math.radians(angle))
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        else:
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)

    def update_preset(self, preset: CrosshairPreset):
        """更新预览预设"""
        self.preset = preset
        self.update()

class CrosshairOverlay(QWidget):
    """准星覆盖层窗口"""
    def __init__(self):
        super().__init__()
        self.preset = CrosshairPreset("Default", "cross")
        self.init_window()
        
    def init_window(self):
        """初始化窗口属性"""
        # Windows特定设置
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # 设置窗口穿透
        self.set_click_through()
        
        # 全屏显示
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
    def set_click_through(self):
        """设置点击穿透"""
        hwnd = int(self.winId())
        extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        
    def paintEvent(self, event):
        """绘制准星"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取屏幕中心
        screen = QApplication.primaryScreen().geometry()
        center = QPoint(screen.center())
        
        # 设置画笔和透明度
        color = QColor(self.preset.color)
        color.setAlphaF(self.preset.opacity)  # 设置透明度
        pen = QPen(color, self.preset.thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # 根据样式绘制准星
        self.draw_crosshair(painter, center, self.preset.style)
        
    def draw_crosshair(self, painter: QPainter, center: QPoint, style: str):
        """根据样式绘制准星"""
        size = self.preset.size
        gap = size // 4
        
        if style == "cross":
            # 十字准星
            painter.drawLine(center.x() - size, center.y(), center.x() - gap, center.y())
            painter.drawLine(center.x() + gap, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - gap)
            painter.drawLine(center.x(), center.y() + gap, center.x(), center.y() + size)
            
        elif style == "dot":
            # 点准星 - 直接使用设置的大小
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, self.preset.size, self.preset.size)
            
        elif style == "circle":
            # 圆形准星 - 使用设置的大小作为半径
            pen = QPen(QColor(self.preset.color), self.preset.thickness)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)  # 空心圆
            painter.drawEllipse(center, self.preset.size, self.preset.size)
            
        elif style == "plus":
            # 加号准星（无间隙）
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)
            
        elif style == "x":
            # X形准星
            offset = size // 2
            painter.drawLine(center.x() - offset, center.y() - offset, center.x() + offset, center.y() + offset)
            painter.drawLine(center.x() - offset, center.y() + offset, center.x() + offset, center.y() - offset)
            
        elif style == "cross_dot":
            # 十字+点
            painter.drawLine(center.x() - size, center.y(), center.x() - gap, center.y())
            painter.drawLine(center.x() + gap, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - gap)
            painter.drawLine(center.x(), center.y() + gap, center.x(), center.y() + size)
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 2, 2)
            
        elif style == "circle_dot":
            # 圆形+点
            painter.drawEllipse(center, size//2, size//2)
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 2, 2)
            
        elif style == "bracket":
            # 括号准星
            bracket_size = size // 3
            # 左上
            painter.drawLine(center.x() - size, center.y() - size, center.x() - size + bracket_size, center.y() - size)
            painter.drawLine(center.x() - size, center.y() - size, center.x() - size, center.y() - size + bracket_size)
            # 右上
            painter.drawLine(center.x() + size - bracket_size, center.y() - size, center.x() + size, center.y() - size)
            painter.drawLine(center.x() + size, center.y() - size, center.x() + size, center.y() - size + bracket_size)
            # 左下
            painter.drawLine(center.x() - size, center.y() + size - bracket_size, center.x() - size, center.y() + size)
            painter.drawLine(center.x() - size, center.y() + size, center.x() - size + bracket_size, center.y() + size)
            # 右下
            painter.drawLine(center.x() + size - bracket_size, center.y() + size, center.x() + size, center.y() + size)
            painter.drawLine(center.x() + size, center.y() + size - bracket_size, center.x() + size, center.y() + size)
            
        elif style == "line":
            # 单线准星
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)
            
        elif style == "double_line":
            # 双线准星
            offset = size // 3
            painter.drawLine(center.x() - offset, center.y() - size, center.x() - offset, center.y() + size)
            painter.drawLine(center.x() + offset, center.y() - size, center.x() + offset, center.y() + size)
            
        elif style == "t_shape":
            # T形准星
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y(), center.x(), center.y() + size)
            
        elif style == "l_shape":
            # L形准星
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y())
            painter.drawLine(center.x(), center.y(), center.x() + size, center.y())
            
        elif style == "triangle":
            # 三角准星
            triangle_points = [
                QPoint(center.x(), center.y() - size),
                QPoint(center.x() - size, center.y() + size),
                QPoint(center.x() + size, center.y() + size)
            ]
            painter.drawPolygon(triangle_points)
            
        elif style == "diamond":
            # 菱形准星
            diamond_points = [
                QPoint(center.x(), center.y() - size),
                QPoint(center.x() + size, center.y()),
                QPoint(center.x(), center.y() + size),
                QPoint(center.x() - size, center.y())
            ]
            painter.drawPolygon(diamond_points)
            
        elif style == "chevron":
            # V形准星
            painter.drawLine(center.x() - size, center.y() - size, center.x(), center.y() + size)
            painter.drawLine(center.x(), center.y() + size, center.x() + size, center.y() - size)
            
        elif style == "square":
            # 方形准星
            square_size = size // 2
            painter.drawRect(center.x() - square_size, center.y() - square_size, square_size * 2, square_size * 2)
            
        elif style == "crosshair_circle":
            # 十字圆准星
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)
            painter.drawEllipse(center, size//2, size//2)
            
        elif style == "dot_circle":
            # 点圆准星
            painter.drawEllipse(center, size//2, size//2)
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 2, 2)
            
        # 新增独特准星样式
        elif style == "hourglass":
            # 沙漏准星
            gap = size // 3
            painter.drawLine(center.x() - size, center.y() - size, center.x() + size, center.y() + size)
            painter.drawLine(center.x() + size, center.y() - size, center.x() - size, center.y() + size)
            painter.drawLine(center.x() - size, center.y() - gap, center.x() + size, center.y() - gap)
            painter.drawLine(center.x() - size, center.y() + gap, center.x() + size, center.y() + gap)
            
        elif style == "star":
            # 星形准星
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            offset = size // 2
            painter.drawLine(center.x() - offset, center.y() - offset, center.x() + offset, center.y() + offset)
            painter.drawLine(center.x() - offset, center.y() + offset, center.x() + offset, center.y() - offset)
            
        elif style == "hexagon":
            # 六边形准星
            hex_size = size // 2
            points = []
            for i in range(6):
                angle = i * 60
                x = center.x() + hex_size * math.cos(math.radians(angle))
                y = center.y() + hex_size * math.sin(math.radians(angle))
                points.append(QPoint(int(x), int(y)))
            painter.drawPolygon(points)
            
        elif style == "crown":
            # 皇冠准星
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y())
            painter.drawLine(center.x() - size//2, center.y() - size//2, center.x() + size//2, center.y() - size//2)
            
        elif style == "arrow":
            # 箭头准星
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size//2)
            painter.drawLine(center.x(), center.y() - size, center.x() - size//3, center.y() - size//2)
            painter.drawLine(center.x(), center.y() - size, center.x() + size//3, center.y() - size//2)
            
        elif style == "target":
            # 靶心准星
            for i in range(3):
                circle_size = size - i * (size // 3)
                painter.drawEllipse(center, circle_size, circle_size)
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 2, 2)
            
        elif style == "grid":
            # 网格准星
            grid_size = size // 3
            painter.drawLine(center.x() - grid_size, center.y(), center.x() + grid_size, center.y())
            painter.drawLine(center.x(), center.y() - grid_size, center.x(), center.y() + grid_size)
            painter.drawRect(center.x() - grid_size, center.y() - grid_size, grid_size * 2, grid_size * 2)
            
        elif style == "spike":
            # 尖刺准星
            for i in range(8):
                angle = i * 45
                x = center.x() + size * math.cos(math.radians(angle))
                y = center.y() + size * math.sin(math.radians(angle))
                painter.drawLine(center.x(), center.y(), int(x), int(y))
                
        elif style == "compass":
            # 指南针准星
            painter.drawEllipse(center, size//2, size//2)
            painter.drawLine(center.x(), center.y() - size//2, center.x(), center.y() + size//2)
            painter.drawLine(center.x() - size//2, center.y(), center.x() + size//2, center.y())
            # 北方向标记
            painter.drawLine(center.x(), center.y() - size//2, center.x(), center.y() - size//2 - size//4)
            
        elif style == "scope":
            # 瞄准镜准星
            painter.drawEllipse(center, size//3, size//3)
            painter.drawLine(center.x() - size, center.y(), center.x() - size//3, center.y())
            painter.drawLine(center.x() + size//3, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - size//3)
            painter.drawLine(center.x(), center.y() + size//3, center.x(), center.y() + size)
            
        elif style == "reticle":
            # 分划线准星
            gap = size // 4
            # 水平线
            painter.drawLine(center.x() - size, center.y(), center.x() - gap, center.y())
            painter.drawLine(center.x() + gap, center.y(), center.x() + size, center.y())
            # 垂直线
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - gap)
            painter.drawLine(center.x(), center.y() + gap, center.x(), center.y() + size)
            # 中心点
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 1, 1)
            
        elif style == "horseshoe":
            # 马蹄铁准星
            painter.drawArc(center.x() - size, center.y() - size, size * 2, size * 2, 30, 300)
            painter.drawLine(center.x(), center.y() + size, center.x(), center.y() + size//2)
            
        elif style == "crosshair_plus":
            # 十字加号准星
            gap = size // 4
            painter.drawLine(center.x() - size, center.y(), center.x() - gap, center.y())
            painter.drawLine(center.x() + gap, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - gap)
            painter.drawLine(center.x(), center.y() + gap, center.x(), center.y() + size)
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 2, 2)
            
        elif style == "dotted_circle":
            # 点线圆准星
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, size//2, size//2)
            # 添加点标记
            for i in range(8):
                angle = i * 45
                x = center.x() + (size//2) * math.cos(math.radians(angle))
                y = center.y() + (size//2) * math.sin(math.radians(angle))
                painter.setBrush(QBrush(QColor(self.preset.color)))
                painter.drawEllipse(int(x), int(y), 1, 1)
                
        elif style == "segmented":
            # 分段准星
            segment_length = size // 3
            gap = size // 6
            # 水平分段
            painter.drawLine(center.x() - size, center.y(), center.x() - size + segment_length, center.y())
            painter.drawLine(center.x() + size - segment_length, center.y(), center.x() + size, center.y())
            # 垂直分段
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - size + segment_length)
            painter.drawLine(center.x(), center.y() + size - segment_length, center.x(), center.y() + size)
            
        elif style == "mil_dot":
            # 军用点准星
            painter.setBrush(QBrush(QColor(self.preset.color)))
            painter.drawEllipse(center, 3, 3)
            # 外圈
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, size//2, size//2)
            # 刻度线
            for i in range(4):
                angle = i * 90
                x1 = center.x() + (size//2 - 2) * math.cos(math.radians(angle))
                y1 = center.y() + (size//2 - 2) * math.sin(math.radians(angle))
                x2 = center.x() + size//2 * math.cos(math.radians(angle))
                y2 = center.y() + size//2 * math.sin(math.radians(angle))
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
        else:
            # 默认十字
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)

    def update_preset(self, preset: CrosshairPreset):
        """更新准星预设"""
        self.preset = preset
        self.update()

class PresetManager:
    """预设管理器"""
    def __init__(self):
        self.style_names = {
            "cross": "十字准星",
            "dot": "点准星", 
            "circle": "圆形准星",
            "plus": "加号准星",
            "x": "X形准星",
            "cross_dot": "十字点准星",
            "circle_dot": "圆点准星",
            "bracket": "括号准星",
            "line": "单线准星",
            "double_line": "双线准星",
            "t_shape": "T形准星",
            "l_shape": "L形准星",
            "triangle": "三角准星",
            "diamond": "菱形准星",
            "chevron": "V形准星",
            "square": "方形准星",
            "crosshair_circle": "十字圆准星",
            "dot_circle": "点圆准星",
            # 新增独特准星样式
            "hourglass": "沙漏准星",
            "star": "星形准星", 
            "hexagon": "六边形准星",
            "crown": "皇冠准星",
            "arrow": "箭头准星",
            "target": "靶心准星",
            "grid": "网格准星",
            "spike": "尖刺准星",
            "compass": "指南针准星",
            "scope": "瞄准镜准星",
            "reticle": "分划线准星",
            "horseshoe": "马蹄铁准星",
            "crosshair_plus": "十字加号准星",
            "dotted_circle": "点线圆准星",
            "segmented": "分段准星",
            "mil_dot": "军用点准星"
        }
        self.presets = self.generate_200_presets()
        
    def get_style_name(self, style: str) -> str:
        """获取样式中文名称"""
        return self.style_names.get(style, style)
        
    def generate_200_presets(self) -> List[CrosshairPreset]:
        """生成200个准星预设"""
        presets = []
        colors = ["#00FF00", "#FF0000", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF", "#FF8800", "#8800FF", "#00FF88"]
        
        # 颜色代码到中文名称的映射
        color_names = {
            "#00FF00": "绿色",
            "#FF0000": "红色", 
            "#0000FF": "蓝色",
            "#FFFF00": "黄色",
            "#FF00FF": "紫色",
            "#00FFFF": "青色",
            "#FFFFFF": "白色",
            "#FF8800": "橙色",
            "#8800FF": "紫罗兰",
            "#00FF88": "薄荷绿"
        }
        
        # 1. 优先生成基础样式（点准星和十字准星优先）
        basic_styles = ["cross", "dot", "circle", "plus"]
        for style in basic_styles:
            for color in colors[:4]:  # 使用前4种颜色
                # 点准星使用小尺寸，其他使用标准尺寸
                if style == "dot":
                    sizes = [3, 5, 6, 7, 8, 9]  # 点准星使用小尺寸，添加6和8
                else:
                    sizes = [6, 8, 10, 15, 20, 25]  # 其他样式使用标准尺寸，添加6和8
                for size in sizes:
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        color_name = color_names.get(color, color.replace('#', ''))
                        name = f"{style_name}_{color_name}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 2. 然后生成新样式预设
        new_styles = ["hourglass", "crown"]
        for style in new_styles:
            for color in colors[:2]:  # 使用前2种颜色
                for size in [6, 8, 15, 20, 25]:  # 添加6和8
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        color_name = color_names.get(color, color.replace('#', ''))
                        name = f"{style_name}_{color_name}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 3. 接着生成几何样式预设
        geo_styles = ["triangle", "diamond"]
        for style in geo_styles:
            for color in colors[:2]:  # 使用前2种颜色
                for size in [6, 8, 12, 18, 25]:  # 添加6和8
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        color_name = color_names.get(color, color.replace('#', ''))
                        name = f"{style_name}_{color_name}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 4. 再生成功能样式预设
        func_styles = ["t_shape", "l_shape"]
        for style in func_styles:
            for color in colors[:2]:  # 使用前2种颜色
                for size in [6, 8, 15, 20, 25]:  # 添加6和8
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        color_name = color_names.get(color, color.replace('#', ''))
                        name = f"{style_name}_{color_name}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 5. 然后生成专业样式预设
        pro_styles = ["target", "scope"]
        for style in pro_styles:
            for color in colors[:2]:  # 使用前2种颜色
                for size in [6, 8, 15, 20, 25]:  # 添加6和8
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        color_name = color_names.get(color, color.replace('#', ''))
                        name = f"{style_name}_{color_name}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 6. 最后生成复合样式预设
        complex_styles = ["crosshair_circle", "dot_circle"]
        for style in complex_styles:
            for color in colors[:2]:  # 使用前2种颜色
                for size in [6, 8, 15, 20, 25]:  # 添加6和8
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        color_name = color_names.get(color, color.replace('#', ''))
                        name = f"{style_name}_{color_name}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 确保正好200个
        while len(presets) < 200:
            presets.append(CrosshairPreset(f"Preset_{len(presets)+1}", "cross", "#00FF00", 25, 2, 1.0))
        
        return presets[:200]

class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.overlay = CrosshairOverlay()
        self.preset_manager = PresetManager()
        self.current_preset_index = 0
        self.current_theme = "minimal"
        
        # 加载配置
        self.config = ConfigManager.load_config()
        self.load_settings()
        
        self.init_ui()
        self.setup_hotkeys()
        self.setup_tray()
        self.apply_theme(self.current_theme)
        
    def load_settings(self):
        """加载配置设置"""
        self.current_preset_index = self.config.get("preset_index", 0)
        self.current_theme = self.config.get("theme", "minimal")
        
        # 应用预设设置
        preset = self.preset_manager.presets[self.current_preset_index]
        preset.color = self.config.get("color", preset.color)
        preset.size = self.config.get("size", preset.size)
        preset.thickness = self.config.get("thickness", preset.thickness)
        preset.opacity = self.config.get("opacity", preset.opacity)
        
    def save_settings(self):
        """保存当前设置"""
        preset = self.preset_manager.presets[self.current_preset_index]
        self.config = {
            "preset_index": self.current_preset_index,
            "theme": self.current_theme,
            "color": preset.color,
            "size": preset.size,
            "thickness": preset.thickness,
            "opacity": preset.opacity,
            "click_through": self.click_through_checkbox.isChecked() if hasattr(self, 'click_through_checkbox') else True
        }
        ConfigManager.save_config(self.config)

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("FPS Crosshair Tool")
        self.setFixedSize(1024, 750)  # 设置窗口宽度为1024
        
        # Material Design QSS样式
        self.setStyleSheet("""
            /* Material Design 主色调 */
            QMainWindow {
                background-color: #FAFAFA;
                color: #212121;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
            }
            
            /* Material Design 卡片样式 */
            QGroupBox {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 25px;
                font-weight: 500;
                color: #212121;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                min-height: 80px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 4px 12px 4px 12px;
                background-color: #2196F3;
                color: #FFFFFF;
                border-radius: 4px;
                font-weight: 500;
                font-size: 12px;
            }
            
            /* Material Design 按钮样式 */
            QPushButton {
                background-color: #2196F3;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 11px;
                letter-spacing: 0.5px;
                min-height: 24px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #1976D2;
                box-shadow: 0 2px 4px rgba(33, 150, 243, 0.3);
            }
            
            QPushButton:pressed {
                background-color: #0D47A1;
                box-shadow: 0 1px 2px rgba(33, 150, 243, 0.4);
            }
            
            /* Material Design 滑块样式 - 优化版本 */
            QSlider::groove:horizontal {
                border: none;
                height: 4px;
                background: #E0E0E0;
                border-radius: 2px;
            }
            
            QSlider::handle:horizontal {
                background: #2196F3;
                border: 1px solid #FFFFFF;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            }
            
            QSlider::handle:horizontal:hover {
                background: #1976D2;
                transform: scale(1.2);
            }
            
            /* Material Design 下拉框样式 */
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 11px;
                color: #212121;
                min-height: 20px;
                min-width: 200px;
            }
            
            QComboBox:hover {
                border: 2px solid #2196F3;
            }
            
            QComboBox:focus {
                border: 2px solid #2196F3;
                outline: none;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 24px;
                background-color: transparent;
            }
            
            QComboBox::down-arrow {
                width: 8px;
                height: 8px;
                background-image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOCIgaGVpZ2h0PSI4IiB2aWV3Qm94PSIwIDAgOCA4IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNNCA2TDggMkwwIDJMNCA2WiIgZmlsbD0iIzc1NzU3NSIvPgo8L3N2Zz4K);
                background-repeat: no-repeat;
                background-position: center;
            }
            
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                selection-background-color: #E3F2FD;
                selection-color: #1976D2;
                padding: 4px;
                min-height: 150px;
            }
            
            /* Material Design 复选框样式 */
            QCheckBox {
                color: #212121;
                font-size: 11px;
                spacing: 8px;
                min-height: 16px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #757575;
                border-radius: 3px;
                background-color: #FFFFFF;
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid #2196F3;
            }
            
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTQiIHZpZXdCb3g9IjAgMCAxNCAxNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDRMMTUgN0w2IDE2TDMgMTNMNiAxMEwxMiA0WiIgZmlsbD0iI0ZGRkZGRiIvPgo8L3N2Zz4K);
            }
            
            /* Material Design 标签样式 */
            QLabel {
                color: #212121;
                font-size: 11px;
                font-weight: 400;
                min-height: 14px;
            }
            
            QLabel#title {
                font-size: 14px;
                font-weight: 500;
                color: #212121;
                margin-bottom: 8px;
                min-height: 18px;
            }
            
            QLabel#value {
                background-color: #E3F2FD;
                color: #1976D2;
                padding: 4px 8px;
                border-radius: 12px;
                font-weight: 500;
                font-size: 10px;
                min-height: 16px;
                min-width: 50px;
            }
            
            /* Material Design 滚动条样式 */
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                min-height: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 设置窗口图标
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 预设选择（带预览）
        preset_group = QGroupBox("准星预设")
        preset_layout = QVBoxLayout()
        preset_layout.setSpacing(12)
        preset_layout.setContentsMargins(16, 16, 16, 16)
        
        # 预设选择和预览的水平布局
        preset_h_layout = QHBoxLayout()
        preset_h_layout.setSpacing(16)
        
        # 预设下拉框
        preset_v_layout = QVBoxLayout()
        preset_v_layout.setSpacing(8)
        
        preset_label = QLabel("选择预设")
        preset_label.setObjectName("title")
        preset_v_layout.addWidget(preset_label)
        
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(250)
        for preset in self.preset_manager.presets:
            self.preset_combo.addItem(preset.name)
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        preset_v_layout.addWidget(self.preset_combo)
        
        # 切换按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.prev_button = QPushButton("上一个")
        self.prev_button.setMinimumWidth(70)
        self.prev_button.clicked.connect(self.prev_preset)
        self.next_button = QPushButton("下一个")
        self.next_button.setMinimumWidth(70)
        self.next_button.clicked.connect(self.next_preset)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        preset_v_layout.addLayout(button_layout)
        
        # 预览组件
        preview_v_layout = QVBoxLayout()
        preview_v_layout.setSpacing(12)
        
        preview_label = QLabel("实时预览")
        preview_label.setObjectName("title")
        preview_v_layout.addWidget(preview_label)
        
        # 预览容器，确保居中
        preview_container = QWidget()
        preview_container.setFixedSize(120, 120)
        preview_container_layout = QVBoxLayout(preview_container)
        preview_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.preview_widget = PreviewWidget()
        preview_container_layout.addWidget(self.preview_widget, 0, Qt.AlignmentFlag.AlignCenter)
        
        preview_v_layout.addWidget(preview_container, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 当前类型显示
        self.style_label = QLabel("当前类型: 十字准星")
        self.style_label.setObjectName("value")
        self.style_label.setStyleSheet("""
            QLabel {
                color: #2E7D32;
                font-weight: 500;
                font-size: 11px;
                min-height: 18px;
            }
        """)
        preview_v_layout.addWidget(self.style_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        preset_h_layout.addLayout(preset_v_layout)
        preset_h_layout.addLayout(preview_v_layout)
        
        preset_layout.addLayout(preset_h_layout)
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # 调整选项
        adjust_group = QGroupBox("调整选项")
        adjust_layout = QGridLayout()
        adjust_layout.setSpacing(16)
        adjust_layout.setContentsMargins(20, 20, 20, 20)  # 增大内边距
        
        # 颜色选择
        self.color_button = QPushButton("选择颜色")
        self.color_button.clicked.connect(self.choose_color)
        self.color_button.setObjectName("color_button")
        color_label = QLabel("颜色")
        color_label.setObjectName("title")
        adjust_layout.addWidget(color_label, 0, 0)
        adjust_layout.addWidget(self.color_button, 0, 1, 1, 2)
        adjust_layout.setVerticalSpacing(20)  # 增加垂直间距
        
        # 大小调整
        size_label = QLabel("大小")
        size_label.setObjectName("title")
        adjust_layout.addWidget(size_label, 1, 0)
        
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(10)  # 设置默认值为10
        self.size_slider.valueChanged.connect(self.on_size_changed)
        adjust_layout.addWidget(self.size_slider, 1, 1)
        self.size_label = QLabel("10")
        self.size_label.setObjectName("value")
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.size_label.setMinimumWidth(40)
        adjust_layout.addWidget(self.size_label, 1, 2)
        
        # 粗细调整
        thickness_label = QLabel("粗细")
        thickness_label.setObjectName("title")
        adjust_layout.addWidget(thickness_label, 2, 0)
        
        self.thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self.thickness_slider.setRange(1, 10)
        self.thickness_slider.valueChanged.connect(self.on_thickness_changed)
        adjust_layout.addWidget(self.thickness_slider, 2, 1)
        self.thickness_label = QLabel("2")
        self.thickness_label.setObjectName("value")
        self.thickness_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thickness_label.setMinimumWidth(40)
        adjust_layout.addWidget(self.thickness_label, 2, 2)
        
        # 透明度调整
        opacity_label = QLabel("透明度")
        opacity_label.setObjectName("title")
        adjust_layout.addWidget(opacity_label, 3, 0)
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        adjust_layout.addWidget(self.opacity_slider, 3, 1)
        self.opacity_label = QLabel("100%")
        self.opacity_label.setObjectName("value")
        self.opacity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.opacity_label.setMinimumWidth(40)
        adjust_layout.addWidget(self.opacity_label, 3, 2)
        
        adjust_group.setLayout(adjust_layout)
        layout.addWidget(adjust_group)
        
        # 控制中心 - 重新设计布局
        control_group = QGroupBox("控制中心")
        control_layout = QVBoxLayout()
        control_layout.setSpacing(12)
        control_layout.setContentsMargins(16, 16, 16, 16)
        
        # 第一行：控制选项和主题选择
        main_theme_layout = QHBoxLayout()
        main_theme_layout.setSpacing(15)
        
        # 控制选项组
        control_options_layout = QHBoxLayout()
        control_options_layout.setSpacing(10)
        
        # 显示/隐藏准星 - 使用checkbox
        self.show_crosshair_checkbox = QCheckBox("显示准星")
        self.show_crosshair_checkbox.setChecked(True)  # 默认选中
        self.show_crosshair_checkbox.setMinimumHeight(24)  # 设置最小高度以完整显示文字
        self.show_crosshair_checkbox.stateChanged.connect(self.toggle_crosshair)
        self.show_crosshair_checkbox.setStyleSheet("""
            QCheckBox {
                color: #FFFFFF;
                font-size: 11px;
                font-weight: 500;
                spacing: 10px;
                padding: 4px 8px;
                border-radius: 6px;
                background-color: transparent;
                border: 1px solid transparent;
                min-height: 24px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border-radius: 3px;
                border: 2px solid #FFFFFF;
                background-color: #424242;
            }
            QCheckBox::indicator:checked {
                background-color: #FF4444;
                border: 2px solid #FF4444;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEuNSA1TDMuNSA3TDguNSAyIiBzdHJva2U9IiNGRjRjRkIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4=);
            }
            QCheckBox::indicator:hover {
                border: 2px solid #757575;
                background-color: #4A4A4A;
            }
            QCheckBox::indicator:checked:hover {
                border: 2px solid #CC0000;
                background-color: #FF4444;
            }
            QCheckBox::indicator:pressed {
                background-color: #616161;
                border: 2px solid #616161;
            }
            QCheckBox::indicator:checked:pressed {
                background-color: #CC0000;
                border: 2px solid #CC0000;
            }
        """)
        control_options_layout.addWidget(self.show_crosshair_checkbox)
        
        # 点击穿透
        self.click_through_checkbox = QCheckBox("点击穿透")
        self.click_through_checkbox.setChecked(True)  # 默认选中
        self.click_through_checkbox.setMinimumHeight(24)  # 统一高度
        self.click_through_checkbox.stateChanged.connect(self.toggle_click_through)
        self.click_through_checkbox.setStyleSheet("""
            QCheckBox {
                color: #FFFFFF;
                font-size: 11px;
                font-weight: 500;
                spacing: 8px;
                min-height: 24px;
                padding: 4px 8px;
                border-radius: 6px;
                background-color: transparent;
                border: 1px solid transparent;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border-radius: 3px;
                border: 2px solid #FFFFFF;
                background-color: #424242;
            }
            QCheckBox::indicator:checked {
                background-color: #FF4444;
                border: 2px solid #FF4444;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTQiIHZpZXdCb3g9IjAgMCAxNCAxNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDRMMTUgN0w2IDE2TDMgMTNMNiAxMEwxMiA0WiIgZmlsbD0iI0ZGRkZGRiIvPgo8L3N2Zz4=);
            }
            QCheckBox::indicator:hover {
                border: 2px solid #757575;
                background-color: #4A4A4A;
            }
            QCheckBox::indicator:checked:hover {
                border: 2px solid #CC0000;
                background-color: #FF4444;
            }
            QCheckBox::indicator:pressed {
                background-color: #616161;
                border: 2px solid #616161;
            }
            QCheckBox::indicator:checked:pressed {
                background-color: #CC0000;
                border: 2px solid #CC0000;
            }
        """)
        control_options_layout.addWidget(self.click_through_checkbox)
        
        # 添加控制选项组到主布局
        main_theme_layout.addLayout(control_options_layout)
        
        # 主题选择 - 移到右边
        main_theme_layout.addStretch()
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(120)
        self.theme_combo.setMinimumHeight(24)  # 统一高度
        self.theme_combo.addItems(["石墨极简", "深海静谧", "青柠薄荷", "暖灰办公", "暗夜紫雾", "晴空淡蓝", "炭黑银线", "燕麦奶咖", "雾蓝冷调", "极简白灰"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        main_theme_layout.addWidget(self.theme_combo)
        
        control_layout.addLayout(main_theme_layout)
        
        # 底部添加5像素间距
        control_layout.addSpacing(5)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 快捷键说明
        hotkey_group = QGroupBox("快捷键指南")
        hotkey_layout = QVBoxLayout()
        hotkey_layout.setSpacing(8)
        hotkey_layout.setContentsMargins(16, 16, 16, 16)
        
        # 一行展示所有快捷键，添加背景色
        self.hotkey_text = QLabel("F6 - 显示/隐藏准星 | F7 - 切换下一个预设 | F8 - 切换上一个预设 | Ctrl+Q - 退出程序")
        # 使用默认主题的固定颜色，避免初始化时的白色背景问题
        default_theme = ThemeManager.THEMES.get("minimal", ThemeManager.THEMES["minimal"])
        self.hotkey_text.setStyleSheet(f"""
            QLabel {{
                color: {default_theme['button']['color']};
                font-size: 10px;
                padding: 8px 12px;
                background-color: {default_theme['button']['background-color']};
                border: 1px solid {default_theme['button']['background-color']};
                border-radius: 4px;
                font-weight: 500;
            }}
        """)
        self.hotkey_text.setWordWrap(True)
        hotkey_layout.addWidget(self.hotkey_text)
        
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
        # 显示准星
        self.overlay.show()
        
        # 初始化当前预设的显示
        self.on_preset_changed(self.current_preset_index)
        self.preset_combo.setCurrentIndex(self.current_preset_index)
        
        # 设置主题下拉框初始值
        theme_display_map = {
            "deep_ocean": "深海静谧",
            "minimal": "石墨极简",
            "mint_lemon": "青柠薄荷",
            "warm_gray": "暖灰办公",
            "dark_purple": "暗夜紫雾",
            "sky_blue": "晴空淡蓝",
            "charcoal_silver": "炭黑银线",
            "heat_coffee": "燕麦奶咖",
            "fog_blue": "雾蓝冷调",
            "minimal_white": "极简白灰"
        }
        self.theme_combo.setCurrentText(theme_display_map.get(self.current_theme, "石墨极简"))
        
    def setup_hotkeys(self):
        """设置全局快捷键"""
        self.hotkey_listener = HotkeyListener()
        self.hotkey_listener.toggle_signal.connect(self.toggle_crosshair)
        self.hotkey_listener.next_signal.connect(self.next_preset)
        self.hotkey_listener.prev_signal.connect(self.prev_preset)
        self.hotkey_listener.exit_signal.connect(self.close)
        self.hotkey_listener.start()
        
    def setup_tray(self):
        """设置系统托盘"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
            
            tray_menu = QMenu()
            show_overlay_action = tray_menu.addAction("显示/隐藏准星")
            show_overlay_action.triggered.connect(self.toggle_crosshair)
            
            show_window_action = tray_menu.addAction("设置窗口")
            show_window_action.triggered.connect(self.show_window)
            
            tray_menu.addSeparator()
            
            quit_action = tray_menu.addAction("退出")
            quit_action.triggered.connect(self.close)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
    def show_window(self):
        """显示主窗口"""
        self.show()
        self.activateWindow()
        self.raise_()
            
    def on_preset_changed(self, index):
        """预设改变事件"""
        self.current_preset_index = index
        preset = self.preset_manager.presets[index]
        self.overlay.update_preset(preset)
        
        # 更新预览
        self.preview_widget.update_preset(preset)
        
        # 更新类型标签
        style_name = self.preset_manager.get_style_name(preset.style)
        self.style_label.setText(f"当前类型: {style_name}")
        
        # 更新控件
        self.size_slider.setValue(preset.size)
        self.thickness_slider.setValue(preset.thickness)
        self.opacity_slider.setValue(int(preset.opacity * 100))
        self.opacity_label.setText(f"{int(preset.opacity * 100)}%")
        
        # 保存设置
        self.save_settings()
        
    def choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            preset = self.preset_manager.presets[self.current_preset_index]
            preset.color = color.name()
            self.overlay.update_preset(preset)
            # 更新预览
            self.preview_widget.update_preset(preset)
            self.save_settings()
            
    def on_size_changed(self, value):
        """大小改变事件"""
        self.size_label.setText(str(value))
        preset = self.preset_manager.presets[self.current_preset_index]
        preset.size = value
        self.overlay.update_preset(preset)
        # 更新预览
        self.preview_widget.update_preset(preset)
        self.save_settings()
        
    def on_thickness_changed(self, value):
        """粗细改变事件"""
        self.thickness_label.setText(str(value))
        preset = self.preset_manager.presets[self.current_preset_index]
        preset.thickness = value
        self.overlay.update_preset(preset)
        # 更新预览
        self.preview_widget.update_preset(preset)
        self.save_settings()
        
    def on_opacity_changed(self, value):
        """透明度改变事件"""
        self.opacity_label.setText(f"{value}%")
        preset = self.preset_manager.presets[self.current_preset_index]
        preset.opacity = value / 100.0  # 转换为0.0-1.0
        self.overlay.update_preset(preset)
        # 更新预览
        self.preview_widget.update_preset(preset)
        self.save_settings()
        
    def toggle_crosshair(self, state):
        """切换准星显示状态"""
        if state == Qt.CheckState.Checked.value:
            self.overlay.show()
        else:
            self.overlay.hide()
            
    def toggle_click_through(self, state):
        """切换点击穿透"""
        if state == Qt.CheckState.Checked.value:
            self.overlay.set_click_through()
        else:
            hwnd = int(self.overlay.winId())
            extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style & ~win32con.WS_EX_TRANSPARENT)
        self.save_settings()
            
    def next_preset(self):
        """下一个预设"""
        self.current_preset_index = (self.current_preset_index + 1) % len(self.preset_manager.presets)
        self.preset_combo.setCurrentIndex(self.current_preset_index)
        
    def prev_preset(self):
        """上一个预设"""
        self.current_preset_index = (self.current_preset_index - 1) % len(self.preset_manager.presets)
        self.preset_combo.setCurrentIndex(self.current_preset_index)
        
    def closeEvent(self, event):
        """关闭事件"""
        # 确保彻底退出程序
        self.overlay.close()
        QApplication.quit()  # 强制退出应用程序
        event.accept()
    
    def apply_theme(self, theme_name: str):
        """应用主题"""
        self.current_theme = theme_name
        self.setStyleSheet(ThemeManager.get_theme_stylesheet(theme_name))
        # 更新预览组件主题
        if hasattr(self, 'preview_widget'):
            self.preview_widget.update_theme(theme_name)
        # 更新快捷键样式
        if hasattr(self, 'hotkey_text'):
            theme = ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES["minimal"])
            self.hotkey_text.setStyleSheet(f"""
                QLabel {{
                    color: {theme['button']['color']};
                    font-size: 10px;
                    padding: 8px 12px;
                    background-color: {theme['button']['background-color']};
                    border: 1px solid {theme['button']['background-color']};
                    border-radius: 4px;
                    font-weight: 500;
                }}
            """)
        # 更新checkbox样式
        if hasattr(self, 'show_crosshair_checkbox'):
            theme = ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES["minimal"])
            
            checkbox_style = f"""
                QCheckBox {{
                    color: {theme['main_window']['color']};
                    font-size: 11px;
                    font-weight: 500;
                    spacing: 10px;
                    padding: 4px 8px;
                    border-radius: 6px;
                    background-color: transparent;
                    border: 1px solid transparent;
                    min-height: 24px;
                }}
                QCheckBox::indicator {{
                    width: 14px;
                    height: 14px;
                    border-radius: 3px;
                    border: 2px solid {theme['main_window']['color']};
                    background-color: {theme['button']['background-color']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: #FF4444;
                    border: 2px solid #FF4444;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEuNSA1TDMuNSA3TDguNSAyIiBzdHJva2U9IiNGRjRjRkIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4=);
                }}
                QCheckBox::indicator:hover {{
                    border: 2px solid {theme['button_hover']['background-color']};
                    background-color: {theme['button_hover']['background-color']};
                }}
                QCheckBox::indicator:checked:hover {{
                    border: 2px solid #CC0000;
                    background-color: #FF4444;
                }}
                QCheckBox::indicator:pressed {{
                    background-color: {theme['button_hover']['background-color']};
                    border: 2px solid {theme['button_hover']['background-color']};
                }}
                QCheckBox::indicator:checked:pressed {{
                    background-color: #CC0000;
                    border: 2px solid #CC0000;
                }}
            """
            
            self.show_crosshair_checkbox.setStyleSheet(checkbox_style)
            
            # 点击穿透checkbox样式
            click_through_style = f"""
                QCheckBox {{
                    color: {theme['main_window']['color']};
                    font-size: 11px;
                    font-weight: 500;
                    spacing: 8px;
                    min-height: 24px;
                    padding: 4px 8px;
                    border-radius: 6px;
                    background-color: transparent;
                    border: 1px solid transparent;
                }}
                QCheckBox::indicator {{
                    width: 14px;
                    height: 14px;
                    border-radius: 3px;
                    border: 2px solid {theme['main_window']['color']};
                    background-color: {theme['button']['background-color']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: #FF4444;
                    border: 2px solid #FF4444;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTQiIHZpZXdCb3g9IjAgMCAxNCAxNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDRMMTUgN0w2IDE2TDMgMTNMNiAxMEwxMiA0WiIgZmlsbD0iI0ZGRkZGRiIvPgo8L3N2Zz4=);
                }}
                QCheckBox::indicator:hover {{
                    border: 2px solid {theme['button_hover']['background-color']};
                    background-color: {theme['button_hover']['background-color']};
                }}
                QCheckBox::indicator:checked:hover {{
                    border: 2px solid #CC0000;
                    background-color: #FF4444;
                }}
                QCheckBox::indicator:pressed {{
                    background-color: {theme['button_hover']['background-color']};
                    border: 2px solid {theme['button_hover']['background-color']};
                }}
                QCheckBox::indicator:checked:pressed {{
                    background-color: #CC0000;
                    border: 2px solid #CC0000;
                }}
            """
            
            self.click_through_checkbox.setStyleSheet(click_through_style)

    def change_theme(self, theme_name: str):
        """切换主题"""
        self.apply_theme(theme_name)
    
    def on_theme_changed(self, theme_display_name: str):
        """主题切换事件处理"""
        theme_map = {
            "深海静谧": "deep_ocean",
            "石墨极简": "minimal",
            "青柠薄荷": "mint_lemon",
            "暖灰办公": "warm_gray",
            "暗夜紫雾": "dark_purple",
            "晴空淡蓝": "sky_blue",
            "炭黑银线": "charcoal_silver",
            "燕麦奶咖": "heat_coffee",
            "雾蓝冷调": "fog_blue",
            "极简白灰": "minimal_white"
        }
        theme_name = theme_map.get(theme_display_name, "minimal")
        self.change_theme(theme_name)
        self.save_settings()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)  # 确保在窗口关闭时程序退出
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
