from suds.sudsobject import Object, asdict  # type: ignore


def suds_to_dict(d: Object) -> dict:
    """
    Convert Suds object into serializable format.

    Source: https://gist.github.com/mattkatz/65bbc17dbad94c97a01a472734b65d50
    """
    out: dict[str | dict, str | dict | list] = {}
    for k, v in asdict(d).items():
        if hasattr(v, "__keylist__"):
            out[k] = suds_to_dict(v)
        elif isinstance(v, list):
            key_list = []
            for item in v:
                if hasattr(item, "__keylist__"):
                    key_list.append(suds_to_dict(item))
                else:
                    key_list.append(item)
            out[k] = key_list
        else:
            out[k] = v
    return out
