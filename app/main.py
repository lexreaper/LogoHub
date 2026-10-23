"""REST API центра логопедии (ЛР2).

Маршруты разделены на группы: авторизация, пользователи, пациенты,
логопеды, специализации, записи на приём, результаты посещений.
Проверки ролей нужны для дополнительного задания с JWT.
"""

from collections.abc import Generator
from datetime import datetime
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import jwt
from app.database import SessionLocal
from app.models import User, Patient, SpeechTherapist, Specialization, Appointment, VisitRecord
from app.schemas.dto import Register, Login, Token, UserOut, UserUpdate, PatientOut, PatientUpdate, TherapistCreate, TherapistOut, TherapistUpdate, SpecCreate, SpecUpdate, SpecOut, AppointmentCreate, AppointmentUpdate, AppointmentOut, RecordCreate, RecordUpdate, RecordOut
from app.security import hash_password, verify_password, create_token, decode_token
# Создаём HTTP-приложение FastAPI.
app = FastAPI(title='Центр логопедии — REST API', version='2.0')
bearer = HTTPBearer(auto_error=False)

# Одна сессия PostgreSQL на один запрос.
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
DatabaseSession = Annotated[Session, Depends(get_db)]

# Из Bearer-токена получаем ID и загружаем пользователя из БД.
def current_user(db: DatabaseSession, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> User:
    if not credentials:
        raise HTTPException(401, 'Bearer token required', headers={'WWW-Authenticate': 'Bearer'})
    try:
        uid = decode_token(credentials.credentials)
    except (jwt.PyJWTError, ValueError, TypeError):
        raise HTTPException(401, 'Invalid or expired token', headers={'WWW-Authenticate': 'Bearer'})
    user = db.get(User, uid)
    if not user:
        raise HTTPException(401, 'User not found')
    return user
CurrentUser = Annotated[User, Depends(current_user)]

# Проверка роли: при недостаточных правах возвращаем HTTP 403.
def require(*roles):

    def check(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(403, 'Insufficient permissions')
        return user
    return check
AdminUser = Annotated[User, Depends(require('admin'))]
TherapistUser = Annotated[User, Depends(require('speech_therapist'))]

def get_or_404(db, model, key):
    obj = db.get(model, key)
    if not obj:
        raise HTTPException(404, f'{model.__name__} not found')
    return obj

def save(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Database constraint conflict')

def own_patient(db, user):
    patient = db.query(Patient).filter_by(user_id=user.id).first()
    if not patient:
        raise HTTPException(403, 'Patient profile required')
    return patient

def own_therapist(db, user):
    therapist = db.query(SpeechTherapist).filter_by(user_id=user.id).first()
    if not therapist:
        raise HTTPException(403, 'TherapistUser profile required')
    return therapist

def can_see_appointment(db, user, a):
    if user.role == 'admin':
        return True
    if user.role == 'patient':
        return a.patient_id == own_patient(db, user).id
    if user.role == 'speech_therapist':
        return a.speech_therapist_id == own_therapist(db, user).id
    return False

@app.get('/health')
def health():
    return {'status': 'ok'}

# Регистрация пациента и вход в систему.
@app.post('/auth/register', response_model=UserOut, status_code=201)
def register(data: Register, db: DatabaseSession):
    if db.query(User).filter_by(email=data.email).first():
        raise HTTPException(409, 'Email already registered')
    user = User(email=data.email, password_hash=hash_password(data.password), role='patient', full_name=data.full_name)
    db.add(user)
    db.flush()
    db.add(Patient(user_id=user.id, birth_date=data.birth_date, phone=data.phone))
    save(db)
    db.refresh(user)
    return user

@app.post('/auth/login', response_model=Token)
def login(data: Login, db: DatabaseSession):
    user = db.query(User).filter_by(email=data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, 'Invalid credentials')
    return Token(access_token=create_token(user.id))

@app.get('/users/me', response_model=UserOut)
def me(user: CurrentUser):
    return user

@app.patch('/users/me', response_model=UserOut)
def edit_me(data: UserUpdate, db: DatabaseSession, user: CurrentUser):
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(user, key, value)
    save(db)
    db.refresh(user)
    return user

@app.get('/users', response_model=list[UserOut])
def users(db: DatabaseSession, admin: AdminUser):
    return db.query(User).all()

@app.get('/users/{user_id}', response_model=UserOut)
def user_by_id(user_id: int, db: DatabaseSession, admin: AdminUser):
    return get_or_404(db, User, user_id)

@app.delete('/users/{user_id}', status_code=204)
def delete_user(user_id: int, db: DatabaseSession, admin: AdminUser):
    if user_id == admin.id:
        raise HTTPException(400, 'Cannot delete own account')
    user = get_or_404(db, User, user_id)
    if user.patient or user.speech_therapist:
        raise HTTPException(409, 'Delete dependent records first')
    db.delete(user)
    save(db)

@app.get('/patients/me', response_model=PatientOut)
def patient_me(db: DatabaseSession, user: CurrentUser):
    return own_patient(db, user)

@app.patch('/patients/me', response_model=PatientOut)
def edit_patient(data: PatientUpdate, db: DatabaseSession, user: CurrentUser):
    patient = own_patient(db, user)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    save(db)
    db.refresh(patient)
    return patient

@app.get('/patients', response_model=list[PatientOut])
def patients(db: DatabaseSession, admin: AdminUser):
    return db.query(Patient).all()

@app.get('/patients/{patient_id}', response_model=PatientOut)
def patient_by_id(patient_id: int, db: DatabaseSession, user: CurrentUser):
    patient = get_or_404(db, Patient, patient_id)
    if user.role == 'admin' or (user.role == 'patient' and patient.user_id == user.id):
        return patient
    if user.role == 'speech_therapist':
        therapist = own_therapist(db, user)
        if db.query(Appointment).filter_by(patient_id=patient_id, speech_therapist_id=therapist.id).first():
            return patient
    raise HTTPException(403, 'Access denied')

@app.post('/therapists', response_model=TherapistOut, status_code=201)
def create_therapist(data: TherapistCreate, db: DatabaseSession, admin: AdminUser):
    user = User(email=data.email, password_hash=hash_password(data.password), role='speech_therapist', full_name=data.full_name)
    db.add(user)
    db.flush()
    therapist = SpeechTherapist(user_id=user.id, description=data.description, experience_years=data.experience_years)
    db.add(therapist)
    save(db)
    db.refresh(therapist)
    return therapist

@app.get('/therapists', response_model=list[TherapistOut])
def therapists(db: DatabaseSession):
    return db.query(SpeechTherapist).all()

@app.get('/therapists/{therapist_id}', response_model=TherapistOut)
def therapist_by_id(therapist_id: int, db: DatabaseSession):
    return get_or_404(db, SpeechTherapist, therapist_id)

@app.patch('/therapists/{therapist_id}', response_model=TherapistOut)
def edit_therapist(therapist_id: int, data: TherapistUpdate, db: DatabaseSession, admin: AdminUser):
    obj = get_or_404(db, SpeechTherapist, therapist_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    save(db)
    db.refresh(obj)
    return obj

@app.delete('/therapists/{therapist_id}', status_code=204)
def delete_therapist(therapist_id: int, db: DatabaseSession, admin: AdminUser):
    obj = get_or_404(db, SpeechTherapist, therapist_id)
    if db.query(Appointment).filter_by(speech_therapist_id=therapist_id).first():
        raise HTTPException(409, 'TherapistUser has appointments')
    obj.specializations.clear()
    db.delete(obj)
    save(db)

@app.post('/specializations', response_model=SpecOut, status_code=201)
def create_spec(data: SpecCreate, db: DatabaseSession, admin: AdminUser):
    obj = Specialization(**data.model_dump())
    db.add(obj)
    save(db)
    db.refresh(obj)
    return obj

@app.get('/specializations', response_model=list[SpecOut])
def specs(db: DatabaseSession):
    return db.query(Specialization).all()

@app.get('/specializations/{spec_id}', response_model=SpecOut)
def spec_by_id(spec_id: int, db: DatabaseSession):
    return get_or_404(db, Specialization, spec_id)

@app.patch('/specializations/{spec_id}', response_model=SpecOut)
def edit_spec(spec_id: int, data: SpecUpdate, db: DatabaseSession, admin: AdminUser):
    obj = get_or_404(db, Specialization, spec_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    save(db)
    db.refresh(obj)
    return obj

@app.delete('/specializations/{spec_id}', status_code=204)
def delete_spec(spec_id: int, db: DatabaseSession, admin: AdminUser):
    obj = get_or_404(db, Specialization, spec_id)
    obj.speech_therapists.clear()
    db.delete(obj)
    save(db)

@app.get('/therapists/{therapist_id}/specializations', response_model=list[SpecOut])
def therapist_specs(therapist_id: int, db: DatabaseSession):
    return get_or_404(db, SpeechTherapist, therapist_id).specializations

@app.put('/therapists/{therapist_id}/specializations/{spec_id}', status_code=204)
def assign_spec(therapist_id: int, spec_id: int, db: DatabaseSession, admin: AdminUser):
    obj = get_or_404(db, SpeechTherapist, therapist_id)
    spec = get_or_404(db, Specialization, spec_id)
    if spec not in obj.specializations:
        obj.specializations.append(spec)
        save(db)

@app.delete('/therapists/{therapist_id}/specializations/{spec_id}', status_code=204)
def unassign_spec(therapist_id: int, spec_id: int, db: DatabaseSession, admin: AdminUser):
    obj = get_or_404(db, SpeechTherapist, therapist_id)
    spec = get_or_404(db, Specialization, spec_id)
    if spec in obj.specializations:
        obj.specializations.remove(spec)
        save(db)

# Пациент записывается на приём; логопед завершает приём.
@app.post('/appointments', response_model=AppointmentOut, status_code=201)
def create_appointment(data: AppointmentCreate, db: DatabaseSession, user: CurrentUser):
    if user.role != 'patient':
        raise HTTPException(403, 'Only patients can book')
    patient = own_patient(db, user)
    get_or_404(db, SpeechTherapist, data.speech_therapist_id)
    if data.appointment_at <= datetime.now(data.appointment_at.tzinfo):
        raise HTTPException(400, 'Appointment must be in future')
    obj = Appointment(patient_id=patient.id, speech_therapist_id=data.speech_therapist_id, appointment_at=data.appointment_at.replace(tzinfo=None), status='scheduled')
    db.add(obj)
    save(db)
    db.refresh(obj)
    return obj

@app.get('/appointments', response_model=list[AppointmentOut])
def appointments(db: DatabaseSession, user: CurrentUser):
    q = db.query(Appointment)
    if user.role == 'patient':
        q = q.filter_by(patient_id=own_patient(db, user).id)
    elif user.role == 'speech_therapist':
        q = q.filter_by(speech_therapist_id=own_therapist(db, user).id)
    elif user.role != 'admin':
        raise HTTPException(403)
    return q.all()

@app.get('/appointments/{appointment_id}', response_model=AppointmentOut)
def appointment_by_id(appointment_id: int, db: DatabaseSession, user: CurrentUser):
    obj = get_or_404(db, Appointment, appointment_id)
    if not can_see_appointment(db, user, obj):
        raise HTTPException(403)
    return obj

@app.patch('/appointments/{appointment_id}', response_model=AppointmentOut)
def edit_appointment(appointment_id: int, data: AppointmentUpdate, db: DatabaseSession, user: CurrentUser):
    obj = get_or_404(db, Appointment, appointment_id)
    if not can_see_appointment(db, user, obj):
        raise HTTPException(403)
    if obj.status != 'scheduled':
        raise HTTPException(409, 'Appointment already finalized')
    if user.role == 'patient':
        if data.status != 'cancelled' or data.appointment_at is not None:
            raise HTTPException(403, 'Patient can only cancel')
    elif user.role == 'speech_therapist':
        if data.status != 'completed' or data.appointment_at is not None:
            raise HTTPException(403, 'TherapistUser can only complete')
    elif data.status not in (None, 'cancelled') or data.appointment_at is not None:
        raise HTTPException(403, 'AdminUser can only cancel')
    if data.status is not None:
        obj.status = data.status
    save(db)
    db.refresh(obj)
    return obj

@app.delete('/appointments/{appointment_id}', status_code=204)
def delete_appointment(appointment_id: int, db: DatabaseSession, admin: AdminUser):
    obj = get_or_404(db, Appointment, appointment_id)
    if obj.visit_record:
        raise HTTPException(409, 'Appointment has visit record')
    db.delete(obj)
    save(db)

@app.post('/visit-records', response_model=RecordOut, status_code=201)
def create_record(data: RecordCreate, db: DatabaseSession, therapist_user: TherapistUser):
    obj = get_or_404(db, Appointment, data.appointment_id)
    if obj.speech_therapist_id != own_therapist(db, therapist_user).id:
        raise HTTPException(403)
    if obj.status != 'completed':
        raise HTTPException(409, 'Complete appointment first')
    record = VisitRecord(**data.model_dump())
    db.add(record)
    save(db)
    db.refresh(record)
    return record

@app.get('/visit-records', response_model=list[RecordOut])
def records(db: DatabaseSession, user: CurrentUser):
    q = db.query(VisitRecord).join(Appointment)
    if user.role == 'patient':
        q = q.filter(Appointment.patient_id == own_patient(db, user).id)
    elif user.role == 'speech_therapist':
        q = q.filter(Appointment.speech_therapist_id == own_therapist(db, user).id)
    elif user.role != 'admin':
        raise HTTPException(403)
    return q.all()

@app.get('/visit-records/{record_id}', response_model=RecordOut)
def record_by_id(record_id: int, db: DatabaseSession, user: CurrentUser):
    record = get_or_404(db, VisitRecord, record_id)
    if not can_see_appointment(db, user, record.appointment):
        raise HTTPException(403)
    return record

@app.patch('/visit-records/{record_id}', response_model=RecordOut)
def edit_record(record_id: int, data: RecordUpdate, db: DatabaseSession, therapist_user: TherapistUser):
    obj = get_or_404(db, VisitRecord, record_id)
    if obj.appointment.speech_therapist_id != own_therapist(db, therapist_user).id:
        raise HTTPException(403)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    save(db)
    db.refresh(obj)
    return obj

@app.delete('/visit-records/{record_id}', status_code=204)
def delete_record(record_id: int, db: DatabaseSession, therapist_user: TherapistUser):
    obj = get_or_404(db, VisitRecord, record_id)
    if obj.appointment.speech_therapist_id != own_therapist(db, therapist_user).id:
        raise HTTPException(403)
    db.delete(obj)
    save(db)
