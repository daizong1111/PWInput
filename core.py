# 导入 sync_api
from playwright.async_api import async_playwright
import asyncio
import logging
# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
from faker import Faker
fake = Faker('zh_CN')
# 正则库
import re

async def login(page, url="http://113.44.142.29:8069", username="xp_test", password="Yik.yik@2024"):
    await page.goto(url,timeout=5000)
    # 输入账号和密码
    await page.get_by_role("textbox", name="账号").fill(username) # 替换为实际的用户名
    await page.get_by_role("textbox", name="密码").fill(password) # 替换为实际的密码
    # 点击登录按钮
    await page.get_by_role("button", name="登 录").click()

async def input_data(page):
    # 使用faker库生成姓名、身份证号、手机号、家庭住址等信息
    name = fake.name()
    id_card = fake.ssn()
    phone = fake.phone_number()
    address = fake.address()
    # 输入姓名·
    await page.get_by_role("textbox", name="* 人员姓名").fill(name)
    logger.debug(f"已输入姓名: {name}")
    # 输入身份证号
    await page.get_by_role("textbox", name="* 证件号码").fill(id_card)
    logger.debug(f"已输入身份证号: {id_card}")
    # 等待1秒
    await page.wait_for_timeout(1000)
    # 输入手机号
    await page.get_by_role("textbox", name="* 联系电话").fill(phone)
    logger.debug(f"已输入手机号: {phone}")
    # 输入家庭住址
    await page.get_by_role("textbox", name="住址").fill(address)
    logger.debug(f"已输入家庭住址: {address}")
    # 点击时段文本框
    await page.get_by_role("textbox", name="* 时段").click()
    logger.debug("已点击时段文本框")
    # 选择时间段
    await page.wait_for_selector('text=07:00-23:59') # 显式等待
    await page.get_by_text("07:00-23:59").click()
    logger.debug("已选择时间段")
    # 在搜索框输入套餐名
    await page.get_by_role("textbox", name="请输入").fill("该套餐下有多个导检科室的项目")
    logger.debug("已输入套餐名")
    # 点击搜索按钮
    await page.get_by_role("button", name="搜索").click()
    logger.debug("已点击搜索按钮")
    # 等待1000毫秒
    await page.wait_for_timeout(1000)
    # 等待指定行元素可见
    await page.wait_for_selector('//div[text()="该套餐下有多个导检科室的项目"]/../../td[6]/div/button',state='visible') # 显式等待
    add_btn = page.get_by_role("row", name="该套餐下有多个导检科室的项目").get_by_role("button")
    await add_btn.click()
    logger.debug("已点击该套餐的添加按钮")
    # 点击套餐的添加按钮后等待一段时间
    await page.wait_for_timeout(2000)
    # 点击保存按钮
    await page.get_by_role("button", name="保存").click()
    logger.debug("已点击保存按钮")
    await page.wait_for_timeout(2000)
    # 断言收费按钮可点击
    assert await page.get_by_role("button", name="收费").is_enabled(), "收费按钮不可点击"

async def pre_handle(page):
    # 点击登记台菜单选项
    await page.get_by_role("menubar").get_by_text("登记台").click()
    # 点击个检登记菜单选项
    # await page.get_by_role("menu").get_by_role("link", name="个检登记").click()
    await page.locator(r"//span[text()='个检登记' and @class='menu-title']").click()

async def post_handle(page):
    # 点击收费按钮
    await page.get_by_role("button", name="收费").click()
    logger.debug("已点击收费按钮")
    # 等待1秒
    await page.wait_for_timeout(2000)
    # 点击确定按钮
    await page.get_by_role("button", name="确认").click()
    logger.debug("已点击确认按钮")
    # 等待2秒
    await page.wait_for_timeout(2000) 
    # 点击打印指引单
    await page.get_by_role("button", name="打印指引单").click()
    logger.debug("已点击打印指引单按钮")
    # 显示等待
    await page.wait_for_selector('role=button[name="打印"]', state='visible') 
    # 若弹出弹窗，则点击打印按钮
    if await page.get_by_role("button", name="打印", exact=True).is_visible():
        await page.get_by_role("button", name="打印", exact=True).click()
        logger.debug("打印按钮已点击")
    # 等待2秒
    await page.wait_for_timeout(2000)

async def registration_data(page):
    try:
        # 点击新增按钮
        await page.get_by_role("button", name="新增").click()
        logger.debug("已点击新增按钮")
        # 填写表单 
        await input_data(page)
        logger.debug("已经填写表单")
        # 做后置操作-收费、打印指引单等
        await post_handle(page)
        logger.debug("已完成后置操作")
    except Exception as e:
        logger.error(f"登记时发生错误: {e}，需要重新登记")
        # 执行前置步骤
        await pre_handle(page)
        # 重新登记
        await registration_data(page) 

async def nurse_handle(page):
    # 前置操作-跳转到个检登记页面
    await pre_handle(page)
    i = 0
    while True:
        logger.debug(f"第{i}次登记开始")
        await registration_data(page)
        logger.debug(f"第{i}次登记完成")
        i += 1


