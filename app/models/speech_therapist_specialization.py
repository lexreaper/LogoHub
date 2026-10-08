from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SpeechTherapistSpecialization(Base):
    __tablename__ = "speech_therapist_specializations"

    speech_therapist_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("speech_therapists.id", ondelete="CASCADE"),
        primary_key=True
    )

    specialization_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("specializations.id", ondelete="CASCADE"),
        primary_key=True
    )