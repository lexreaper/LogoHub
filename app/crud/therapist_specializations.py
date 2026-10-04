from sqlalchemy.orm import Session
from app.models.speech_therapist import SpeechTherapist
from app.models.specialization import Specialization


def add_specialization_to_therapist(
    db: Session, therapist_id: int, specialization_id: int
) -> bool:
    therapist = db.get(SpeechTherapist, therapist_id)
    spec = db.get(Specialization, specialization_id)
    if therapist is None or spec is None:
        return False
    if spec not in therapist.specializations:
        therapist.specializations.append(spec)
        db.commit()
    return True


def remove_specialization_from_therapist(
    db: Session, therapist_id: int, specialization_id: int
) -> bool:
    therapist = db.get(SpeechTherapist, therapist_id)
    spec = db.get(Specialization, specialization_id)
    if therapist is None or spec is None:
        return False
    if spec in therapist.specializations:
        therapist.specializations.remove(spec)
        db.commit()
    return True


def get_therapist_specializations(
    db: Session, therapist_id: int
) -> list[Specialization]:
    therapist = db.get(SpeechTherapist, therapist_id)
    return therapist.specializations if therapist else []