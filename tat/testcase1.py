from numba import jit


def fib(n: int) -> int:
    if n == 0 or n == 1:
        return n
    return fib(n - 1), fib(n - 2)


@jit(nopython=True)
def fast_fib(n: int) -> int:
    if n == 0 or n == 1:
        return n
    return fib(n - 1), fib(n - 2)

print("starting slofib")
print(fib(20))
print("starting slofib")
print(fast_fib(20))
