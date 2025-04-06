# @Author  : 木森
# @weixin: python771
import re
# 用于连接到已经打开的Chrome浏览器
import asyncio
# 正则库，用于匹配字符串
import re
import logging
from faker import Faker
from playwright.async_api import Playwright

from logging.handlers import RotatingFileHandler  # 添加这行导入
fc = Faker('zh_CN')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        RotatingFileHandler('d:\\PWInput\\app.log', maxBytes=10*1024*1024, backupCount=5)  # 日志文件输出
    ]
)
logger = logging.getLogger(__name__)


class BasePage:

    def __init__(self, pw: Playwright, users: dict):
        self.pw = pw
        self.users = users

    async def open_page_login(self, page):
        """登录操作"""
        logger.debug(f'账号{self.users.get("id")}正在打开登录页面')
        await page.goto('http://113.44.142.29:8069/')
        logger.debug(f'账号{self.users.get("id")}正在输入用户名')
        await page.fill('//input[@placeholder="账号"]', self.users.get('username'))
        logger.debug(f'账号{self.users.get("id")}正在输入密码')
        await page.fill('//input[@placeholder="密码"]', self.users.get('password'))
        await page.wait_for_timeout(500)
        logger.debug(f'账号{self.users.get("id")}正在点击登录按钮')
        # 等待元素可点击
        await page.click('//button//span[text()="登 录"]')
        await page.wait_for_timeout(500)
        logger.debug(f'账号{self.users.get("id")}登录成功')


