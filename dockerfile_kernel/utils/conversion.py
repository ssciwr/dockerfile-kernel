def try_convert(value: any, default: any, *types: type):
    """Try to convert a *value* into a specific *type*. Return *default* if not possible.

    Args:
        value (any): Value to be converted.
        default (any): The default value to be returned if all *types* fail casting.
        *types (type): Types the conversion is tried on **in order**.

    Returns:
        any: Converted *value* or *default*.
    """
    for t in types:
        try:
            return t(value)
        except (ValueError, TypeError):
            continue
    return default
