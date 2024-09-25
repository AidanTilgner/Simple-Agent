def parse_range(range: str, length: int):
    default_start = 0
    default_end = length

    if range == "-":
        return default_start, default_end

    parts = range.split("-", 1)

    if len(parts) == 1:
        if range.startswith("-"):
            start = default_start
            if parts[0]:
                end = int(parts[0])
            else:
                end = default_end
        elif range.endswith("-"):
            end = default_end
            if parts[0]:
                start = int(parts[0]) - 1
            else:
                start = default_start
        else:
            return None, None
    elif len(parts) == 2:
        if not parts[0] and not parts[1]:
            return None, None
        if parts[0]:
            start = int(parts[0]) - 1
        else:
            start = default_start
        if parts[1]:
            end = int(parts[1])
        else:
            end = default_end
    else:
        raise ValueError("Invalid range format")

    # Validate range bounds
    if start is not None and (start < 0 or start > length - 1):
        return None, None
    if end is not None and (end < 0 or end > length):
        return None, None

    return start, end
