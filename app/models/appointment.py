from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        UniqueConstraint(
            "speech_therapist_id", "appointment_at",
            name="uq_therapist_appointment_time"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"), nullable=False
    )
    speech_therapist_id: Mapped[int] = mapped_column(
        ForeignKey("speech_therapists.id"), nullable=False
    )
    appointment_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    patient = relationship("Patient", back_populates="appointments")
    speech_therapist = relationship(
        "SpeechTherapist", back_populates="appointments"
    )
    visit_record = relationship(
        "VisitRecord", back_populates="appointment", uselist=False
    )