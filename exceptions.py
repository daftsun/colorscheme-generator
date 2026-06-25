class LocationError(Exception):
    def __init__(self, location: str) -> None:
        super().__init__(f"File doesn't exists at: {location}")


class PaletteError(Exception):
    def __init__(self) -> None:
        super().__init__("No color palette found for image")


class IndexChosenError(Exception):
    def __init__(self, max_idx: int, inp_idx: int) -> None:
        super().__init__(f"Index: {inp_idx} not between 0 and {max_idx - 1}")