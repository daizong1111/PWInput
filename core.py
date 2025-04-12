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

async def login(page, url="http://113.44.142.29:8069", username="xp_test", password="Yik.yik@2024"):
    await page.goto(url,timeout=5000)
    # 输入账号和密码
    await page.get_by_role("textbox", name="账号").fill(username) # 替换为实际的用户名
    await page.get_by_role("textbox", name="密码").fill(password) # 替换为实际的密码
    # 点击登录按钮
    await page.get_by_role("button", name="登 录").click()

async def input_data(page):
    # 点击新增按钮
    await page.get_by_role("button", name="新增").click()
    # 使用faker库生成姓名、身份证号、手机号、家庭住址等信息
    name = fake.name()
    id_card = fake.ssn()
    phone = fake.phone_number()
    address = fake.address()
    # 输入姓名·
    await page.get_by_role("textbox", name="* 人员姓名").fill(name)
    # 输入身份证号
    await page.get_by_role("textbox", name="* 证件号码").fill(id_card)
    # 输入手机号
    await page.get_by_role("textbox", name="* 联系电话").fill(phone)
    # 输入家庭住址
    await page.get_by_role("textbox", name="住址").fill(address)
    # 点击时段文本框
    await page.get_by_role("textbox", name="* 时段").click()
    # 选择时间段
    await page.wait_for_selector('text=07:00-23:59') # 显式等待
    await page.get_by_text("07:00-23:59").click()
    # 在搜索框输入套餐名
    await page.get_by_role("textbox", name="请输入").fill("该套餐下有多个导检科室的项目")
    # 点击搜索按钮
    await page.get_by_role("button", name="搜索").click()
    # 等待1000毫秒
    await page.wait_for_timeout(1000)
    # 等待指定行元素可见

    await page.wait_for_selector('//div[text()="该套餐下有多个导检科室的项目"]/../../td[6]/div/button',state='visible') # 显式等待
    add_btn = page.get_by_role("row", name="该套餐下有多个导检科室的项目").get_by_role("button")
    await add_btn.click()
    # 点击套餐的添加按钮后等待一段时间
    await page.wait_for_timeout(2000)
    # 点击保存按钮
    await page.get_by_role("button", name="保存").click()
    await page.wait_for_timeout(2000)

async def pre_handle(page):
    # 点击登记台菜单选项
    await page.get_by_role("menubar").get_by_text("登记台").click()
    # 点击个检登记菜单选项
    await page.get_by_role("menu").get_by_role("link", name="个检登记").click()

    

async def post_handle(page):
    # 点击收费按钮
    await page.get_by_role("button", name="收费").click()
    # 等待1秒
    await page.wait_for_timeout(2000)
    # 点击确定按钮
    await page.get_by_role("button", name="确认").click()
    # 等待2秒
    await page.wait_for_timeout(2000) 
    # 点击打印指引单
    await page.get_by_role("button", name="打印指引单").click()
    # 显示等待
    await page.wait_for_selector('role=button[name="打印"]', state='visible') 
    # 若弹出弹窗，则点击打印按钮
    if await page.get_by_role("button", name="打印", exact=True).is_visible():
        await page.get_by_role("button", name="打印", exact=True).click()
        logger.debug("打印按钮已点击")
    # 等待2秒
    await page.wait_for_timeout(2000)

async def nurse_handle(page):
    # 前置操作
    await pre_handle(page)
    while True:
        try:
            # 填写表单
            await input_data(page)
        except Exception as e:
            logger.error(f"填写表单时发生错误: {e}")
            await nurse_handle(page)
        # 后置操作
        await post_handle(page)

    




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

if __name__ == "__main__":
    asyncio.run(nurse_main())