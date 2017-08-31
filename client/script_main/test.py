import threading

class Singleton:

    INSTANCE = None

    lock = threading.RLock()

    def __init__(self,a,b):
        print('hello')
        print (a,b)

    def __new__(cls, a, b):
        cls.lock.acquire()
        if cls.INSTANCE is None:
            cls.INSTANCE = super(Singleton, cls).__new__(cls)
        cls.lock.release()
        return cls.INSTANCE


def test_singleton_in_thread():
    print (id(Singleton(2,3)))

if __name__ == "__main__":
    idx = 0
    while 1:
        threading.Thread(target=test_singleton_in_thread).start()
        idx += 1
        if idx > 0X100:
            break