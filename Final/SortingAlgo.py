import random
import math

def clean_value(value):
    try:
        return int(value.replace(",", "").replace("$", "").strip())
    except ValueError:
        try:
            return float(value.replace(",", "").replace("$", "").strip())
        except ValueError:
            return value.strip()


def insertion_sort(start, end, data, column_index, ascending=True):
    for i in range(start + 1, end + 1):
        key = data[i]
        j = i - 1
        while j >= start and (clean_value(data[j][column_index]) > clean_value(key[column_index]) if ascending else clean_value(data[j][column_index]) < clean_value(key[column_index])):
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key

def insertion_sort1(start, end,data, column_index, ascending=True):
    for i in range(start + 1, end):
        key = data[i]
        j = i - 1
        key_value = clean_value(key[column_index])
        while j >= start and ((clean_value(data[j][column_index]) > key_value) if ascending else (clean_value(data[j][column_index]) < key_value)):
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key
    return data


def bubble_sort(data, column_index, ascending=True):
    for i in range(len(data)):
        for j in range(0, len(data) - i - 1):
            key1 = clean_value(data[j][column_index])
            key2 = clean_value(data[j + 1][column_index])
            if ascending:
                if key1 > key2:
                    data[j], data[j + 1] = data[j + 1], data[j]
            else:
                if key1 < key2:
                    data[j], data[j + 1] = data[j + 1], data[j]
    return data


def selection_sort(data, column_index, ascending=True):
    for i in range(len(data)):
        least_value_index = i
        for j in range(i + 1, len(data)):
            key1 = clean_value(data[j][column_index])
            key2 = clean_value(data[least_value_index][column_index])
            if ascending:
                if key1 < key2:
                    least_value_index = j
            else:
                if key1 > key2:
                    least_value_index = j
        data[i], data[least_value_index] = data[least_value_index], data[i]
    return data

def merge(left_index, mid_index, right_index, data, column_index, ascending=True):
    merged_result = []
    i = left_index
    j = mid_index + 1

    while i <= mid_index and j <= right_index:
        key1 = clean_value(data[i][column_index])
        key2 = clean_value(data[j][column_index])

        if ascending:
            if key1 < key2:
                merged_result.append(data[i])
                i += 1
            else:
                merged_result.append(data[j])
                j += 1
        else:
            if key1 > key2:
                merged_result.append(data[i])
                i += 1
            else:
                merged_result.append(data[j])
                j += 1

    while i <= mid_index:
        merged_result.append(data[i])
        i += 1

    while j <= right_index:
        merged_result.append(data[j])
        j += 1

    for k in range(len(merged_result)):
        data[left_index + k] = merged_result[k]

    return data

def merge_sort(data, column_index, ascending=True, start=None, end=None):
    if start is None:
        start = 0
    if end is None:
        end = len(data) - 1

    if start < end:
        mid = (start + end) // 2
        merge_sort(data, column_index, ascending, start, mid)
        merge_sort(data, column_index, ascending, mid + 1, end)
        merge(start, mid, end, data, column_index, ascending)
    return data


def hybrid_merge_sort(data, column_index, ascending=True, start=0, end=None, n=10):
    if end is None:
        end = len(data) - 1

    if start < end:
        if end - start <= n:
            insertion_sort(start, end, data, column_index, ascending)
        else:
            mid = (start + end) // 2
            hybrid_merge_sort(data, column_index, ascending, start, mid, n)
            hybrid_merge_sort(data, column_index, ascending, mid + 1, end, n)
            merge(start, mid, end, data, column_index, ascending)

    return data


def QuickSort(arr, start, end, column_index, ascending=True):
    if start < end:
        part = partitionRandom(arr, start, end, column_index, ascending)
        QuickSort(arr, start, part - 1, column_index, ascending)
        QuickSort(arr, part + 1, end, column_index, ascending)
    return arr

def partitionRandom(arr, start, end, column_index, ascending=True):
    rand = random.randint(start, end)
    arr[end], arr[rand] = arr[rand], arr[end]
    return partition(arr, start, end, column_index, ascending)

def partition(arr, start, end, column_index, ascending=True):
    pivot = clean_value(arr[end][column_index])
    i = start - 1
    for j in range(start, end):
        key = clean_value(arr[j][column_index])
        if (key <= pivot) if ascending else (key >= pivot):
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[end] = arr[end], arr[i + 1]
    return i + 1

