from funlib.attempt import retry_function


def main():
    def _print_attempt(attempt):
        print attempt

    attempts = []

    @retry_function(max_times=10, callback=_print_attempt, err_callback=_print_attempt)
    def test(i):
        attempts.append(i)
        attempted = len(attempts)

        if attempted < 10:
            raise ValueError(attempted)

        return i

    test(1)

if __name__ == '__main__':
    main()