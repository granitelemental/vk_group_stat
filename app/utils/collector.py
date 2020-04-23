def get_all(get_function, max_count):
    """get_function - function which collects data from api;
    max_count - max count of items;
    """
    offset = 0
    all_items = []
    result = get_function(offset, max_count)

    while offset < result["count"]:
        result = get_function(offset=offset, count=max_count)
        all_items.extend(result)
        offset += max_count
    return all_items
