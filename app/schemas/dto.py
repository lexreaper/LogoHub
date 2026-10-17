from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class DTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
class Register(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1)
    birth_date: date
    phone: str | None = None
class Login(BaseModel):
    email: EmailStr
    password: str
class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
class UserOut(DTO):
    id: int
    email: str
    role: str
    full_name: str
class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
class PatientOut(DTO):
    id: int
    user_id: int
    birth_date: date
    phone: str | None
class PatientUpdate(BaseModel):
    birth_date: date | None = None
    phone: str | None = None
class TherapistCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    description: str | None = None
    experience_years: int = Field(ge=0)
class TherapistOut(DTO):
    id: int
    user_id: int
    description: str | None
    experience_years: int
class TherapistUpdate(BaseModel):
    description: str | None = None
    experience_years: int | None = Field(default=None, ge=0)
class SpecCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
class SpecUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
class SpecOut(DTO):
    id: int
    name: str
    description: str | None
class AppointmentCreate(BaseModel):
    speech_therapist_id: int
    appointment_at: datetime
class AppointmentUpdate(BaseModel):
    appointment_at: datetime | None = None
    status: str | None = None
class AppointmentOut(DTO):
    id: int
    patient_id: int
    speech_therapist_id: int
    appointment_at: datetime
    status: str
    created_at: datetime
class RecordCreate(BaseModel):
    appointment_id: int
    description: str | None = None
    result: str | None = None
    recommendations: str | None = None
class RecordUpdate(BaseModel):
    description: str | None = None
    result: str | None = None
    recommendations: str | None = None
class RecordOut(DTO):
    id: int
    appointment_id: int
    description: str | None
    result: str | None
    recommendations: str | None
    created_at: datetime
