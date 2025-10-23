from flowchart import to_flowchart


def fizzbuzz():
    for i in range(100):
        match (i % 3 == 0, i % 5 == 0):
            case True, True:
                print("FizzBuzz")
            case True, False:
                print("Fizz")
            case False, True:
                print("Buzz")
            case False, False:
                print(i)

def fizzbuzz2():
    for i in range(100):
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)


def fizzbuzz3():
    for i in range(100):
        divisors = [d for d in [3, 5] if i % d == 0]
        match divisors:
            case [3]:
                print("Fizz")
            case [5]:
                print("Buzz")
            case [3, 5]:
                print("FizzBuzz")
            case _:
                print(i)


def other_function(lo=0, l=[0, 2, 3, 4]):
    keep_running = True
    while (keep_running):
        lo += 1
        for i in range(len(l)):
            if not l[i] < 3:
                # this will effectively
                # stop the while loop:
                keep_running = False
                break
            print(lo)

def SieveOfEratosthenes(num):
    is_prime = [True for i in range(num+1)]
    p = 2
    while p * p <= num:
        if is_prime[p]:
            for i in range(p * p, num+1, p):
                is_prime[i] = False
        p += 1

    # Print all prime numbers
    for p in range(2, num+1):
        if is_prime[p]:
            print(p)

def read_junk(lines):
    try:
        with open("junk.txt") as fp:
            for line in fp.readlines():
                if line == "q":
                    break
                elif line == "c":
                    continue
                else:
                    print(line)
            else:
                print("no more lines!")
    except IOError:
        print("Unable to read junk")


def crazy_division():
    try:
        (a + 1) / b
    except TypeError:
        pass
    except ValueError:
        print("Is division even possible?")
    else:
        print("No worries")




# graph = to_flowchart(fizzbuzz2)
# graph = to_flowchart(fizzbuzz3)
# graph = to_flowchart(other_function)
# graph = to_flowchart(SieveOfEratosthenes)
graph = to_flowchart(read_junk)
print(graph.to_string(indent=2))

# with open("fizzbuzz.png", "bw") as fp:
#     fp.write(graph.create(format="png"))

with open("junk.png", "bw") as fp:
    fp.write(graph.create(format="png"))
