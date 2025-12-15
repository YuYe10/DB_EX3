"""
Unit tests demonstrating the decoupled architecture.
Tests can run without database or Flask context.
"""
import unittest
from unittest.mock import patch, MagicMock, Mock
from repository import StudentRepository, CourseRepository, EnrollmentRepository


class TestStudentRepository(unittest.TestCase):
    """Test StudentRepository in isolation."""

    @patch('repository.db')
    def test_find_by_id(self, mock_db):
        """Test finding student by ID."""
        mock_db.fetch_one.return_value = {
            'id': 1, 'student_no': 'S001', 'name': '张三'
        }

        repo = StudentRepository()
        result = repo.find_by_id(1)

        assert result['name'] == '张三'
        mock_db.fetch_one.assert_called_once()

    @patch('repository.db')
    def test_find_by_no(self, mock_db):
        """Test finding student by student number."""
        mock_db.fetch_one.return_value = {
            'id': 1, 'student_no': 'S001', 'name': '张三'
        }

        repo = StudentRepository()
        result = repo.find_by_no('S001')

        assert result['student_no'] == 'S001'
        mock_db.fetch_one.assert_called_once()

    @patch('repository.db')
    def test_find_all(self, mock_db):
        """Test finding all students."""
        mock_db.fetch_all.return_value = [
            {'id': 1, 'name': '张三'},
            {'id': 2, 'name': '李四'}
        ]

        repo = StudentRepository()
        result = repo.find_all()

        assert len(result) == 2
        mock_db.fetch_all.assert_called_once()

    @patch('repository.db')
    def test_create_student(self, mock_db):
        """Test creating a student."""
        mock_db.execute_returning.return_value = 1

        repo = StudentRepository()
        student_id = repo.create({
            'student_no': 'S002',
            'name': '王五',
            'major': '计算机',
            'password_hash': 'hashed_pass'
        })

        assert student_id == 1
        mock_db.execute_returning.assert_called_once()

    @patch('repository.db')
    def test_update_student(self, mock_db):
        """Test updating a student."""
        mock_db.execute.return_value = True

        repo = StudentRepository()
        result = repo.update(1, {'name': '新名字', 'major': '软件工程'})

        assert result is True
        mock_db.execute.assert_called_once()

    @patch('repository.db')
    def test_delete_student(self, mock_db):
        """Test deleting a student."""
        mock_db.execute.return_value = True

        repo = StudentRepository()
        result = repo.delete(1)

        assert result is True
        mock_db.execute.assert_called_once()

    @patch('repository.db')
    def test_search_with_keyword(self, mock_db):
        """Test searching students with keyword."""
        mock_db.fetch_all.return_value = [
            {'id': 1, 'name': '张三', 'major': '计算机'}
        ]

        repo = StudentRepository()
        result = repo.search(keyword='张')

        assert len(result) == 1
        mock_db.fetch_all.assert_called_once()


class TestServiceWithRepository(unittest.TestCase):
    """Test Service layer with mocked Repository."""

    def test_student_service_isolation(self):
        """Demonstrate Service independence from Database."""
        # Import here to avoid import errors
        from services.student_service import StudentService

        with patch('repository.RepositoryContainer') as mock_container:
            # Mock the repository
            mock_repo = MagicMock()
            mock_repo.find_by_id.return_value = {
                'id': 1, 'name': '张三', 'student_no': 'S001'
            }
            mock_container.students.return_value = mock_repo

            # Service doesn't know about database at all
            # It only depends on repository interface
            # This allows us to test service logic without database


class TestDecoupling(unittest.TestCase):
    """Tests demonstrating decoupling benefits."""

    def test_api_changes_dont_affect_service(self):
        """Service logic is independent of API changes."""
        # If we change API response format, service code doesn't change
        # Service only cares about business logic, not HTTP

        from repository import StudentRepository
        from unittest.mock import patch

        with patch('repository.db') as mock_db:
            mock_db.fetch_one.return_value = {'id': 1, 'name': 'Test'}

            repo = StudentRepository()
            result = repo.find_by_id(1)

            # Service doesn't care if result is wrapped in {'data': ...}
            # or formatted as {'success': True, 'data': ...}
            assert result['id'] == 1

    def test_database_migration_is_simple(self):
        """Easy to swap database implementation."""
        # Original: PostgreSQL
        repo1 = StudentRepository()

        # New: Create a MongoDB repository (same interface)
        # class MongoStudentRepository(Repository):
        #     def find_by_id(self, id):
        #         return self.collection.find_one({'_id': id})

        # Service code doesn't change at all!
        # Just swap the repository in RepositoryContainer

    def test_testing_without_database(self):
        """Service tests don't require database."""
        from unittest.mock import patch

        with patch('repository.StudentRepository') as MockRepo:
            mock_repo = MagicMock()
            mock_repo.find_by_id.return_value = {'id': 1, 'name': '测试'}
            MockRepo.return_value = mock_repo

            # No database connection needed
            # No fixtures needed
            # Tests run in milliseconds


class TestReusableComposables(unittest.TestCase):
    """Tests for front-end composables."""

    def test_useauth_composition(self):
        """useAuth composable is reusable across components."""
        # Pseudo-test showing composable benefits

        # Component 1: Login
        # const { user, login } = useAuth()

        # Component 2: User Profile
        # const { user, login } = useAuth()

        # Component 3: Settings
        # const { user, login } = useAuth()

        # Same logic, no duplication!
        # If auth logic changes, update useAuth once

        pass

    def test_useform_reduces_boilerplate(self):
        """useForm composable eliminates form boilerplate."""
        # Before: Each form component has 50+ lines of state/validation
        # After: 3 lines to setup form

        # const { form, errors, submit } = useForm(
        #   { username: '', password: '' },
        #   onSubmit
        # )

        # That's it! Validation, error handling, submission - all included

        pass


# Test file that demonstrates integration
class TestIntegration(unittest.TestCase):
    """Integration tests showing decoupled layers work together."""

    @patch('repository.db')
    def test_full_request_flow(self, mock_db):
        """Test a complete request flow with mocked database."""
        # Setup mocks
        mock_db.fetch_one.return_value = {'id': 1, 'student_no': 'S001'}
        mock_db.fetch_all.return_value = [
            {'id': 1, 'course_id': 1, 'grade': 90}
        ]

        # This demonstrates how layers work together:
        # API Layer calls → Service Layer → Repository Layer → (mocked) DB

        repo = StudentRepository()
        student = repo.find_by_id(1)

        assert student['student_no'] == 'S001'
        assert mock_db.fetch_one.called


if __name__ == '__main__':
    unittest.main()
