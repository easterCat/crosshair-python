# PyQt6 FPS 准星工具 - 设计文档

## 1. 项目概述

### 1.1 项目简介
PyQt6 FPS 准星工具是一款专为 Windows 设计的 FPS 游戏准星辅助工具，提供 200 个预设准星样式和 20 个专业主题，支持全屏/窗口化游戏。

### 1.2 核心特性
- **200 个准星预设**：自动生成，覆盖所有主流 FPS 样式
- **20 个专业主题**：精心设计的配色方案
- **Windows 全屏/窗口化游戏通用**：完美适配各种游戏模式
- **穿透点击不影响操作**：点击穿透功能
- **纯覆盖层技术**：不读写游戏内存，100% 安全
- **可调参数**：颜色、大小、粗细、透明度
- **全局快捷键**：F6/F7/F8/Ctrl+Q
- **系统托盘集成**：后台运行
- **配置持久化**：自动保存用户设置

### 1.3 技术栈
- **GUI 框架**：PyQt6 6.6.1
- **Windows API**：pywin32 306
- **全局热键**：keyboard 0.13.5
- **打包工具**：PyInstaller 6.3.0
- **Python 版本**：Python 3.x

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         MainWindow                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  UI Layer (PyQt6 Widgets)                              │  │
│  │  - Preset Selection (ComboBox, Buttons)                │  │
│  │  - Adjustment Controls (Sliders, Color Picker)        │  │
│  │  - Control Center (Checkboxes, Theme Selector)         │  │
│  │  - Preview Widget                                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                              │                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Manager Layer                                        │  │
│  │  - ConfigManager (配置管理)                           │  │
│  │  - ThemeManager (主题管理)                             │  │
│  │  - PresetManager (预设管理)                           │  │
│  └───────────────────────────────────────────────────────┘  │
│                              │                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Service Layer                                        │  │
│  │  - HotkeyListener (全局热键监听)                       │  │
│  │  - SystemTray (系统托盘)                               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CrosshairOverlay                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Overlay Window (全屏覆盖层)                           │  │
│  │  - Frameless Window (无边框窗口)                       │  │
│  │  - Click-Through (点击穿透)                            │  │
│  │  - Always on Top (置顶显示)                            │  │
│  │  - Transparent Background (透明背景)                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                              │                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Rendering Engine                                     │  │
│  │  - QPainter (绘制引擎)                                 │  │
│  │  - 30+ Crosshair Styles (30+准星样式)                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

#### 2.2.1 ConfigManager (配置管理器)
- **职责**：管理用户配置的加载和保存
- **文件**：config.json
- **配置项**：
  - preset_index: 当前预设索引
  - theme: 当前主题
  - color: 准星颜色
  - size: 准星大小
  - thickness: 准星粗细
  - opacity: 透明度
  - click_through: 点击穿透状态

#### 2.2.2 HotkeyListener (全局热键监听器)
- **职责**：监听全局快捷键并发送信号
- **热键定义**：
  - F6: 显示/隐藏准星
  - F7: 切换下一个预设
  - F8: 切换上一个预设
  - Ctrl+Q: 退出程序
- **实现方式**：继承 QThread，使用 keyboard 库

#### 2.2.3 ThemeManager (主题管理器)
- **职责**：管理 20 个主题的样式表
- **主题类型**：
  - 深色主题 (9个)：极简黑、赛博灰蓝、森林深绿等
  - 浅色主题 (2个)：极简白、极简蓝白
  - 特殊主题 (9个)：樱花粉灰、沙漠棕褐、薄荷浅绿等
- **样式组件**：main_window, groupbox, button, slider, combobox, label, preview

#### 2.2.4 CrosshairPreset (准星预设数据类)
- **职责**：封装准星属性
- **属性**：
  - name: 预设名称
  - style: 准星样式类型
  - color: 颜色
  - size: 大小
  - thickness: 粗细
  - opacity: 透明度

#### 2.2.5 PreviewWidget (预览组件)
- **职责**：在主窗口中显示准星预览
- **实现**：继承 QWidget，重写 paintEvent
- **特性**：缩放显示 (scale=0.5)，实时更新

