def clamp(value: float, min_val: int = 0, max_val: int = 255) -> int:
    # use rounding to better represent values between max and min
    return int(round(max(min(value, max_val), min_val)))
