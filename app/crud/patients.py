from datetime import date

from sqlalchemy.orm import Session

from app.models.patient import Patient


def create_patient(
    db: Session,
    user_id: int,
    birth_date: date,
    phone: str | None = None
) -> Patient:

    patient = Patient(
        user_id=user_id,
        birth_date=birth_date,
        phone=phone
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.get(Patient, patient_id)


def get_patients(db: Session) -> list[Patient]:
    return db.query(Patient).all()


def update_patient(
    db: Session,
    patient_id: int,
    birth_date: date | None = None,
    phone: str | None = None
) -> Patient | None:

    patient = db.get(Patient, patient_id)

    if patient is None:
        return None

    if birth_date is not None:
        patient.birth_date = birth_date

    if phone is not None:
        patient.phone = phone

    db.commit()
    db.refresh(patient)

    return patient


def delete_patient(db: Session, patient_id: int) -> bool:
    patient = db.get(Patient, patient_id)

    if patient is None:
        return False

    db.delete(patient)
    db.commit()

    return True