#### 2.2.6 CrosshairOverlay (准星覆盖层)
- **职责**：在全屏显示实际准星
- **实现**：继承 QWidget，无边框窗口
- **Windows 特性**：
  - WS_EX_LAYERED: 分层窗口
  - WS_EX_TRANSPARENT: 点击穿透
  - WindowStaysOnTopHint: 置顶显示
  - WA_TranslucentBackground: 透明背景

#### 2.2.7 PresetManager (预设管理器)
- **职责**：生成和管理 200 个准星预设
- **生成策略**：
  1. 基础样式优先 (dot, cross, circle, plus)
  2. 新增样式 (hourglass, crown)
  3. 几何样式 (triangle, diamond)
  4. 功能样式 (t_shape, l_shape)
  5. 专业样式 (target, scope)
  6. 复合样式 (crosshair_circle, dot_circle)
- **颜色方案**：10 种预设颜色
- **尺寸范围**：3-25 像素

#### 2.2.8 MainWindow (主窗口)
- **职责**：应用程序主界面
- **UI 布局**：
  - 准星预设区 (下拉框 + 预览 + 切换按钮)
  - 调整选项区 (颜色、大小、粗细、透明度)
  - 控制中心区 (显示/隐藏、点击穿透、主题选择)
  - 快捷键指南区
- **尺寸**：1024x750 固定窗口

## 3. 数据流设计

### 3.1 启动流程

```
main()
  │
  ├─> QApplication 初始化
  │
  ├─> MainWindow.__init__()
  │     │
  │     ├─> 创建 CrosshairOverlay
  │     ├─> 创建 PresetManager (生成200个预设)
  │     ├─> ConfigManager.load_config() (加载配置)
  │     ├─> load_settings() (应用配置)
  │     ├─> init_ui() (初始化界面)
  │     ├─> setup_hotkeys() (启动热键监听)
  │     ├─> setup_tray() (设置系统托盘)
  │     └─> apply_theme() (应用主题)
  │
  ├─> window.show()
  │
  └─> app.exec()
```

### 3.2 用户交互流程

#### 3.2.1 切换预设
```
用户操作 (下拉框/按钮/热键)
  │
  ├─> on_preset_changed(index)
  │     │
  │     ├─> 更新 current_preset_index
  │     ├─> overlay.update_preset(preset)
  │     ├─> preview_widget.update_preset(preset)
  │     ├─> 更新 UI 控件值
  │     └─> save_settings()
  │
  └─> 触发 overlay.paintEvent() → 重绘准星
```

#### 3.2.2 调整参数
```
用户操作 (滑块/颜色选择器)
  │
  ├─> on_size_changed() / on_thickness_changed() / on_opacity_changed() / choose_color()
  │     │
  │     ├─> 更新 preset 属性
  │     ├─> overlay.update_preset(preset)
  │     ├─> preview_widget.update_preset(preset)
  │     └─> save_settings()
  │
  └─> 触发 overlay.paintEvent() → 重绘准星
```

#### 3.2.3 切换主题
```
用户操作 (主题下拉框)
  │
  ├─> on_theme_changed(theme_display_name)
  │     │
  │     ├─> 映射到主题名称
  │     ├─> apply_theme(theme_name)
  │     │     │
  │     │     ├─> ThemeManager.get_theme_stylesheet()
  │     │     ├─> setStyleSheet() (应用样式表)
  │     │     ├─> preview_widget.update_theme()
  │     │     └─> 更新 checkbox 样式
  │     │
  │     └─> save_settings()
  │
  └─> 界面样式更新
```

## 4. 准星样式系统

### 4.1 样式类型 (30+ 种)

#### 基础样式
- **cross**: 十字准星 (带间隙)
- **dot**: 点准星
- **circle**: 圆形准星
- **plus**: 加号准星 (无间隙)
- **x**: X形准星

#### 复合样式
- **cross_dot**: 十字+点组合
- **circle_dot**: 圆形+点组合
- **crosshair_circle**: 十字圆准星
- **dot_circle**: 点圆准星
- **crosshair_plus**: 十字加号准星

