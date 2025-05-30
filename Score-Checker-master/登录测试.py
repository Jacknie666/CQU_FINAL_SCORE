import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- 用户配置 ---
LOGIN_URL = 'https://sso.cqu.edu.cn/login?service=https:%2F%2Fmy.cqu.edu.cn%2Fauthserver%2Fauthentication%2Fcas'  # 登录页面 URL
USERNAME_SE = '20244252'  # 替换为你的学号/账号
PASSWORD_SE = 'Lw13647638779'  # 替换为你的密码

# --- Selenium WebDriver 初始化 ---
def setup_driver():
    """初始化并返回一个 Chrome WebDriver 实例"""
    print("正在使用 webdriver-manager 设置 ChromeDriver...")
    chrome_options = webdriver.ChromeOptions()
    # 如果需要无头模式（不打开浏览器窗口），取消以下行的注释：
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu') # 在某些系统上，无头模式需要这个
    # chrome_options.add_argument('--window-size=1920,1080') # 可以设置窗口大小
    # chrome_options.add_argument('--log-level=DEBUG') # 增加日志级别以获取更多信息
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36") # 设置User-Agent

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("ChromeDriver 启动成功。")
        return driver
    except Exception as e:
        print(f"使用 webdriver-manager 初始化 WebDriver 时出错: {e}")
        print("请确保你的网络连接正常，并且 Chrome 浏览器已安装。")
        print("如果问题持续，尝试手动下载与你 Chrome 浏览器版本匹配的 ChromeDriver，")
        print("然后通过 CHROME_DRIVER_PATH = '你的驱动路径' 的方式在代码中指定路径。")
        return None

# --- 元素定位器 ---
# 根据之前的讨论，这些定位器基于 placeholder 和 class/text
# 如果页面结构变化，你可能需要更新它们
USERNAME_FIELD_LOCATOR = (By.XPATH, '//input[@placeholder="统一身份认证号/身份证件号"]')
PASSWORD_FIELD_LOCATOR = (By.XPATH, '//input[@placeholder="Please enter Password"]')
# 登录按钮定位器选项:
# 选项1: 通过 class "login-button" (如果这个class是唯一的且稳定)
LOGIN_BUTTON_LOCATOR = (By.CLASS_NAME, 'login-button')
# 选项2: 通过更具体的XPath，结合按钮内的span文本 "Log in" (注意实际文本的大小写)
# LOGIN_BUTTON_LOCATOR = (By.XPATH, "//button[.//span[normalize-space()='Log in']]")
# 选项3: 综合class和文本
# LOGIN_BUTTON_LOCATOR = (By.XPATH, "//button[contains(@class, 'login-button') and .//span[normalize-space()='Log in']]")


def login(driver, login_url, username, password):
    """执行登录操作"""
    try:
        print(f"正在打开登录页面: {login_url}")
        driver.get(login_url)

        print("等待并定位用户名输入框...")
        username_input = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(USERNAME_FIELD_LOCATOR)
        )
        print("用户名输入框已找到。正在输入用户名...")
        username_input.clear() # 清空输入框，以防有预填内容
        username_input.send_keys(username)
        print("用户名输入完成。")
        time.sleep(0.5) # 短暂等待，模拟人工输入间隔

        print("等待并定位密码输入框...")
        password_input = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(PASSWORD_FIELD_LOCATOR)
        )
        print("密码输入框已找到。正在输入密码...")
        password_input.clear()
        password_input.send_keys(password)
        print("密码输入完成。")
        time.sleep(0.5)

        print("等待并定位登录按钮...")
        # 注意：如果按钮初始是disabled，EC.element_to_be_clickable 会等待它变为可点击
        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(LOGIN_BUTTON_LOCATOR)
        )
        print("登录按钮已找到且可点击。尝试点击登录...")
        login_button.click()
        print("登录按钮已点击。")

        # --- 等待登录成功并且包含成绩的页面加载 ---
        # !!! 这是非常关键的一步，你需要根据实际情况调整判断条件 !!!
        # 常见的判断方式：
        # 1. URL 发生变化，包含某个特定的关键字
        # 2. 页面标题包含某个特定的关键字
        # 3. 页面上出现某个只有登录后才会有的特定元素 (例如你的名字、退出按钮、成绩表格的ID)
        print("等待登录成功后的页面响应...")
        WebDriverWait(driver, 40).until( # 登录后跳转或加载可能需要更长时间
            EC.url_contains("https://my.cqu.edu.cn/workspace/home")  # 假设登录后会跳转到包含 "i.cqu.edu.cn" 的URL (请根据实际情况修改!)
            # 或者: EC.title_contains("我的门户") # 假设登录后页面标题包含 "我的门户"
            # 或者: EC.presence_of_element_located((By.ID, "dashboard-username-display")) # 假设有个显示用户名的元素
            # 或者: EC.presence_of_element_located((By.XPATH, "//h1[contains(text(),'我的成绩')]")) # 假设有个H1标题是“我的成绩”
        )
        print("登录成功！当前 URL:", driver.current_url)
        return True

    except Exception as e:
        print(f"登录过程中发生错误: {e}")
        try:
            error_screenshot_path = 'login_error.png'
            driver.save_screenshot(error_screenshot_path)
            print(f"错误截图已保存为: {error_screenshot_path}")
        except Exception as screenshot_e:
            print(f"保存错误截图失败: {screenshot_e}")
        return False


