import datetime
import os
import shutil
import sys
import time
import subprocess
import config
import driver_helper
import webpage_info
import save_info
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions

# Global Variables
check_count = 0
download_count = 0


class Browse:
    def __init__(self):
        self.name = None
        self.exe_path = None
        self.debug_port = None
        self.driver_path = None
        self.user_data_path = None

    def open(self):
        if not os.path.exists(self.user_data_path):
            os.makedirs(self.user_data_path)
        # require new user-data-dir
        subprocess.Popen(
            [
                self.exe_path,
                f"--remote-debugging-port={self.debug_port}",
                f"--user-data-dir={self.user_data_path}",
            ]
        )

    def check_exe_path(self):
        if os.path.exists(self.exe_path):
            print("成功")
        else:
            print("失败")
            print("请检查路径：", self.exe_path)
            sys.exit("查找可执行文件失败")

    def check_driver(self):
        if os.path.exists(self.driver_path):
            print("成功")
        else:
            print("失败\n尝试自动下载 WebDriver...", end="")
            driver_helper.get_driver(self.name)
            print("成功")

    def driver(self) -> webdriver:
        pass


class Chrome(Browse):
    def __init__(self):
        self.name = config.ChromeName
        self.exe_path = config.ChromePath
        self.debug_port = config.ChromeDebugPort
        self.driver_path = config.ChromeDriverName
        self.user_data_path = config.ChromeUserDataPath

    def driver(self) -> webdriver:
        ChromeOptions = webdriver.ChromeOptions()
        ChromeOptions.add_experimental_option(
            "debuggerAddress", f"127.0.0.1:{self.debug_port}"
        )
        service = webdriver.ChromeService(executable_path=self.driver_path)
        driver = webdriver.Chrome(options=ChromeOptions, service=service)
        return driver


# https://learn.microsoft.com/en-us/microsoft-edge/devtools-protocol-chromium/
class Edge(Browse):
    def __init__(self):
        self.name = config.EdgeName
        self.exe_path = config.EdgePath
        self.debug_port = config.EdgeDebugPort
        self.driver_path = config.EdgeDriverName
        self.user_data_path = config.EdgeUserDataPath

    def driver(self) -> webdriver:
        EdgeOptions = webdriver.EdgeOptions()
        EdgeOptions.add_experimental_option(
            "debuggerAddress", f"127.0.0.1:{self.debug_port}"
        )
        service = webdriver.EdgeService(executable_path=self.driver_path)
        driver = webdriver.Edge(options=EdgeOptions, service=service)
        return driver


def download(driver: webdriver, browse_name: str,author_name:str=""):
    global download_count, check_count
    download_count = 0
    check_count = 0
    papers_dir = os.path.join(author_name,'papers')
    save = save_info.TXTInfo(folder=os.path.join(author_name,'information'))
    if not os.path.exists(papers_dir):
        os.makedirs(papers_dir)
    if driver is None:
        return
    else:
        start_time = datetime.datetime.now()
        print("正在接管浏览器控制，请不要操作。", flush=True)
        # Find serach window
        all_handles = driver.window_handles
        hit = False
        for handle in all_handles:
            driver.switch_to.window(handle)
            if driver.title == "检索-中国知网" or driver.title == "高级检索-中国知网":
                cnki(driver, browse_name, save)
                hit = True
            elif driver.title == "万方数据知识服务平台":
                # Ensure we are now in search window
                try:
                    driver.find_element(By.CLASS_NAME, "normal-list")
                except exceptions.NoSuchElementException:
                    continue
                else:
                    wanfang(driver)
                    hit = True
        downloads_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        for filename in os.listdir(downloads_path):
            file_path = os.path.join(downloads_path, filename)
            if filename.endswith('.pdf') and datetime.datetime.fromtimestamp(os.path.getctime(file_path)) > start_time:
                shutil.move(file_path, papers_dir)
        if hit:
            # fmt: off
            print(f"下载完成, 共找到 {check_count} 处下载任务, 成功下载 {download_count} 项内容。")
            # print(f"文件保存位置: {os.path.join(os.environ['USERPROFILE'], 'Downloads')}")
            print(f"文件保存位置: {papers_dir}")
            # fmt: on
        else:
            print("错误：没有找到符合的检索页面\n")

