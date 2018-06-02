import random


def bubble_sort(a):
    n = len(a)
    for i in range(0, n-1):
        changed = False
        for j in range(0, n-1-i):
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                changed = True
        print('# after bubble %d' % i)
        print(a)
        if not changed:
            print('not changed, break loop')
            break

if __name__ == '__main__':

    for i in range(1000):
        a = [random.randint(0, 100) for x in range(0, 10)]
        print(a)
        b = a[:]
        b.sort()
        bubble_sort(a)

        print('# test:')
        print(a)
        print(b)
        assert a == b