async def nurse_main():
    # 连接到已打开的浏览器实例，方便调试
    # try:
    # # 使用 async with 上下文管理器启动 Playwright
    #     async with async_playwright() as playwright:
    #         browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
    #         context = browser.contexts[0] if browser.contexts else await browser.new_context()
    #         page = context.pages[0] if context.pages else await context.new_page()
    #         # 后续操作
    #         # await input_data(page)
    #         # await login(page)
    #         # await nurse_handle(page)  
    # except Exception as e:
    #     print(f"连接到浏览器实例失败: {e}")
        
    async with async_playwright() as p:
    # 启动浏览器并创建上下文
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        # 打开登录页面
        page = await context.new_page()
        # 设置页面默认超时时间，单位为毫秒，这里设置为 10000 毫秒即 10 秒
        page.set_default_timeout(5000)
        await login(page)
        await nurse_handle(page)

async def sort_pre_handle(page):
    # 点击请选择科室文本框
    await page.get_by_role("textbox", name="请选择子科室").click()
    # 点击科室选项
    await page.get_by_role("listitem").filter(has_text="妇科").click()
    # 点击电脑状图标，叫出工作台
    await page.get_by_label("待检人员").get_by_role("button").filter(has_text=re.compile(r"^$")).click()
    # 等待窗口可见
    dialog = page.get_by_role("dialog", name="医生叫号工作台")
    await dialog.wait_for(state='visible')
    # 点击选择科室按钮
    # await page.get_by_role("button", name="选择科室").click()
    await dialog.get_by_role("button", name=re.compile(r"选择科室|妇科二室")).click()
    # 点击科室选项
    await page.get_by_role("menuitem", name="妇科二室").click()

async def sort_handle(page):
    # 点击科室分检菜单项
    await page.get_by_role("menubar").get_by_role("link", name="科室分检").click()
    while True:
        # 做前置操作-选择科室、叫出工作台窗口
        await sort_pre_handle(page)
        # 获取到医生叫号工作台窗口中的表格
        table_in_window = dialog.get_by_role("table")
        # 获取表格的行数
        rows = await table_in_window.locator("tbody tr").all()
        logger.debug(f"表格行数: {len(rows)}")
        # 获取到体检列表中的表格
        table_in_healthlist = page.get_by_label("待检人员").get_by_role("table")       
        # 遍历工作台窗口中表格的每一行
        for row in rows:
            # 点击叫号按钮
            await dialog.get_by_role("button", name=re.compile(r"呼叫|重呼")).click()
            # 获取该行中表头为姓名的列中的值
            name_cell = row.locator(f"td:nth-child(2)")
            name = await name_cell.text_content()
            logger.debug(f"姓名：{name}")
            # 定位就诊列表中该姓名所在的行,可能会匹配到多个
            rows_in_healthlist = table_in_healthlist.locator(f"tr:has-text('{name}')")
            logger.debug(f"匹配到的行: {rows_in_healthlist}")
            if(await rows_in_healthlist.count() > 0):
                logger.debug(f"在体检列表中找到了姓名为{name}的行")
                # 点击该姓名所在的行，若匹配到多个，会点击第一个
                await rows_in_healthlist.first.get_by_role("button", name=re.compile(r"就诊|就诊中")).click()
                # await rows_in_healthlist.first().locator('role=button[name=/就诊|就诊中/]').click()
                logger.debug(f"成功点击了就诊|就诊中按钮")
                # 等待一段时间，不同科室不一样
                await page.wait_for_timeout(2000)
                # 点击签名提交按钮
                await page.get_by_role("button", name="签名提交").click()
                logger.debug(f"成功点击了签名提交按钮")
                await page.wait_for_timeout(2000)
                confirm_button = page.get_by_role("button", name="确定")
                # 若弹出确认框，则点击确定按钮
                if await confirm_button.is_visible():
                    await confirm_button.click()
                    logger.debug("确定按钮已点击")
                # 点击工作台窗口中的就诊完成按钮
                await dialog.get_by_role("button", name="就诊完成").click()
                logger.debug(f"成功点击了就诊完成按钮")
            else:
                logger.debug(f"在体检列表中未找到姓名为{name}的行")
                # 若未找到，强制点击就诊完成按钮
                await dialog.get_by_role("button", name="就诊完成").click()
                logger.debug(f"强制点击了就诊完成按钮")
        #刷新页面 
        await page.reload()   

async def sort_main():
    # 连接到已打开的浏览器实例，方便调试
    try:
    # 使用 async with 上下文管理器启动 Playwright
        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = context.pages[0] if context.pages else await context.new_page()
            page.set_default_timeout(5000) # 设置页面默认超时时间，单位为毫秒，这里设置为 10000 毫秒即 10 秒 
            # 后续操作
            await sort_handle(page)
            # await input_data(page)
            # await login(page)
            # await nurse_handle(page)  
    except Exception as e:
        print(f"连接到浏览器实例失败: {e}")
        
    # async with async_playwright() as p:
    # # 启动浏览器并创建上下文
    #     browser = await p.chromium.launch(headless=False)
    #     context = await browser.new_context()
    #     # 打开登录页面
    #     page = await context.new_page()
    #     # 设置页面默认超时时间，单位为毫秒，这里设置为 10000 毫秒即 10 秒
    #     page.set_default_timeout(5000)
    #     await login(page, username="10590", password="Yik.yik@2024")
    #     await sort_handle(page)

if __name__ == "__main__":
    asyncio.run(nurse_main())
    # asyncio.run(sort_main())