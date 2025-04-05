from playwright.async_api import async_playwright # 异步API
# from playwright.sync_api import sync_playwright  # 同步API
import asyncio
from core import PageHande
from user_data import USERS


async def main():
    """根据用户数量开启异步任务"""
    async with async_playwright() as pw:
        pages = [PageHande(pw, user) for user in USERS]
        await asyncio.gather(*(page.start() for page in pages))


# __exit__()方法会在with语句块结束时自动调用，用于清理资源,会自动关闭pw对象和connext。
# __enter__()方法会在with语句块开始时自动调用，用于设置资源。

if __name__ == '__main__':
    asyncio.run(main())



# asyncio.gather(协程1，协程2，协程3)函数用于并发执行多个协程。


# def work():
#     print('-1----1-------------')
#     yield
#     print('--1---2-------------')
#     yield
#     print('--1---3-------------')
#     yield


# def work2():
#     print('--2---1-------------')
#     yield
#     print('--2---2-------------')
#     yield
#     print('--2---3-------------')
#     yield


# a = work()
# b = work2()

# for i in range(3):
#    next(a)
#    next(b)

