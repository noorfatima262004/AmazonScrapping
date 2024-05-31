def contains_search(data, search_text):
    results = []
    for item in data:
        if search_text in item.lower():
            results.append(item)
    return results

def starts_with_search(data, prefix):
    results = []
    for item in data:
        if item.lower().startswith(prefix):
            results.append(item)
    return results

def ends_with_search(data, suffix):
    results = []
    for item in data:
        if item.lower().endswith(suffix):
            results.append(item)
    return results

def and_search(data, search_text):
    results = []
    for item in data:
        if all(term in item.lower() for term in search_text.split()):
            results.append(item)
    return results

def not_search(data, search_text):
    results = []
    exclude_terms = search_text.split()
    for item in data:
        if not any(term in item.lower() for term in exclude_terms):
            results.append(item)
    return results


def or_search(data, search_text):
    results = []
    for item in data:
        if any(term in item.lower() for term in search_text.split()):
            results.append(item)
    return results

def hash_search(data, search_text, attribute_index):
    search_text = search_text.lower()
    search_results = []

    hash_table = {}
    for row in data[1:]:
        # Convert the attribute value to lowercase for case-insensitive search
        value = row[attribute_index].lower()

        if search_text in value:
            search_results.append(row)
    return search_results


def linear_search(data, search_text, attribute_index):
    search_text = search_text.lower()
    results = []

    for row in data:
        col_text = row[attribute_index].lower()
        if search_text in col_text:
            results.append(row)

    return results

def binary_search(arr, target):
    start, end = 0, len(arr) - 1

    while start <= end:
        mid = (start + end) // 2
        if arr[mid] == target:
            return mid  # Element found, return its index
        elif arr[mid] < target:
            start = mid + 1  # Update start index for right half
        else:
            end = mid - 1  # Update end index for left half

    return -1  # Element not found in the array