def cnki(driver: webdriver, browse_name: str, save: save_info):
    global download_count, check_count
    print("检测到知网检索页面, 开始下载......")
    index_window = driver.current_window_handle
    result = driver.find_element(By.CLASS_NAME, "result-table-list").find_element(
        By.TAG_NAME, "tbody"
    )
    rows = result.find_elements(By.TAG_NAME, "tr")
    # print(f"rows = {rows}")
    for i in range(len(rows)):
        # Determine if selected
        # if not rows[i].find_element(By.CLASS_NAME, "cbItem").is_selected():
        #     continue
        # else:
        print("正在下载第", i + 1, "项……")
        check_count += 1
        current_window_number = len(driver.window_handles)
        rows[i].find_element(By.CLASS_NAME, "fz14").click()
        WebDriverWait(driver, int(config.WaitTime)).until(
            EC.number_of_windows_to_be(current_window_number + 1)
        )
        # Switch to new window
        driver.switch_to.window(driver.window_handles[-1])
        try:
            WebDriverWait(driver, int(config.WaitTime)).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "abstract-text"))
            )
        except:
            print("错误：摘要加载超时，或者没有摘要。\n")
        try:
            WebDriverWait(driver, int(config.WaitTime)).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "keywords"))
            )
        except:
            print("错误：关键词加载超时，或者没有关键词。\n")
        try:
            save.update_entry(*webpage_info.extract_info(driver))
            # Wait for the page to finish loading
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            wait = WebDriverWait(driver, 10)
            download_button = wait.until(EC.element_to_be_clickable((By.ID, 'pdfDown')))
            driver.execute_script("window.scrollBy(0, 250);")
            time.sleep(1)
            # download_button = driver.find_element(By.ID, "pdfDown")
        except exceptions.NoSuchElementException:
            name = rows[i].find_element(By.CLASS, "wx-tit").text
            print(f"错误：不能下载 {name}\n。")
            continue
        finally:
            current_window_number = len(driver.window_handles)
            download_button.click()
            # edge 的 webdriver 有问题，页面关闭后数量不减
            if browse_name == config.EdgeName:
                time.sleep(int(config.Interval))
                driver.close()
                driver.switch_to.window(index_window)
                download_count += 1
            else:
                try:
                    WebDriverWait(driver, int(config.WaitTime)).until(
                        EC.number_of_windows_to_be(current_window_number)
                    )
                except exceptions.TimeoutException:
                    print("错误：账号未登录或响应超时，下载中断。\n")
                    return
                else:
                    driver.close()
                    # Switch back to index
                    driver.switch_to.window(index_window)
                    download_count += 1
                    time.sleep(int(config.Interval))
    # 处理完当前页后，查找并点击“下一页”按钮
    try:
        # 查找包含“下一页”文本的<a>标签
        next_page_link = driver.find_element(By.XPATH, "//a[contains(text(), '下一页')]")
        if next_page_link:
            # 点击“下一页”按钮
            next_page_link.click()
            time.sleep(int(config.Interval))
            # 等待页面加载
            WebDriverWait(driver, int(config.WaitTime)).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result-table-list"))
            )
            # 递归调用cnki函数处理新页面的内容
            all_handles = driver.window_handles
            for handle in all_handles:
                driver.switch_to.window(handle)
                if driver.title == "检索-中国知网" or driver.title == "高级检索-中国知网":
                    cnki(driver, browse_name, save)
    except exceptions.NoSuchElementException:
        print("已经是最后一页。")
    except exceptions.TimeoutException:
        print("错误：响应超时，无法加载下一页。\n")


def wanfang(driver: webdriver):
    global download_count, check_count
    print("检测到万方检索页面, 开始下载......")
    index_window = driver.current_window_handle
    rows = driver.find_elements(By.CLASS_NAME, "normal-list")
    for i in range(len(rows)):
        # Determine if selected
        if not rows[i].find_element(By.CLASS_NAME, "ivu-checkbox-input").is_selected():
            continue
        else:
            check_count += 1
            current_window_number = len(driver.window_handles)
            try:
                download_button = rows[i].find_element(
                    By.CSS_SELECTOR,
                    f"div:nth-child({str(i + 1)}) > .normal-list .t-DIB:nth-child(2) span",
                )
            except exceptions.NoSuchElementException:
                name = rows[i].find_element(By.CLASS_NAME, "title").text
                print(f"错误：不能下载 {name}。\n")
                continue
            else:
                download_button.click()
                # Switch to new window
                WebDriverWait(driver, int(config.WaitTime)).until(
                    EC.number_of_windows_to_be(current_window_number + 1)
                )
                driver.switch_to.window(driver.window_handles[-1])
                if driver.title == "万方登录":
                    print("错误：账号未登录或响应超时，下载中断。\n")
                    return
                else:
                    time.sleep(int(config.Interval))
                    driver.close()
                    # Switch back to index
                    driver.switch_to.window(index_window)
                    download_count += 1
