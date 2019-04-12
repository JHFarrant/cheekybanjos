from .exceptions import CheekyException

class BanjosAPIObject():
    _client = None

    def __init__(self, _client, vals):
        self._client = _client
        self._update_values(vals)

    def _update_values(self, vals):
        for att in dir(self):
            if att in vals:
                setattr(self, att, vals[att])

    @staticmethod
    def _select(iterator, search):
        if type(search) == str:
            search = [search]
        if type(search) not in [list,tuple] and len(search) < 1:
            raise CheekyException("Invalid search list")
        results = []
        for i in iterator:
            if search[0] in i.name:
                results.append(i)
        if len(results) == 0:
            raise CheekyException("No menu matches found", [i.name for i in iterator])
        elif len(results) > 1:
            raise CheekyException("Ambiguous search. Multiple menu matches found", [r.name for r in results])
        if len(search) == 1:
            return results[0]
        return results[0].select(*search[1:])