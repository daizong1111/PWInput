# @Author  : 木森
# @weixin: python771
import re
# 用于连接到已经打开的Chrome浏览器
import asyncio
# 正则库，用于匹配字符串
import re

from playwright.async_api import async_playwright, Playwright
import logging
from faker import Faker

fc = Faker('zh_CN')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BasePage:
    # 定义 shared_browser 类属性
    shared_browser = None
    def __init__(self, pw: Playwright, users: dict):
        self.pw = pw
        self.users = users
        # 全局超时时间设置（毫秒）
        self.global_timeout = 10000  # 例如设置为 30 秒
        # if BasePage.shared_browser is None:
        #     BasePage.shared_browser = self.create_shared_browser(pw)

    # 创建共享的浏览器实例，用于所有用户共享
    async def create_shared_browser(self, pw: Playwright):
            browser = await self.pw.chromium.launch(headless=False)
            return browser
            
    # async def get_existing_browser_context(self):
    #     try:
    #         # 启动Playwright
    #             # 连接到已打开的Chrome浏览器
    #             browser = await self.pw.chromium.connect_over_cdp("http://localhost:9222")
    #             logger.info("成功连接到已打开的 Chrome 浏览器")
    #             # 获取默认上下文
    #             context = browser.contexts[0] if browser.contexts else await browser.new_context()
    #             # 获取第一个页面
    #             page = context.pages[0] if context.pages else await context.new_page()
    #             return context, page
    #     except Exception as e:
    #         logger.error(f"连接到已打开的 Chrome 浏览器失败: {e}")
    #         return None, None


    async def open_page_login(self, page):
        """登录操作"""
        logger.info(f'账号{self.users.get("id")}正在打开登录页面')
        # await page.goto('http://59.36.171.126:20082/')
        await page.goto('http://113.44.142.29:8069/')

        await page.fill('//input[@placeholder="账号"]', self.users.get('username'))
        await page.fill('//input[@placeholder="密码"]', self.users.get('password'))
        await page.wait_for_timeout(500)
        # 等待元素可点击
        await page.click('//button//span[text()="登 录"]')
        await page.wait_for_timeout(500)


class NursePage(BasePage):
    """护士的操作逻辑"""
    async def wait_for_clickable(self, locator):
            await locator.wait_for(state='visible')
            while not await locator.is_enabled():
                await asyncio.sleep(1)

    async def nurse_main(self):
        # # 获取当前的浏览器上下文和页面
        # context, page = await self.get_existing_browser_context()
        
        """护士操作"""
        browser = await self.pw.chromium.launch(headless=False)
        # browser = await BasePage.shared_browser
        context = await browser.new_context()
        page = await context.new_page()
        # 设置页面的默认超时时间
        page.set_default_timeout(self.global_timeout)
        page.set_default_timeout(20000)
        # 进行登录
        await self.open_page_login(page)
        await page.click('//li//span[text()="登记台"]')
        await page.click('//span[text()="个检登记"]')
        await page.wait_for_timeout(1000)
        logger.info(f'账号{self.users.get("id")}正在开始登记')
        # 进行循环1000次登记
        for i in range(1000):
            logger.info(f'账号{self.users.get("id")}正在第{i}次登记')
            # 填写登记数据
            try:
                await self.input_data(page)
            except Exception as e:
                logger.error(f'账号{self.users.get("id")}第{i}次登记失败，原因：{e}')
                # 回到个检登记页面
                await page.click('//li//span[text()="登记台"]')
                await page.wait_for_timeout(1000)
                await page.click('//span[text()="个检登记"]')
                # 刷新页面
                # await page.reload()
                # 继续进行下一次登记
                continue
            else:
                logger.info(f'账号{self.users.get("id")}第{i}次登记成功')

        # 关闭页面上下文
        await context.close()

    async def input_data(self, page):
        """护士填写登记数据"""
                # 点击新增按钮
        await page.click('//button/span[text()="新增"]')
        await page.wait_for_timeout(1000)
        # 输入姓名称
        await page.get_by_role("textbox", name="* 人员姓名").click()
        # 使用faker生成姓名
        await page.get_by_role("textbox", name="* 人员姓名").fill(fc.name())
        await page.get_by_role("textbox", name="* 证件号码").click()
        # 使用faker生成身份证号码
        await page.get_by_role("textbox", name="* 证件号码").fill(fc.ssn())
        await page.wait_for_timeout(1000)
        # 使用faker生成联系电话
        await page.get_by_role("textbox", name="* 联系电话").fill(fc.phone_number())
        # 使用faker生成住址
        await page.get_by_role("textbox", name="住址").fill(fc.address().replace("\n", " "))
        await page.get_by_role("textbox", name="* 时段").click()
        
        await page.get_by_text("07:00-23:59").click()

        await page.get_by_role("textbox", name="请输入").fill("该套餐下有多个导检科室的项目")
        await page.get_by_role("button", name="搜索").click()
        # 等待按钮可点击
        # await page.wait_for_selector('role=row[name="该套餐下有多个导检科室的项目"] >> role=button', state='visible')
        await page.wait_for_selector('//div[text()="该套餐下有多个导检科室的项目"]/../../child::*[6]/div/button', state='visible')
        await page.get_by_role("row", name="该套餐下有多个导检科室的项目").get_by_role("button").click()
        # await page.wait_for_timeout(2000)
        # await page.get_by_role("button", name="保存").click()
        # await page.wait_for_timeout(2000)
        # await page.get_by_role("button", name="收费").click()
        # await page.wait_for_timeout(2000)
        # await page.get_by_role("button", name="确认").click()
        # await page.wait_for_timeout(2000)
        # await page.get_by_role("button", name="打印指引单").click()
        # await page.wait_for_timeout(2000)
        # button = page.get_by_role("button", name="打印", exact=True)
        await page.wait_for_timeout(1000)
        # await self.wait_for_clickable(page.get_by_role("button", name="保存"))
        await page.get_by_role("button", name="保存").click()
        await page.wait_for_timeout(1000)
        # await self.wait_for_clickable(page.get_by_role("button", name="收费"))
        await page.get_by_role("button", name="收费").click()

        # await self.wait_for_clickable(page.get_by_role("button", name="确认"))
        await page.wait_for_timeout(1000)
        await page.get_by_role("button", name="确认").click()

        # await self.wait_for_clickable(page.get_by_role("button", name="打印指引单"))
        await page.wait_for_timeout(1000)
        await page.get_by_role("button", name="打印指引单").click()

        await self.wait_for_clickable(page.get_by_role("button", name="打印", exact=True))
        button = page.get_by_role("button", name="打印", exact=True)
        if await button.is_visible():
            await button.click()


