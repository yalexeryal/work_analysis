"""
Модули для обработки различных типов заданий.
"""
from .diploma import process_diploma_works
from .homework import process_unverified_works
from .course import CourseWorksProcessor, process_course_works

__all__ = [
    'process_diploma_works',
    'process_unverified_works',
    'CourseWorksProcessor',
    'process_course_works'
]