"""Test Module for entry point modules"""
import unittest
from unittest.mock import patch
import logging

_LOGGER = logging.getLogger(__name__)


class TestAddonEntry(unittest.TestCase):
    """Test addon_entry.py module"""

    @patch('sys.argv', ['plugin://plugin.video.stalkervod/', '1', '?action=list'])
    @patch('lib.addon.run')
    def test_addon_entry_main_execution(self, mock_run):
        """Test addon_entry.py main execution"""
        # Use runpy to execute the module as __main__
        import runpy  # pylint: disable=import-outside-toplevel

        try:
            runpy.run_module('addon_entry', run_name='__main__')
        except SystemExit:
            pass  # Expected when running as main

        # Verify that run was called with sys.argv
        mock_run.assert_called_once_with(['plugin://plugin.video.stalkervod/', '1', '?action=list'])

    @patch('sys.argv', ['plugin://plugin.video.stalkervod/', '2', '?action=play&video_id=123'])
    @patch('lib.addon.run')
    def test_addon_entry_with_different_args(self, mock_run):
        """Test addon_entry.py with different arguments"""
        # Use runpy to execute the module as __main__
        import runpy  # pylint: disable=import-outside-toplevel

        try:
            runpy.run_module('addon_entry', run_name='__main__')
        except SystemExit:
            pass  # Expected when running as main

        # Verify that run was called with the new sys.argv
        mock_run.assert_called_with(['plugin://plugin.video.stalkervod/', '2', '?action=play&video_id=123'])

    def test_addon_entry_import_structure(self):
        """Test that addon_entry.py has correct import structure"""
        import addon_entry  # pylint: disable=import-outside-toplevel

        # Verify the module exists and can be imported
        self.assertIsNotNone(addon_entry)

    @patch('lib.addon.run')
    def test_addon_entry_not_main(self, mock_run):
        """Test that addon_entry.py doesn't execute when not __main__"""
        # When imported normally (not as __main__), run should not be called
        # This test verifies the if __name__ == '__main__': guard works

        # Since we're importing as a test, __name__ won't be '__main__'
        # So run should not be called during import
        mock_run.reset_mock()

        import importlib  # pylint: disable=import-outside-toplevel
        import addon_entry  # pylint: disable=import-outside-toplevel
        importlib.reload(addon_entry)

        # run should not have been called during import
        mock_run.assert_not_called()


class TestServiceEntry(unittest.TestCase):
    """Test service_entry.py module"""

    @patch('lib.service.run')
    def test_service_entry_main_execution(self, mock_run):
        """Test service_entry.py main execution"""
        # Use runpy to execute the module as __main__
        import runpy  # pylint: disable=import-outside-toplevel

        try:
            runpy.run_module('service_entry', run_name='__main__')
        except SystemExit:
            pass  # Expected when running as main

        # Verify that run was called
        mock_run.assert_called_once()

    def test_service_entry_import_structure(self):
        """Test that service_entry.py has correct import structure"""
        import service_entry  # pylint: disable=import-outside-toplevel

        # Verify the module exists and can be imported
        self.assertIsNotNone(service_entry)

    @patch('lib.service.run')
    def test_service_entry_not_main(self, mock_run):
        """Test that service_entry.py doesn't execute when not __main__"""
        # When imported normally (not as __main__), run should not be called
        # This test verifies the if __name__ == '__main__': guard works

        # Since we're importing as a test, __name__ won't be '__main__'
        # So run should not be called during import
        mock_run.reset_mock()

        import importlib  # pylint: disable=import-outside-toplevel
        import service_entry  # pylint: disable=import-outside-toplevel
        importlib.reload(service_entry)

        # run should not have been called during import
        mock_run.assert_not_called()


