
# 自动校园网登录脚本（Auto Campus Network Login）

本项目用于 **自动化校园网登录 + 掉线自动重连**，特别适用于基于 **深澜 Srun 系统** 的校园网环境。  
脚本采用 **Selenium 模拟人类点击 + 随机延迟 + 逐字输入** 的方式，实现更加稳定、可靠的自动登录。

本项目支持 **Linux / Windows**，可在后台长期运行（systemd / nohup）。

---

## ✨ 功能特点

- ⏱️ **定时检测网络状态**：自动判断是否能访问外网（如 baidu.com / google.com）
- 🔐 **自动登录校园网**：打开登录页面 → 填写账号密码 → 勾选“记住密码” → 点击登录
- 🧠 **模拟人类行为**：逐字输入 + 随机延迟，避免被识别为脚本操作
- 🖥️ **跨平台支持**：Linux / Windows 均可使用
- 🌙 **支持无头模式**：浏览器可后台运行，不弹窗
- 🛠️ **可自定义浏览器与驱动路径**
- 🔄 **掉线自动重连**

---

## 📁 项目结构
```

.
 ├── auto-login.py     # 主脚本：自动登录 + 网络检测
 ├── requirements.txt  # Python 依赖列表
 └── README.md         # 项目说明文档

```
---

## 🚀 使用方法

### 1. 克隆项目

```bash
git clone https://github.com/laowang404/BIT-Srun-Autologin-Browser.git
cd BIT-Srun-Autologin-Browser
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

---

## 🔧 安装浏览器（linux / windows）

### 🐧 Linux 用户：使用 Chromium

#### 1. 安装 Chromium 浏览器 + chromedriver（自动配套版本）

```bash
sudo apt update
sudo apt install -y chromium-browser chromium-chromedriver
````

系统会自动确保：

* `chromium-browser` 与 `chromedriver` 版本一致
* Selenium 可以直接驱动它

验证安装：

```bash
chromium-browser --version
chromedriver --version
```

#### 2. 在脚本中配置浏览器路径

在 `auto-login.py` 中写：

```python
chrome_options.binary_location = "/usr/bin/chromium-browser"
CHROME_DRIVER_PATH = "/usr/bin/chromedriver"
```

### 🪟 Windows 用户：使用 Chrome 浏览器

#### 1. 安装 Google Chrome（官方最新稳定版）

安装地址（官方下载）：
[https://www.google.com/chrome/](https://www.google.com/chrome/)

#### 2. 下载与 Chrome 主版本号一致的 ChromeDriver

ChromeDriver 官方下载页：
[https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)

步骤：

1. 先查看 Chrome 版本
   在地址栏输入：

```
chrome://version/
```

例如：

```
Google Chrome 121.0.6167.85
```

主版本号为：**121**

2. 在下载页面选择 **对应主版本号的 chromedriver**
3. 下载 `chromedriver-win64.zip`
4. 解压后将 `chromedriver.exe` 放到任意路径，例如：

```
C:\chrome-driver\chromedriver.exe
```

#### 3. 配置脚本路径

在 `auto-login.py` 中写：

```python
CHROME_DRIVER_PATH = r"C:\chrome-driver\chromedriver.exe"
```

Windows 下 **无需设置 binary_location**（Chrome 会自动被找到）。

---

## 🔧 环境要求

你需要安装以下组件：

- Python 3.8+
- Chrome / Chromium / Firefox（任选其一）
- 与浏览器对应版本的 WebDriver
  - Chrome → chromedriver
  - Firefox → geckodriver

> 本程序已在 windows/linux 的 chrome-chromedriver 上进行调试

------

## 🛠 配置 auto-login.py

根据你的实际情况编辑：

```python
# 登录页面 URL（深澜 Srun 登录页）
LOGIN_URL = "http://10.0.0.55"

# 校园网账号密码
USERNAME = "你的校园网账号"
PASSWORD = "你的校园网密码"

# 浏览器驱动路径（若在 PATH 中可设为 None）
CHROME_DRIVER_PATH = "/home/yourname/chromedriver"
```

如果你使用 **Chromium**，建议写死浏览器路径：

```python
chrome_options.binary_location = "/usr/bin/chromium-browser"
```

如果你想后台运行浏览器：

```python
chrome_options.add_argument("--headless=new")
```

------

## ▶️ 运行脚本

```bash
python auto-login.py
```

脚本将自动：

- 每隔一段时间检测外网连通性
- 掉线时自动打开浏览器模拟登录
- 登录成功会继续进入后台监控

------

## ❓ 常见问题（FAQ）

### 1. Chrome 与 chromedriver 版本必须一致吗？

**主版本号必须一致**
 小版本号不要求一致。

### 2. 报错：`cannot find Chrome binary`

说明 Selenium 找不到 Chrome 可执行文件。
 解决方法：手动设置路径，例如：

```python
chrome_options.binary_location = "/usr/bin/google-chrome"
```

### 3. 报错：`NoSuchDriverException: Unable to locate driver`

说明 chromedriver 路径错误或缺少执行权限：

```bash
chmod +x ~/Desktop/chromedriver
./chromedriver --version
```

### 4. Linux 上运行失败？

请检查：

- 驱动是否为 **linux64** 版本
- 驱动是否有执行权限
- Chrome/Chromium 是否能正常打开

------

## 🌙 后台运行方案（Linux）

### 方案 1：nohup（简单）

```bash
nohup python auto-login.py > log.txt 2>&1 &
```

### 方案 2：systemd（推荐长期运行）

创建：

```bash
sudo nano /etc/systemd/system/campus-login.service
```

填入：

```ini
[Unit]
Description=Auto Campus Login
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/yourname/your-repo-name/auto-login.py
Restart=always
User=yourname

[Install]
WantedBy=multi-user.target
```

启用：

```bash
sudo systemctl enable campus-login
sudo systemctl start campus-login
```

查看状态：

```bash
systemctl status campus-login
```

------

## 📄 开源协议

本项目采用 **MIT License**。

你可以自由修改、引用、二次开发。

------

## ⭐ Star 支持一下！

如果本项目对你有帮助，请点一个 Star ⭐ 支持一下！
你的支持是我持续优化的动力 😊