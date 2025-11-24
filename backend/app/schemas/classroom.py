from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

class ClassroomBase(BaseModel):
    name: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Classroom name cannot be empty')
        return v.strip()

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomResponse(ClassroomBase):
    id: int
    teacher_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AddStudentRequest(BaseModel):
    student_email: str

class StudentInClassroom(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    classroom_id: int
    student: "UserResponse"

    class Config:
        from_attributes = True

