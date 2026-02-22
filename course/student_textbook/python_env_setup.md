# 🐍 Python 数据分析开发环境安装指南 (2026 中文入门版)

欢迎来到数据分析的世界！本指南专为《Python 数据分析》课程的学生编写，考虑到国内网络环境和零基础起步的需要，我们将手把手带你完成环境搭建。

---

## 🚀 第一步：了解我们要安装什么

在开始之前，先认识一下我们要配置的“三剑客”：
1.  **Mamba (小曼巴)**：就像是一个功能更强的“手机应用商店”，用来下载和安装 Python 及其各种工具库。相比传统的 Anaconda，它的下载和安装速度快得惊人。
2.  **VS Code**：你的“笔记本”和“编辑器”，这是目前全球最流行的写代码软件。
3.  **核心库**：我们要处理数据、画图、做预测所必备的“工具包”（如 Pandas, NumPy）。

---

## 🌏 第二步：国内镜像源配置 (关键步骤)

为了让后续下载不再卡顿，我们需要将下载地址切换到国内服务器（如清华大学镜像源）。

> [!IMPORTANT]
> **请务必在安装完 Mamba 后执行此步骤！** (具体执行时机见下文各系统指南)

---

## 🪟 Windows 安装指南 (适合 90% 的同学)

### 1. 下载并安装 Mambaforge
- **点击下载**：[Mambaforge-Windows-x86_64](https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Windows-x86_64.exe)
- **安装注意**：
  - 下载后双击运行。
  - 在点击 "Next" 的过程中，遇到 **"Advanced Options"** 界面时，**强烈建议勾选** "Add Mambaforge to my PATH environment variable"。虽然它是红色的警告，但勾选后你可以在任何地方使用它，对入门同学更友好。

### 2. 配置国内加速
- 点击 Windows 开始菜单，输入 `cmd` 或 `PowerShell` 并打开。
- **依次复制并运行**以下命令（一行一行运行）：
  ```bash
  mamba config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
  mamba config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
  mamba config --set show_channel_urls yes
  ```

---

## 🍎 macOS 安装指南

### 1. 确定你的芯片类型
- 点击屏幕左上角 🍏 标志 -> "关于本机"。
- 如果显示 **Apple M1/M2/M3**，下载：[Apple Silicon 版](https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-MacOSX-arm64.sh)
- 如果显示 **Intel**，下载：[Intel 版](https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-MacOSX-x86_64.sh)

### 2. 安装步骤
- 打开“终端 (Terminal)”。
- 输入 `bash` 然后把下载好的文件拖进终端，接着按回车。
- 一路按回车或输入 `yes`。
- 安装完后重启终端，配置国内加速（命令同 Windows）。

---

## �️ 第三步：安装 VS Code 与插件

1.  从 [官网](https://code.visualstudio.com/) 下载并安装。
2.  打开 VS Code，点击左侧边栏顶部的第五个图标（像方块一样的“扩展”按钮）。
3.  在搜索框输入并安装：
    - `Chinese (Simplified)` (中文语言包)
    - `Python`
    - `Jupyter`

---

## 🧪 第四步：创建环境与安装核心库 (超级重点)

现在我们要创建一个隔离的“实验室”，把所有的核心工具安装进去。

### 1. 创建环境
在终端（Windows 下是 CMD 或 PowerShell，macOS 下是终端）运行：
```bash
# 创建一个名为 da2026 的 Python 3.10 环境
mamba create -n da2026 python=3.10 -y
```

### 2. 激活并安装核心库
这是最重要的步骤，一行命令搞定所有工具：
```bash
# 激活环境
mamba activate da2026

# 安装核心工具库 (指定 2026 课程要求的版本)
mamba install pandas>=2.1.0 numpy>=1.24.0 matplotlib seaborn plotly scikit-learn polars jupyterlab -c conda-forge -y
```

**工具库小结：**
- **Pandas 2.0+**：处理表格数据的高手。
- **NumPy 1.24+**：基础数学运算。
- **Matplotlib & Seaborn**：画静态图。
- **Plotly**：画那种能用鼠标点来点去的交互图。
- **Scikit-learn**：机器学习。
- **Polars**：处理海量数据的最新极速工具。

---

## ✅ 第五步：验证是否安装成功

1.  打开 VS Code。
2.  新建一个文件，命名为 `test.ipynb` (注意后缀是 .ipynb)。
3.  在文件右上角点击 **"选择内核 (Select Kernel)"** -> **"Python Environments"** -> 选择带有 `da2026` 字样的那个。
4.  在代码格中输入以下内容，点击左边的运行按钮：
    ```python
    import pandas as pd
    import numpy as np
    import polars as pl
    
    print(f"Pandas 版本: {pd.__version__}")
    print(f"NumPy 版本: {np.__version__}")
    print(f"Polars 版本: {pl.__version__}")
    print("恭喜你！环境搭建圆满成功！🚀")
    ```

---

## 🆘 网络排错 (常见问题)

- **下载还是慢？**：有时候网络波动，可以尝试多次运行 `mamba install` 命令。
- **命令找不到？**：如果提示 `mamba: command not found`，请重启你的 VS Code 或 终端。
- **库版本冲突？**：只要你是在 `mamba activate da2026` 之后安装的，通常不会有冲突。

---
祝你在《Python 数据分析》课程中取得优异成绩！有问题请随时咨询助教。
