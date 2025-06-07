# 重庆大学成绩自动查询与通知脚本使用说明

这是一个用于 **重庆大学教务系统** 的自动化成绩查询程序，解决了查成绩心急的问题。它会定期检查是否有新的成绩发布，并通过邮箱通知你，请加星🌟，后续会开发更多实用的项目，对开发感兴趣的友友🐧1321953481。
<img width="1470" alt="image" src="https://github.com/user-attachments/assets/e4383043-a0b3-4e02-9f74-9e1321eba9ff" />
效果图展示

---

## 📦 功能特点

- 自动登录重庆大学统一身份认证系统
- 查询最新成绩
- 比较成绩变化
- 成绩变动时发送邮件提醒
- 支持无头模式运行（后台静默执行）
- 支持首次运行、定时检测、失败重试等机制

---

## 🧩 依赖安装

在运行脚本前，请确保已安装以下依赖库：

### 安装方式：

```bash
pip install -r requirements.txt
```

### requirements.txt 示例内容：

```
selenium
webdriver-manager
beautifulsoup4
smtplib
requests
json
email
```

---

## ⚙️ 配置说明

请根据你的实际情况修改以下配置项：

### 1. 登录信息

```python
LOGIN_URL = 'https://sso.cqu.edu.cn/login?service=https:%2F%2Fmy.cqu.edu.cn%2Fauthserver%2Fauthentication%2Fcas'
USERNAME_SE = '你的学号'          # 替换为你的学号
PASSWORD_SE = '你的密码'          # 替换为你的统一身份认证密码
```

### 2. 邮件配置

```python
SMTP_SERVER = 'smtp.qq.com'       # SMTP 服务器地址
SMTP_PORT = 587                   # SMTP 端口
EMAIL_ADDRESS = '你的QQ邮箱@qq.com'  # 发件人邮箱
EMAIL_PASSWORD = '你的QQ邮箱应用专用密码'  # QQ邮箱应用专用密码
RECIPIENT_EMAIL = '接收成绩通知的邮箱'  # 接收者邮箱
```

> 🔐 获取 QQ 邮箱应用专用密码：  
> 进入 [QQ邮箱设置 > POP3/SMTP服务](https://mail.qq.com/)，开启服务并生成密码。

### 3. 数据存储文件

```python
LAST_GRADES_FILE = 'latest_grades.json'  # 成绩记录保存路径
```

---

## 🚀 使用方法

### 步骤一：克隆或下载项目

```bash
git clone https://github.com/yourname/cqu-grade-checker.git
cd cqu-grade-checker
```

或者直接将脚本文件保存到本地目录。

---

### 步骤二：安装依赖包

```bash
pip install -r requirements.txt
```

---

### 步骤三：配置账号信息

打开 `your_script_name.py` 文件，修改以下变量：

- `USERNAME_SE`: 学号
- `PASSWORD_SE`: 统一身份认证密码
- `EMAIL_ADDRESS`: 发件人邮箱
- `EMAIL_PASSWORD`: 邮箱应用专用密码
- `RECIPIENT_EMAIL`: 接收成绩通知的邮箱

---

### 步骤四：运行脚本

```bash
python your_script_name.py
```

---

## 🕒 检查频率说明

- 前 10 次每 **10 秒** 检查一次（测试用）
- 超过 10 次后改为每 **5 分钟** 检查一次（正常运行）

---

## 📨 邮件通知示例

你会收到类似如下内容的邮件：

```
你好，

你的成绩信息发生变动：
新增课程: 大学物理I[PH1101], 成绩: 88, 学分: 4.5, 类型: 必修课
成绩变动: 高等数学I[MA1101], 旧成绩: 90, 新成绩: 92, 学分: 5, 类型: 必修课

祝好！
自动成绩通知程序
```

---

## 📁 输出文件说明

脚本会在当前目录下生成以下文件：

| 文件名 | 说明 |
|--------|------|
| `latest_grades.json` | 最新成绩数据（JSON 格式） |
| `login_error_*.png` | 登录失败截图 |
| `grades_content_not_found_*.png` | 页面结构异常截图 |
| `critical_error_*.png` | 严重错误截图 |

---

## 🧪 日志输出

脚本运行时会在终端输出日志信息，包括：

- 登录状态
- 成绩解析结果
- 是否有变动
- 邮件发送状态
- 错误提示及截图保存情况

---

## 📌 注意事项

- ✅ 该脚本适用于 **重庆大学统一身份认证系统 + 教务系统**
- ✅ 支持验证码识别（需配合神经网络模型文件 `THETA.mat`）
- ✅ 不需要浏览器界面显示时，可启用无头模式（默认启用）
- ✅ 如果你想部署到服务器上长期运行，建议使用 `nohup` 或 `screen`

---

## 💡 提示

- 如果你希望部署到服务器或后台运行，可以使用以下命令：

```bash
nohup python your_script_name.py > app.log 2>&1 &
```

- 脚本支持失败重试、截图记录错误等功能。
- 你可以根据需要调整检查频率和邮件模板内容。

---

## 📞 反馈建议

如果你有任何问题或改进意见，欢迎提交 issue 或联系作者 🐧1321953481。

--- 

## 📎 附录：完整目录结构推荐

```
cqu-grade-checker/
├── 邮件自动通知.py      # 主程序
├── requirements.txt         # 依赖包列表
├── latest_grades.json       # 成绩缓存文件
├── THETA.mat                # 验证码识别模型文件（如需）
├── logs/
│   ├── app.log              # 日志文件（可选）
└── screenshots/
    ├── login_error_*.png
    └── critical_error_*.png
```

---

