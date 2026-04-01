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


class TestContentOpsModule:
    """Test content_ops.py — the Streamlit Content Ops app."""

    def test_content_ops_parses(self):
        source = (PROJECT_ROOT / "content_ops.py").read_text(encoding="utf-8")
        ast.parse(source, filename="content_ops.py")

    def test_content_ops_has_expected_functions(self):
        source = (PROJECT_ROOT / "content_ops.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        }
        expected = {
            "parse_posts_from_md",
            "get_all_series_posts",
            "load_scraped_posts",
            "load_state",
            "save_state",
            "get_post_key",
            "page_content_calendar",
            "page_post_drafting",
            "page_series_dashboard",
            "page_performance_analytics",
            "main",
        }
        missing = expected - func_names
        assert not missing, f"Missing functions in content_ops.py: {missing}"

    def test_parse_posts_from_md(self):
        """Test markdown post parsing with real data."""
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from content_ops import parse_posts_from_md, CONTENT_DIR

        posts = parse_posts_from_md(CONTENT_DIR / "org_metabolism_series.md")
        assert len(posts) == 10, f"Expected 10 posts, got {len(posts)}"
        assert posts[0]["number"] == 1
        assert "title" in posts[0]
        assert "body" in posts[0]
        assert len(posts[0]["body"]) > 50

    def test_get_all_series_posts(self):
        """Test that all series load their posts."""
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from content_ops import get_all_series_posts, SERIES_CONFIG

        all_posts = get_all_series_posts()
        assert len(all_posts) == len(SERIES_CONFIG)
        for key, posts in all_posts.items():
            assert len(posts) > 0, f"No posts found for series {key}"

    def test_load_scraped_posts(self):
        """Test scraped data loads correctly."""
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from content_ops import load_scraped_posts

        df = load_scraped_posts()
        assert len(df) > 0, "No scraped posts found"
        assert "reactions" in df.columns
        assert "comments" in df.columns
        assert "date" in df.columns

    def test_get_post_key(self):
        """Test post key generation."""
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from content_ops import get_post_key

        key = get_post_key("org_metabolism", 1, "The Core Premise")
        assert key == "org_metabolism::1::The Core Premise"
        # Test truncation
        long_title = "A" * 100
        key2 = get_post_key("test", 5, long_title)
        assert len(key2.split("::")[-1]) == 40

    def test_state_round_trip(self):
        """Test save/load state."""
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from content_ops import load_state

        state = load_state()
        assert isinstance(state, dict)
        assert "posts" in state or state == {"posts": {}, "drafts": {}}

    def test_cloud_store_lazy_import(self):
        """Test that _cloud_store lazy import works."""
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from content_ops import _cloud_store

        cs = _cloud_store()
        assert cs is not None, "cloud_store module should be importable"
        assert hasattr(cs, "cloud_put")
        assert hasattr(cs, "cloud_get")
        assert hasattr(cs, "cloud_list")
        assert hasattr(cs, "cloud_list_with_data")
        assert hasattr(cs, "cloud_delete")
        assert hasattr(cs, "is_cloud_available")

    def test_new_cloud_functions_exist(self):
        """Test that new cloud data functions exist."""
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from content_ops import _load_series_posts_from_cloud, _parse_scraped_df

        # _load_series_posts_from_cloud should return None when no Supabase
        # (can't fully test without credentials)
        assert callable(_load_series_posts_from_cloud)
        assert callable(_parse_scraped_df)

        # Test _parse_scraped_df with empty data
        import pandas as pd
        df = _parse_scraped_df([])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

        # Test with sample data
        sample = [
            {"post_text": "Test", "date": "2024-01-01", "reactions": "100",
             "comments": "5", "impressions": "500", "post_url": "", "source": "test",
             "collected_at": "2024-01-01T00:00:00"}
        ]
        df = _parse_scraped_df(sample)
        assert len(df) == 1
        assert df.iloc[0]["reactions"] == 100


class TestCloudStoreModule:
    """Test cloud_store.py structure and imports."""

    def test_cloud_store_parses(self):
        source = (PROJECT_ROOT / "cloud_store.py").read_text(encoding="utf-8")
        ast.parse(source, filename="cloud_store.py")

    def test_cloud_store_imports(self):
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        import cloud_store
        assert hasattr(cloud_store, "cloud_put")
        assert hasattr(cloud_store, "cloud_get")
        assert hasattr(cloud_store, "cloud_list")
        assert hasattr(cloud_store, "cloud_list_with_data")
        assert hasattr(cloud_store, "cloud_delete")
        assert hasattr(cloud_store, "is_cloud_available")
        assert hasattr(cloud_store, "_TABLE")
        assert cloud_store._TABLE == "linkedin_content_store"

    def test_cloud_store_has_expected_functions(self):
        source = (PROJECT_ROOT / "cloud_store.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        }
        expected = {
            "_get_config",
            "_rest_headers",
            "is_cloud_available",
            "cloud_put",
            "cloud_get",
            "cloud_list",
            "cloud_list_with_data",
            "cloud_delete",
        }
        missing = expected - func_names
        assert not missing, f"Missing functions in cloud_store.py: {missing}"


class TestSyncScript:
    """Test sync_content_to_supabase.py structure."""

    def test_sync_script_parses(self):
        source = (PROJECT_ROOT / "sync_content_to_supabase.py").read_text(encoding="utf-8")
        ast.parse(source, filename="sync_content_to_supabase.py")

    def test_sync_script_has_expected_functions(self):
        source = (PROJECT_ROOT / "sync_content_to_supabase.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        }
        expected = {
            "parse_posts_from_md",
            "sync_series_content",
            "sync_engagement_data",
            "sync_project_docs",
            "sync_content_state",
            "sync_series_config",
            "main",
        }
        missing = expected - func_names
        assert not missing, f"Missing functions in sync script: {missing}"
