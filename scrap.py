import timeit

structure = []
for x in range(1000):
    should_process = x % 3 == 0 or x % 5 == 0
    structure.append({"id": x,
                      "should_process": should_process,
                      "list": [i for i in range(1000)]})


def predicate(x):
    return x % 3 == 0 and x % 5 == 0


def do_something(x):
    str = "whatever man you were right =P"


def comprehension():
    for i in (i for x in structure if x['should_process'] for i in x['list'] if predicate(i)):
        do_something(i)


def two_loops():
    for x in structure:
        if x['should_process']:
            for i in x['list']:
                if predicate(i):
                    do_something(i)


print(timeit.timeit(two_loops, number=3))       # Result 7.375
print(timeit.timeit(comprehension, number=3))   # Result 7.687
