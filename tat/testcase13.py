from functools import reduce
import time

data = """1005162
19,x,x,x,x,x,x,x,x,41,x,x,x,x,x,x,x,x,x,823,x,x,x,x,x,x,x,23,x,x,x,x,x,x,x,x,17,x,x,x,x,x,x,x,x,x,x,x,29,x,443,x,x,x,x,x,37,x,x,x,x,x,x,13"""

target = data.split("\n")[0]
times = data.split("\n")[1]


def chinese_remainder(n, a):
    sum = 0
    prod = reduce(lambda a, b: a*b, n)
    for n_i, a_i in zip(n, a):
        p = prod // n_i
        sum += a_i * mul_inv(p, n_i) * p
    return prod - sum % prod

def mul_inv(a, b):
    b0 = b
    x0, x1 = 0, 1
    if b == 1:
        return 1
    while a > 1:
        q = a // b
        a, b = b, a % b
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += b0
    return x1

def diff(target, step):
    return (step * (int(target / step) + 1)) - target

def task1():
    global target
    global times
    tg = int(target)
    tm = [int(t) for t in times.split(",") if t != "x"]
    rmin = 100000000
    best = 1
    for t in tm:
        d = diff(tg, t)
        if d < rmin:
            best = t
            rmin = d
    print(f"best: {best}, time to wait: {rmin}, product: {best * rmin}")

def test(values):
    return all([(y - x) == 1 for x, y in zip(values, values[1:])])

def mindex(l):
    minval = l[0]
    best = 0
    for i, val in enumerate(l[1:]):
        if val < minval:
            minval = val
            best = i+1
    return best

def process(l):
    return [x + i for i, x in zip(reversed(range(len(l))), l)]

# def task2(tm):
#     nums = [int(t) if t != "x" else int(tm.split(",")[0]) for t in tm.split(",")]
#     values = [0 if n != 1 else i for i, n in enumerate(nums)]
#     while not test(values):
#         c = mindex(process(values))
#         values[c] += nums[c]
#         #print(f"values: {values}")
#     print(f"values: {values}")

def proc(thing):
    return int(thing) if thing != "x" else 1

def task2():
    global times
    a = list(map(proc, times.split(",")))
    print(f"earliest time: {chinese_remainder(a, range(len(a)))}")

start = time.time()
task1()
task2()
print(f"time taken: {time.time() - start}s")
