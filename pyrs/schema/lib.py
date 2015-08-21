class NA:
    pass


def get_public_attributes(cls):
    if not cls:
        return {}
    return dict(
        [(k, v) for k, v in cls.__dict__.items() if not k.startswith("_")]
    )


def ensure_set(thing):
    if thing is None:
        return set()
    if isinstance(thing, set):
        return thing
    if isinstance(thing, (list, tuple)):
        return set(thing)
    return set([thing])


def ensure_list(thing):
    if thing is None:
        return list()
    if isinstance(thing, list):
        return thing
    if isinstance(thing, (set, tuple)):
        return list(thing)
    return list([thing])