#### 功能样式
- **bracket**: 括号准星
- **line**: 单线准星
- **double_line**: 双线准星
- **t_shape**: T形准星
- **l_shape**: L形准星

#### 几何样式
- **triangle**: 三角准星
- **diamond**: 菱形准星
- **chevron**: V形准星
- **square**: 方形准星
- **hexagon**: 六边形准星

#### 专业样式
- **target**: 靶心准星
- **scope**: 瞄准镜准星
- **reticle**: 分划线准星
- **mil_dot**: 军用点准星
- **horseshoe**: 马蹄铁准星

#### 特殊样式
- **hourglass**: 沙漏准星
- **star**: 星形准星
- **crown**: 皇冠准星
- **arrow**: 箭头准星
- **grid**: 网格准星
- **spike**: 尖刺准星
- **compass**: 指南针准星
- **dotted_circle**: 点线圆准星
- **segmented**: 分段准星

### 4.2 绘制实现

所有样式通过 `QPainter` 在 `paintEvent` 中绘制：
- 使用 `QPen` 设置线条颜色和粗细
- 使用 `QBrush` 填充形状
- 支持 `Antialiasing` 抗锯齿
- 支持透明度 (Alpha通道)

## 5. 主题系统设计

### 5.1 主题结构

每个主题包含以下组件的样式定义：
- **main_window**: 主窗口背景和字体
- **groupbox**: 分组框样式
- **groupbox_title**: 分组框标题
- **button**: 按钮样式
- **button_hover**: 按钮悬停样式
- **slider**: 滑块轨道样式
- **slider_handle**: 滑块手柄样式
- **preview**: 预览区域样式
- **combobox**: 下拉框样式
- **label_title**: 标题标签样式
- **label_value**: 值标签样式

### 5.2 样式表生成

`ThemeManager.get_theme_stylesheet()` 动态生成 Qt 样式表 (QSS)：
- 使用字符串格式化注入主题颜色
- 支持所有 PyQt6 控件样式
- 包含 Material Design 风格

### 5.3 主题切换机制

1. 用户选择主题
2. 映射显示名称到主题键名
3. 调用 `apply_theme()`
4. 生成并应用样式表
5. 更新子组件主题
6. 保存配置

## 6. Windows 特定实现

### 6.1 点击穿透

```python
def set_click_through(self):
    hwnd = int(self.winId())
    extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                          extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
```

**原理**：
- `WS_EX_LAYERED`: 创建分层窗口
- `WS_EX_TRANSPARENT`: 窗口点击穿透，鼠标事件传递到下层窗口

### 6.2 窗口属性

```python
self.setWindowFlags(
    Qt.WindowType.FramelessWindowHint |      # 无边框
    Qt.WindowType.WindowStaysOnTopHint |     # 置顶
    Qt.WindowType.Tool                       # 工具窗口
)
self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 透明背景
self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # 不激活
```

### 6.3 全屏覆盖

```python
screen = QApplication.primaryScreen().geometry()
self.setGeometry(screen)  # 覆盖整个屏幕
```

## 7. 配置管理

### 7.1 配置文件格式 (config.json)

```json
{
    "preset_index": 0,
    "theme": "minimal_black",
    "color": "#00FF00",
    "size": 3,
    "thickness": 2,
    "opacity": 1.0,
    "click_through": true
}
```

### 7.2 配置生命周期

1. **启动时**：`ConfigManager.load_config()` → `load_settings()`
2. **运行时**：任何修改后调用 `save_settings()`
3. **关闭时**：自动保存最后状态

## 8. 性能优化

### 8.1 绘制优化
- 使用 `QPainter.RenderHint.Antialiasing` 保证质量
- 预览组件使用缩放绘制减少计算
- 只在参数变化时触发重绘

### 8.2 线程管理
- 热键监听在独立线程中运行
- 使用 PyQt 信号槽机制线程安全通信
- 主线程专注于 UI 渲染

