


# with open("test.txt", "w") as f:
#     # print(f.read())
#
#     print(dir(f))


# __exit__
#  __enter__

# 上下文协议：任何一个对象，只要实现了__enter__和__exit__方法，就是一个上下文协议
# with obj  ---调用 obj.__enter__()
# with中的代码块执行完毕，会自动调用obj.__exit__()


# 异步上下文协议：任何一个对象，只要实现了__aenter__和__aexit__方法，就是一个异步上下文协议

class Demo:

    def __enter__(self):
        print('进入了with语句')

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('离开了with语句')



d = Demo()

print('---------------------1--------------------')
with d:
    print('----2--------------')

print('----3--------------')