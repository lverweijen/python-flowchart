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


# graph = to_flowchart(fizzbuzz2)
graph = to_flowchart(other_function)
# graph = to_flowchart(SieveOfEratosthenes)
print(graph.to_string(indent=2))
