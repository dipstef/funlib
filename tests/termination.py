import time

from funlib.signals import termination_raise, Termination


@termination_raise
def _looper():
    while True:
        print 'Loop'
        time.sleep(1)


def loop():
    try:
        _looper()
    except Termination:
        print 'Catched Termination'
        return

    print 'Noo'
    assert False


if __name__ == '__main__':
    loop()
    #kill the process