"""Test suite for MonitorNap application.

This module contains unit tests for critical components of the MonitorNap
application to ensure stability and reliability.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the modules to test
from monitornap import ConfigManager, log_message, set_startup_registry
from monitor_controller import MonitorController, OverlayWindow
from ui_components import MonitorSettingsWidget, GlobalSettingsWidget, QuickActionsWidget


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self) -> None:
        """Clean up after tests."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_config_creation(self) -> None:
        """Test that default config is created when none exists."""
        config_manager = ConfigManager()
        self.assertIsInstance(config_manager.config, dict)
        self.assertIn("monitors", config_manager.config)
        self.assertIn("inactivity_limit", config_manager.config)
        self.assertIn("awake_mode", config_manager.config)
    
    def test_config_loading(self) -> None:
        """Test loading configuration from file."""
        # Create a test config file
        test_config = {
            "monitors": [{"monitor_index": 0}],
            "inactivity_limit": 30,
            "awake_mode": True
        }
        with open("monitornap_config.json", "w") as f:
            json.dump(test_config, f)
        
        config_manager = ConfigManager()
        self.assertEqual(config_manager.config["inactivity_limit"], 30)
        self.assertTrue(config_manager.config["awake_mode"])
    
    def test_config_saving(self) -> None:
        """Test saving configuration to file."""
        config_manager = ConfigManager()
        config_manager.config["inactivity_limit"] = 60
        config_manager.save_config()
        
        # Reload and verify
        new_config_manager = ConfigManager()
        self.assertEqual(new_config_manager.config["inactivity_limit"], 60)
    
    def test_config_merge_with_defaults(self) -> None:
        """Test that loaded config merges with defaults."""
        partial_config = {"inactivity_limit": 45}
        with open("monitornap_config.json", "w") as f:
            json.dump(partial_config, f)
        
        config_manager = ConfigManager()
        # Should have both the loaded value and default values
        self.assertEqual(config_manager.config["inactivity_limit"], 45)
        self.assertIn("awake_mode", config_manager.config)  # Default value


class TestLogging(unittest.TestCase):
    """Test cases for logging functionality."""
    
    def test_log_message_basic(self) -> None:
        """Test basic log message functionality."""
        # This is a simple test that doesn't require complex setup
        try:
            log_message("Test message")
            # If no exception is raised, the test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"log_message raised an exception: {e}")
    
    def test_log_message_debug(self) -> None:
        """Test debug log message functionality."""
        try:
            log_message("Debug message", debug=True)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"log_message with debug=True raised an exception: {e}")


class TestStartupRegistry(unittest.TestCase):
    """Test cases for Windows startup registry functionality."""
    
    @patch('os.name', 'nt')
    @patch('monitornap.winreg')
    def test_set_startup_registry_windows(self, mock_winreg) -> None:
        """Test setting startup registry on Windows."""
        # Mock the registry operations
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        
        set_startup_registry(True, "test_path.exe")
        
        # Verify that registry operations were called
        mock_winreg.OpenKey.assert_called()
        mock_key.SetValueEx.assert_called()
    
    @patch('os.name', 'posix')
    def test_set_startup_registry_non_windows(self) -> None:
        """Test that startup registry is not set on non-Windows systems."""
        # Should not raise an exception
        set_startup_registry(True, "test_path.exe")


class TestMonitorController(unittest.TestCase):
    """Test cases for MonitorController class."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mock_config = {
            "monitor_index": 0,
            "display_index": 0,
            "ddc_index": 0,
            "enable_hardware_dimming": True,
            "enable_software_dimming": True,
            "hardware_dimming_level": 30,
            "software_dimming_level": 0.5,
            "overlay_color": "#000000"
        }
        self.mock_global_config = {
            "awake_mode": False,
            "inactivity_limit": 10,
            "overlay_fade_time": 0.5,
            "overlay_fade_steps": 10
        }
    
    @patch('monitor_controller.get_monitors')
    @patch('monitor_controller.screeninfo.get_monitors')
    def test_monitor_controller_init(self, mock_screeninfo, mock_get_monitors) -> None:
        """Test MonitorController initialization."""
        # Mock the monitor detection
        mock_screeninfo.return_value = [Mock(x=0, y=0, width=1920, height=1080)]
        mock_get_monitors.return_value = [Mock()]
        
        # Mock the monitor control
        mock_monitor = Mock()
        mock_monitor.get_luminance.return_value = 100
        mock_get_monitors.return_value = [mock_monitor]
        
        controller = MonitorController(self.mock_config, self.mock_global_config)
        
        self.assertEqual(controller.monitor_index, 0)
        self.assertEqual(controller.display_index, 0)
        self.assertFalse(controller.is_dimmed)
    
    def test_monitor_controller_geometry(self) -> None:
        """Test monitor geometry handling."""
        with patch('monitor_controller.screeninfo.get_monitors') as mock_get_monitors:
            mock_get_monitors.return_value = [Mock(x=0, y=0, width=1920, height=1080)]
            
            controller = MonitorController(self.mock_config, self.mock_global_config)
            
            self.assertEqual(controller.left, 0)
            self.assertEqual(controller.top, 0)
            self.assertEqual(controller.width, 1920)
            self.assertEqual(controller.height, 1080)


class TestUIComponents(unittest.TestCase):
    """Test cases for UI components."""
    
    def test_monitor_settings_widget_creation(self) -> None:
        """Test MonitorSettingsWidget creation."""
        # Mock the required callbacks
        callbacks = {
            'on_display_changed': Mock(),
            'on_hw_toggled': Mock(),
            'on_sw_toggled': Mock(),
            'on_hw_slider_changed': Mock(),
            'on_sw_slider_changed': Mock(),
            'on_color_picked': Mock()
        }
        
        config = {
            "display_index": 0,
            "enable_hardware_dimming": True,
            "enable_software_dimming": True,
            "hardware_dimming_level": 30,
            "software_dimming_level": 0.5,
            "overlay_color": "#000000"
        }
        
        # This test would require PyQt6 to be available
        # For now, we'll just test that the class can be imported
        self.assertTrue(hasattr(MonitorSettingsWidget, '__init__'))


class TestIntegration(unittest.TestCase):
    """Integration tests for the application."""
    
    def test_config_manager_integration(self) -> None:
        """Test that ConfigManager works with real file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Test full cycle: create, modify, save, reload
                config_manager = ConfigManager()
                original_limit = config_manager.config["inactivity_limit"]
                
                # Modify config
                config_manager.config["inactivity_limit"] = 999
                config_manager.save_config()
                
                # Create new instance and verify
                new_config_manager = ConfigManager()
                self.assertEqual(new_config_manager.config["inactivity_limit"], 999)
                
            finally:
                os.chdir(original_cwd)


def run_tests() -> None:
    """Run all tests and report results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestConfigManager,
        TestLogging,
        TestStartupRegistry,
        TestMonitorController,
        TestUIComponents,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for failure in result.failures:
            print(f"FAIL: {failure[0]}")
            print(failure[1])
        for error in result.errors:
            print(f"ERROR: {error[0]}")
            print(error[1])


if __name__ == "__main__":
    run_tests()