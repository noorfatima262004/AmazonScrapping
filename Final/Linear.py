def linear_search(data, search_text, attribute_index):
    search_text = search_text.lower()
    results = []

    for row in data:
        col_text = row[attribute_index].lower()
        if search_text in col_text:
            results.append(row)

    return results