def parse_grades_from_html(html_content):
    """从HTML内容中解析成绩"""
    if not html_content:
        print("没有HTML内容可供解析。")
        return

    print("\n--- 开始使用BeautifulSoup解析成绩 ---")
    soup = BeautifulSoup(html_content, 'html.parser')

    # !!! 在这里编写你实际的成绩解析逻辑 !!!
    # 你需要检查登录后页面的HTML结构 (html_content)，找到包含成绩的标签、class或id。
    # 以下为通用示例，你需要替换成针对你学校成绩页面的具体代码：

    # 示例1: 假设成绩在一个ID为'gradesTable'的表格中
    # grades_table = soup.find('table', {'id': 'gradesTable'})
    # if grades_table:
    #     print("找到了成绩表格！")
    #     rows = grades_table.find_all('tr')
    #     for i, row in enumerate(rows):
    #         if i == 0: # 跳过表头
    #             # print("表头:", [th.text.strip() for th in row.find_all('th')])
    #             continue
    #         cells = row.find_all('td')
    #         if len(cells) >= 2: # 假设至少有课程名和成绩
    #             course_name = cells[0].text.strip()
    #             grade = cells[1].text.strip()
    #             print(f"课程: {course_name}, 成绩: {grade}")
    #         else:
    #             print(f"无法解析行: {[cell.text.strip() for cell in cells]}")
    # else:
    #     print("在HTML中未找到ID为 'gradesTable' 的成绩表格。请检查HTML结构和ID。")
    #     print("或者，成绩可能不在表格中，尝试其他解析方式。")

    # 示例2: 假设每个成绩项在一个 class='course-item' 的 div 中
    # course_items = soup.find_all('div', class_='course-item')
    # if course_items:
    # for item in course_items:
    #         course_name_tag = item.find('span', class_='course-name') # 假设课程名在 class='course-name' 的 span
    #         grade_tag = item.find('span', class_='grade')         # 假设成绩在 class='grade' 的 span
    # if course_name_tag and grade_tag:
    #             print(f"课程: {course_name_tag.text.strip()}, 成绩: {grade_tag.text.strip()}")
    # else:
    # print("未找到 class 为 'course-item' 的成绩条目，或条目内结构不符。")

    print("\n（请在此处填充针对你学校成绩页面的具体解析逻辑）")
    print("你可以将获取到的 `html_content` 保存到文件再用浏览器打开分析，")
    print("例如：with open('grades_page.html', 'w', encoding='utf-8') as f: f.write(html_content)")


def main():
    """主函数"""
    if not USERNAME_SE or USERNAME_SE == '你的真实用户名' or \
       not PASSWORD_SE or PASSWORD_SE == '你的真实密码':
        print("错误：请在脚本顶部设置 USERNAME_SE 和 PASSWORD_SE 变量为你的真实凭据。")
        return

    driver = setup_driver()
    if not driver:
        return

    try:
        if login(driver, LOGIN_URL, USERNAME_SE, PASSWORD_SE):
            print("\n登录成功，准备获取页面HTML以解析成绩...")
            # 等待一下，确保所有动态内容都加载完毕（如果需要）
            time.sleep(2) # 可以根据需要调整或移除这个延时
            html_content_after_login = driver.page_source
            print("已获取登录后的页面HTML。")

            # (可选) 将HTML保存到文件，方便调试解析逻辑
            # with open('temp_grades_page.html', 'w', encoding='utf-8') as f:
            #     f.write(html_content_after_login)
            # print("登录后的HTML内容已保存到 temp_grades_page.html，可用于分析。")

            parse_grades_from_html(html_content_after_login)
        else:
            print("\n登录失败，无法获取成绩。")

    except Exception as e:
        print(f"主程序执行过程中发生未捕获的错误: {e}")
        try:
            error_screenshot_path = 'main_execution_error.png'
            driver.save_screenshot(error_screenshot_path)
            print(f"主程序错误截图已保存为: {error_screenshot_path}")
        except Exception as screenshot_e:
            print(f"保存主程序错误截图失败: {screenshot_e}")

    finally:
        if driver:
            print("\n操作完成，准备关闭浏览器...")
            time.sleep(3) # 暂停几秒以便查看最终状态 (可选)
            driver.quit()
            print("浏览器已关闭。")

if __name__ == '__main__':
    main()