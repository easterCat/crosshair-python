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
                            QCheckBox, QSystemTrayIcon, QMenu, QStyle)
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

class CrosshairPreset:
    """准星预设数据类"""
    def __init__(self, name: str, style: str, color: str = "#00FF00", size: int = 20, thickness: int = 2):
        self.name = name
        self.style = style  # cross, dot, circle, plus, x, etc.
        self.color = color
        self.size = size
        self.thickness = thickness

class PreviewWidget(QWidget):
    """准星预览组件"""
    def __init__(self):
        super().__init__()
        self.preset = CrosshairPreset("Preview", "cross")
        self.setFixedSize(100, 100)
        self.setStyleSheet("background-color: #2b2b2b; border: 1px solid #555;")
        
    def paintEvent(self, event):
        """绘制预览准星"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取预览区域中心
        center = QPoint(self.width() // 2, self.height() // 2)
        
        # 设置画笔
        color = QColor(self.preset.color)
        pen = QPen(color, max(1, self.preset.thickness // 2))  # 预览中使用较细的线条
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # 根据样式绘制准星（缩放版本）
        self.draw_crosshair(painter, center, self.preset.style, scale=0.6)
        
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
            dot_size = max(2, self.preset.size // 3)  # 预览中的点大小
            painter.drawEllipse(center, dot_size, dot_size)
        elif style == "circle":
            pen = QPen(QColor(self.preset.color), max(1, self.preset.thickness // 2))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)  # 空心圆
            painter.drawEllipse(center, size//2, size//2)
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
        center = self.rect().center()
        
        # 设置画笔
        color = QColor(self.preset.color)
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
            # 点准星 - 使用更大的圆点
            painter.setBrush(QBrush(QColor(self.preset.color)))
            dot_size = max(3, self.preset.size // 3)  # 根据大小调整点的大小
            painter.drawEllipse(center, dot_size, dot_size)
            
        elif style == "circle":
            # 圆形准星 - 确保线条粗细合适
            pen = QPen(QColor(self.preset.color), max(2, self.preset.thickness))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)  # 空心圆
            painter.drawEllipse(center, self.preset.size//2, self.preset.size//2)
            
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
            "double_line": "双线准星"
        }
        self.presets = self.generate_200_presets()
        
    def get_style_name(self, style: str) -> str:
        """获取样式中文名称"""
        return self.style_names.get(style, style)
        
    def generate_200_presets(self) -> List[CrosshairPreset]:
        """生成200个准星预设"""
        presets = []
        styles = ["cross", "dot", "circle", "plus", "x", "cross_dot", "circle_dot", "bracket", "line", "double_line"]
        colors = ["#00FF00", "#FF0000", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF", "#FF8800", "#8800FF", "#00FF88"]
        
        # 专门添加更多圆点和圆形准星预设
        dot_sizes = [2, 3, 4, 5, 6, 8, 10]
        circle_sizes = [8, 10, 12, 15, 18, 20, 25]
        
        # 添加更多点准星预设
        for color in colors[:5]:  # 使用前5种颜色
            for dot_size in dot_sizes:
                if len(presets) < 200:
                    style_name = self.get_style_name("dot")
                    name = f"{style_name}_{color.replace('#', '')}_大小{dot_size}"
                    presets.append(CrosshairPreset(name, "dot", color, dot_size, 1))
        
        # 添加更多圆形准星预设
        for color in colors[:5]:  # 使用前5种颜色
            for circle_size in circle_sizes:
                if len(presets) < 200:
                    style_name = self.get_style_name("circle")
                    name = f"{style_name}_{color.replace('#', '')}_大小{circle_size}"
                    presets.append(CrosshairPreset(name, "circle", color, circle_size, 2))
        
        # 添加圆环准星（空心圆）
        for color in colors[:3]:  # 使用前3种颜色
            for ring_size in [10, 15, 20, 25]:
                if len(presets) < 200:
                    name = f"圆环准星_{color.replace('#', '')}_大小{ring_size}"
                    presets.append(CrosshairPreset(name, "circle", color, ring_size, 3))
        
        # 添加多层圆点准星
        for color in colors[:3]:
            if len(presets) < 200:
                name = f"多层圆点_{color.replace('#', '')}"
                presets.append(CrosshairPreset(name, "dot", color, 8, 1))
        
        # 添加同心圆准星
        for color in colors[:3]:
            if len(presets) < 200:
                name = f"同心圆_{color.replace('#', '')}"
                presets.append(CrosshairPreset(name, "circle_dot", color, 15, 2))
        
        # 基础预设（填充剩余位置）
        for i, style in enumerate(styles):
            for j, color in enumerate(colors):
                for size in [10, 15, 20, 25, 30]:
                    for thickness in [1, 2, 3, 4]:
                        if len(presets) < 200:
                            style_name = self.get_style_name(style)
                            name = f"{style_name}_{color.replace('#', '')}_大小{size}_粗细{thickness}"
                            presets.append(CrosshairPreset(name, style, color, size, thickness))
        
        # 确保正好200个
        while len(presets) < 200:
            presets.append(CrosshairPreset(f"Preset_{len(presets)+1}", "cross", "#00FF00", 20, 2))
        
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
        self.setFixedSize(450, 650)
        
        # 设置窗口图标
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 预设选择（带预览）
        preset_group = QGroupBox("准星预设")
        preset_layout = QVBoxLayout()
        
        # 预设选择和预览的水平布局
        preset_h_layout = QHBoxLayout()
        
        # 预设下拉框
        preset_v_layout = QVBoxLayout()
        preset_v_layout.addWidget(QLabel("选择预设:"))
        self.preset_combo = QComboBox()
        for preset in self.preset_manager.presets:
            self.preset_combo.addItem(preset.name)
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        preset_v_layout.addWidget(self.preset_combo)
        
        # 切换按钮
        button_layout = QHBoxLayout()
        self.prev_button = QPushButton("◀ 上一个")
        self.prev_button.clicked.connect(self.prev_preset)
        self.next_button = QPushButton("下一个 ▶")
        self.next_button.clicked.connect(self.next_preset)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        preset_v_layout.addLayout(button_layout)
        
        # 预览组件
        preview_v_layout = QVBoxLayout()
        preview_v_layout.addWidget(QLabel("预览:"))
        self.preview_widget = PreviewWidget()
        preview_v_layout.addWidget(self.preview_widget)
        
        # 当前类型显示
        self.style_label = QLabel("当前类型: 十字准星")
        self.style_label.setStyleSheet("font-weight: bold; color: #00FF00;")
        preview_v_layout.addWidget(self.style_label)
        
        preset_h_layout.addLayout(preset_v_layout)
        preset_h_layout.addLayout(preview_v_layout)
        
        preset_layout.addLayout(preset_h_layout)
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # 调整选项
        adjust_group = QGroupBox("调整选项")
        adjust_layout = QGridLayout()
        
        # 颜色选择
        self.color_button = QPushButton("选择颜色")
        self.color_button.clicked.connect(self.choose_color)
        adjust_layout.addWidget(QLabel("颜色:"), 0, 0)
        adjust_layout.addWidget(self.color_button, 0, 1)
        
        # 大小调整
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(5, 50)
        self.size_slider.setValue(20)
        self.size_slider.valueChanged.connect(self.on_size_changed)
        adjust_layout.addWidget(QLabel("大小:"), 1, 0)
        adjust_layout.addWidget(self.size_slider, 1, 1)
        self.size_label = QLabel("20")
        adjust_layout.addWidget(self.size_label, 1, 2)
        
        # 粗细调整
        self.thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self.thickness_slider.setRange(1, 10)
        self.thickness_slider.setValue(2)
        self.thickness_slider.valueChanged.connect(self.on_thickness_changed)
        adjust_layout.addWidget(QLabel("粗细:"), 2, 0)
        adjust_layout.addWidget(self.thickness_slider, 2, 1)
        self.thickness_label = QLabel("2")
        adjust_layout.addWidget(self.thickness_label, 2, 2)
        
        adjust_group.setLayout(adjust_layout)
        layout.addWidget(adjust_group)
        
        # 控制按钮
        control_group = QGroupBox("控制")
        control_layout = QVBoxLayout()
        
        self.toggle_button = QPushButton("显示/隐藏准星")
        self.toggle_button.clicked.connect(self.toggle_crosshair)
        control_layout.addWidget(self.toggle_button)
        
        self.click_through_checkbox = QCheckBox("点击穿透")
        self.click_through_checkbox.setChecked(True)
        self.click_through_checkbox.stateChanged.connect(self.toggle_click_through)
        control_layout.addWidget(self.click_through_checkbox)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 快捷键说明
        hotkey_group = QGroupBox("快捷键")
        hotkey_layout = QVBoxLayout()
        hotkey_layout.addWidget(QLabel("F6 - 显示/隐藏准星"))
        hotkey_layout.addWidget(QLabel("F7 - 切换下一个预设"))
        hotkey_layout.addWidget(QLabel("F8 - 切换上一个预设"))
        hotkey_layout.addWidget(QLabel("Ctrl+Q - 退出程序"))
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
        # 显示准星
        self.overlay.show()
        
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
