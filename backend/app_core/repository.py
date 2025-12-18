"""
Repository pattern for database abstraction.
Decouples business logic from database implementation.
"""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from app_core.db import db


class Repository(ABC):
    """Abstract base repository for all data entities."""
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """Find entity by id."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Dict[str, Any]]:
        """Find all entities."""
        pass
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> int:
        """Create new entity."""
        pass
    
    @abstractmethod
    def update(self, entity_id: int, data: Dict[str, Any]) -> bool:
        """Update entity."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete entity."""
        pass


class StudentRepository(Repository):
    """Repository for student entity."""
    
    TABLE = "students"
    
    def find_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Find student by id."""
        return db.fetch_one(
            f"SELECT * FROM {self.TABLE} WHERE id = %s",
            [student_id]
        )
    
    def find_by_no(self, student_no: str) -> Optional[Dict[str, Any]]:
        """Find student by student number."""
        return db.fetch_one(
            f"SELECT * FROM {self.TABLE} WHERE student_no = %s",
            [student_no]
        )
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Get all students."""
        return db.fetch_all(f"SELECT * FROM {self.TABLE} ORDER BY id")
    
    def find_by_major(self, major: str) -> List[Dict[str, Any]]:
        """Find students by major."""
        return db.fetch_all(
            f"SELECT * FROM {self.TABLE} WHERE major = %s ORDER BY id",
            [major]
        )
    
    def search(self, major: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search students with optional filters."""
        query = f"SELECT * FROM {self.TABLE} WHERE 1=1"
        params = []
        
        if major:
            query += " AND major = %s"
            params.append(major)
        
        if keyword:
            query += " AND (student_no ILIKE %s OR name ILIKE %s)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        query += " ORDER BY id"
        return db.fetch_all(query, params)
    
    def create(self, data: Dict[str, Any]) -> int:
        """Create new student."""
        return db.execute_returning(
            f"""INSERT INTO {self.TABLE} (student_no, name, major, password_hash)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            [data.get('student_no'), data.get('name'), data.get('major'), data.get('password_hash')]
        )
    
    def update(self, student_id: int, data: Dict[str, Any]) -> bool:
        """Update student."""
        fields = []
        values = []
        for key, val in data.items():
            fields.append(f"{key} = %s")
            values.append(val)
        
        if not fields:
            return True
        
        values.append(student_id)
        query = f"UPDATE {self.TABLE} SET {', '.join(fields)} WHERE id = %s"
        return db.execute(query, values)
    
    def delete(self, student_id: int) -> bool:
        """Delete student."""
        return db.execute(f"DELETE FROM {self.TABLE} WHERE id = %s", [student_id])


class TeacherRepository(Repository):
    """Repository for teacher entity."""
    
    TABLE = "teachers"
    
    def find_by_id(self, teacher_id: int) -> Optional[Dict[str, Any]]:
        """Find teacher by id."""
        return db.fetch_one(
            f"SELECT * FROM {self.TABLE} WHERE id = %s",
            [teacher_id]
        )
    
    def find_by_no(self, teacher_no: str) -> Optional[Dict[str, Any]]:
        """Find teacher by teacher number."""
        return db.fetch_one(
            f"SELECT * FROM {self.TABLE} WHERE teacher_no = %s",
            [teacher_no]
        )
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Get all teachers."""
        return db.fetch_all(f"SELECT * FROM {self.TABLE} ORDER BY id")
    
    def create(self, data: Dict[str, Any]) -> int:
        """Create new teacher."""
        return db.execute_returning(
            f"""INSERT INTO {self.TABLE} (teacher_no, name, department, password_hash)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            [data.get('teacher_no'), data.get('name'), data.get('department'), data.get('password_hash')]
        )
    
    def update(self, teacher_id: int, data: Dict[str, Any]) -> bool:
        """Update teacher."""
        fields = []
        values = []
        for key, val in data.items():
            fields.append(f"{key} = %s")
            values.append(val)
        
        if not fields:
            return True
        
        values.append(teacher_id)
        query = f"UPDATE {self.TABLE} SET {', '.join(fields)} WHERE id = %s"
        return db.execute(query, values)
    
    def delete(self, teacher_id: int) -> bool:
        """Delete teacher."""
        return db.execute(f"DELETE FROM {self.TABLE} WHERE id = %s", [teacher_id])


