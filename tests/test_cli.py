"""Tests for CLI."""

import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch, MagicMock
import pytest
import csv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from click.testing import CliRunner
from src.weather_module.cli import cli


class TestCLI:
    """Essential tests for CLI."""

    def test_cli_basic_run(self):
        """Test basic CLI run command with input and output."""
        # Arrange - Create temporary input CSV
        input_csv_content = """country,city
United Kingdom,London
United States,New York"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            # Mock the pipeline to avoid actual API calls
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Act
                result = runner.invoke(cli, ['run', input_file, output_file])
            
            # Assert
            assert result.exit_code == 0
            mock_pipeline.assert_called_once()
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs['input_csv'] == input_file
            assert call_kwargs['output_csv'] == output_file
            assert call_kwargs['units'] == 'C'  # default
            assert call_kwargs['use_cache'] is True  # default
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    def test_cli_with_units_option_celsius(self):
        """Test CLI with --units C option."""
        # Arrange
        input_csv_content = """country,city
United Kingdom,London"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Act
                result = runner.invoke(cli, ['run', input_file, output_file, '--units', 'C'])
            
            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs['units'] == 'C'
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    def test_cli_with_units_option_fahrenheit(self):
        """Test CLI with --units F option."""
        # Arrange
        input_csv_content = """country,city
United States,New York"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Act
                result = runner.invoke(cli, ['run', input_file, output_file, '--units', 'F'])
            
            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs['units'] == 'F'
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    def test_cli_with_units_option_both(self):
        """Test CLI with --units both option."""
        # Arrange
        input_csv_content = """country,city
France,Paris"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Act
                result = runner.invoke(cli, ['run', input_file, output_file, '--units', 'both'])
            
            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs['units'] == 'BOTH'
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    def test_cli_with_no_cache_flag(self):
        """Test CLI with --no-cache flag."""
        # Arrange
        input_csv_content = """country,city
United Kingdom,London"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Act
                result = runner.invoke(cli, ['run', input_file, output_file, '--no-cache'])
            
            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs['use_cache'] is False
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    def test_cli_with_ttl_option(self):
        """Test CLI with --ttl option."""
        # Arrange
        input_csv_content = """country,city
United Kingdom,London"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Act
                result = runner.invoke(cli, ['run', input_file, output_file, '--ttl', '600'])
            
            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs['cache_ttl'] == 600
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    def test_cli_with_max_rows_option(self):
        """Test CLI with --max-rows option."""
        # Arrange
        input_csv_content = """country,city
United Kingdom,London
United States,New York
France,Paris
Germany,Berlin"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Act
                result = runner.invoke(cli, ['run', input_file, output_file, '--max-rows', '2'])
            
            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs['max_rows'] == 2
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    def test_cli_with_verbose_flag(self):
        """Test CLI with --verbose flag."""
        # Arrange
        input_csv_content = """country,city
United Kingdom,London"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Act
                result = runner.invoke(cli, ['run', input_file, output_file, '--verbose'])
            
            # Assert
            assert result.exit_code == 0
            assert 'Running pipeline:' in result.output
            assert 'input:' in result.output
            assert 'output:' in result.output
            assert 'Done.' in result.output
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs['verbose'] is True
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    def test_cli_error_handling(self):
        """Test CLI error handling when pipeline fails."""
        # Arrange
        input_csv_content = """country,city
United Kingdom,London"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Mock pipeline to raise an error
                mock_pipeline.side_effect = Exception("Pipeline error")
                
                # Act
                result = runner.invoke(cli, ['run', input_file, output_file])
            
            # Assert
            assert result.exit_code == 1
            assert 'Error:' in result.output
            assert 'Pipeline error' in result.output
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    def test_cli_missing_input_file(self):
        """Test CLI error when input file doesn't exist."""
        # Arrange
        runner = CliRunner()
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            with patch('src.weather_module.cli.run_pipeline'):
                # Act
                result = runner.invoke(cli, ['run', 'nonexistent.csv', output_file])
            
            # Assert
            assert result.exit_code != 0
            assert 'nonexistent.csv' in result.output or 'does not exist' in result.output.lower()
        finally:
            Path(output_file).unlink(missing_ok=True)

    def test_cli_with_detailed_flag(self):
        """Test CLI with --detailed flag."""
        # Arrange
        input_csv_content = """country,city
United Kingdom,London"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Act
                result = runner.invoke(cli, ['run', input_file, output_file, '--detailed'])
            
            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs['detailed'] is True
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    def test_cli_without_detailed_flag(self):
        """Test CLI without --detailed flag (default should be False)."""
        # Arrange
        input_csv_content = """country,city
United Kingdom,London"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Act
                result = runner.invoke(cli, ['run', input_file, output_file])
            
            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs['detailed'] is False
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    def test_cli_combined_options(self):
        """Test CLI with multiple options combined."""
        # Arrange
        input_csv_content = """country,city
United Kingdom,London
United States,New York"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(input_csv_content)
            input_file = f.name
        
        output_file = NamedTemporaryFile(mode='w', suffix='.csv', delete=False).name
        
        try:
            runner = CliRunner()
            
            with patch('src.weather_module.cli.run_pipeline') as mock_pipeline:
                # Act - Combine multiple options including --detailed
                result = runner.invoke(cli, [
                    'run',
                    input_file,
                    output_file,
                    '--units', 'both',
                    '--no-cache',
                    '--ttl', '300',
                    '--max-rows', '1',
                    '--verbose',
                    '--detailed'
                ])
            
            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs['units'] == 'BOTH'
            assert call_kwargs['use_cache'] is False
            assert call_kwargs['cache_ttl'] == 300
            assert call_kwargs['max_rows'] == 1
            assert call_kwargs['verbose'] is True
            assert call_kwargs['detailed'] is True
        finally:
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

