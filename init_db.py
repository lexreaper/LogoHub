from app.database import Base, engine

from app.models.user import User
from app.models.patient import Patient
from app.models.speech_therapist import SpeechTherapist
from app.models.specialization import Specialization
from app.models.speech_therapist_specialization import speech_therapist_specializations
from app.models.appointment import Appointment
from app.models.visit_record import VisitRecord


def init_db():
    print("Таблицы, известные SQLAlchemy:")
    print(Base.metadata.tables.keys())

    Base.metadata.create_all(bind=engine)

    print("Таблицы успешно созданы.")


if __name__ == "__main__":
    init_db()