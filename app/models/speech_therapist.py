from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SpeechTherapist(Base):
    __tablename__ = "speech_therapists"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    experience_years: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="speech_therapist"
    )

    appointments = relationship(
        "Appointment",
        back_populates="speech_therapist"
    )

    specializations = relationship(
        "Specialization",
        secondary="speech_therapist_specializations",
        back_populates="speech_therapists"
    )