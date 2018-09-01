# 使用selenium+chromedriver实现12306抢票

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class GrabVotesSpider:
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path='D:\chromedriver\chromedriver.exe')
        self.login_url = 'https://kyfw.12306.cn/otn/login/init'  # 登录界面url
        self.initmy_url = 'https://kyfw.12306.cn/otn/index/initMy12306'  # 个人中心页面url
        self.search_url = 'https://kyfw.12306.cn/otn/leftTicket/init'  # 车票预订界面url
        self.passenger_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'  # 提交订单页面url

    # 先登录12306
    def _login(self):
        self.driver.get(self.login_url)  # 打开登录界面

        # 然后手动登录，现在只要监测driver是否跳转到个人中心页面
        # 显示等待用户手动输入用户名密码完成
        WebDriverWait(self.driver, 1000).until(
            EC.url_to_be(self.initmy_url)  # 当前url是否等于initmy_url，说明登录成功
        )
        print("登录成功！")  # 登录成功后跳转到车票预订界面

    # 开始订票
    def _order_ticket(self):
        self.driver.get(self.search_url)  # 跳转到车票预订的界面

        # 然后手动输入出发地、目的地、出发日，监测是否将这些数据输入，输入之后点击查询按钮
        # 等待用户在页面手动输入出发地和程序中输入的出发地是否相同
        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, 'fromStationText'), self.from_station)
        )

        # 等待用户在页面手动输入目的地和程序中输入的目的地是否相同
        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, 'toStationText'), self.to_station)
        )

        # 等待用户在页面手动输入出发日和程序中输入的出发日是否相同
        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, 'train_date'), self.depart_time)
        )

        # 等待查询按钮是否可用
        WebDriverWait(self.driver, 1000).until(
            EC.element_to_be_clickable((By.ID, 'query_ticket'))
        )
        # 如果查询按钮能够被点击，找到查询按钮执行点击查询事件
        searchBtn = self.driver.find_element_by_id('query_ticket')
        searchBtn.click()

        # 等待在点击查询按钮之后车次是否显示出来了
        WebDriverWait(self.driver, 1000).until(
            EC.presence_of_element_located((By.XPATH, './/tbody[@id="queryLeftTable"]/tr'))
        )

        # 车次出现之后，获取车次信息
        # 找到所有tr标签没有datatran属性的，也就是找到包含车次信息的tr标签
        tr_list = self.driver.find_elements_by_xpath('.//tbody[@id="queryLeftTable"]/tr[not(@datatran)]')
        for tr in tr_list:
            train_number = tr.find_element_by_class_name('number').text  # 车次名
            if train_number in self.trains:  # 是否和程序中输入的一致
                left_ticket = tr.find_element_by_xpath('.//td[10]').text  # 硬座票
                if left_ticket == '有' or left_ticket.isdigit:  # 硬座信息文本是否是有或者是数字
                    # 然后就可以点击预订按钮
                    orderBtn = tr.find_element_by_class_name('btn72')  # 找到点击按钮
                    orderBtn.click()

                    # 等待是否来到了提交订单的页面
                    WebDriverWait(self.driver, 1000).until(
                        EC.url_to_be(self.passenger_url)
                    )

                    # 等待所有的乘客信息是否被加载进来了
                    WebDriverWait(self.driver, 1000).until(
                        EC.presence_of_element_located((By.XPATH, './/ul[@id="normal_passenger_id"]/li'))
                    )

                    # 获取所有的乘客信息
                    passenger_labels = self.driver.find_elements_by_xpath('.//ul[@id="normal_passenger_id"]/li/label')
                    for passenger_label in passenger_labels:
                        name = passenger_label.text  # 获取名字
                        if name in self.passengers:  # 姓名是否在之前程序输入姓名列表中
                            passenger_label.click()  # 浏览器中选中姓名

                    # 获取提交订单按钮，点击提交订单
                    submitBtn = self.driver.find_element_by_id('submitOrder_id')
                    submitBtn.click()

                    # 等待核对信息的对话框弹出
                    WebDriverWait(self.driver, 1000).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'dhtmlx_wins_body_outer'))
                    )
                    # 等待该对话框中的确认按钮是否出现
                    WebDriverWait(self.driver, 1000).until(
                        EC.presence_of_element_located((By.ID, 'qr_submit_id'))
                    )
                    try:
                        # 执行点击操作
                        confirmBtn = self.driver.find_element_by_id('qr_submit_id')
                        confirmBtn.click()
                        while confirmBtn:  # 一直点击
                            confirmBtn.click()
                            confirmBtn = self.driver.find_element_by_id('qr_submit_id')
                    except:
                        print('抢票成功')

    # 程序中输入操作
    def wait_input(self):
        self.from_station = input('出发地：')
        self.to_station = input('目的地：')
        self.depart_time = input('出发日：')  # 时间格式必须是：yyyy-mm-dd
        self.passengers = input('乘客姓名（如有多个乘客请用英文逗号隔开）：').split(',')
        self.trains = input('车次（如果多个车次请用英文逗号隔开）:').split(',')

    # 程序开始执行
    def run(self):
        # 1、现在程序中输入购票信息
        self.wait_input()

        # 2、登录
        self._login()

        # 3、抢票
        self._order_ticket()


if __name__ == '__main__':
    spider = GrabVotesSpider()
    spider.run()
