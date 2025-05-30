# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
#
# # 设置无头模式（可选）
# chrome_options = Options()
# # chrome_options.add_argument("--headless")  # 如果你想在后台运行可以取消注释
#
# # 使用 webdriver-manager 自动下载匹配的 chromedriver
# service = Service(ChromeDriverManager().install())
#
# # 启动浏览器
# driver = webdriver.Chrome(service=service, options=chrome_options)
#
# # 示例：打开一个网页
# driver.get("https://www.google.com")
# print(driver.title)
#
# # 关闭浏览器
# driver.quit()
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 获取并打印 chromedriver 路径
driver_path = ChromeDriverManager().install()
print("ChromeDriver 路径为：", driver_path)

# 设置浏览器选项
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 可选：无头模式

# 启动浏览器
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 示例：打开网页
driver.get("https://www.google.com")
print("当前页面标题:", driver.title)

# 关闭浏览器
driver.quit()