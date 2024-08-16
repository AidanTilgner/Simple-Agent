def parse_range(range: str, length: int):
    parts = range.split("-", 1)

    if len(parts) == 1:
        if range.startswith("-"):
            start = None
            end = int(parts[0]) if parts[0] else None
        else:
            start = int(parts[0]) if parts[0] else None
            end = None
    elif len(parts) == 2:
        start = int(parts[0]) if parts[0] else None
        end = int(parts[1]) if parts[1] else None
    else:
        raise ValueError("Invalid range format")

    return start, end
