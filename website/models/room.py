from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from website import db


class Strain(db.Model):
    __tablename__ = "strains"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    @property
    def initials(self) -> str:
        parts = self.name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        elif len(parts) == 1:
            return parts[0][0].upper()
        return self.name[0].upper()


class Pot(db.Model):
    __tablename__ = "pots"

    id: Mapped[int] = mapped_column(primary_key=True)
    light_id: Mapped[int] = mapped_column(ForeignKey("lights.id"))
    strain_id: Mapped[int] = mapped_column(ForeignKey("strains.id"), nullable=True)
    strain: Mapped[Strain] = relationship()

    def __init__(self, light_id: int) -> None:
        super().__init__()
        self.light_id = light_id


class Light(db.Model):
    __tablename__ = "lights"

    id: Mapped[int] = mapped_column(primary_key=True)
    tray_id: Mapped[int] = mapped_column(ForeignKey("trays.id"))
    width: Mapped[int] = mapped_column()
    height: Mapped[int] = mapped_column()
    pots: Mapped[list[Pot]] = relationship()

    def __init__(self, tray_id: int, width: int, height: int, pots: list[Pot]) -> None:
        super().__init__()
        self.tray_id = tray_id
        self.width = width
        self.height = height
        self.pots = pots


class Tray(db.Model):
    __tablename__ = "trays"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    name: Mapped[str] = mapped_column()
    planted_date: Mapped[datetime | None] = mapped_column()
    harvest_date: Mapped[datetime | None] = mapped_column()
    lights: Mapped[list[Light]] = relationship()

    def __init__(
        self, room_id: int, name: str, num_of_lights: int, width: int, height: int
    ) -> None:
        super().__init__()
        self.room_id = room_id
        self.name = name
        self.lights = [
            Light(
                self.id,
                width,
                height,
                [Pot(i + 1) for j in range(width * height)],
            )
            for i in range(num_of_lights)
        ]

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
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    trays: Mapped[list[Tray]] = relationship(cascade="all, delete-orphan")

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

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