class SortingPage(BasePage):
    def __init__(self, pw: Playwright, users: dict):
        super().__init__(pw, users)
        self.lock = asyncio.Lock()  # 创建一个锁
    # 定义科室等待时间字典
    DEPARTMENT_WAIT_TIME = {
        "亚健康1室": 3000,  
        "亚健康2室": 3000,  
        "妇科二室": 7000,  
        "心电图一室": 10000,  
        "心电图二室": 10000,  
        "腹部彩超一室": 5000,  
        "颈部彩超一室": 5000,  
        # 可以根据需要添加更多科室和对应的等待时间
    }
    """
    分检的操作逻辑
    """

    async def sorting_main(self):
        # 获取当前的浏览器上下文和页面
        # context, page = await self.get_existing_browser_context()

        browser = await self.pw.firefox.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # 设置页面的默认超时时间
        page.set_default_timeout(self.global_timeout)
        page.set_default_timeout(10000)
        # 打开登录页面进行登录
        await self.open_page_login(page)

        await self.sorting_handle(page)

        # 关闭页面上下文
        await context.close()

    async def sorting_handle(self, page):
        """分检医生操作"""
        await page.wait_for_timeout(1000)
        # 点击右上角的科室选择框
        await page.click('//input[@placeholder="请选择子科室"]')
        # 显式等待，科室选项出现后，点击
        await page.wait_for_selector('(//div[@class="el-popper is-pure is-light el-select__popper"])[2]', state='visible')
        await page.click('(//div[@class="el-popper is-pure is-light el-select__popper"])[2]')
        # 获取科室名称
        room = self.users.get("room")
        logger.info(f'账号{self.users.get("id")}正在开始分检，科室名称为：{room}')
        # 点击科室分检
        await page.click('//li//span[text()="科室分检"]')
        await page.wait_for_timeout(1000)
        
        i = 0
        while True:
            try:
                # 点击电脑状图标叫出登记台
                # await page.click('(//button[@class="el-button el-button--default"])[3]')
                await page.click('(//div[@class="el-badge item"]/button[@class="el-button el-button--default"])')
                # 点击科室名称按钮
                # ... existing code ...
                # 点击科室名称按钮，添加了显式等待，确保元素可见后再点击
                # 设置超时时间为2000毫秒（即2秒）
                # await page.get_by_role("button", name="科室名称").click()
                await page.wait_for_timeout(1000)
                if i == 0:
                    await page.get_by_role("button", name="选择科室").click()
                else:
                    await page.get_by_role("button", name=f"{room}").click()

                # await page.wait_for_selector('//div[@class="select-Department-blue el-tooltip__trigger el-tooltip__trigger"]', state='visible', timeout=2000)
                # room_button = await page.query_selector('//div[@class="select-Department-blue el-tooltip__trigger el-tooltip__trigger" and @role="button"]')
                # if room_button:
                #     await room_button.click()
                # 点击科室选项
                # 添加显式等待，确保元素可见后再点击
                await page.wait_for_selector(f'(//li[text()="{room}"])[1]', state='visible')
                await page.click(f'(//li[text()="{room}"])[1]')
                # 定位标题为“医生叫号工作台”的窗口
                doctor_workbench = await page.get_by_role('dialog', name='医生叫号工作台').first.element_handle()
                if doctor_workbench:
                    # 假设表格在医生叫号工作台窗口内，可以直接在该元素内查找表格
                    table = await doctor_workbench.query_selector('table')
                    if table:
                        logger.info("成功定位到医生叫号工作台下面的表格")
                        # 这里可以继续对表格进行操作，例如获取表格的行数
                        rows = await table.query_selector_all('tr')
                        logger.info(f"表格共有 {len(rows)} 行")
                    else:
                        logger.error("未找到医生叫号工作台下面的表格")
                else:
                    logger.error("未找到医生叫号工作台")
                
                # 对侯检队列下面的所有待检人员进行分检
                # 获取列表中的行数
                rows = await page.query_selector_all('(//table[@class="el-table__body"])[4]//tr')
                logger.info(f'账号{self.users.get("id")}正在第{i}次分检，目前该科室下已经有{len(rows)}人在排队')
                # 遍历表格中的每一行，呼叫->就诊->签名提交->确定->就诊完成
                for j in range(len(rows)):
                    # 点击呼叫按钮 
                    # 使用正则表达式匹配“呼叫”或“重呼”
                    await page.get_by_role("button", name=re.compile(r'^(呼叫|重呼)$')).nth(1).click()
                    # await page.get_by_label("医生叫号工作台").get_by_role("button", name="呼叫").click()
                    # 获取到该列表当前行的人员姓名
                    # 假设表格的xpath是'(//table[@class="el-table__body"])[4]'
                    table_xpath = '//div[@class="el-dialog__body"]/div/div[3]/div/div/div[3]'
                    # 定位到其所在的行
                    row = await page.query_selector(f'{table_xpath}//tr[{j + 1}]')
                    if row:
                        # 假设“姓名”列是第2列（根据实际情况调整）
                        name_cell = await row.query_selector('td:nth-child(2)')
                        if name_cell:
                            name = await name_cell.text_content()
                            logger.info(f'第{j + 1}行姓名列的数据是: {name}')
                        else:
                            logger.error('未找到“姓名”列的单元格')
                    else:
                        logger.error(f'未找到第{j+1}行')
                    try:
                        div_element = await page.query_selector(f'(//tbody)[1]/tr/td/div/div[p[text()="{name}"]]')
                        if div_element:
                            logger.info(f"找到了包含文本内容为 {name} 的 p 元素的 div 元素")
                            # 假设使用XPath来定位
                            button_element = await div_element.query_selector('..//p[6]/button')
                            if button_element:
                                logger.info(f"找到了姓名为{name}的行的就诊按钮")
                                async with self.lock:  # 使用锁确保代码块作为一个整体执行
                                    # 点击就诊按钮
                                    await button_element.click()
                                    # 从此处开始，经过一段时间后，签名提交->确定->就诊完成
                                    # 等待一段时间
                                    # 根据科室名称获取等待时间
                                    # 确保 room 是字符串类型，避免类型不匹配问题
                                    if room is not None:
                                        room = str(room)
                                    # 确保 room 是字符串类型，避免类型不匹配问题
                                    if isinstance(room, str):
                                        wait_time = self.DEPARTMENT_WAIT_TIME.get(room, 1000)  # 默认等待1秒
                                    else:
                                        wait_time = 10000  # 如果 room 不是字符串类型，使用默认等待时间
                                    await page.wait_for_timeout(wait_time)
                                    # 点击签名提交按钮
                                    await page.get_by_role("button", name="签名提交").click()
                                    # 弹出弹窗，点击确定按钮
                                    await page.get_by_role("button", name="确定").click()
                                    # 点击工作台窗口中的就诊完成按钮
                                    await page.get_by_role("button", name="就诊完成").click()
                                    # 打印日志
                                    logger.info(f"姓名为{name}的人员已经就诊完成")
                            else:
                                logger.info(f"未找到姓名为{name}的行的就诊按钮")
                        else:
                            logger.info(f"未找到包含文本内容为 {name} 的 p 元素的 div 元素，可能是就诊完成按钮点击失败导致该人员仍然在列表中导致的")
                            # 没找到说明是就诊完成按钮未点击成功，点击就诊完成按钮
                            await page.get_by_role("button", name="就诊完成").click()
                            # 打印日志
                            logger.info(f"强制将姓名为{name}的行已从列表中移除")
                    except Exception as e:
                        logger.error(f"查找元素时出错: {e}")
                    
                # 刷新页面
                await page.reload()
                
            except Exception as e:
                logger.error(f'账号{self.users.get("id")}第{i}次分检失败，原因：{e}')
            i += 1



class PageHande(NursePage, SortingPage):
    async def start(self):
        if self.users.get('type') == 'nurse':
            await self.nurse_main()
        elif self.users.get('type') == 'sorting':
            await self.sorting_main()
