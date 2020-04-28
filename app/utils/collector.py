def get_all(get_function, max_count):
    """get_function - function which collects data from api;
    max_count - max count of items per one attempt;
    """
    offset = 0
    all_items = []
    result, total_count = get_function(offset, max_count)

    while offset < total_count:
        result, _ = get_function(offset, max_count)
        all_items.extend(result)
        offset += max_count
    return all_items
