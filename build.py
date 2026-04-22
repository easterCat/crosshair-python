#!/usr/bin/env python3
"""
PyInstaller 构建脚本 - FPS Crosshair Tool
==========================================

将 PyQt6 FPS 准星工具打包为单个可执行文件。

使用方法：
    python build.py

构建产物：
    - dist/FPS_Crosshair_Tool.exe: 单个可执行文件 (~15MB)
    - build/: 构建临时文件（可删除）

PyInstaller 参数说明：
    --name: 输出文件名
    --onefile: 打包为单个可执行文件
    --windowed: 无控制台窗口（GUI应用）
    --noconfirm: 自动确认覆盖
    --clean: 清理临时文件

依赖要求：
    - PyInstaller 6.3.0
    - PyQt6 6.6.1
    - pywin32 306
    - keyboard 0.13.5
"""

import PyInstaller.__main__
import os
import sys

def build_exe():
    """
    构建单个可执行文件
    
    使用 PyInstaller 将 main.py 打包为 Windows 可执行文件。
    
    Returns:
        bool: 构建成功返回 True，失败返回 False
    
    Note:
        构建过程可能需要几分钟时间
        确保所有依赖已正确安装
    """
    
    # PyInstaller 参数
    args = [
        '--name=FPS_Crosshair_Tool',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--clean',
        'main.py'
    ]
    
    # 过滤空参数
    args = [arg for arg in args if arg]
    
    print("开始构建可执行文件...")
    print(f"参数: {' '.join(args)}")
    
    try:
        PyInstaller.__main__.run(args)
        print("构建完成！")
        print("可执行文件位于: dist/FPS_Crosshair_Tool.exe")
    except Exception as e:
        print(f"构建失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_exe()
