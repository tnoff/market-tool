def round_decimal(float_value, number_decimals):
    try:
        new_value = int(float_value * (10 ** (number_decimals + 1)))
    except ValueError:
        return None
    last_value = new_value % 10
    if last_value > 4:
        new_value += 10
    new_value = new_value - last_value
    new_value = new_value / (10.0 ** (number_decimals + 1))
    return new_value
