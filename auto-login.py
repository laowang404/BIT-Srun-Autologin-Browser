import time
import random
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ================== 需要你修改的配置 ==================
LOGIN_URL = "http://10.0.0.55"
TEST_URL = "https://www.baidu.com"

USERNAME = ""
PASSWORD = ""

CHECK_INTERVAL = 60  # 每隔多少秒检查一次外网

# chromedriver 的绝对路径
CHROME_DRIVER_PATH = ".\\chromedriver-win64\\chromedriver.exe"
# =====================================================

# ======== 页面元素定位（来自 to-login.html / already-login.html）========
USERNAME_LOCATOR = (By.ID, "username")
PASSWORD_LOCATOR = (By.ID, "password")
REMEMBER_LOCATOR = (By.ID, "remember")
LOGIN_BUTTON_LOCATOR = (By.ID, "login")
LOGOUT_BUTTON_LOCATOR = (By.ID, "logout")
# =====================================================


def has_internet(timeout=5):
    # return False
    """访问 TEST_URL 判断是否有外网"""
    try:
        resp = requests.get(TEST_URL, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


def create_driver():
    """创建 Chrome 实例"""
    chrome_options = Options()
    # 如需无头模式可打开
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def human_type(element, text, min_delay=0.05, max_delay=0.2):
    """模拟人类逐字输入"""
    element.clear()
    for ch in text:
        element.send_keys(ch)
        time.sleep(random.uniform(min_delay, max_delay))


def do_login_form(driver, wait=None):
    """
    在“未登录”页面上执行实际的登录动作：
    - 输入账号密码
    - 勾选“记住密码”（可选）
    - 点击“登录”
    """
    if wait is None:
        wait = WebDriverWait(driver, 15)

    # 等待账号/密码输入框就绪
    user_elem = wait.until(EC.presence_of_element_located(USERNAME_LOCATOR))
    pass_elem = wait.until(EC.presence_of_element_located(PASSWORD_LOCATOR))

    time.sleep(random.uniform(0.5, 1.5))

    # 逐字输入
    human_type(user_elem, USERNAME)
    time.sleep(random.uniform(0.5, 1.0))
    human_type(pass_elem, PASSWORD)

    # 勾选“记住密码”（如果不需要可以直接删掉这一段）
    try:
        remember_elem = driver.find_element(*REMEMBER_LOCATOR)
        if not remember_elem.is_selected():
            remember_elem.click()
    except Exception:
        pass

    time.sleep(random.uniform(0.5, 1.0))

    # 点击登录按钮
    login_btn = wait.until(EC.element_to_be_clickable(LOGIN_BUTTON_LOCATOR))
    login_btn.click()
    print("[INFO] 已点击登录按钮，等待认证生效...")
    time.sleep(5)


def login_once():
    """
    执行一次登录流程：
    1. 打开 LOGIN_URL
    2. 判断当前是“已登录页”还是“未登录页”
    3. 已登录 → 先点击注销，再走登录表单
       未登录 → 直接走登录表单
    """
    print("[INFO] 开始尝试登录校园网...")
    driver = create_driver()

    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 15)

        # === 关键：等待 login 或 logout 任意一个元素出现 ===
        try:
            # selenium 4 有 EC.any_of，如果你的版本较老报 AttributeError，
            # 可以用下面的 while 循环替代。
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located(LOGIN_BUTTON_LOCATOR),
                    EC.presence_of_element_located(LOGOUT_BUTTON_LOCATOR),
                )
            )
        except AttributeError:
            # 兼容没有 any_of 的老版本 selenium
            for _ in range(30):  # 最多等 15 秒
                if driver.find_elements(*LOGIN_BUTTON_LOCATOR) or \
                   driver.find_elements(*LOGOUT_BUTTON_LOCATOR):
                    break
                time.sleep(0.5)

        # === 判断当前是哪种页面 ===
        if driver.find_elements(*LOGOUT_BUTTON_LOCATOR):
            # 已登录页面：有“注销”按钮
            print("[INFO] 检测到当前是已登录页面，先执行注销...")
            try:
                logout_btn = wait.until(
                    EC.element_to_be_clickable(LOGOUT_BUTTON_LOCATOR)
                )
                logout_btn.click()
                print("[INFO] 已点击注销按钮，等待跳转回登录页...")
            except Exception as e:
                print("[WARN] 点击注销按钮时出错：", e)

            # 等待回到登录页（出现 login 按钮/账号密码输入框）
            wait.until(EC.presence_of_element_located(LOGIN_BUTTON_LOCATOR))

        else:
            # 未登录页面：直接走登录流程
            print("[INFO] 检测到当前是未登录页面，直接登录...")

        # 到这里时，一定已经在“未登录页面”上，统一调用登录表单逻辑
        do_login_form(driver, wait)

    except Exception as e:
        print("[ERROR] 登录过程出现异常：", e)

    finally:
        try:
            driver.quit()
        except Exception:
            pass
        print("[INFO] 本次登录流程结束，已关闭浏览器。")


def main_loop():
    print("[INFO] 自动校园网脚本已启动，定期检查网络并自动登录。")
    while True:
        if has_internet():
            print(f"[OK] 当前有外网，{CHECK_INTERVAL} 秒后再次检查。")
        else:
            print("[WARN] 检测到无外网，开始执行登录流程...")
            login_once()

            # 登录后再检查一次
            time.sleep(5)
            if has_internet():
                print("[OK] 登录成功，网络恢复。")
            else:
                print("[WARN] 登录后仍无外网，可能是校园网故障或页面改版。")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main_loop()
