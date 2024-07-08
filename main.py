import config
import core
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os

def input_int() -> int:
    while True:
        try:
            user_input = int(input("请输入一个整数: "))
            return user_input
        except ValueError:
            print("错误: 请输入一个有效的整数。")


if __name__ == "__main__":

    browse : core.Browse

    print("=======================================")
    print("欢迎使用论文批量下载器 PaperDownloader！\n程序开始运行后，将会自动跳转到知网。请不要操作下载文件夹。")
    print(f"当前版本: {config.VERSION}")
    print("=======================================")

    # 选择浏览器
    ###
    '''
    print("请选择使用的浏览器:")
    print(f"1: {config.ChromeName}")
    print(f"2: {config.EdgeName}")
    print("")
    user_input = input_int()
    match user_input:
        case 1:
            print("使用浏览器: Google Chrome")
            browse = core.Chrome()
        case 2:
            print("使用浏览器: Microsoft Edge")
            browse = core.Edge()
    '''
    browse = core.Edge()
    # 检查 webdriver
    print("=======================================")
    print("查找可执行文件......", end="")
    browse.check_exe_path()
    print("=======================================")
    print("查找 WebDriver......", end="", flush=True)
    browse.check_driver()
    print("=======================================")
    print("即将打开浏览器......")
    browse.open()
    f=open("namelist.txt",encoding="utf-8")
    s=f.readline()
    names=s.split(',')
    for name in names:
        # try:
            if os.path.exists(os.path.join("data",name)):
                print(name,"的文章已经收集，跳过")
                continue
            browse.driver().get("https://kns.cnki.net/kns8s/AdvSearch?classid=WD0FTY92")
            driver=browse.driver()
            WebDriverWait(driver, int(config.WaitTime)).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="ModuleSearch"]/div[1]/div/div[2]/ul/li[3]'))
            )
            search_option = driver.find_element(By.XPATH, '//*[@id="ModuleSearch"]/div[1]/div/div[2]/ul/li[3]')
            search_option.click()
            WebDriverWait(driver, int(config.WaitTime)).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="autxt"]/dd[1]/div[2]/input'))
            )
            autor_name=driver.find_element(By.XPATH, '//*[@id="autxt"]/dd[1]/div[2]/input')
            autor_name.clear()
            autor_name.send_keys(name)
            autor_university=driver.find_element(By.XPATH, '//*[@id="autxt"]/dd[2]/div[2]/input')
            autor_university.clear()
            autor_university.send_keys("复旦大学")
            autor_university.send_keys(Keys.RETURN)
            # time.sleep(3) 
            # download_count=core.download(browse.driver(), browse.name,name)
            # if download_count is None:
            #     download_count=0
            print(name,"的文章已经全部收集")
            # time.sleep(download_count*10)
        # except:
        #     print("没有找到复旦大学",name)
        #     downloads_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        #     papers_dir = os.path.join("data",os.path.join(name,'papers'))
        #     s="move "+downloads_path+"\\* "+papers_dir
        #     os.system(s)