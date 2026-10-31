from sqlalchemy.orm import Session
from app.models.specialization import Specialization


def create_specialization(
    db: Session, name: str, description: str | None = None
) -> Specialization:
    spec = Specialization(name=name, description=description)
    db.add(spec)
    db.commit()
    db.refresh(spec)
    return spec


def get_specialization(db: Session, spec_id: int) -> Specialization | None:
    return db.get(Specialization, spec_id)


def get_specializations(db: Session) -> list[Specialization]:
    return db.query(Specialization).all()


def update_specialization(
    db: Session,
    spec_id: int,
    name: str | None = None,
    description: str | None = None
) -> Specialization | None:
    spec = db.get(Specialization, spec_id)
    if spec is None:
        return None
    if name is not None:
        spec.name = name
    if description is not None:
        spec.description = description
    db.commit()
    db.refresh(spec)
    return spec


def delete_specialization(db: Session, spec_id: int) -> bool:
    spec = db.get(Specialization, spec_id)
    if spec is None:
        return False
    db.delete(spec)
    db.commit()
    return True