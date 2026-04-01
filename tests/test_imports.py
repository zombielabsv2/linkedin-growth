"""Baseline smoke tests for linkedin-growth project.

Tests syntax validity and basic functionality of all Python modules.
Does NOT require external dependencies (requests, bs4, openpyxl).
"""

import ast
import os
import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _get_all_py_files():
    """Return all .py files in the project root (non-recursive for now)."""
    return list(PROJECT_ROOT.glob("*.py"))


class TestSyntax:
    """Verify all Python files parse without syntax errors."""

    def test_all_py_files_parse(self):
        py_files = _get_all_py_files()
        assert len(py_files) > 0, "No .py files found in project root"
        for f in py_files:
            source = f.read_text(encoding="utf-8")
            try:
                ast.parse(source, filename=str(f))
            except SyntaxError as e:
                raise AssertionError(f"Syntax error in {f.name}: {e}")

    def test_scraper_py_exists(self):
        assert (PROJECT_ROOT / "scraper.py").exists(), "scraper.py not found"

    def test_seed_data_py_exists(self):
        assert (PROJECT_ROOT / "seed_data.py").exists(), "seed_data.py not found"


class TestScraperModule:
    """Test scraper.py functions that don't require network or external deps."""

    def _import_scraper(self):
        """Import scraper module by adding project root to path."""
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        # Only import the module's stdlib-only parts via ast to check structure
        source = (PROJECT_ROOT / "scraper.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        return tree

    def test_scraper_has_expected_functions(self):
        tree = self._import_scraper()
        func_names = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        }
        expected = {
            "ensure_data_dir",
            "load_existing_posts",
            "save_posts",
            "dedup_posts",
            "safe_int",
            "normalize_date",
            "scrape_profile",
            "manual_entry_mode",
            "xlsx_import_mode",
            "report_mode",
            "main",
        }
        missing = expected - func_names
        assert not missing, f"Missing functions in scraper.py: {missing}"

    def test_scraper_has_expected_constants(self):
        tree = self._import_scraper()
        # Check top-level assignments
        top_names = set()
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        top_names.add(target.id)
        expected = {"CSV_FIELDS", "HEADERS", "DEFAULT_PROFILE"}
        missing = expected - top_names
        assert not missing, f"Missing constants in scraper.py: {missing}"

    def test_safe_int_function(self):
        """Actually import and test safe_int since it only uses stdlib."""
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from scraper import safe_int

        assert safe_int(None) == 0
        assert safe_int(0) == 0
        assert safe_int(42) == 42
        assert safe_int(3.7) == 3
        assert safe_int("1,234") == 1234
        assert safe_int("5k") == 5000
        assert safe_int("2.5K") == 2500
        assert safe_int("1M") == 1000000
        assert safe_int("garbage") == 0

    def test_normalize_date_function(self):
        """Test normalize_date with various formats."""
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from scraper import normalize_date

        assert normalize_date("2024-01-15") == "2024-01-15"
        assert normalize_date("") == ""
        assert normalize_date("15/01/2024") == "2024-01-15"
        # Relative dates return something parseable
        result = normalize_date("2 days ago")
        assert len(result) == 10  # YYYY-MM-DD format

    def test_dedup_posts_function(self):
        """Test dedup_posts removes duplicates correctly."""
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from scraper import dedup_posts

        posts = [
            {"post_text": "Hello world", "date": "2024-01-01", "post_url": ""},
            {"post_text": "Hello world", "date": "2024-01-01", "post_url": ""},
            {"post_text": "Different post", "date": "2024-01-02", "post_url": "https://example.com/1"},
            {"post_text": "Another post", "date": "2024-01-03", "post_url": "https://example.com/1"},
        ]
        result = dedup_posts(posts)
        assert len(result) == 2, f"Expected 2 unique posts, got {len(result)}"


class TestSeedDataModule:
    """Test seed_data.py structure."""

    def test_seed_data_parses(self):
        source = (PROJECT_ROOT / "seed_data.py").read_text(encoding="utf-8")
        tree = ast.parse(source, filename="seed_data.py")
        # Check it has a 'posts' variable
        top_names = set()
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        top_names.add(target.id)
        assert "posts" in top_names, "seed_data.py should define a 'posts' variable"
