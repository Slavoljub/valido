"""
Tests for Data Integrator
Following TDD approach for comprehensive testing
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
from src.ai_local_models.data_integrator import DataIntegrator, DataSourceError

class TestDataIntegrator:
    """Test cases for DataIntegrator following TDD principles"""

    def setup_method(self):
        """Setup test fixtures"""
        self.integrator = DataIntegrator()

    def test_initialization(self):
        """Test DataIntegrator initialization"""
        assert self.integrator is not None
        assert hasattr(self.integrator, 'supported_formats')
        assert 'csv' in self.integrator.supported_formats
        assert 'json' in self.integrator.supported_formats

    def test_format_detection_csv(self):
        """Test CSV format detection"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,value\ntest,123\n")
            temp_path = f.name

        try:
            format_type = self.integrator._detect_format(temp_path)
            assert format_type == 'csv'
        finally:
            os.unlink(temp_path)

    def test_format_detection_excel(self):
        """Test Excel format detection"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name

        try:
            format_type = self.integrator._detect_format(temp_path)
            assert format_type == 'excel'
        finally:
            os.unlink(temp_path)

    def test_load_csv_data(self):
        """Test CSV data loading"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,value\ntest,123\nrow2,456\n")
            temp_path = f.name

        try:
            df = self.integrator._load_csv(temp_path)
            assert len(df) == 2
            assert list(df.columns) == ['name', 'value']
            assert df.iloc[0]['name'] == 'test'
        finally:
            os.unlink(temp_path)

    def test_load_json_data(self):
        """Test JSON data loading"""
        test_data = [
            {"name": "test1", "value": 123},
            {"name": "test2", "value": 456}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(test_data, f)
            temp_path = f.name

        try:
            df = self.integrator._load_json(temp_path)
            assert len(df) == 2
            assert 'name' in df.columns
            assert 'value' in df.columns
        finally:
            os.unlink(temp_path)

    def test_merge_data_sources(self):
        """Test data source merging"""
        df1 = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
        df2 = pd.DataFrame({'id': [3, 4], 'name': ['C', 'D']})

        merged = self.integrator.merge_data_sources([df1, df2])
        assert len(merged) == 4
        assert list(merged.columns) == ['id', 'name']

    def test_validate_data(self):
        """Test data validation"""
        df = pd.DataFrame({
            'name': ['A', 'B', None],
            'value': [1, 2, 3]
        })

        validation = self.integrator.validate_data(df)
        assert validation['shape'] == (3, 2)
        assert validation['null_counts']['name'] == 1
        assert validation['duplicate_count'] == 0

    def test_error_handling_invalid_file(self):
        """Test error handling for invalid files"""
        with pytest.raises(DataSourceError):
            self.integrator.load_data_source("/nonexistent/file.csv")

    def test_unsupported_format(self):
        """Test handling of unsupported formats"""
        with tempfile.NamedTemporaryFile(suffix='.unsupported', delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(DataSourceError):
                self.integrator.load_data_source(temp_path, 'unsupported')
        finally:
            os.unlink(temp_path)

    def test_create_embeddings(self):
        """Test embedding creation"""
        df = pd.DataFrame({
            'text': ['This is a test', 'Another test document']
        })

        # Test without embeddings (fallback)
        result = self.integrator.create_embeddings(df)
        assert len(result) == 2
        assert 'text' in result.columns
