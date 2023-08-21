import enum
from pathlib import Path

_DATA_ROOT_PATH = Path(__file__).parent.parent.parent.joinpath("data")


class DataDirectory(enum.Enum):
    BRONZE = _DATA_ROOT_PATH.joinpath("0_bronze")
    SILVER = _DATA_ROOT_PATH.joinpath("1_silver")
    GOLD = _DATA_ROOT_PATH.joinpath("2_gold")
