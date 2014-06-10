import time
from funlib.decorators.timeout import timeout, TimeoutError


@timeout(seconds=1)
def foo():
    time.sleep(2)
    print 'Fooo'


def main():
    try:
        foo()
    except TimeoutError:
        print 'Expired'

if __name__ == '__main__':
    main()