#!/usr/bin/env python3
"""
Test Content Management System
==============================

Comprehensive tests for the ValidoAI content management system.
Tests file upload, processing, storage, retrieval, and management features.
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import io

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask.testing import FlaskClient

class TestContentManagement(unittest.TestCase):
    """Test cases for content management system"""

    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.upload_dir = Path(self.temp_dir) / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Mock the content manager
        with patch('src.content_manager.Path') as mock_path:
            mock_path.return_value = self.upload_dir
            from src.content_manager import ContentManager
            self.content_manager = ContentManager(str(self.upload_dir))

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_content_manager_initialization(self):
        """Test content manager initialization"""
        from src.content_manager import ContentManager

        cm = ContentManager()
        self.assertIsNotNone(cm)
        self.assertTrue(hasattr(cm, 'upload_folder'))
        self.assertTrue(hasattr(cm, 'content_db'))

    def test_file_validation_success(self):
        """Test successful file validation"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        # Create a mock file object
        mock_file = MagicMock()
        mock_file.filename = 'test.pdf'
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=1024)  # 1KB

        result = cm.validate_file(mock_file, ['.pdf'])

        self.assertTrue(result['valid'])
        self.assertEqual(result['filename'], 'test.pdf')
        self.assertEqual(result['size'], 1024)

    def test_file_validation_failure_size(self):
        """Test file validation failure due to size"""
        from src.content_manager import ContentManager

        cm = ContentManager(max_file_size=1000)  # 1000 bytes

        mock_file = MagicMock()
        mock_file.filename = 'large_file.pdf'
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=2000)  # 2KB > limit

        result = cm.validate_file(mock_file)

        self.assertFalse(result['valid'])
        self.assertIn('too large', result['error'].lower())

    def test_file_validation_failure_extension(self):
        """Test file validation failure due to extension"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        mock_file = MagicMock()
        mock_file.filename = 'test.exe'
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=1024)

        result = cm.validate_file(mock_file, ['.pdf', '.doc'])

        self.assertFalse(result['valid'])
        self.assertIn('not allowed', result['error'].lower())

    def test_file_validation_no_filename(self):
        """Test file validation with no filename"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        mock_file = MagicMock()
        mock_file.filename = None

        result = cm.validate_file(mock_file)

        self.assertFalse(result['valid'])
        self.assertIn('no file', result['error'].lower())

    def test_mime_type_detection(self):
        """Test MIME type detection"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        # Test with filename
        mock_file = MagicMock()
        mock_file.filename = 'test.pdf'

        mime_type = cm._detect_mime_type(mock_file)
        self.assertEqual(mime_type, 'application/pdf')

        # Test with different extensions
        test_cases = [
            ('document.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            ('image.jpg', 'image/jpeg'),
            ('text.txt', 'text/plain'),
            ('video.mp4', 'video/mp4'),
            ('audio.mp3', 'audio/mpeg')
        ]

        for filename, expected_mime in test_cases:
            mock_file.filename = filename
            mime_type = cm._detect_mime_type(mock_file)
            self.assertEqual(mime_type, expected_mime)

    def test_file_hash_calculation(self):
        """Test file hash calculation"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        # Create a temporary test file
        test_content = b"Hello, World! This is a test file."
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            hash_value = cm._calculate_file_hash(temp_file_path)
            self.assertIsInstance(hash_value, str)
            self.assertEqual(len(hash_value), 64)  # SHA-256 hash length
        finally:
            os.unlink(temp_file_path)

    def test_content_database_operations(self):
        """Test content database operations"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        # Test saving and loading database
        test_content = {
            'test_id': {
                'id': 'test_id',
                'filename': 'test.pdf',
                'path': '/path/to/test.pdf',
                'size': 1024,
                'uploaded_at': '2024-01-01T00:00:00'
            }
        }

        cm.content_db = test_content
        cm._save_content_database()

        # Verify file was created
        db_path = cm.upload_folder / "content_db.json"
        self.assertTrue(db_path.exists())

        # Load database
        new_cm = ContentManager()
        self.assertEqual(new_cm.content_db, test_content)

    def test_get_content(self):
        """Test getting content by ID"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        # Test non-existent content
        result = cm.get_content('non_existent_id')
        self.assertIsNone(result)

        # Test existing content
        test_content = {
            'id': 'test_id',
            'filename': 'test.pdf',
            'path': '/path/to/test.pdf',
            'size': 1024,
            'uploaded_at': '2024-01-01T00:00:00'
        }

        cm.content_db['test_id'] = test_content
        result = cm.get_content('test_id')

        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 'test_id')
        self.assertEqual(result['filename'], 'test.pdf')

    def test_list_content(self):
        """Test listing content"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        # Test empty content
        result = cm.list_content()
        self.assertEqual(result['total'], 0)
        self.assertEqual(len(result['content']), 0)

        # Test with content
        test_content = [
            {
                'id': 'id1',
                'filename': 'file1.pdf',
                'category': 'documents',
                'uploaded_at': '2024-01-02T00:00:00'
            },
            {
                'id': 'id2',
                'filename': 'file2.jpg',
                'category': 'images',
                'uploaded_at': '2024-01-01T00:00:00'
            }
        ]

        for content in test_content:
            cm.content_db[content['id']] = content

        result = cm.list_content()
        self.assertEqual(result['total'], 2)
        self.assertEqual(len(result['content']), 2)

        # Test with category filter
        result = cm.list_content(category='documents')
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['content'][0]['filename'], 'file1.pdf')

    def test_search_content(self):
        """Test content search functionality"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        # Add test content
        test_content = [
            {
                'id': 'id1',
                'filename': 'report.pdf',
                'category': 'documents',
                'metadata': {'description': 'Monthly sales report'}
            },
            {
                'id': 'id2',
                'filename': 'photo.jpg',
                'category': 'images',
                'metadata': {'description': 'Company logo'}
            }
        ]

        for content in test_content:
            cm.content_db[content['id']] = content

        # Test filename search
        results = cm.search_content('report')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['filename'], 'report.pdf')

        # Test metadata search
        results = cm.search_content('sales')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['filename'], 'report.pdf')

        # Test no results
        results = cm.search_content('nonexistent')
        self.assertEqual(len(results), 0)

    def test_delete_content(self):
        """Test content deletion"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        # Test deleting non-existent content
        result = cm.delete_content('non_existent_id')
        self.assertFalse(result['success'])

        # Test deleting existing content
        test_content = {
            'id': 'test_id',
            'filename': 'test.pdf',
            'path': '/path/to/test.pdf',
            'user_id': 'test_user'
        }

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b'test content')
            test_content['path'] = temp_file.name

        cm.content_db['test_id'] = test_content

        # Delete content
        result = cm.delete_content('test_id', 'test_user')
        self.assertTrue(result['success'])

        # Verify content was removed from database
        self.assertNotIn('test_id', cm.content_db)

        # Clean up temp file
        os.unlink(temp_file.name)

    def test_content_stats(self):
        """Test content statistics generation"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        # Test with no content
        stats = cm.get_content_stats()
        self.assertEqual(stats['total_content'], 0)

        # Test with content
        test_content = [
            {
                'id': 'id1',
                'filename': 'doc.pdf',
                'category': 'documents',
                'size': 1024,
                'extension': '.pdf'
            },
            {
                'id': 'id2',
                'filename': 'image.jpg',
                'category': 'images',
                'size': 2048,
                'extension': '.jpg'
            },
            {
                'id': 'id3',
                'filename': 'doc2.pdf',
                'category': 'documents',
                'size': 512,
                'extension': '.pdf'
            }
        ]

        for content in test_content:
            cm.content_db[content['id']] = content

        stats = cm.get_content_stats()
        self.assertEqual(stats['total_content'], 3)
        self.assertEqual(stats['total_size'], 3584)  # 1024 + 2048 + 512
        self.assertEqual(stats['categories']['documents'], 2)
        self.assertEqual(stats['categories']['images'], 1)
        self.assertEqual(stats['file_types']['.pdf'], 2)
        self.assertEqual(stats['file_types']['.jpg'], 1)

    def test_cleanup_temp_files(self):
        """Test temporary file cleanup"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        # Create a temp file
        temp_file = cm.temp_folder / "test_temp_file.txt"
        temp_file.write_text("test content")

        # Verify file exists
        self.assertTrue(temp_file.exists())

        # Clean up files older than 0 hours (should remove all)
        result = cm.cleanup_temp_files(older_than_hours=0)
        self.assertTrue(result['success'])
        self.assertEqual(result['cleaned_files'], 1)

        # Verify file was removed
        self.assertFalse(temp_file.exists())

class TestContentManagementAPI(unittest.TestCase):
    """Test cases for content management API endpoints"""

    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_upload_content_api(self):
        """Test content upload API endpoint"""
        from routes import api_bp
        self.app.register_blueprint(api_bp)

        # Test without file
        response = self.client.post('/api/content/upload')
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_list_content_api(self):
        """Test content listing API endpoint"""
        from routes import api_bp
        self.app.register_blueprint(api_bp)

        response = self.client.get('/api/content/list')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertIn('content', data)
        self.assertIn('total', data)

    def test_search_content_api(self):
        """Test content search API endpoint"""
        from routes import api_bp
        self.app.register_blueprint(api_bp)

        # Test without query
        response = self.client.get('/api/content/search')
        self.assertEqual(response.status_code, 400)

        # Test with query
        response = self.client.get('/api/content/search?q=test')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertIn('query', data)
        self.assertIn('results', data)

    def test_content_stats_api(self):
        """Test content statistics API endpoint"""
        from routes import api_bp
        self.app.register_blueprint(api_bp)

        response = self.client.get('/api/content/stats')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertIn('stats', data)

    def test_get_content_api(self):
        """Test get content API endpoint"""
        from routes import api_bp
        self.app.register_blueprint(api_bp)

        # Test with non-existent content ID
        response = self.client.get('/api/content/non_existent_id')
        self.assertEqual(response.status_code, 404)

class TestContentProcessing(unittest.TestCase):
    """Test cases for content processing functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.upload_dir = Path(self.temp_dir) / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_image_metadata_extraction(self):
        """Test image metadata extraction"""
        from src.content_manager import ContentManager
        from PIL import Image

        cm = ContentManager()

        # Create a test image
        test_image = self.upload_dir / "test_image.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image)

        try:
            metadata = cm._extract_image_metadata(test_image)

            self.assertIn('dimensions', metadata)
            self.assertEqual(metadata['dimensions']['width'], 100)
            self.assertEqual(metadata['dimensions']['height'], 100)
        finally:
            test_image.unlink(missing_ok=True)

    def test_text_metadata_extraction(self):
        """Test text file metadata extraction"""
        from src.content_manager import ContentManager

        cm = ContentManager()

        # Create a test text file
        test_text = self.upload_dir / "test_text.txt"
        content = "Hello, World!\nThis is a test file.\nIt has multiple lines."
        test_text.write_text(content, encoding='utf-8')

        try:
            metadata = cm._extract_text_metadata(test_text)

            self.assertIn('line_count', metadata)
            self.assertIn('word_count', metadata)
            self.assertIn('character_count', metadata)
            self.assertEqual(metadata['line_count'], 3)
            self.assertEqual(metadata['word_count'], 10)
            self.assertEqual(metadata['character_count'], len(content))
        finally:
            test_text.unlink(missing_ok=True)

if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2)
