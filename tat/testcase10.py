from functools import reduce

data = """149
87
67
45
76
29
107
88
4
11
118
160
20
115
130
91
144
152
33
94
53
148
138
47
104
121
112
116
99
105
34
14
44
137
52
2
65
141
140
86
84
81
124
62
15
68
147
27
106
28
69
163
97
111
162
17
159
122
156
127
46
35
128
123
48
38
129
161
3
24
60
58
155
22
55
75
16
8
78
134
30
61
72
54
41
1
59
101
10
85
139
9
98
21
108
117
131
66
23
77
7
100
51"""

vector = list[int]

plugs = list(map(int, data.split("\n")))
plugs.append(0)
plugs.append(max(plugs)+3)
plugs = sorted(plugs)

def adjs(list: vector):
    return (pair for pair in zip(list, list[1:]))

def task1(plugs: vector):
    ones = 0
    threes = 0
    for a, b in adjs(plugs):
        diff = (b - a)
        if diff == 1:
            ones += 1
        elif diff == 3:
            threes += 1
    return f"product: {ones * threes}, ones: {ones}, threes: {threes}"


def spaces(alist: vector):
    return (b - a for a, b in adjs(sorted(alist)))

def blocks(alist: vector):
    return "".join(map(str, list(spaces(alist)))).split("3")

def perms(x: int) -> int:
    return [1, 1, 2, 4, 7][x]

def lens(alist: vector) -> vector:
    return list(map(perms, map(len, blocks(alist))))

def mult(a: int, b: int) -> int:
    return a * b

def prod(alist: vector) -> int:
    return reduce(mult, alist)

def task2(plugs: vector) -> str:
    return f"paths: {prod(lens(plugs))}"

print(task1(plugs))
print(task2(plugs))