class NursePage(BasePage):
    """护士的操作逻辑"""

    async def wait_for_clickable(self, locator):
        await locator.wait_for(state='visible')
        while not await locator.is_enabled():
            await asyncio.sleep(0.1)

    async def nurse_main(self):
        # # 获取当前的浏览器上下文和页面
        """护士操作"""
        browser = await self.pw.chromium.launch(headless=False)
        # browser = await self.pw.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        try:
            # 进行登录
            await self.open_page_login(page)
            logger.debug(f'账号{self.users.get("id")}正在点击登记台')
            await page.click('//li//span[text()="登记台"]')
            logger.debug(f'账号{self.users.get("id")}正在点击个检登记')
            await page.click('//span[text()="个检登记"]')
            await page.wait_for_timeout(1000)
            logger.debug(f'账号{self.users.get("id")}正在开始登记')
        except Exception as e:
            logger.error(f'账号{self.users.get("id")}登录失败,原因:{e}')
            await self.nurse_main()
        # 进行循环1000次登记
        for i in range(1, 10000):
            logger.info(f'******【开始】*****:账号{self.users.get("id")}正在第{i}次登记')
            # 登记数据
            await self.registration_data(page, i)

    async def click_add(self, page):
        """点击新增"""
        # 点击新增按钮
        logger.debug(f'账号{self.users.get("id")}正在点击新增按钮')
        await page.click('//button/span[text()="新增"]')
        await page.wait_for_timeout(1000)

    async def input_data(self, page):
        """输入数据"""
        # 输入姓名称
        logger.debug(f'账号{self.users.get("id")}正在输入姓名')
        await page.get_by_role("textbox", name="* 人员姓名").click()
        # 使用faker生成姓名
        name = fc.name()
        await page.get_by_role("textbox", name="* 人员姓名").fill(name)
        logger.debug(f'账号{self.users.get("id")}输入的姓名是: {name}')
        logger.debug(f'账号{self.users.get("id")}正在输入证件号码')
        await page.get_by_role("textbox", name="* 证件号码").click()
        # 使用faker生成身份证号码
        ssn = fc.ssn()
        await page.get_by_role("textbox", name="* 证件号码").fill(ssn)
        logger.debug(f'账号{self.users.get("id")}输入的证件号码是: {ssn}')
        await page.wait_for_timeout(1000)
        logger.debug(f'账号{self.users.get("id")}正在输入联系电话')
        # 使用faker生成联系电话
        phone_number = fc.phone_number()
        await page.get_by_role("textbox", name="* 联系电话").fill(phone_number)
        logger.debug(f'账号{self.users.get("id")}输入的联系电话是: {phone_number}')
        # 使用faker生成住址
        logger.debug(f'账号{self.users.get("id")}正在输入住址')
        address = fc.address().replace("\n", " ")
        await page.get_by_role("textbox", name="住址").fill(address)
        logger.debug(f'账号{self.users.get("id")}输入的住址是: {address}')
        logger.debug(f'账号{self.users.get("id")}正在选择时段')
        await page.get_by_role("textbox", name="* 时段").click()
        await page.get_by_text("07:00-23:59").click()

    async def search_and_save(self, page):
        """搜索并保存"""
        logger.debug(f'账号{self.users.get("id")}正在输入搜索内容')
        await page.get_by_role("textbox", name="请输入").fill("该套餐下有多个导检科室的项目")
        logger.debug(f'账号{self.users.get("id")}正在点击搜索按钮')
        await page.get_by_role("button", name="搜索").click()
        # 等待按钮可点击
        logger.debug(f'账号{self.users.get("id")}正在等待保存按钮可点击')
        await page.wait_for_selector('//div[text()="该套餐下有多个导检科室的项目"]/../../child::*[6]/div/button',
                                     state='visible')
        logger.debug(f'账号{self.users.get("id")}正在点击保存按钮')
        await page.get_by_role("row", name="该套餐下有多个导检科室的项目").get_by_role("button").click()
        await page.wait_for_timeout(1000)
        logger.debug(f'账号{self.users.get("id")}正在点击确认保存按钮')
        await page.get_by_role("button", name="保存").click()
        await page.wait_for_timeout(1000)

    async def charge(self, page):
        """收费"""
        logger.debug(f'账号{self.users.get("id")}正在点击收费按钮')
        await page.get_by_role("button", name="收费").click()
        await page.wait_for_timeout(1000)
        logger.debug(f'账号{self.users.get("id")}正在点击确认收费按钮')
        await page.get_by_role("button", name="确认").click()
        await page.wait_for_timeout(1000)
        # TODO:点击确认收费按钮，会偶尔出现页面状态不更新的情况，需要刷新页面
        await page.reload()
        await page.wait_for_timeout(1000)

    async def print_guide_sheet(self, page):
        """打印指引单"""
        logger.debug(f'账号{self.users.get("id")}正在点击打印指引单按钮')
        await page.get_by_role("button", name="打印指引单").click()
        await self.wait_for_clickable(page.get_by_role("button", name="打印", exact=True))
        button = page.get_by_role("button", name="打印", exact=True)
        if await button.is_visible():
            logger.debug(f'账号{self.users.get("id")}正在点击打印按钮')
            await button.click()

    async def registration_data(self, page, i):
        """护士填写登记数据"""
        try:
            await self.click_add(page)
            await self.input_data(page)
            await self.search_and_save(page)
            await self.charge(page)
            await self.print_guide_sheet(page)
        except Exception as e:
            logger.error(f'***【失败】***：账号{self.users.get("id")}第{i}次登记失败,准备对本次登记进行重试')
            # 切换到个人检登记
            logger.debug(f'账号{self.users.get("id")}切换到个人检登记，')
            await page.click('//span[text()="个检登记"]')
            # 失败重试，递归调用进行再次登记
            await self.registration_data(page, i)
        else:
            logger.info(f'***【成功】***：账号{self.users.get("id")}第{i}次登记成功')


