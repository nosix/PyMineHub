class LevelDBError(Exception):
    pass


class LevelDB:

    # noinspection PyUnusedLocal
    def __init__(self, path: str) -> None:
        pass

    # noinspection PyPep8Naming
    def Get(self, *args, **kwargs) -> bytes:
        raise LevelDBError()
