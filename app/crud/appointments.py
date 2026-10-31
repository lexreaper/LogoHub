from datetime import datetime
from sqlalchemy.orm import Session
from app.models.appointment import Appointment


def create_appointment(
    db: Session,
    patient_id: int,
    speech_therapist_id: int,
    appointment_at: datetime,
    status: str = "scheduled"
) -> Appointment:
    appt = Appointment(
        patient_id=patient_id,
        speech_therapist_id=speech_therapist_id,
        appointment_at=appointment_at,
        status=status,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


def get_appointment(db: Session, appt_id: int) -> Appointment | None:
    return db.get(Appointment, appt_id)


def get_appointments(db: Session) -> list[Appointment]:
    return db.query(Appointment).all()


def get_appointments_by_patient(db: Session, patient_id: int) -> list[Appointment]:
    return db.query(Appointment).filter(Appointment.patient_id == patient_id).all()


def get_appointments_by_therapist(db: Session, therapist_id: int) -> list[Appointment]:
    return db.query(Appointment).filter(
        Appointment.speech_therapist_id == therapist_id
    ).all()


def update_appointment(
    db: Session,
    appt_id: int,
    appointment_at: datetime | None = None,
    status: str | None = None
) -> Appointment | None:
    appt = db.get(Appointment, appt_id)
    if appt is None:
        return None
    if appointment_at is not None:
        appt.appointment_at = appointment_at
    if status is not None:
        appt.status = status
    db.commit()
    db.refresh(appt)
    return appt


def delete_appointment(db: Session, appt_id: int) -> bool:
    appt = db.get(Appointment, appt_id)
    if appt is None:
        return False
    db.delete(appt)
    db.commit()
    return True