from funlib.retry import retry_function


def main():
    def _print_attempt(attempt):
        print attempt

    attempts = []

    @retry_function(times=10, err_callback=_print_attempt)
    def test(i):
        attempts.append(i)
        attempted = len(attempts)

        if attempted < 10:
            raise ValueError(attempted)

        return i

    assert test(1) == 1

if __name__ == '__main__':
    main()