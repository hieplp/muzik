"""
Tests for validation utilities.
"""

import pytest

from muzik.utils.validators import (
    validate_email,
    validate_url,
    validate_required,
    validate_length,
    validate_range,
    validate_choice,
    validate_file_exists,
    validate_directory_exists,
)


class TestValidators:
    """Test cases for validation functions."""

    def test_validate_email_valid(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@example.com",
        ]

        for email in valid_emails:
            assert validate_email(email) is True

    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
        ]

        for email in invalid_emails:
            assert validate_email(email) is False

    def test_validate_url_valid(self):
        """Test valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://example.org",
            "https://sub.example.com/path",
            "http://example.com:8080",
        ]

        for url in valid_urls:
            assert validate_url(url) is True

    def test_validate_url_invalid(self):
        """Test invalid URLs."""
        invalid_urls = [
            "not-a-url",
            "example.com",
            "ftp://",
            "://example.com",
        ]

        for url in invalid_urls:
            assert validate_url(url) is False

    def test_validate_required_valid(self):
        """Test valid required values."""
        valid_values = [
            "non-empty string",
            [1, 2, 3],
            {"key": "value"},
            {1, 2, 3},
            0,
            False,
        ]

        for value in valid_values:
            validate_required(value, "test_field")  # Should not raise

    def test_validate_required_invalid(self):
        """Test invalid required values."""
        invalid_values = [
            None,
            "",
            "   ",
            [],
            {},
            set(),
        ]

        for value in invalid_values:
            with pytest.raises(ValueError, match="test_field"):
                validate_required(value, "test_field")

    def test_validate_length_valid(self):
        """Test valid string lengths."""
        # Test with min_length
        validate_length("test", min_length=3, field_name="test_field")
        validate_length("test", min_length=4, field_name="test_field")

        # Test with max_length
        validate_length("test", max_length=5, field_name="test_field")
        validate_length("test", max_length=4, field_name="test_field")

        # Test with both
        validate_length("test", min_length=3, max_length=5, field_name="test_field")

    def test_validate_length_invalid(self):
        """Test invalid string lengths."""
        # Test non-string
        with pytest.raises(ValueError, match="must be a string"):
            validate_length(123, min_length=1, field_name="test_field")

        # Test too short
        with pytest.raises(ValueError, match="at least 5 characters"):
            validate_length("test", min_length=5, field_name="test_field")

        # Test too long
        with pytest.raises(ValueError, match="at most 3 characters"):
            validate_length("test", max_length=3, field_name="test_field")

    def test_validate_range_valid(self):
        """Test valid numeric ranges."""
        # Test with min_value
        validate_range(5, min_value=3, field_name="test_field")
        validate_range(5, min_value=5, field_name="test_field")

        # Test with max_value
        validate_range(5, max_value=7, field_name="test_field")
        validate_range(5, max_value=5, field_name="test_field")

        # Test with both
        validate_range(5, min_value=3, max_value=7, field_name="test_field")

    def test_validate_range_invalid(self):
        """Test invalid numeric ranges."""
        # Test non-numeric
        with pytest.raises(ValueError, match="must be a number"):
            validate_range("not a number", min_value=1, field_name="test_field")

        # Test too small
        with pytest.raises(ValueError, match="at least 5"):
            validate_range(3, min_value=5, field_name="test_field")

        # Test too large
        with pytest.raises(ValueError, match="at most 3"):
            validate_range(5, max_value=3, field_name="test_field")

    def test_validate_choice_valid(self):
        """Test valid choices."""
        choices = ["option1", "option2", "option3"]

        for choice in choices:
            validate_choice(choice, choices, "test_field")  # Should not raise

    def test_validate_choice_invalid(self):
        """Test invalid choices."""
        choices = ["option1", "option2", "option3"]

        with pytest.raises(ValueError, match="must be one of"):
            validate_choice("invalid_option", choices, "test_field")

    def test_validate_file_exists(self, tmp_path):
        """Test file existence validation."""
        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Should not raise
        validate_file_exists(str(test_file))

        # Should raise for non-existent file
        with pytest.raises(FileNotFoundError):
            validate_file_exists(str(tmp_path / "nonexistent.txt"))

    def test_validate_directory_exists(self, tmp_path):
        """Test directory existence validation."""
        # Create a temporary directory
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Should not raise
        validate_directory_exists(str(test_dir))

        # Should raise for non-existent directory
        with pytest.raises(FileNotFoundError):
            validate_directory_exists(str(tmp_path / "nonexistent_dir"))

        # Should raise for file (not directory)
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with pytest.raises(ValueError, match="not a directory"):
            validate_directory_exists(str(test_file))
