from flowchart import to_flowchart


def fizzbuzz():
    for num in range(100):
        if num % 3 == 0 and num % 5 == 0:
            print("FizzBuzz")
        elif num % 3 == 0:
            print("Fizz")
        elif num % 5 == 0:
            print("Buzz")
        else:
            print(num)

        num += 1


def fizzbuzz2():
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


def infinite_fizz():
    num = 0
    while True:
        if num % 3 == 0 and num % 5 == 0:
            print("FizzBuzz")
        elif num % 3 == 0:
            print("Fizz")
        elif num % 5 == 0:
            print("Buzz")
        else:
            print(num)

        num += 1




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


with open("fizzbuzz.png", "bw") as fp:
    graph = to_flowchart(fizzbuzz)
    fp.write(graph.create(format="png"))


with open("junk.png", "bw") as fp:
    graph = to_flowchart(read_junk)
    fp.write(graph.create(format="png"))
