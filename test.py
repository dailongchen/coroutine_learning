#!/usr/bin/env python3


def loop_func(n):
    while n >= 0:
        new_value = (yield n)
        if new_value:
            n = new_value
        else:
            n -= 1


def test_loop_func():
    k = loop_func(5)
    next(k)  # k.send(None)
    for i in k:
        print(i)

        if i == 4:
            k.send(3)

        print("here")


def my_generator(func):
    def step(*args, **kwargs):
        c = func(*args, **kwargs)
        next(c)
        return c
    return step


@my_generator
def average():
    current_sum = 0
    num = 0
    while True:
        print('before', current_sum, num)
        value = current_sum / num if num > 0 else 12
        print('to_post_yield', value)
        received = (yield value)
        print('received', received)
        current_sum += received
        num += 1
        print('after', current_sum, num)


def test_average():
    x = average()
    for i in range(10):
        current = x.send(i)
        print(i, current)


def test_yield(n):
    yield n


if __name__ == "__main__":
    # test_average()

    for i in range(10):
        c = test_yield(i)
        while True:
            try:
                print(next(c))
            except StopIteration:
                break
