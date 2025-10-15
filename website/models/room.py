from dataclasses import dataclass
from datetime import datetime

from website import db


@dataclass
class Strain:
    id: int
    name: str

    @property
    def initials(self) -> str:
        parts = self.name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        elif len(parts) == 1:
            return parts[0][0].upper()
        return self.name[0].upper()


@dataclass
class Pot:
    id: int
    strain: Strain | None = None


@dataclass
class Light:
    id: int
    width: int
    height: int
    pots: list[Pot]


@dataclass
class Tray:
    id: int
    name: str
    lights: list[Light]
    planted_date: datetime | None = None
    harvest_date: datetime | None = None

    @property
    def is_planted(self) -> bool:
        return self.planted_date is not None

    @property
    def days_since_planted(self) -> int:
        if not self.planted_date:
            return 0
        return (datetime.now() - self.planted_date).days

    @property
    def days_until_harvest(self) -> int:
        if not self.harvest_date:
            return 0
        return (self.harvest_date - datetime.now()).days


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    trays = db.Column(db.PickleType)

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.trays: list[Tray] = []

    @property
    def is_planted(self) -> bool:
        return any(tray.is_planted for tray in self.trays)

    @property
    def days_since_planted(self) -> int:
        if not self.is_planted:
            return 0
        return min(
            (tray.days_since_planted for tray in self.trays if tray.is_planted),
            default=0,
        )

    @property
    def days_for_harvest(self) -> int:
        if not self.is_planted:
            return 0
        days_until_harvest_list = [
            tray.days_until_harvest
            for tray in self.trays
            if tray.is_planted and tray.days_until_harvest is not None
        ]
        return min(days_until_harvest_list, default=0)
