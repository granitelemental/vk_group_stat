def get_diff_by(items_are_in, items_not_in, by = None):
    """by - str; items_are_in and items_not_in - lists of dicts. diff - list of dicts"""
    if by == None:
        diff = [item for item in items_are_in if item not in items_not_in]
    else:
        by_not_in = [item[by] for item in items_not_in]
        diff = [item for item in items_are_in if item[by] not in by_not_in]
    return diff