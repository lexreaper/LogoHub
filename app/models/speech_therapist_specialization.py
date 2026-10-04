from sqlalchemy import BigInteger, Column, ForeignKey, Table
from app.database import Base


speech_therapist_specializations = Table(
    "speech_therapist_specializations",
    Base.metadata,
    Column(
        "speech_therapist_id",
        BigInteger,
        ForeignKey("speech_therapists.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "specialization_id",
        BigInteger,
        ForeignKey("specializations.id", ondelete="CASCADE"),
        primary_key=True
    ),
)