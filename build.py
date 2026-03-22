#!/usr/bin/env python3
"""
PyInstaller build script for FPS Crosshair Tool
Creates a single executable file
"""

import PyInstaller.__main__
import os
import sys

def build_exe():
    """构建单个可执行文件"""
    
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
