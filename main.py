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
        # Material Design 预览样式
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """)
        
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
        
        # 1. 优先生成基础样式（点准星和十字准星优先）
        basic_styles = ["cross", "dot", "circle", "plus", "x", "cross_dot", "circle_dot"]
        for style in basic_styles:
            for color in colors[:5]:  # 使用前5种颜色
                for size in [10, 15, 20, 25]:
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        name = f"{style_name}_{color.replace('#', '')}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 2. 然后生成新样式预设
        new_styles = ["hourglass", "crown", "grid", "spike", "compass", "segmented"]
        for style in new_styles:
            for color in colors[:5]:  # 使用前5种颜色
                for size in [15, 20, 25]:
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        name = f"{style_name}_{color.replace('#', '')}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 3. 接着生成几何样式预设
        geo_styles = ["triangle", "diamond", "square", "hexagon", "star"]
        for style in geo_styles:
            for color in colors[:5]:  # 使用前5种颜色
                for size in [12, 18, 25]:
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        name = f"{style_name}_{color.replace('#', '')}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 4. 再生成功能样式预设
        func_styles = ["t_shape", "l_shape", "chevron", "arrow", "bracket"]
        for style in func_styles:
            for color in colors[:5]:  # 使用前5种颜色
                for size in [15, 20, 25]:
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        name = f"{style_name}_{color.replace('#', '')}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 5. 然后生成专业样式预设
        pro_styles = ["target", "scope", "reticle", "mil_dot", "horseshoe"]
        for style in pro_styles:
            for color in colors[:3]:  # 使用前3种颜色
                for size in [15, 20, 25]:
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        name = f"{style_name}_{color.replace('#', '')}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 6. 最后生成复合样式预设
        complex_styles = ["crosshair_circle", "dot_circle", "crosshair_plus", "dotted_circle"]
        for style in complex_styles:
            for color in colors[:3]:  # 使用前3种颜色
                for size in [15, 20, 25]:
                    if len(presets) < 200:
                        style_name = self.get_style_name(style)
                        name = f"{style_name}_{color.replace('#', '')}_大小{size}"
                        presets.append(CrosshairPreset(name, style, color, size, 2, 1.0))
        
        # 确保正好200个
        while len(presets) < 200:
            presets.append(CrosshairPreset(f"Preset_{len(presets)+1}", "cross", "#00FF00", 20, 2, 1.0))
        
        return presets[:200]

class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.overlay = CrosshairOverlay()
        self.preset_manager = PresetManager()
        self.current_preset_index = 0
        self.init_ui()
        self.setup_hotkeys()
        self.setup_tray()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("FPS Crosshair Tool")
        self.setFixedSize(1200, 800)  # 增加窗口尺寸
        
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
                padding: 6px 12px;
                font-weight: 500;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                min-height: 20px;
                min-width: 60px;
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
                background-color: #E8F5E8;
                color: #2E7D32;
                padding: 6px 10px;
                border-radius: 16px;
                font-weight: 500;
                font-size: 11px;
                border: 1px solid #A5D6A7;
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
        self.color_button.setFixedSize(60, 25)
        self.color_button.clicked.connect(self.choose_color)
        color_label = QLabel("颜色")
        color_label.setObjectName("title")
        color_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # 垂直居中
        adjust_layout.addWidget(color_label, 0, 0, Qt.AlignmentFlag.AlignVCenter)  # 垂直居中对齐
        adjust_layout.addWidget(self.color_button, 0, 1, 1, 2, Qt.AlignmentFlag.AlignVCenter)  # 按钮也垂直居中
        adjust_layout.setVerticalSpacing(20)  # 增加垂直间距
        
        # 大小调整
        size_label = QLabel("大小")
        size_label.setObjectName("title")
        adjust_layout.addWidget(size_label, 1, 0)
        
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(3, 9)
        self.size_slider.setValue(5)  # 设置默认值为5
        self.size_slider.valueChanged.connect(self.on_size_changed)
        adjust_layout.addWidget(self.size_slider, 1, 1)
        self.size_label = QLabel("5")
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
        
        # 控制按钮
        control_group = QGroupBox("控制中心")
        control_layout = QVBoxLayout()
        control_layout.setSpacing(16)  # 增加间距
        control_layout.setContentsMargins(16, 16, 16, 16)
        
        self.toggle_button = QPushButton("显示/隐藏")
        self.toggle_button.setFixedSize(80, 25)  # 固定尺寸
        self.toggle_button.clicked.connect(self.toggle_crosshair)
        control_layout.addWidget(self.toggle_button)
        
        # 修复复选框样式
        self.click_through_checkbox = QCheckBox("点击穿透")
        self.click_through_checkbox.setMinimumHeight(20)
        self.click_through_checkbox.setStyleSheet("""
            QCheckBox {
                color: #212121;
                font-size: 11px;
                spacing: 8px;
                min-height: 20px;
                padding: 4px 0px;
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
        """)
        self.click_through_checkbox.setChecked(True)
        self.click_through_checkbox.stateChanged.connect(self.toggle_click_through)
        control_layout.addWidget(self.click_through_checkbox)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 快捷键说明
        hotkey_group = QGroupBox("快捷键指南")
        hotkey_layout = QVBoxLayout()
        hotkey_layout.setSpacing(12)
        hotkey_layout.setContentsMargins(16, 16, 16, 16)
        
        hotkey_title = QLabel("全局快捷键")
        hotkey_title.setObjectName("title")
        hotkey_layout.addWidget(hotkey_title)
        
        # 使用水平布局，一行展示所有快捷键
        hotkey_h_layout = QHBoxLayout()
        hotkey_h_layout.setSpacing(15)
        hotkey_h_layout.setContentsMargins(0, 0, 0, 0)
        
        hotkey_items = [
            ("F6", "显示/隐藏准星"),
            ("F7", "切换下一个预设"),
            ("F8", "切换上一个预设"),
            ("Ctrl+Q", "退出程序")
        ]
        
        for key, desc in hotkey_items:
            # 快捷键容器
            hotkey_container = QWidget()
            hotkey_container_layout = QHBoxLayout(hotkey_container)
            hotkey_container_layout.setSpacing(6)
            hotkey_container_layout.setContentsMargins(0, 0, 0, 0)
            
            # 快捷键标签
            key_label = QLabel(key)
            key_label.setStyleSheet("""
                QLabel {
                    background-color: #FFF3E0;
                    color: #E65100;
                    padding: 2px 5px;
                    border-radius: 4px;
                    font-weight: 500;
                    font-size: 8px;
                    border: 1px solid #FFCC80;
                    min-width: 25px;
                    max-width: 35px;
                    text-align: center;
                    min-height: 12px;
                }
            """)
            key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 描述标签
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("""
                QLabel {
                    color: #424242;
                    font-size: 8px;
                    padding: 2px 5px;
                    min-height: 12px;
                }
            """)
            
            hotkey_container_layout.addWidget(key_label)
            hotkey_container_layout.addWidget(desc_label)
            hotkey_h_layout.addWidget(hotkey_container)
        
        hotkey_h_layout.addStretch()
        hotkey_layout.addLayout(hotkey_h_layout)
        
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
        # 显示准星
        self.overlay.show()
        
        # 初始化第一个预设的显示
        self.on_preset_changed(0)
        
    def setup_hotkeys(self):
        """设置全局快捷键"""
        self.hotkey_thread = threading.Thread(target=self.setup_global_hotkeys, daemon=True)
        self.hotkey_thread.start()
        
    def setup_global_hotkeys(self):
        """设置全局快捷键监听"""
        keyboard.add_hotkey('f6', self.toggle_crosshair)
        keyboard.add_hotkey('f7', self.next_preset)
        keyboard.add_hotkey('f8', self.prev_preset)
        keyboard.add_hotkey('ctrl+q', self.close)
        
        # 保持线程运行
        while True:
            time.sleep(0.1)
            
    def setup_tray(self):
        """设置系统托盘"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
            
            tray_menu = QMenu()
            show_action = tray_menu.addAction("显示/隐藏")
            show_action.triggered.connect(self.toggle_crosshair)
            
            quit_action = tray_menu.addAction("退出")
            quit_action.triggered.connect(self.close)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
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
        
    def choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            preset = self.preset_manager.presets[self.current_preset_index]
            preset.color = color.name()
            self.overlay.update_preset(preset)
            # 更新预览
            self.preview_widget.update_preset(preset)
            
    def on_size_changed(self, value):
        """大小改变事件"""
        self.size_label.setText(str(value))
        preset = self.preset_manager.presets[self.current_preset_index]
        preset.size = value
        self.overlay.update_preset(preset)
        # 更新预览
        self.preview_widget.update_preset(preset)
        
    def on_thickness_changed(self, value):
        """粗细改变事件"""
        self.thickness_label.setText(str(value))
        preset = self.preset_manager.presets[self.current_preset_index]
        preset.thickness = value
        self.overlay.update_preset(preset)
        # 更新预览
        self.preview_widget.update_preset(preset)
        
    def on_opacity_changed(self, value):
        """透明度改变事件"""
        self.opacity_label.setText(f"{value}%")
        preset = self.preset_manager.presets[self.current_preset_index]
        preset.opacity = value / 100.0  # 转换为0.0-1.0
        self.overlay.update_preset(preset)
        # 更新预览
        self.preview_widget.update_preset(preset)
        
    def toggle_crosshair(self):
        """切换准星显示"""
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show()
            
    def toggle_click_through(self, state):
        """切换点击穿透"""
        if state == Qt.CheckState.Checked.value:
            self.overlay.set_click_through()
        else:
            hwnd = int(self.overlay.winId())
            extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style & ~win32con.WS_EX_TRANSPARENT)
            
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
        self.overlay.close()
        event.accept()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 允许程序在后台运行
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