def heapSort(arr, start, end, column_index, ascending=True):
    try:
        if start < 0 or end >= len(arr):
            raise ValueError("Invalid start or end index")

        n = end - start + 1
        for i in range(n // 2 - 1, -1, -1):
            heapify(arr, start, end, i, column_index, ascending)

        for i in range(n - 1, 0, -1):
            arr[start + i], arr[start] = arr[start], arr[start + i]  # Swap
            heapify(arr, start, start + i - 1, 0, column_index, ascending)  # Adjusted the end index
        return arr
    except Exception as e:
        print("Error occurred during sorting:", str(e))
        return arr


def heapify(arr, start, end, i, column_index, ascending=True):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left <= end and (
    (clean_value(arr[left][column_index]) > clean_value(arr[largest][column_index])) if ascending else (
            clean_value(arr[left][column_index]) < clean_value(arr[largest][column_index]))):
        largest = left

    if right <= end and (
    (clean_value(arr[right][column_index]) > clean_value(arr[largest][column_index])) if ascending else (
            clean_value(arr[right][column_index]) < clean_value(arr[largest][column_index]))):
        largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, start, end, largest, column_index, ascending)


def shellSort(arr, start, end, column_index, ascending=True):
    try:
        gap = (end - start) // 2
        while gap > 0:
            j = gap + start
            while j <= end:
                i = j - gap
                key = arr[j][column_index]
                key_value = clean_value(key)
                while i >= start and ((clean_value(arr[i][column_index]) > key_value) if ascending else (clean_value(arr[i][column_index]) < key_value)):
                    arr[i + gap][column_index] = arr[i][column_index]
                    i -= gap
                arr[i + gap][column_index] = key
                j += 1
            gap //= 2
        return arr
    except Exception as e:
        print("Error occurred during sorting:", str(e))
        return arr




def bucket_sort(data, column_index, ascending=True):
    max_value = max(clean_value(row[column_index]) for row in data)
    min_value = min(clean_value(row[column_index]) for row in data)
    bucket_range = (max_value - min_value) / len(data)
    num_buckets = len(data)
    buckets = [[] for _ in range(num_buckets)]

    # Distribute the elements into buckets
    for row in data:
        value = clean_value(row[column_index])
        bucket_index = int((value - min_value) / bucket_range)
        if bucket_index == num_buckets:
            bucket_index -= 1
        buckets[bucket_index].append(row)

    # Sort individual buckets using insertion sort
    for i in range(num_buckets):
        insertion_sort(0, len(buckets[i])-1, buckets[i], column_index, ascending)

    # Concatenate the sorted buckets
    sorted_data = []
    for bucket in reversed(buckets) if not ascending else buckets:
        sorted_data.extend(bucket)

    return sorted_data


def pigeonhole_sort(data, column_index, ascending=True):
    min_value = float("inf")
    max_value = float("-inf")
    for row in data:
        value = clean_value(row[column_index])
        if isinstance(value, (int, float)):
            min_value = min(min_value, value)
            max_value = max(max_value, value)

    range_size = int(max_value - min_value) + 1

    pigeonholes = [[] for _ in range(range_size)]
    for row in data:
        value = clean_value(row[column_index])
        pigeonhole_index = int(value - min_value)
        pigeonholes[pigeonhole_index].append(row)
    sorted_data = []
    for pigeonhole in pigeonholes:
        sorted_data.extend(pigeonhole)

    return sorted_data if ascending else sorted_data[::-1]


def counting_sort(data, column_index, ascending=True):
    if not data:
        return data

    max_value = max(int(row[column_index]) for row in data)
    min_value = min(int(row[column_index]) for row in data)
    range_size = max_value - min_value + 1

    count = [0] * range_size
    output = [None] * len(data)

    for row in data:
        value = int(row[column_index]) - min_value
        count[value] += 1

    for i in range(1, len(count)):
        count[i] += count[i - 1]

    for row in reversed(data):
        value = int(row[column_index]) - min_value
        output[count[value] - 1] = row
        count[value] -= 1

    return output if ascending else output[::-1]


def get_digit(num, digit_index):
    # Extract the digit at the given index from the number
    return num // 10**digit_index % 10

def counting_sort_radix(data, column_index, digit_index, ascending=True):
    count = [0] * 10
    output = [None] * len(data)

    for row in data:
        num = int(row[column_index])
        digit = get_digit(num, digit_index)
        count[digit] += 1

    if ascending:
        for i in range(1, 10):
            count[i] += count[i - 1]
    else:
        for i in range(8, -1, -1):
            count[i] += count[i + 1]

    i = len(data) - 1
    while i >= 0:
        num = int(data[i][column_index])
        digit = get_digit(num, digit_index)
        output[count[digit] - 1] = data[i]
        count[digit] -= 1
        i -= 1

    return output


def radix_sort(data, column_index, ascending=True):
    # Find the maximum number to determine the number of digits
    max_num = max(int(row[column_index]) for row in data)
    digit_index = 0
    while max_num // 10**digit_index > 0:
        data = counting_sort_radix(data, column_index, digit_index, ascending)
        digit_index += 1
    return data







