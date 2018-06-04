from pdb import set_trace


def binary_search(alist, item):
    low = 0
    high = len(alist)-1
    times = 0
    while(high>=low):
        times += 1
        #print('search times: %d' % times)
        #print(alist[low:high+1])
        #set_trace()
        mid = (low+high)//2
        if alist[mid] == item:
            print('found, %d: %d' % (mid, item))
            return alist[mid]
        elif alist[mid] > item:
            high = mid-1
        elif alist[mid] < item:
            low = mid+1

    print('not found' + str(item))

if __name__ == '__main__':
    #alist = [x for x in range(0, 100, 2)]
    #print(alist)

    #binary_search(alist, 8)
    #for x in range(0, 110):
    #    binary_search(alist, x)

    alist = [0, 1]
    print(alist)
    binary_search(alist, 0)
    binary_search(alist, 1)

    alist = [1,]
    print(alist)
    binary_search(alist, 0)
    binary_search(alist, 1)

    alist = [1,2,3,4,5,]
    print(alist)
    binary_search(alist, 1)
    binary_search(alist, 3)
    binary_search(alist, 5)