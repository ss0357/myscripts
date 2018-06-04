import random

def find_min(arr):
    minvalue = arr[0]
    #min_index = 0
    for i in range(len(arr)):
        if arr[i] < minvalue:
            minvalue = arr[i]
            #min_index = i
    return minvalue


def select_sort(arr):
    newarr = []
    for i in range(len(arr)):
        minvalue = find_min(arr)
        newarr.append(minvalue)
        arr.remove(minvalue)
    return newarr


if __name__ == '__main__':
    arr = [random.randint(0, 100) for x in range(10)]
    print(arr)
    print(select_sort(arr))