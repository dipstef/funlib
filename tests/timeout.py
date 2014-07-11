import time
from funlib.signals import timeout, CallTimeout


@timeout(seconds=1)
def foo():
    time.sleep(2)
    print 'Fooo'


def main():
    try:
        foo()
    except CallTimeout:
        print 'Expired'

if __name__ == '__main__':
    main()