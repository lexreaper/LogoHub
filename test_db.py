from datetime import date, datetime, timedelta

from app.database import SessionLocal
from app.models.user import User
from app.models.patient import Patient
from app.models.speech_therapist import SpeechTherapist
from app.models.specialization import Specialization
from app.models.appointment import Appointment
from app.models.visit_record import VisitRecord
from app.models.speech_therapist_specialization import SpeechTherapistSpecialization

from app.crud.user import (
    create_user,
    get_user,
    get_user_by_email,
    get_users,
    update_user,
)
from app.crud.patients import (
    create_patient,
    get_patient,
    get_patients,
    update_patient,
)
from app.crud.speech_therapist import (
    create_speech_therapist,
    get_speech_therapist,
    get_speech_therapists,
    update_speech_therapist,
)
from app.crud.specializations import (
    create_specialization,
    get_specialization,
    get_specializations,
    update_specialization,
    delete_specialization,
)
from app.crud.therapist_specializations import (
    add_specialization_to_therapist,
    get_therapist_specializations,
)
from app.crud.appointments import (
    create_appointment,
    get_appointment,
    get_appointments,
    get_appointments_by_patient,
    get_appointments_by_therapist,
    update_appointment,
)
from app.crud.visit_records import (
    create_visit_record,
    get_visit_record,
    get_visit_record_by_appointment,
    get_visit_records,
    update_visit_record,
)


def print_section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def clear_database(db) -> None:
    """Очищает тестовые таблицы, чтобы скрипт можно было запускать повторно."""
    db.query(VisitRecord).delete()
    db.query(Appointment).delete()
    db.query(SpeechTherapistSpecialization).delete()
    db.query(Patient).delete()
    db.query(SpeechTherapist).delete()
    db.query(Specialization).delete()
    db.query(User).delete()
    db.commit()


