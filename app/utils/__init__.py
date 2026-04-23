"""
utils/__init__.py
-----------------
Expose les utilitaires principaux.
Usage : from app.utils import role_required, get_global_stats
"""

from app.utils.decorators import (
    role_required,
    student_required,
    teacher_required,
    admin_required,
)
from app.utils.helpers import (
    allowed_file,
    save_file,
    get_global_stats,
    get_teacher_stats,
    get_student_stats,
    format_date,
)

__all__ = [
    "role_required",
    "student_required",
    "teacher_required",
    "admin_required",
    "allowed_file",
    "save_file",
    "get_global_stats",
    "get_teacher_stats",
    "get_student_stats",
    "format_date",
]
