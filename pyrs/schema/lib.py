class NA:
    pass


def get_public_attributes(cls):
    if not cls:
        return {}
    return dict(
        [(k, v) for k, v in cls.__dict__.items() if not k.startswith("_")]
    )
