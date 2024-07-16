"""Test Module for addon.py"""
import unittest
from unittest.mock import patch
from lib.loggers import Logger


class TestLogger(unittest.TestCase):
    """TestLogger class"""

    @patch('lib.loggers.xbmc')
    def test_info(self, mock_xbmc):
        """Test run"""
        with patch.object(mock_xbmc, 'LOGINFO', 1):
            Logger.info('test')
            mock_xbmc.log.assert_called_with('plugin.video.stalkervod: test', 1)

    @patch('lib.loggers.xbmc')
    def test_error(self, mock_xbmc):
        """Test run"""
        with patch.object(mock_xbmc, 'LOGERROR', 4):
            Logger.error('test')
            mock_xbmc.log.assert_called_with('plugin.video.stalkervod: test', 4)

    @patch('lib.loggers.xbmc')
    def test_warn(self, mock_xbmc):
        """Test run"""
        with patch.object(mock_xbmc, 'LOGWARNING', 3):
            Logger.warn('test')
            mock_xbmc.log.assert_called_with('plugin.video.stalkervod: test', 3)

    @patch('lib.loggers.xbmc')
    def test_debug(self, mock_xbmc):
        """Test run"""
        with patch.object(mock_xbmc, 'LOGDEBUG', 0):
            Logger.debug('test')
            mock_xbmc.log.assert_called_with('plugin.video.stalkervod: test', 0)
