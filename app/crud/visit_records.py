from sqlalchemy.orm import Session
from app.models.visit_record import VisitRecord


def create_visit_record(
    db: Session,
    appointment_id: int,
    description: str | None = None,
    result: str | None = None,
    recommendations: str | None = None
) -> VisitRecord:
    record = VisitRecord(
        appointment_id=appointment_id,
        description=description,
        result=result,
        recommendations=recommendations,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_visit_record(db: Session, record_id: int) -> VisitRecord | None:
    return db.get(VisitRecord, record_id)


def get_visit_record_by_appointment(
    db: Session, appointment_id: int
) -> VisitRecord | None:
    return (
        db.query(VisitRecord)
        .filter(VisitRecord.appointment_id == appointment_id)
        .first()
    )


def get_visit_records(db: Session) -> list[VisitRecord]:
    return db.query(VisitRecord).all()


def update_visit_record(
    db: Session,
    record_id: int,
    description: str | None = None,
    result: str | None = None,
    recommendations: str | None = None
) -> VisitRecord | None:
    record = db.get(VisitRecord, record_id)
    if record is None:
        return None
    if description is not None:
        record.description = description
    if result is not None:
        record.result = result
    if recommendations is not None:
        record.recommendations = recommendations
    db.commit()
    db.refresh(record)
    return record


def delete_visit_record(db: Session, record_id: int) -> bool:
    record = db.get(VisitRecord, record_id)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True