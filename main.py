import config
import core
import time

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
    print("即将打开浏览器......",end="")
    for t in range(3, 0, -1):
        print(t, end="", flush=True)
        time.sleep(1)
    print()
    browse.open()
    browse.driver().get("https://www.cnki.net/")
    print("=======================================")
    input(
        "请登录数据库网站进行内容检索，完成后输入回车键开始下载。脚本将自动下载当前页的所有搜索结果，并前往下一页继续下载。"
    )
    print("=======================================")
    core.download(browse.driver(), browse.name)
    print("=======================================")
    print("程序结束", flush=True)
