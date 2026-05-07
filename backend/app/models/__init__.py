# Models module
from app.models.base import BaseModel, TimestampMixin
from app.models.user import User, StudentProfile, UserRole
from app.models.teacher_profile import TeacherProfile
from app.models.course import Course
from app.models.course_catalog import CourseCatalog
from app.models.schedule import Schedule
from app.models.review import ReviewRecord, Transcription, Summary
from app.models.chat import Conversation, Message
from app.models.knowledge import KnowledgeBase
from app.models.admin import AdminUser
from app.models.timetable import CourseAIInsight, CourseReminder
from app.models.translation import TranslationTask

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "User",
    "StudentProfile",
    "UserRole",
    "TeacherProfile",
    "Course",
    "CourseCatalog",
    "Schedule",
    "ReviewRecord",
    "Transcription",
    "Summary",
    "Conversation",
    "Message",
    "KnowledgeBase",
    "AdminUser",
    "CourseAIInsight",
    "CourseReminder",
    "TranslationTask",
]
