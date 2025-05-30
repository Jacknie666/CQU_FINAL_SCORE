import time
import smtplib
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import json  # 用于处理 JSON 文件
import os  # 用于检查文件是否存在
# --- 用户配置 ---
LOGIN_URL = 'https://sso.cqu.edu.cn/login?service=https:%2F%2Fmy.cqu.edu.cn%2Fauthserver%2Fauthentication%2Fcas'
USERNAME_SE = ''  # 你的学号/账号
PASSWORD_SE = ''  # 你的密码

# --- Email Configuration ---
SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 587
EMAIL_ADDRESS = '2125661354@qq.com'  # 发件人QQ邮箱
EMAIL_PASSWORD = 'ytwdrdhfqsxyjhia'  # QQ邮箱应用专用密码，强烈建议自己注册，该邮箱仅提供测试学习使用，若用于非法用途，自行承担法律后果
RECIPIENT_EMAIL = ''  # 收件人邮箱同理

# --- 数据文件 ---
LAST_GRADES_FILE = 'latest_grades.json'


# --- Selenium WebDriver 初始化 ---
def setup_driver():
    """初始化并返回一个 Chrome WebDriver 实例"""
    print("正在使用 webdriver-manager 设置 ChromeDriver...")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("ChromeDriver 启动成功。")
        driver.implicitly_wait(10)  # 增加隐式等待时间
        return driver
    except Exception as e:
        print(f"使用 webdriver-manager 初始化 WebDriver 时出错: {e}")
        return None


# --- 元素定位器 ---
USERNAME_FIELD_LOCATOR = (By.XPATH, '//input[@placeholder="统一身份认证号/身份证件号"]')
PASSWORD_FIELD_LOCATOR = (By.XPATH, '//input[@placeholder="Please enter Password"]')
LOGIN_BUTTON_LOCATOR = (By.CLASS_NAME, 'login-button')
GRADE_INQUIRY_BUTTON_OR_TAB_LOCATOR = (By.XPATH, "//span[@title='成绩查询' and normalize-space()='成绩查询']")


def login(driver, login_url, username, password):
    """执行登录操作，目标是到达主工作区页面"""
    try:
        print(f"正在打开登录页面: {login_url}")
        driver.get(login_url)

        print("等待并定位用户名输入框...")
        username_input = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(USERNAME_FIELD_LOCATOR)
        )
        username_input.clear()
        username_input.send_keys(username)
        print("用户名输入完成。")
        time.sleep(0.3)

        print("等待并定位密码输入框...")
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(PASSWORD_FIELD_LOCATOR)
        )
        password_input.clear()
        password_input.send_keys(password)
        print("密码输入完成。")
        time.sleep(0.3)

        print("等待并定位登录按钮...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(LOGIN_BUTTON_LOCATOR)
        )
        login_button.click()
        print("登录按钮已点击。")

        print("等待登录成功并跳转到主工作区页面...")
        WebDriverWait(driver, 40).until(
            EC.url_contains("https://my.cqu.edu.cn/workspace/home")
        )
        print("已成功登录到主工作区！当前 URL:", driver.current_url)
        return True
    except Exception as e:
        print(f"登录过程中发生错误: {e}")
        try:
            driver.save_screenshot(f'login_error_{time.strftime("%Y%m%d-%H%M%S")}.png')
        except:
            pass
        return False


