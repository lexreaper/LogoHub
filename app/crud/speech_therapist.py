from sqlalchemy.orm import Session

from app.models.speech_therapist import SpeechTherapist


def create_speech_therapist(
    db: Session,
    user_id: int,
    description: str | None,
    experience_years: int
) -> SpeechTherapist:

    therapist = SpeechTherapist(
        user_id=user_id,
        description=description,
        experience_years=experience_years
    )

    db.add(therapist)
    db.commit()
    db.refresh(therapist)

    return therapist


def get_speech_therapist(
    db: Session,
    therapist_id: int
) -> SpeechTherapist | None:

    return db.get(SpeechTherapist, therapist_id)


def get_speech_therapists(
    db: Session
) -> list[SpeechTherapist]:

    return db.query(SpeechTherapist).all()


def update_speech_therapist(
    db: Session,
    therapist_id: int,
    description: str | None = None,
    experience_years: int | None = None
) -> SpeechTherapist | None:

    therapist = db.get(SpeechTherapist, therapist_id)

    if therapist is None:
        return None

    if description is not None:
        therapist.description = description

    if experience_years is not None:
        therapist.experience_years = experience_years

    db.commit()
    db.refresh(therapist)

    return therapist


def delete_speech_therapist(
    db: Session,
    therapist_id: int
) -> bool:

    therapist = db.get(SpeechTherapist, therapist_id)

    if therapist is None:
        return False

    db.delete(therapist)
    db.commit()

    return True