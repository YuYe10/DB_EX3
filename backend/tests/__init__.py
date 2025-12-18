"""
Test suite initialization and utilities.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

__all__ = ['test_decoupling', 'test_refactoring']
