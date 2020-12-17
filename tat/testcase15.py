data = "2,20,0,4,1,17"

nums = list(map(int, data.split(",")))

def task1(run):
    # for _ in range(2020):
    #     if run[-1] in run[:-1]:
    #         space = list(reversed(run[:-1])).index(run[-1])
    #         run.append(space+1)
    #     else:
    #         run.append(0)
    ans = main(run, len(run), 2020)
    print(f"the 2020th number is: {ans}")

def task2(run):
    ans = main(run, len(run), 30000000)
    print(f"the 30000000th number is: {ans}")

#@profile
def main(run: list, runlength: int, loops: int):
    numPositions = dict()
    for i, r in enumerate(run[:-1]):
        numPositions[r] = i

    current = run[-1]
    for i in range(runlength, loops):
        probe = numPositions.get(current, -1)
        
        if probe == -1:
            current = 0
            print("a", current)
        else:
            current = i - probe
            print("b", current)
        numPositions[current] = i  # CHECK WHERE THIS GOES AND WHAT i IS
        #if i % 10000 == 0:
            #print(f"{i/300000}% done!")
    return current

def test(n):
    return main([0, 3, 6], 3, n)

# for n in [0, 3, 6]:
#     print(n)
# print(test(10))
#task1([0, 3, 6])
task1(nums)
#task2(nums)