def click_grade_inquiry_button_and_wait_for_grades(driver):
    """
    在主工作区页面点击“成绩查询”按钮或确保成绩视图已激活，
    并等待成绩内容加载。返回包含成绩内容的HTML源码。
    """
    try:
        print("尝试定位“成绩查询”按钮/标签页...")
        grade_button_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(GRADE_INQUIRY_BUTTON_OR_TAB_LOCATOR)
        )
        print("“成绩查询”按钮/标签已找到且可点击。")

        print("尝试点击“成绩查询”...")
        driver.execute_script("arguments[0].click();", grade_button_element)
        print("“成绩查询”按钮/标签已点击。")

        time.sleep(2)  # 点击后给页面一些反应时间，等待可能的JS加载或iframe切换

        html_source_to_parse = None

        # 尝试1: 在主文档中查找成绩
        try:
            print("在主文档中等待成绩容器 'stu-sam-view-item-model' 加载...")
            WebDriverWait(driver, 15).until(  # 初始等待时间
                EC.presence_of_element_located((By.CLASS_NAME, 'stu-sam-view-item-model'))
            )
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'content-box'))
            )
            print("成绩内容容器在主文档中找到。")
            html_source_to_parse = driver.page_source
            return html_source_to_parse
        except TimeoutException:
            print("在主文档中等待成绩内容超时。")

        # 尝试2: 查找并切换到 iframe
        print("尝试查找并切换到 iframe...")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        if not iframes:
            print("页面上没有找到 iframe。")
        else:
            for index, iframe_el in enumerate(iframes):
                try:
                    print(f"尝试切换到 iframe (索引 {index})...")
                    driver.switch_to.frame(iframe_el)
                    print(f"已切换到 iframe (索引 {index})。检查成绩容器...")
                    WebDriverWait(driver, 10).until(  # 在iframe内等待时间可以短一些
                        EC.presence_of_element_located((By.CLASS_NAME, 'stu-sam-view-item-model'))
                    )
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'content-box'))
                    )
                    print("成绩内容容器在 iframe 中找到。")
                    html_source_to_parse = driver.page_source
                    driver.switch_to.default_content()  # 操作完毕切回主文档
                    return html_source_to_parse
                except TimeoutException:
                    print(f"在 iframe (索引 {index}) 内等待成绩内容超时。")
                    driver.switch_to.default_content()
                    continue
                except Exception as e_iframe_switch:
                    print(f"切换到 iframe (索引 {index}) 或在其内操作时发生其他错误: {e_iframe_switch}")
                    driver.switch_to.default_content()
                    continue

        print("未能通过主文档或 iframe 找到预期的成绩内容结构。")
        driver.save_screenshot(f'grades_content_not_found_{time.strftime("%Y%m%d-%H%M%S")}.png')
        print("截图已保存。将返回当前主文档的源码。")
        return driver.page_source  # 即使没找到特定结构，也返回当前页面源码供分析

    except Exception as e:
        print(f"点击“成绩查询”按钮或等待成绩加载时发生错误: {e}")
        try:
            driver.save_screenshot(f'click_grades_error_{time.strftime("%Y%m%d-%H%M%S")}.png')
        except:
            pass
        return driver.page_source  # 出错时返回当前页面源码


def parse_grades_from_html(html_content):
    """从HTML内容中解析成绩"""
    if not html_content:
        print("没有HTML内容可供解析。")
        return None
    print("\n--- 开始使用BeautifulSoup解析成绩 ---")
    soup = BeautifulSoup(html_content, 'html.parser')
    grades_data = []

    main_grades_container = soup.find('div', class_='stu-sam-view-item-model')

    if not main_grades_container:
        print("警告：在HTML中未找到 class='stu-sam-view-item-model' 的主容器。")
        print("将尝试直接在整个页面查找 'content-box'...")
        course_entries = soup.find_all('div', class_='content-box')
        if not course_entries:
            print("解析失败：未能找到任何 'stu-sam-view-item-model' 或 'content-box' 课程条目容器。")
            return None
    else:
        print("找到了 'stu-sam-view-item-model' 容器。")
        course_entries = main_grades_container.find_all('div', class_='content-box')
        if not course_entries:
            print("在 'stu-sam-view-item-model' 容器内未找到 'content-box' 条目。")
            return None

    print(f"找到了 {len(course_entries)} 个课程条目。")
    for i, entry in enumerate(course_entries):
        score_tag = entry.find('div', class_='left effective-score')
        score = score_tag.text.strip() if score_tag else f"N/A"

        course_name_tag = entry.find('span', class_='course-name')
        course_name_full = course_name_tag.text.strip() if course_name_tag else f"N/A"
        course_name = course_name_full.split('[')[0].strip() if '[' in course_name_full else course_name_full

        course_type = "N/A"
        middle_content = entry.find('div', class_='middle-content')
        if middle_content:
            course_content_div = middle_content.find('div', class_='course-content')
            if course_content_div:
                course_type_tag = course_content_div.find('span', class_='ant-tag')
                if course_type_tag:
                    course_type = course_type_tag.text.strip()

        credit_tag = entry.find('div', class_='credit')
        credit_text = credit_tag.text.strip() if credit_tag else "N/A"
        credit = credit_text.replace('分', '').strip()

        # 使用课程全名（含代码）作为唯一标识符，如果课程名称可能重复的话
        # 或者组合课程名和学分等作为更可靠的键
        # 这里我们简单用 "课程名称" + "类型" + "学分" 作为键，以处理可能的同名课程
        # 但更好的做法是如果课程代码唯一，就用课程代码
        course_identifier = f"{course_name_full}_{course_type}_{credit}"

        grades_data.append({
            "identifier": course_identifier,  # 用于比较的唯一标识
            "课程名称": course_name,
            "成绩": score,
            "课程类型": course_type,
            "学分": credit,
            "原始课程名": course_name_full
        })

    if not grades_data and course_entries:
        print("警告：找到了课程条目，但未能从中提取详细成绩数据。")
    elif not grades_data:
        print("未提取到成绩数据。")
    return grades_data if grades_data else None


