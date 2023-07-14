from suds.sudsobject import Object, asdict  # type: ignore


def suds_to_dict(d: Object) -> dict:
    """
    Convert Suds object into serializable format.

    Source: https://gist.github.com/mattkatz/65bbc17dbad94c97a01a472734b65d50
    """
    out = {}
    for k, v in asdict(d).items():
        if hasattr(v, '__keylist__'):
            out[k] = suds_to_dict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(suds_to_dict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out