class SortingPage(BasePage):
    """
    分检的操作逻辑
    """

    async def sorting_main(self):
        # 获取当前的浏览器上下文和页面
        browser = await self.pw.firefox.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 1、打开登录页面进行登录
        await self.open_page_login(page)
        # 2、打开分检页面
        await self.open_sorting_page(page)
        # 3、为分检医生选择科室
        await self.choose_room(page)
        await page.wait_for_timeout(1000)
        # 3、进行批量分检操作
        await self.sorting_handle(page)

    async def sorting_handle(self, page):
        """分检医生操作"""
        while True:

            # 1、点击选择科室
            await self.click_room_button(page)
            i = 0
            while True:
                # 2、判断页面呼叫按钮是否可用(有患者的情况下是可用的)
                disabled = await page.get_by_label("医生叫号工作台").get_by_role("button", name=re.compile(
                    r'^(呼叫|重呼)$')).is_disabled()
                if not disabled:
                    i = 0
                    # 3、进行呼叫、就诊操作
                    await self.visit_handle(page)
                    await page.wait_for_timeout(1000)
                elif i >= 10:
                    logger.error(f'账号{self.users.get("id")}连续10秒无数据,刷新页面重新加载当前科室患者数据')
                    await page.reload()
                    # 刷新后，重新选择科室
                    max_retries = 3
                    retry_count = 0
                    while retry_count < max_retries:
                        try:
                            await page.get_by_placeholder("请选择子科室").click()
                            await page.get_by_role("listitem").click()
                            break
                        except Exception as e:
                            logger.error(f'账号{self.users.get("id")}点击子科室失败，原因:{e}')
                            retry_count += 1
                            # 等待1秒后重试
                            await page.wait_for_timeout(1000)
                    else:
                        logger.error(f'账号{self.users.get("id")}点击子科室失败，重试次数已达上限')        
                    await page.wait_for_timeout(1000)
                    break
                else:
                    logger.debug(f'账号{self.users.get("id")}当前科室暂无排队患者，正在等待1秒')
                    i += 1
                    await page.wait_for_timeout(1000)

    async def open_sorting_page(self, page):
        """打开分检页面"""
        logger.debug(f'账号{self.users.get("id")}正在点击科室分检')
        await page.click('//li//span[text()="科室分检"]')

    
    async def choose_room(self, page):
        """前置操作-为分检医生选择科室"""
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                await page.get_by_placeholder("请选择子科室").click()
                await page.get_by_role("listitem").click()
                break
            except Exception as e:
                logger.error(f'账号{self.users.get("id")}点击子科室失败，原因:{e}')
                retry_count += 1
                # 等待1秒后重试
                await page.wait_for_timeout(1000)
        else:
            logger.error(f'账号{self.users.get("id")}点击子科室失败，重试次数已达上限')        
        await page.wait_for_timeout(1000)    

    async def click_room_button(self, page):
        """工作台窗口-点击选择科室"""
        while True:
            try:
                # 1、点击电脑状图标叫出登记台
                logger.debug(f'账号{self.users.get("id")}正在点击电脑状图标')
                await page.click('(//div[@class="el-badge item"]/button[@class="el-button el-button--default"])')
                # 2、点击科室名称按钮
                room = self.users.get("room")
                await page.wait_for_timeout(1000)
                logger.debug(f'账号{self.users.get("id")}正在点击科室名称按钮')

                # 3、点击选择科室
                # 判断科室名称按钮是否可见
                room_button = await page.get_by_role("button", name="选择科室").is_visible()
                if room_button:
                    await page.get_by_role("button", name="选择科室").click()
                    logger.debug(f'账号{self.users.get("id")}正在等待科室选项可点击')
                else:
                    try_count = 0
                    max_tries = 3  # 最大重试次数
                    while try_count < max_tries:
                        try:
                            await page.locator('//div[@class="el-dropdown"]').wait_for(state='visible')
                            await page.locator('//div[@class="el-dropdown"]').click()
                            break  # 成功等待到元素可见，退出循环
                        except Exception as e:
                            logger.error(f'账号{self.users.get("id")}点击选择科室（已存在科室名称）失败，原因：{e}')
                            try_count += 1  # 增加重试次数
                            await page.wait_for_timeout(1000)  # 等待1秒后重试
                    else:
                        logger.error(f'账号{self.users.get("id")}点击选择科室（已存在科室名称）失败，达到最大重试次数')
                    # await page.locator('//div[@class="el-dropdown"]').click()
                # 4、选择科室
                await page.get_by_role("menuitem", name=room).wait_for(state='visible')
                logger.debug(f'账号{self.users.get("id")}正在点击科室选项')
                await page.get_by_role("menuitem", name=room).click()
            except Exception as e:
                logger.error(f'***【失败】***：账号{self.users.get("id")}点击选择科室失败，原因：{e}')
                # 刷新页面
                await page.reload()
                # 重新为分检医生选择科室
                await self.choose_room(page)
            else:
                break

    async def get_row(self, page):
        """获取就诊人所在行"""
        # 获取就诊人名字
        name_string = await page.locator('//span[@class="cp-btnList-info-name"]').inner_text()
        name = name_string.split('：')[1]
        logger.debug(f'账号{self.users.get("id")}获取就诊人名字:{name}', )
        # 判断就诊人名字是否在表格中
        datas = await page.locator('//div[@class="el-scrollbar"]//tr').all_inner_texts()
        for i, data in enumerate(datas):
            if name in data:
                logger.debug(f'账号{self.users.get("id")}获取就诊人所在行:{i + 1}', )
                return i + 1

    async def visit_handle(self, page):
        """呼叫、就诊操作"""
        try:
            # 1、点击呼叫
            logger.debug(f'账号{self.users.get("id")}正在点击医生叫号工作台呼叫按钮')
            await page.get_by_label("医生叫号工作台").get_by_role("button", name=re.compile(r'^(呼叫|重呼)$')).click()
            # 2、获取就诊人所在行，并进行点击
            index = await self.get_row(page)
            if index:
                logger.debug(f'账号{self.users.get("id")}正在点击就诊')
                xpath = f'//tr[{index}]//span[text()="就诊"]'
                try:
                    await page.locator(xpath).click()
                except Exception as e:
                    logger.error(f'账号{self.users.get("id")}点击就诊失败，原因：{e}')
                    logger.debug(f'账号{self.users.get("id")}正在点击呼叫按钮')
                    # 点击呼叫或重呼按钮
                    await page.get_by_label("医生叫号工作台").get_by_role("button", name=re.compile(r'^(呼叫|重呼)$')).click()

                    # 点击就诊完成按钮
                    logger.debug(f'账号{self.users.get("id")}正在点击就诊完成按钮')
                    max_retries = 3  # 最大重试次数
                    retry_count = 0  # 当前重试次数
                    while retry_count < max_retries:
                        try:
                            await page.get_by_role("button", name="就诊完成").click()
                            break  # 成功点击后退出循环
                        except Exception as e:
                            logger.error(f'账号{self.users.get("id")}点击就诊完成按钮失败，原因：{e}')
                            retry_count += 1  # 增加重试次数
                            await page.wait_for_timeout(1000)  # 等待1秒后重试
                    else:
                        logger.error(f'账号{self.users.get("id")}点击就诊完成按钮失败，达到最大重试次数')
            # 等待一段时间
            time = self.users.get("time")
            logger.debug(f'账号{self.users.get("id")}正在等{time}秒')
            await page.wait_for_timeout(time * 1000)
            # 3、点击签名提交按钮
            logger.debug(f'账号{self.users.get("id")}正在点击签名提交按钮')
            await page.get_by_role("button", name="签名提交").click()
            # 4、弹出弹窗，点击确定按钮
            retry_count = 0
            max_retries = 3  # 最大重试次数
            while retry_count < max_retries:
                try:
                    await page.get_by_role("button", name="确定").click()
                    break  # 成功点击后退出循环
                except Exception as e:
                    logger.error(f'账号{self.users.get("id")}点击确定按钮失败，原因：{e}')
                    retry_count += 1  # 增加重试次数
                    await page.wait_for_timeout(1000)  # 等待1秒后重试
            else:
                logger.error('账号{self.users.get("id")}点击确定按钮失败，达到最大重试次数')
            # logger.debug(f'账号{self.users.get("id")}正在点击确定按钮')
            await page.get_by_role("button", name="确定").click()
            # 5、点击工作台窗口中的就诊完成按钮
            logger.debug(f'账号{self.users.get("id")}正在点击就诊完成按钮')
            await page.get_by_role("button", name="就诊完成").click()
        except Exception as e:
            logger.error(f'账号{self.users.get("id")}分检失败，原因：{e}')
        else:
            logger.error(f'账号{self.users.get("id")}分检成功')


class PageHande(NursePage, SortingPage):
    async def start(self):
        if self.users.get('type') == 'nurse':
            await self.nurse_main()
        elif self.users.get('type') == 'sorting':
            await self.sorting_main()
