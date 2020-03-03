def chunks(n, iterable):
    """
    Split given iterable into chunks by N size.

    Arguments:
        n {string} -- Size of chunk
        iterable {iterable} -- Data

    Returns:
        {iterable} -- Chunks
    """
    chunks = []
    for i in range(0, len(iterable), n):
        chunks.append(iterable[i:i + n])
    return chunks