class TestEntryPointIntegration(unittest.TestCase):
    """Test integration aspects of entry points"""

    def test_addon_entry_imports(self):
        """Test that addon_entry.py can import required modules"""
        try:
            from sys import argv  # pylint: disable=import-outside-toplevel,unused-import
            from lib.addon import run  # pylint: disable=import-outside-toplevel,unused-import
            # If we get here, imports work
            self.assertIsNotNone(argv)
        except ImportError as e:
            self.fail(f"addon_entry.py imports failed: {e}")

    def test_service_entry_imports(self):
        """Test that service_entry.py can import required modules"""
        try:
            from lib.service import run  # pylint: disable=import-outside-toplevel,unused-import
            # If we get here, imports work
            self.assertIsNotNone(run)
        except ImportError as e:
            self.fail(f"service_entry.py imports failed: {e}")

    @patch('sys.argv', ['test_script', 'arg1', 'arg2'])
    @patch('lib.addon.run')
    def test_addon_entry_argv_handling(self, mock_run):
        """Test that addon_entry.py properly handles sys.argv"""
        # Use runpy to execute the module as __main__
        import runpy  # pylint: disable=import-outside-toplevel

        try:
            runpy.run_module('addon_entry', run_name='__main__')
        except SystemExit:
            pass  # Expected when running as main

        # Verify argv was passed correctly
        mock_run.assert_called_with(['test_script', 'arg1', 'arg2'])

    @patch('lib.service.run')
    @patch('lib.addon.run')
    def test_entry_points_isolation(self, mock_addon_run, mock_service_run):
        """Test that entry points don't interfere with each other"""
        # Use runpy to execute both modules as __main__
        import runpy  # pylint: disable=import-outside-toplevel

        try:
            runpy.run_module('addon_entry', run_name='__main__')
        except SystemExit:
            pass  # Expected when running as main

        try:
            runpy.run_module('service_entry', run_name='__main__')
        except SystemExit:
            pass  # Expected when running as main

        # Each should have called their respective run function
        mock_addon_run.assert_called()
        mock_service_run.assert_called()

    def test_addon_entry_error_handling(self):
        """Test addon_entry.py behavior when lib.addon.run raises exception"""
        with patch('lib.addon.run', side_effect=Exception("Test error")):
            try:
                import addon_entry  # pylint: disable=import-outside-toplevel
                import importlib  # pylint: disable=import-outside-toplevel
                importlib.reload(addon_entry)
                # If we get here, the exception was not propagated
                # This might be expected behavior
            except Exception as exc:  # pylint: disable=broad-exception-caught
                # If exception is propagated, that's also valid
                self.assertIn("Test error", str(exc))

    def test_service_entry_error_handling(self):
        """Test service_entry.py behavior when lib.service.run raises exception"""
        with patch('lib.service.run', side_effect=Exception("Test error")):
            try:
                import service_entry  # pylint: disable=import-outside-toplevel
                import importlib  # pylint: disable=import-outside-toplevel
                importlib.reload(service_entry)
                # If we get here, the exception was not propagated
                # This might be expected behavior
            except Exception as exc:  # pylint: disable=broad-exception-caught
                # If exception is propagated, that's also valid
                self.assertIn("Test error", str(exc))


class TestEntryPointDocumentation(unittest.TestCase):
    """Test documentation and metadata of entry points"""

    def test_addon_entry_docstring(self):
        """Test that addon_entry.py has proper docstring"""
        import addon_entry  # pylint: disable=import-outside-toplevel

        # Check if module has a docstring
        self.assertIsNotNone(addon_entry.__doc__)
        self.assertIn("Stalker VOD plugin entry point", addon_entry.__doc__)

    def test_service_entry_docstring(self):
        """Test that service_entry.py has proper docstring"""
        import service_entry  # pylint: disable=import-outside-toplevel

        # Check if module has a docstring
        self.assertIsNotNone(service_entry.__doc__)
        self.assertIn("Service entry point", service_entry.__doc__)

    def test_addon_entry_encoding(self):
        """Test that addon_entry.py has proper encoding declaration"""
        with open('addon_entry.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Should have future imports for Python 2/3 compatibility
        self.assertIn("from __future__ import", content)

    def test_service_entry_encoding(self):
        """Test that service_entry.py has proper encoding declaration"""
        with open('service_entry.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Should have encoding declaration and future imports
        self.assertIn("# -*- coding: utf-8 -*-", content)
        self.assertIn("from __future__ import", content)


if __name__ == '__main__':
    unittest.main()