### 8.3 内存优化
- 预设对象复用
- 样式表按需生成
- 配置文件最小化

## 9. 安全性设计

### 9.1 合规性
- **纯覆盖层技术**：不读取或写入游戏内存
- **无进程注入**：不注入任何代码到游戏进程
- **无网络通信**：完全本地运行
- **无文件修改**：不修改任何游戏文件

### 9.2 反作弊兼容性
- 不会被反作弊系统检测为作弊工具
- 不影响游戏完整性
- 符合游戏服务条款

## 10. 扩展性设计

### 10.1 新增准星样式
1. 在 `CrosshairOverlay.draw_crosshair()` 添加绘制逻辑
2. 在 `PreviewWidget.draw_crosshair()` 添加预览逻辑
3. 在 `PresetManager.style_names` 添加名称映射
4. 在 `PresetManager.generate_200_presets()` 添加生成逻辑

### 10.2 新增主题
1. 在 `ThemeManager.THEMES` 添加主题定义
2. 在主题下拉框添加显示名称
3. 在主题映射字典添加映射关系

### 10.3 新增配置项
1. 修改 `CrosshairPreset` 类添加属性
2. 在 UI 添加对应控件
3. 在 `save_settings()` 和 `load_settings()` 处理
4. 更新 config.json 结构

## 11. 打包与分发

### 11.1 打包配置 (build.py)

```python
PyInstaller 参数：
- --name=FPS_Crosshair_Tool
- --onefile              # 单文件打包
- --windowed             # 无控制台窗口
- --noconfirm            # 自动确认
- --clean                # 清理临时文件
```

### 11.2 依赖管理
- PyQt6 6.6.1
- pywin32 306
- keyboard 0.13.5
- PyInstaller 6.3.0

## 12. 故障排除

### 12.1 常见问题

#### 快捷键不响应
- 以管理员身份运行
- 检查其他程序占用
- 验证 keyboard 库权限

#### 准星不显示
- 检查游戏模式 (非独占全屏)
- 验证窗口置顶状态
- 检查透明度设置

#### 打包失败
- 验证依赖版本
- 检查 Python 环境
- 使用虚拟环境

### 12.2 权限要求
- 建议管理员权限运行
- 需要键盘监听权限
- 需要窗口管理权限
- 可能需要杀毒软件白名单

## 13. 设计模式应用

### 13.1 单例模式
- `ConfigManager`: 配置管理器
- `ThemeManager`: 主题管理器

### 13.2 观察者模式
- `HotkeyListener`: 热键事件通过 PyQt 信号通知
- UI 控件通过信号槽机制响应变化

### 13.3 工厂模式
- `PresetManager.generate_200_presets()`: 批量生成预设

### 13.4 策略模式
- `draw_crosshair()`: 根据样式类型选择不同绘制策略

## 14. 未来改进方向

### 14.1 功能增强
- 支持自定义准星样式
- 支持多显示器配置
- 添加准星动画效果
- 支持配置导入/导出

### 14.2 性能优化
- 使用 OpenGL 加速绘制
- 优化样式表生成
- 减少重绘频率

### 14.3 跨平台支持
- 支持 macOS (使用不同的 API)
- 支持 Linux (X11/Wayland)

### 14.4 用户体验
- 添加准星预设收藏功能
- 支持快捷键自定义
- 添加使用统计
- 提供多语言支持

## 15. 总结

本设计文档详细描述了 PyQt6 FPS 准星工具的架构设计、核心组件、数据流、技术实现等各个方面。项目采用模块化设计，职责清晰，易于维护和扩展。通过纯覆盖层技术实现了安全合规的游戏辅助功能，为 FPS 玩家提供了丰富的准星选择和主题定制能力。

**项目优势**：
- 安全合规：不修改游戏内存
- 功能丰富：200预设 + 20主题
- 用户友好：快捷键 + 托盘集成
- 性能优异：轻量级实现
- 易于扩展：模块化设计

**技术亮点**：
- Windows API 深度集成
- PyQt6 高级特性应用
- 主题系统动态生成
- 全局热键线程安全
