"""Test Module for service.py"""
# pylint: disable=invalid-name
import unittest
from unittest.mock import patch, Mock
import logging
from lib.service import BackgroundService, PlayerMonitor, run

_LOGGER = logging.getLogger(__name__)


class TestBackgroundService(unittest.TestCase):
    """Test BackgroundService class"""

    @patch('lib.service.PlayerMonitor')
    @patch('lib.service.Monitor')
    @patch('lib.service.Logger')
    def test_background_service_initialization(self, mock_logger, mock_monitor, mock_player_monitor):  # pylint: disable=unused-argument
        """Test BackgroundService initialization"""
        service = BackgroundService()

        self.assertIsNotNone(service._player)  # pylint: disable=protected-access
        mock_player_monitor.assert_called_once()

    @patch('lib.service.PlayerMonitor')
    @patch('lib.service.Logger')
    def test_background_service_run_normal_exit(self, mock_logger, mock_player_monitor):  # pylint: disable=unused-argument,invalid-name
        """Test BackgroundService run method with normal exit"""
        service = BackgroundService()

        # Mock abortRequested to return True immediately
        abort_requested_mock = Mock(return_value=True)
        wait_for_abort_mock = Mock(return_value=True)

        # Use setattr to avoid pylint naming issues
        setattr(service, 'abortRequested', abort_requested_mock)
        setattr(service, 'waitForAbort', wait_for_abort_mock)

        service.run()

        mock_logger.debug.assert_any_call('Service started')
        mock_logger.debug.assert_any_call('Service stopped')

    @patch('lib.service.PlayerMonitor')
    @patch('lib.service.Logger')
    def test_background_service_run_with_wait_cycles(self, mock_logger, mock_player_monitor):  # pylint: disable=unused-argument,invalid-name
        """Test BackgroundService run method with wait cycles"""
        service = BackgroundService()

        # Mock abortRequested to return False first few times, then True
        abort_requested_mock = Mock(side_effect=[False, False, False, True])
        wait_for_abort_mock = Mock(side_effect=[False, False, False, True])
        service.abortRequested = abort_requested_mock
        setattr(service, 'waitForAbort', wait_for_abort_mock)

        service.run()

        # Should have called waitForAbort 3 times (loop exits when abortRequested returns True)
        self.assertEqual(wait_for_abort_mock.call_count, 3)
        mock_logger.debug.assert_any_call('Service started')
        mock_logger.debug.assert_any_call('Service stopped')

    @patch('lib.service.PlayerMonitor')
    @patch('lib.service.Logger')
    def test_background_service_run_wait_for_abort_break(self, mock_logger, mock_player_monitor):  # pylint: disable=unused-argument,invalid-name
        """Test BackgroundService run method when waitForAbort returns True (covers line 27)"""
        service = BackgroundService()

        # Mock abortRequested to return False (so we enter the loop)
        # Mock waitForAbort to return True immediately (to trigger the break on line 27)
        abort_requested_mock = Mock(return_value=False)
        wait_for_abort_mock = Mock(return_value=True)
        service.abortRequested = abort_requested_mock
        setattr(service, 'waitForAbort', wait_for_abort_mock)

        service.run()

        # Should have called waitForAbort once and then broken out of the loop
        self.assertEqual(wait_for_abort_mock.call_count, 1)
        wait_for_abort_mock.assert_called_with(10)
        mock_logger.debug.assert_any_call('Service started')
        mock_logger.debug.assert_any_call('Service stopped')


