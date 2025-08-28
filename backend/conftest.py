import pytest
from unittest.mock import Mock, patch
import os

os.environ['SUPABASE_PROJECT_ID'] = 'test-project'
os.environ['SUPABASE_SERVICE_KEY'] = 'test-key'

@pytest.fixture
def mock_supabase():
    """Mock the Supabase client"""
    with patch('app.supabase') as mock:
        yield mock
