from funlib.retry import retry, retry_on_errors, try_times, handle
from funlib.retry.sleep import sleep, random_sleep


def main():
    def _print_attempt(attempt):
        print attempt

    attempts = []

    def _test(i):
        attempts.append(i)
        attempted = len(attempts)

        if attempted < 10:
            raise ValueError(attempted)

        return i

    @retry(times=10, on_err=_print_attempt, sleep=sleep(1))
    def test(i):
        return _test(i)

    assert test(1) == 1

    def _print_value_error(attempt):
        print attempt.call, 'Value Error: ', attempt.error

    @retry_on_errors((ValueError, try_times(10, on_err=_print_value_error, sleep=sleep(1))))
    def test2(i):
        return _test(i)

    attempts = []
    assert test2(1) == 1

    @retry_on_errors(handle(BaseException).doing(try_times(10, on_err=_print_attempt, sleep=random_sleep(1, to=2))),
                     handle(ValueError).doing(try_times(2, on_err=_print_value_error, sleep=sleep(1))))
    def test3(i):
        return _test(i)

    attempts = []
    try:
        test3(1)
    except ValueError, e:
        pass


if __name__ == '__main__':
    main()