class CourseRepository(Repository):
    """Repository for course entity."""
    
    TABLE = "courses"
    
    def find_by_id(self, course_id: int) -> Optional[Dict[str, Any]]:
        """Find course by id."""
        return db.fetch_one(
            f"SELECT * FROM {self.TABLE} WHERE id = %s",
            [course_id]
        )
    
    def find_by_code(self, course_code: str) -> Optional[Dict[str, Any]]:
        """Find course by course code."""
        return db.fetch_one(
            f"SELECT * FROM {self.TABLE} WHERE course_code = %s",
            [course_code]
        )
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Get all courses."""
        return db.fetch_all(f"SELECT * FROM {self.TABLE} ORDER BY id")
    
    def find_by_teacher(self, teacher_id: int) -> List[Dict[str, Any]]:
        """Get courses by teacher."""
        return db.fetch_all(
            f"SELECT * FROM {self.TABLE} WHERE teacher_id = %s ORDER BY id",
            [teacher_id]
        )
    
    def create(self, data: Dict[str, Any]) -> int:
        """Create new course."""
        return db.execute_returning(
            f"""INSERT INTO {self.TABLE} (course_code, name, credit, capacity, teacher_id)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            [data.get('course_code'), data.get('name'), data.get('credit'), 
             data.get('capacity'), data.get('teacher_id')]
        )
    
    def update(self, course_id: int, data: Dict[str, Any]) -> bool:
        """Update course."""
        fields = []
        values = []
        for key, val in data.items():
            fields.append(f"{key} = %s")
            values.append(val)
        
        if not fields:
            return True
        
        values.append(course_id)
        query = f"UPDATE {self.TABLE} SET {', '.join(fields)} WHERE id = %s"
        return db.execute(query, values)
    
    def delete(self, course_id: int) -> bool:
        """Delete course."""
        return db.execute(f"DELETE FROM {self.TABLE} WHERE id = %s", [course_id])


class EnrollmentRepository(Repository):
    """Repository for enrollment entity."""
    
    TABLE = "enrollments"
    
    def find_by_id(self, enrollment_id: int) -> Optional[Dict[str, Any]]:
        """Find enrollment by id."""
        return db.fetch_one(
            f"SELECT * FROM {self.TABLE} WHERE id = %s",
            [enrollment_id]
        )
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Get all enrollments."""
        return db.fetch_all(f"SELECT * FROM {self.TABLE} ORDER BY id")
    
    def find_by_student(self, student_id: int) -> List[Dict[str, Any]]:
        """Get enrollments by student."""
        return db.fetch_all(
            f"SELECT * FROM {self.TABLE} WHERE student_id = %s ORDER BY id",
            [student_id]
        )
    
    def find_by_course(self, course_id: int) -> List[Dict[str, Any]]:
        """Get enrollments by course."""
        return db.fetch_all(
            f"SELECT * FROM {self.TABLE} WHERE course_id = %s ORDER BY id",
            [course_id]
        )
    
    def create(self, data: Dict[str, Any]) -> int:
        """Create new enrollment."""
        return db.execute_returning(
            f"""INSERT INTO {self.TABLE} (student_id, course_id, grade, status)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            [data.get('student_id'), data.get('course_id'), 
             data.get('grade'), data.get('status', 'enrolled')]
        )
    
    def update(self, enrollment_id: int, data: Dict[str, Any]) -> bool:
        """Update enrollment."""
        fields = []
        values = []
        for key, val in data.items():
            fields.append(f"{key} = %s")
            values.append(val)
        
        if not fields:
            return True
        
        values.append(enrollment_id)
        query = f"UPDATE {self.TABLE} SET {', '.join(fields)} WHERE id = %s"
        return db.execute(query, values)
    
    def delete(self, enrollment_id: int) -> bool:
        """Delete enrollment."""
        return db.execute(f"DELETE FROM {self.TABLE} WHERE id = %s", [enrollment_id])


# Repository container (简易的依赖注入)
class RepositoryContainer:
    """Container for all repositories."""
    
    _students = StudentRepository()
    _teachers = TeacherRepository()
    _courses = CourseRepository()
    _enrollments = EnrollmentRepository()
    
    @classmethod
    def students(cls) -> StudentRepository:
        """Get student repository."""
        return cls._students
    
    @classmethod
    def teachers(cls) -> TeacherRepository:
        """Get teacher repository."""
        return cls._teachers
    
    @classmethod
    def courses(cls) -> CourseRepository:
        """Get course repository."""
        return cls._courses
    
    @classmethod
    def enrollments(cls) -> EnrollmentRepository:
        """Get enrollment repository."""
        return cls._enrollments