# --- Email Sending Function ---
def send_email(subject, body_content, recipient=RECIPIENT_EMAIL):
    print(f"准备发送邮件，主题: '{subject}'")
    message = MIMEText(body_content, 'plain', 'GBK')  # 保持用户指定的GBK编码
    message['Subject'] = subject
    message['From'] = EMAIL_ADDRESS
    message['To'] = recipient
    server = None
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipient, message.as_string())
        print(f"邮件已成功发送至 {recipient}.")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False
    finally:
        if server:
            try:
                server.quit()
            except:
                pass


# --- 成绩比较和存储 ---
def load_previous_grades(filepath=LAST_GRADES_FILE):
    """从文件加载上次的成绩数据"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"警告: '{filepath}' 文件内容不是有效的JSON格式，将视为空。")
            return None
        except Exception as e:
            print(f"读取旧成绩文件 '{filepath}' 时出错: {e}")
            return None
    return None


def save_current_grades(grades_data, filepath=LAST_GRADES_FILE):
    """将当前成绩数据保存到文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(grades_data, f, ensure_ascii=False, indent=4)
        print(f"当前成绩已保存到: {filepath}")
    except Exception as e:
        print(f"保存当前成绩到 '{filepath}' 时出错: {e}")


def compare_grades(old_grades_list, new_grades_list):
    """
    比较新旧成绩列表。
    返回 (是否有变化, 变化详情描述字符串)。
    """
    if old_grades_list is None:  # 第一次运行或旧文件有问题
        return True, "首次获取成绩，或无历史成绩对比。"

    # 为了方便比较，将列表转换为以课程 identifier 为键的字典
    old_grades_dict = {item['identifier']: item for item in old_grades_list}
    new_grades_dict = {item['identifier']: item for item in new_grades_list}

    changes = []
    changed_course_count = 0

    # 检查新增或修改的课程
    for identifier, new_item in new_grades_dict.items():
        old_item = old_grades_dict.get(identifier)
        if not old_item:
            changes.append(
                f"新增课程: {new_item['原始课程名']}, 成绩: {new_item['成绩']}, 学分: {new_item['学分']}, 类型: {new_item['课程类型']}")
            changed_course_count += 1
        elif old_item['成绩'] != new_item['成绩']:  # 假设我们主要关心成绩的变化
            changes.append(
                f"成绩变动: {new_item['原始课程名']}, 旧成绩: {old_item['成绩']}, 新成绩: {new_item['成绩']}, 学分: {new_item['学分']}, 类型: {new_item['课程类型']}")
            changed_course_count += 1
        # 你也可以在这里比较学分、类型等其他字段的变化

    # 检查删除的课程 (如果需要)
    # for identifier, old_item in old_grades_dict.items():
    #     if identifier not in new_grades_dict:
    #         changes.append(f"课程移除: {old_item['原始课程名']}, 原成绩: {old_item['成绩']}")
    #         changed_course_count +=1

    if changed_course_count > 0:
        return True, f"成绩发生变动 ({changed_course_count}门课程):\n" + "\n".join(changes)
    else:
        return False, "成绩与上次查询结果一致。"


