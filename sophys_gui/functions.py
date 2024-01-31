def getItemRecursively(original_obj: object, attrs: list):
    _prev = original_obj
    for attr in attrs:
        _prev = getattr(_prev, attr, _prev[attr])
    return _prev