def main() -> None:
    db = SessionLocal()

    try:
        print_section("0. Подготовка тестовой базы")
        clear_database(db)
        print("База очищена. Начинаем демонстрацию CRUD и сценариев ЛР1.")

        print_section("1. Создание пользователей")

        patient_user = create_user(
            db=db,
            email="patient@example.com",
            password_hash="test_hash_patient",
            role="patient",
            full_name="Иванов Иван Иванович",
        )

        therapist_user = create_user(
            db=db,
            email="therapist@example.com",
            password_hash="test_hash_therapist",
            role="speech_therapist",
            full_name="Петрова Анна Сергеевна",
        )

        admin_user = create_user(
            db=db,
            email="admin@example.com",
            password_hash="test_hash_admin",
            role="admin",
            full_name="Администратор Системы",
        )

        print(f"Создан пациент: id={patient_user.id}, {patient_user.full_name}")
        print(f"Создан логопед: id={therapist_user.id}, {therapist_user.full_name}")
        print(f"Создан администратор: id={admin_user.id}, {admin_user.full_name}")

        print("\nВсе пользователи:")
        for user in get_users(db):
            print(f"  id={user.id}, email={user.email}, role={user.role}, ФИО={user.full_name}")

        found_user = get_user_by_email(db, "patient@example.com")
        print(f"\nПоиск по email: {found_user.full_name if found_user else 'не найден'}")

        updated_admin = update_user(
            db=db,
            user_id=admin_user.id,
            full_name="Главный Администратор",
        )
        print(f"Изменён пользователь: {updated_admin.full_name}")

        print_section("2. Создание профиля пациента")

        patient = create_patient(
            db=db,
            user_id=patient_user.id,
            birth_date=date(2003, 5, 15),
            phone="+7-900-111-22-33",
        )
        print(
            f"Пациент: id={patient.id}, user_id={patient.user_id}, "
            f"дата рождения={patient.birth_date}, телефон={patient.phone}"
        )

        updated_patient = update_patient(
            db=db,
            patient_id=patient.id,
            phone="+7-900-999-88-77",
        )
        print(f"Телефон после изменения: {updated_patient.phone}")

        print(f"Количество пациентов в БД: {len(get_patients(db))}")
        assert get_patient(db, patient.id) is not None

        print_section("3. Создание профиля логопеда")

        therapist = create_speech_therapist(
            db=db,
            user_id=therapist_user.id,
            description="Логопед, работающий с нарушениями звукопроизношения и речи.",
            experience_years=5,
        )
        print(
            f"Логопед: id={therapist.id}, user_id={therapist.user_id}, "
            f"стаж={therapist.experience_years} лет"
        )

        updated_therapist = update_speech_therapist(
            db=db,
            therapist_id=therapist.id,
            experience_years=6,
        )
        print(f"Стаж после изменения: {updated_therapist.experience_years} лет")

        print(f"Количество логопедов в БД: {len(get_speech_therapists(db))}")
        assert get_speech_therapist(db, therapist.id) is not None

        print_section("4. Специализации и связь многие-ко-многим")

        spec_speech = create_specialization(
            db=db,
            name="Развитие речи",
            description="Развитие устной речи и словарного запаса.",
        )
        spec_pronunciation = create_specialization(
            db=db,
            name="Коррекция звукопроизношения",
            description="Постановка и автоматизация звуков.",
        )

        add_specialization_to_therapist(db, therapist.id, spec_speech.id)
        add_specialization_to_therapist(db, therapist.id, spec_pronunciation.id)

        print("Специализации логопеда:")
        for spec in get_therapist_specializations(db, therapist.id):
            print(f"  id={spec.id}, {spec.name}")

        updated_spec = update_specialization(
            db=db,
            spec_id=spec_speech.id,
            description="Развитие речи, словарного запаса и связной речи.",
        )
        print(f"\nОбновлено описание специализации: {updated_spec.description}")
        print(f"Всего специализаций: {len(get_specializations(db))}")
        assert get_specialization(db, spec_speech.id) is not None

        print_section("5. Создание записи на приём")

        appointment_time = datetime.now().replace(
            second=0,
            microsecond=0,
        ) + timedelta(days=1)

        appointment = create_appointment(
            db=db,
            patient_id=patient.id,
            speech_therapist_id=therapist.id,
            appointment_at=appointment_time,
        )

        print(
            f"Создана запись: id={appointment.id}, "
            f"дата={appointment.appointment_at}, статус={appointment.status}"
        )

        print("\nЗаписи пациента:")
        for appt in get_appointments_by_patient(db, patient.id):
            print(
                f"  id={appt.id}, логопед={appt.speech_therapist_id}, "
                f"дата={appt.appointment_at}, статус={appt.status}"
            )

        print("\nРасписание логопеда:")
        for appt in get_appointments_by_therapist(db, therapist.id):
            print(
                f"  id={appt.id}, пациент={appt.patient_id}, "
                f"дата={appt.appointment_at}, статус={appt.status}"
            )

        print(f"\nВсего записей: {len(get_appointments(db))}")
        assert get_appointment(db, appointment.id) is not None

        print_section("6. Завершение приёма")

        completed_appointment = update_appointment(
            db=db,
            appt_id=appointment.id,
            status="completed",
        )
        print(f"Новый статус записи: {completed_appointment.status}")

        print_section("7. Создание результата посещения")

        visit_record = create_visit_record(
            db=db,
            appointment_id=appointment.id,
            description="Проведена диагностика речи и упражнения на постановку звуков.",
            result="Выявлены отдельные нарушения звукопроизношения.",
            recommendations="Выполнять артикуляционную гимнастику ежедневно.",
        )

        print(f"Создан результат посещения: id={visit_record.id}")
        print(f"Описание: {visit_record.description}")
        print(f"Результат: {visit_record.result}")
        print(f"Рекомендации: {visit_record.recommendations}")

        record_by_appointment = get_visit_record_by_appointment(db, appointment.id)
        print(
            "\nПоиск результата по записи: "
            f"{record_by_appointment.result if record_by_appointment else 'не найден'}"
        )
        assert get_visit_record(db, visit_record.id) is not None
        print(f"Всего результатов посещений: {len(get_visit_records(db))}")

        print_section("8. Редактирование результата посещения")

        updated_record = update_visit_record(
            db=db,
            record_id=visit_record.id,
            recommendations=(
                "Выполнять артикуляционную гимнастику ежедневно "
                "по 10 минут и повторно посетить логопеда через неделю."
            ),
        )
        print(f"Новые рекомендации: {updated_record.recommendations}")

        print_section("9. Демонстрация удаления")

        temp_spec = create_specialization(
            db=db,
            name="Временная специализация",
            description="Создана только для проверки операции DELETE.",
        )
        print(f"Создана временная специализация: id={temp_spec.id}")

        deleted = delete_specialization(db, temp_spec.id)
        print(f"Удаление выполнено: {deleted}")
        print(
            "Проверка после удаления: "
            + ("запись отсутствует" if get_specialization(db, temp_spec.id) is None else "ошибка")
        )

        print_section("10. Итог")
        print("ЛР1: тестовый сценарий выполнен успешно.")
        print("Продемонстрированы CREATE, READ, UPDATE и DELETE,")
        print("связь M:N, запись пациента на приём и сохранение результата посещения.")

    except Exception as error:
        db.rollback()
        print("\nОШИБКА ПРИ ВЫПОЛНЕНИИ ТЕСТА:")
        print(error)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