# --- 主要的成绩获取和通知流程 ---
def run_grade_check_and_notify():
    """
    执行一次完整的成绩获取、比较和通知流程。
    """
    print("开始新一轮成绩检查...")
    if USERNAME_SE == '你的真实用户名' or PASSWORD_SE == '你的真实密码':  # 示例凭据检查
        msg = "严重错误：请更新脚本中的 USERNAME_SE 和 PASSWORD_SE 为你的真实凭据。"
        print(msg)
        # 不发送邮件，因为这是配置问题
        return

    driver = setup_driver()
    if not driver:
        send_email("成绩查询脚本错误通知", f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n错误: WebDriver 初始化失败。",
                   RECIPIENT_EMAIL)
        return

    try:
        if login(driver, LOGIN_URL, USERNAME_SE, PASSWORD_SE):
            print("\n登录成功。")
            time.sleep(2)  # 等待工作区页面稳定

            html_for_parsing = click_grade_inquiry_button_and_wait_for_grades(driver)

            if html_for_parsing:
                # 调试时保存HTML
                # with open(f'grades_page_{time.strftime("%Y%m%d-%H%M%S")}.html', 'w', encoding='utf-8') as f:
                #     f.write(html_for_parsing)
                # print("当前成绩页面HTML已保存。")

                current_grades = parse_grades_from_html(html_for_parsing)

                if current_grades is not None:  # parse_grades_from_html 可能返回 None
                    print("成绩解析成功。")
                    previous_grades = load_previous_grades()

                    has_changed, change_details = compare_grades(previous_grades, current_grades)

                    if has_changed:
                        print(f"成绩变动详情: {change_details}")
                        email_subject = f"【重要】成绩更新通知 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
                        email_body = f"你好，\n\n你的成绩信息发生变动：\n\n{change_details}\n\n"
                        email_body += "最新完整成绩列表：\n"
                        for item in current_grades:
                            email_body += f"- {item['原始课程名']}: {item['成绩']} (学分: {item['学分']}, 类型: {item['课程类型']})\n"
                        email_body += "\n祝好！\n自动成绩通知程序"
                        send_email(email_subject, email_body)
                        save_current_grades(current_grades)  # 保存新的成绩作为下一次的对比基准
                    else:
                        print("成绩无变动，无需通知。")
                        # 即使无变动，也更新一下本地文件，确保时间戳或细微格式统一
                        save_current_grades(current_grades)
                else:
                    err_msg = "获取到成绩页面HTML，但解析成绩失败。"
                    print(err_msg)
                    send_email(f"成绩解析失败通知 - {time.strftime('%Y-%m-%d %H:%M:%S')}",
                               f"你好，\n\n脚本获取到了成绩页面的HTML，但在解析具体成绩条目时失败了。\n请检查 'final_grades_page.html' (如果已保存) 和脚本中的解析逻辑。\n\n自动通知程序",
                               RECIPIENT_EMAIL)
            else:
                err_msg = "未能获取成绩页面的HTML内容（可能在点击“成绩查询”后）。"
                print(err_msg)
                send_email(f"成绩页面获取失败通知 - {time.strftime('%Y-%m-%d %H:%M:%S')}",
                           f"你好，\n\n脚本在点击“成绩查询”后，未能成功获取到包含成绩的页面HTML。\n\n错误信息可能在控制台日志中。\n自动通知程序",
                           RECIPIENT_EMAIL)
        else:
            err_msg = "登录教务系统失败。"
            print(err_msg)
            send_email(f"登录失败通知 - {time.strftime('%Y-%m-%d %H:%M:%S')}",
                       f"你好，\n\n脚本尝试登录教务系统失败。\n请检查网络或凭据。\n\n自动通知程序",
                       RECIPIENT_EMAIL)

    except Exception as e:
        print(f"执行成绩检查过程中发生未捕获的严重错误: {e}")
        try:
            driver.save_screenshot(f'critical_error_{time.strftime("%Y%m%d-%H%M%S")}.png')
            print(f"严重错误截图已保存为: critical_error_{time.strftime('%Y%m%d-%H%M%S')}.png")
        except:
            pass
        send_email(f"脚本运行严重错误 - {time.strftime('%Y-%m-%d %H:%M:%S')}",
                   f"你好，\n\n成绩查询脚本在执行过程中遇到严重错误，已停止本次尝试。\n错误详情: {e}\n\n自动通知程序",
                   RECIPIENT_EMAIL)
    finally:
        if 'driver' in locals() and driver is not None:
            try:
                driver.quit()
                print("WebDriver已关闭。")
            except Exception as e_quit:
                print(f"关闭WebDriver时出错: {e_quit}")


# --- Main Execution Loop ---
if __name__ == '__main__':
    print("启动成绩变动通知程序...")

    # 全局常量
    LOGIN_URL = 'https://sso.cqu.edu.cn/login?service=https:%2F%2Fmy.cqu.edu.cn%2Fauthserver%2Fauthentication%2Fcas'

    # 检查是否还是示例凭据 (可选，但为了安全)
    if USERNAME_SE == '你的真实用户名' or PASSWORD_SE == '你的真实密码':
        print("警告：正在使用示例凭据。请在脚本中更新 USERNAME_SE 和 PASSWORD_SE。为防止意外，脚本将退出。")
        exit()

    attempt_count = 0
    max_initial_fast_attempts = 10
    fast_interval_seconds = 10  # 测试阶段：每10秒
    normal_interval_seconds = 5 * 60  # 正常阶段：每5分钟

    while True:
        attempt_count += 1
        print(f"\n--- 第 {attempt_count} 次尝试获取成绩 --- ({time.strftime('%Y-%m-%d %H:%M:%S')})")

        run_grade_check_and_notify()  # 执行检查和通知的核心逻辑

        print("-" * 30)
        if attempt_count < max_initial_fast_attempts:
            print(f"测试阶段：下一次尝试将在 {fast_interval_seconds} 秒后。")
            time.sleep(fast_interval_seconds)
        else:
            if attempt_count == max_initial_fast_attempts:
                print("初始测试阶段完成。切换到正常检查间隔。")
            print(f"下一次尝试将在 {normal_interval_seconds / 60:.0f} 分钟后。")
            time.sleep(normal_interval_seconds)