class TestPlayerMonitor(unittest.TestCase):
    """Test PlayerMonitor class"""

    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_player_monitor_initialization(self, mock_logger, mock_player):  # pylint: disable=unused-argument
        """Test PlayerMonitor initialization"""
        player = PlayerMonitor()

        self.assertFalse(player._PlayerMonitor__listen)  # pylint: disable=protected-access
        self.assertFalse(player._PlayerMonitor__av_started)  # pylint: disable=protected-access
        self.assertIsNone(player._PlayerMonitor__path)  # pylint: disable=protected-access

    @patch('lib.service.getInfoLabel')
    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_playback_started_stalker_plugin(self, mock_logger, mock_player, mock_get_info_label):  # pylint: disable=unused-argument
        """Test onPlayBackStarted with Stalker plugin URL"""
        mock_get_info_label.return_value = 'plugin://plugin.video.stalkervod/play?video_id=123'

        player = PlayerMonitor()
        player.onPlayBackStarted()

        self.assertTrue(player._PlayerMonitor__listen)  # pylint: disable=protected-access
        self.assertFalse(player._PlayerMonitor__av_started)  # pylint: disable=protected-access
        self.assertEqual(player._PlayerMonitor__path, 'plugin://plugin.video.stalkervod/play?video_id=123')  # pylint: disable=protected-access
        mock_logger.debug.assert_called_with('Stalker Player: [onPlayBackStarted] called')

    @patch('lib.service.getInfoLabel')
    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_playback_started_other_plugin(self, mock_logger, mock_player, mock_get_info_label):  # pylint: disable=unused-argument
        """Test onPlayBackStarted with other plugin URL"""
        mock_get_info_label.return_value = 'plugin://plugin.video.other/play?video_id=123'

        player = PlayerMonitor()
        player.onPlayBackStarted()

        self.assertFalse(player._PlayerMonitor__listen)  # pylint: disable=protected-access
        mock_logger.debug.assert_not_called()

    @patch('lib.service.get_next_info_and_send_signal')
    @patch('lib.service.get_int_value')
    @patch('lib.service.parse_qsl')
    @patch('lib.service.urlsplit')
    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_av_started_with_next_episode(self, mock_logger, mock_player, mock_urlsplit,  # pylint: disable=unused-argument,too-many-positional-arguments
                                           mock_parse_qsl, mock_get_int_value, mock_get_next_info):
        """Test onAVStarted with next episode available"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = True  # pylint: disable=protected-access
        player._PlayerMonitor__path = 'plugin://plugin.video.stalkervod/play?video_id=123&series=1&total_episodes=5'  # pylint: disable=protected-access

        # Mock URL parsing
        mock_urlsplit.return_value.query = 'video_id=123&series=1&total_episodes=5'
        mock_parse_qsl.return_value = [('video_id', '123'), ('series', '1'), ('total_episodes', '5')]

        # Mock get_int_value to return episode numbers
        mock_get_int_value.side_effect = lambda params, key: {'series': 1, 'total_episodes': 5}.get(key, 0)

        player.onAVStarted()

        self.assertTrue(player._PlayerMonitor__av_started)  # pylint: disable=protected-access
        mock_get_next_info.assert_called_once()
        mock_logger.debug.assert_called_with('Stalker Player: [onAVStarted] called')

    @patch('lib.service.get_int_value')
    @patch('lib.service.parse_qsl')
    @patch('lib.service.urlsplit')
    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_av_started_last_episode(self, mock_logger, mock_player, mock_urlsplit,  # pylint: disable=unused-argument,too-many-positional-arguments
                                      mock_parse_qsl, mock_get_int_value):
        """Test onAVStarted with last episode"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = True  # pylint: disable=protected-access
        player._PlayerMonitor__path = 'plugin://plugin.video.stalkervod/play?video_id=123&series=5&total_episodes=5'  # pylint: disable=protected-access

        # Mock URL parsing
        mock_urlsplit.return_value.query = 'video_id=123&series=5&total_episodes=5'
        mock_parse_qsl.return_value = [('video_id', '123'), ('series', '5'), ('total_episodes', '5')]

        # Mock get_int_value to return episode numbers
        mock_get_int_value.side_effect = lambda params, key: {'series': 5, 'total_episodes': 5}.get(key, 0)

        player.onAVStarted()

        self.assertTrue(player._PlayerMonitor__av_started)  # pylint: disable=protected-access
        mock_logger.debug.assert_called_with('Stalker Player: [onAVStarted] called')

    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_av_started_not_listening(self, mock_logger, mock_player):  # pylint: disable=unused-argument
        """Test onAVStarted when not listening"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = False  # pylint: disable=protected-access

        player.onAVStarted()

        self.assertFalse(player._PlayerMonitor__av_started)  # pylint: disable=protected-access
        mock_logger.debug.assert_not_called()

    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_playback_error(self, mock_logger, mock_player):  # pylint: disable=unused-argument
        """Test onPlayBackError"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = True  # pylint: disable=protected-access
        player._PlayerMonitor__av_started = True  # pylint: disable=protected-access

        player.onPlayBackError()

        self.assertFalse(player._PlayerMonitor__av_started)  # pylint: disable=protected-access
        self.assertFalse(player._PlayerMonitor__listen)  # pylint: disable=protected-access
        mock_logger.debug.assert_called_with('Stalker Player: [onPlayBackError] called')

    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_playback_error_not_listening(self, mock_logger, mock_player):  # pylint: disable=unused-argument
        """Test onPlayBackError when not listening"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = False  # pylint: disable=protected-access

        player.onPlayBackError()

        mock_logger.debug.assert_not_called()

    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_playback_ended(self, mock_logger, mock_player):  # pylint: disable=unused-argument
        """Test onPlayBackEnded"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = True  # pylint: disable=protected-access
        player._PlayerMonitor__av_started = True  # pylint: disable=protected-access

        player.onPlayBackEnded()

        self.assertFalse(player._PlayerMonitor__listen)  # pylint: disable=protected-access
        self.assertFalse(player._PlayerMonitor__av_started)  # pylint: disable=protected-access
        mock_logger.debug.assert_called_with('Stalker Player: [onPlayBackEnded] called')

    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_playback_ended_not_listening(self, mock_logger, mock_player):  # pylint: disable=unused-argument
        """Test onPlayBackEnded when not listening"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = False  # pylint: disable=protected-access

        player.onPlayBackEnded()

        mock_logger.debug.assert_not_called()

    @patch('lib.service.xbmc')
    @patch('lib.service.parse_qsl')
    @patch('lib.service.urlsplit')
    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_playback_stopped_retry_with_cmd(self, mock_logger, mock_player,  # pylint: disable=unused-argument,too-many-positional-arguments
                                               mock_urlsplit, mock_parse_qsl, mock_xbmc):
        """Test onPlayBackStopped with retry using cmd parameter"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = True  # pylint: disable=protected-access
        player._PlayerMonitor__av_started = False  # pylint: disable=protected-access
        player._PlayerMonitor__path = 'plugin://plugin.video.stalkervod/play?video_id=123&cmd=test&use_cmd=0'  # pylint: disable=protected-access

        # Mock URL parsing
        mock_urlsplit.return_value.query = 'video_id=123&cmd=test&use_cmd=0'
        mock_parse_qsl.return_value = [('video_id', '123'), ('cmd', 'test'), ('use_cmd', '0')]

        player.onPlayBackStopped()

        self.assertFalse(player._PlayerMonitor__av_started)  # pylint: disable=protected-access
        mock_xbmc.executebuiltin.assert_any_call("Dialog.Close(all, true)")
        mock_xbmc.executebuiltin.assert_any_call('PlayMedia(plugin://plugin.video.stalkervod/play?video_id=123&cmd=test&use_cmd=0&use_cmd=1)')
        mock_logger.debug.assert_any_call('Stalker Player: [onPlayBackStopped] playback failed? retrying with cmd plugin://plugin.video.stalkervod/play?video_id=123&cmd=test&use_cmd=0&use_cmd=1')

    @patch('lib.service.parse_qsl')
    @patch('lib.service.urlsplit')
    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_playback_stopped_no_retry_conditions(self, mock_logger, mock_player, mock_urlsplit, mock_parse_qsl):  # pylint: disable=unused-argument
        """Test onPlayBackStopped without retry conditions"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = True  # pylint: disable=protected-access
        player._PlayerMonitor__av_started = False  # pylint: disable=protected-access
        player._PlayerMonitor__path = 'plugin://plugin.video.stalkervod/play?video_id=123'  # pylint: disable=protected-access

        # Mock URL parsing - no cmd parameter
        mock_urlsplit.return_value.query = 'video_id=123'
        mock_parse_qsl.return_value = [('video_id', '123')]

        player.onPlayBackStopped()

        self.assertFalse(player._PlayerMonitor__av_started)  # pylint: disable=protected-access
        mock_logger.debug.assert_called_with('Stalker Player: [onPlayBackStopped] called')

    @patch('lib.service.parse_qsl')
    @patch('lib.service.urlsplit')
    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_playback_stopped_use_cmd_already_set(self, mock_logger, mock_player, mock_urlsplit, mock_parse_qsl):  # pylint: disable=unused-argument
        """Test onPlayBackStopped when use_cmd is already 1"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = True  # pylint: disable=protected-access
        player._PlayerMonitor__av_started = False  # pylint: disable=protected-access
        player._PlayerMonitor__path = 'plugin://plugin.video.stalkervod/play?video_id=123&cmd=test&use_cmd=1'  # pylint: disable=protected-access

        # Mock URL parsing
        mock_urlsplit.return_value.query = 'video_id=123&cmd=test&use_cmd=1'
        mock_parse_qsl.return_value = [('video_id', '123'), ('cmd', 'test'), ('use_cmd', '1')]

        player.onPlayBackStopped()

        self.assertFalse(player._PlayerMonitor__av_started)  # pylint: disable=protected-access
        mock_logger.debug.assert_called_with('Stalker Player: [onPlayBackStopped] called')

    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_playback_stopped_av_started(self, mock_logger, mock_player):  # pylint: disable=unused-argument
        """Test onPlayBackStopped when AV was started"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = True  # pylint: disable=protected-access
        player._PlayerMonitor__av_started = True  # pylint: disable=protected-access

        player.onPlayBackStopped()

        self.assertFalse(player._PlayerMonitor__listen)  # pylint: disable=protected-access
        self.assertFalse(player._PlayerMonitor__av_started)  # pylint: disable=protected-access
        mock_logger.debug.assert_called_with('Stalker Player: [onPlayBackStopped] called')

    @patch('lib.service.Player')
    @patch('lib.service.Logger')
    def test_on_playback_stopped_not_listening(self, mock_logger, mock_player):  # pylint: disable=unused-argument
        """Test onPlayBackStopped when not listening"""
        player = PlayerMonitor()
        player._PlayerMonitor__listen = False  # pylint: disable=protected-access

        player.onPlayBackStopped()

        mock_logger.debug.assert_not_called()


class TestRunFunction(unittest.TestCase):
    """Test run function"""

    @patch('lib.service.BackgroundService')
    def test_run_function(self, mock_background_service):
        """Test run function creates and runs BackgroundService"""
        mock_service_instance = Mock()
        mock_background_service.return_value = mock_service_instance

        run()

        mock_background_service.assert_called_once()
        mock_service_instance.run.assert_called_once()


if __name__ == '__main__':
    unittest.main()
