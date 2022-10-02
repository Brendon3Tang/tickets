import os
import time
import pickle
from time import sleep
import click
from selenium import webdriver
from selenium.webdriver.common.by import By

url = 'https://www.damai.cn/'

login_url = 'https://passport.damai.cn/login?ru=https%3A%2F%2Fwww.damai.cn%2F'

#抢票目标 (周杰伦为例)
target = 'https://detail.damai.cn/item.htm?spm=a2oeg.search_category.0.0.227928df9QWv4b&id=607865020360&clicktitle=%E5%91%A8%E6%9D%B0%E4%BC%A62020%E5%98%89%E5%B9%B4%E5%8D%8E%E4%B8%96%E7%95%8C%E5%B7%A1%E5%9B%9E%E6%BC%94%E5%94%B1%E4%BC%9A--%E6%B5%B7%E5%8F%A3%E7%AB%99'

class Concert:
    def __init__(self):
        self.status = 0         # 当前操作执行执行状态（抢票/刷新/付款）
        self.login_method = 1   # {0:模拟登陆， 1:cookie登陆}
        self.driver = webdriver.Chrome(executable_path='./chromedriver')

    def set_cookie(self):
        #登录调用设置cookie
        self.driver.get(url)
        print('###请点击登录###')
        # 未点击登陆，就会一直在主页，不会跳转
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:
            sleep(1)
        print('###已跳转到登陆页面，请扫描###')

        #登录失败
        while self.driver.title != '大麦网-全球演出赛事官方购票平台-100%正品、先付先抢、在线选座！':
            sleep(1)
        print('###扫描成功！###')
        pickle.dump(self.driver.get_cookies(), open('cookies.pkl', 'wb'))
        print('###保存成功！###')
        self.driver.get(target)

    # 假如本地有cookie.pkl,直接获取
    def get_cookie(self):
        cookies = pickle.load(open('cookies.pkl','rb'))
        for cookie in cookies:
            cookie_dict = {
                'domain': '.domain.cn', #设置域名，否则是假登陆
                'name': cookie.get('name'),
                'value': cookie.get('value')
            }
            self.driver.add_cookie(cookie_dict)
        print('###载入cookie###')

    def login(self):
        """登陆"""
        if self.login_method == 0:
            self.driver.get(login_url)
            print('###开始登陆###')
        elif self.login_method == 1:
            # 创建文件夹，文件是否存在
            if not os.path.exists('cookies.pkl'):
                self.set_cookie()
            else:
                self.driver.get(target) #跳转到抢票页面
                self.get_cookie()      #并且登陆
    
    def enter_concert(self):
        """打开浏览器"""
        print('###打开浏览器，进入网站###')
        #调用登陆
        self.login()            #登陆
        self.driver.refresh()   #刷新，selenium特性：刷新才会跳转？
        self.status = 2         #登陆成功标识
        print('###登陆成功###')

    #抢票且下单
    def choose_ticket(self):
        if self.status == 2:
            print('=' * 30)
            print('###开始选择日期以及票价###')
            while self.driver.title.find("确认订单") == -1:
                try:
                    buybutton = self.driver.find_element(By.CLASS_NAME, 'buybtn').text
                    if buybutton == '提交缺货登记':
                        self.status == 2 #没有更改操作
                        self.driver.get(target)
                    elif buybutton == '立即预定':
                        self.status = 3
                        self.driver.find_element(By.CLASS_NAME, 'buybtn').click()
                    elif buybutton == '立即购买':
                        self.driver.find_element(By.CLASS_NAME, 'buybtn').click()
                        self.status = 4
                    elif buybutton == '选座购买':
                        self.driver.find_element(By.CLASS_NAME, 'buybtn').click()
                        self.status = 5
                except:
                    print('###没有跳转到订单结算页面###')
                
                title = self.driver.title
                if title == '选座购买':
                    #选座购买
                    self.choose_seats()
                elif title == '确认订单':
                    # 确认订单
                    while True:
                        # 如果标题是确认订单
                        print('正在加载......')
                        # 如果当前购票人的信息存在，就点击
                        if self.isElementExist('copy the xpath'):
                            #执行下单操作
                            self.check_order()

    def choose_seats(self):
        """选座座位"""
        while self.driver.title == '选座购买':
            while self.isElementExist('未选座的xpath'):
                print('###迅速选座###')
            while self.isElementExist('已选座的xpath'):
                self.driver.find_element(By.XPATH, '确认订单的xpath').click()

    def check_order(self):
        """下单操作"""
        if self.status in [3,4,5]:
            print('###开始确认订单###')
            try:
                #默认选第一个购票人
                self.driver.find_element(By.XPATH, '购票人的xpath').click()
            except Exception as err:
                print('###购票人信息不存在, 自行查看元素位置')
                print(err)
            # 提交订单
            time.sleep(0.5) #休眠0.5s,影响加载，导致按钮点击无效
            self.driver.find_element(By.XPATH, '提交订单的xpath').click()

    def isElementExist(self, element):
        flag = True
        browser = self.driver
        try:
            browser.find_element(By.XPATH, element)
            return flag
        except:
            flag = False
            return flag

    def finish(self):
        """退出"""
        self.driver.quit()

if __name__ == '__main__':
    try:
        con = Concert()
        con.enter_concert() #打开浏览器
        #con.login()
        con.choose_ticket() #选座座位
    except Exception as err:
        print(e)
        con.finish() 