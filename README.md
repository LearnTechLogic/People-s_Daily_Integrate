# 人民日报每日版面爬取与PDF合并工具

使用Python爬取每日人民日报的所有版面，并按顺序合并成一个PDF文件。

## 功能特点

- 支持指定日期爬取（默认今天）
- 自动获取所有版面
- 按版面顺序合并为单个PDF
- 自动清理临时文件
- 提供命令行和多种图形界面使用方式

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式一：图形界面（推荐）

我们提供了两个GUI版本，您可以根据需要选择：

#### 版本1: 简化版GUI（兼容性最好）
```bash
python gui_simple.py
```

#### 版本2: 标准版GUI
```bash
python gui.py
```

#### 测试GUI是否正常工作
```bash
python test_gui.py
```

打开图形界面后：
1. **日期选择**（三种方式）：
   - 点击"📅 选择日期"按钮，打开日历选择器
   - 使用快捷按钮：今天/昨天/前天快速选择
   - 下拉框选择最近30天的日期
2. 点击"浏览..."选择输出PDF文件的保存位置
3. 点击"开始爬取"按钮
4. 等待爬取完成，日志窗口会显示进度
5. 完成后会弹出提示对话框

### 日历选择器功能

- 支持月份切换（上一月/下一月）
- 今天日期高亮显示
- 未来日期自动禁用（因为还没有报纸）
- 支持"今天"和"昨天"快捷按钮

### 方式二：命令行

#### 基本用法

```bash
python main.py --output 人民日报_2026-03-01.pdf
```

#### 指定日期

```bash
python main.py --date 2026-03-01 --output 人民日报_2026-03-01.pdf
```

#### 参数说明

- `--date`, `-d`: 日期，格式为 YYYY-MM-DD，默认为今天
- `--output`, `-o`: 输出PDF文件路径（必填）

## 常见问题

### GUI窗口不显示怎么办？

1. 先运行 `python test_gui.py` 测试tkinter是否正常工作
2. 如果test_gui.py也不显示，请检查：
   - Python是否正确安装了tkinter
   - 窗口是否被最小化
   - 是否有防火墙或杀毒软件阻止
3. 尝试使用简化版GUI: `python gui_simple.py`
4. 如果GUI仍然有问题，可以使用命令行版本

### 使用哪个GUI版本？

- **gui_simple.py**: 推荐优先使用，兼容性最好，界面简洁
- **gui.py**: 界面更美观，但可能在某些系统上有兼容性问题
- **test_gui.py**: 用于测试tkinter是否正常工作

## 如何设置默认输出地址

您可以通过修改 `config.py` 文件来设置默认的PDF保存路径或目录！

### 灵活的路径设置

现在支持两种方式：

**方式1：只指定目录（推荐！）**
程序会自动根据日期生成文件名：
```python
# 保存到桌面
DEFAULT_OUTPUT_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

# 保存到E盘考公文件夹（您的情况）
DEFAULT_OUTPUT_PATH = "E:\\考公"

# 保存到当前项目目录
DEFAULT_OUTPUT_PATH = os.getcwd()
```

文件名会自动生成为：`人民日报_2026-03-01.pdf`

**方式2：指定完整文件名**
如果您想自己指定文件名：
```python
DEFAULT_OUTPUT_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "人民日报.pdf")
```

### 配置示例

打开 `config.py` 文件，根据需要选择：

```python
# 方式1: 只指定目录（推荐！自动生成带日期的文件名）
DEFAULT_OUTPUT_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

# 方式2: 指定完整文件名
# DEFAULT_OUTPUT_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "人民日报.pdf")

# 方式3: 您的情况 - 保存到E盘考公文件夹
# DEFAULT_OUTPUT_PATH = "E:\\考公"
```

### 文件名模板

您还可以自定义文件名模板（在config.py中修改）：
```python
FILENAME_TEMPLATE = "人民日报_{date}.pdf"
```
- `{date}` 会自动替换为日期（如 2026-03-01）

### 常用路径参考

- **桌面**: `os.path.join(os.path.expanduser("~"), "Desktop")`
- **文档**: `os.path.join(os.path.expanduser("~"), "Documents")`
- **下载**: `os.path.join(os.path.expanduser("~"), "Downloads")`
- **当前目录**: `os.getcwd()`
- **指定文件夹**: `"E:\\考公"` 或 `"E:/考公"`

### 注意事项

- 修改配置文件后，重新启动GUI即可生效
- 如果 `config.py` 不存在或出错，程序会自动使用当前目录作为默认路径
- Windows路径中的反斜杠需要用双反斜杠 `\\` 或使用正斜杠 `/`
- 如果指定的是目录，程序会自动创建该目录（如果不存在）

## 注意事项

1. 请确保网络连接正常
2. 请遵守人民日报电子版的版权声明
3. 仅供个人学习研究使用
4. 使用图形界面时，爬取过程中请勿关闭窗口
