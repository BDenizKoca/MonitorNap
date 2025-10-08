#!/usr/bin/env python3
"""Test runner for MonitorNap application.

This script runs the test suite and provides a simple way to verify
that the application components are working correctly.
"""

import sys
import os
import subprocess

def run_tests() -> None:
    """Run the test suite and report results."""
    print("🧪 Running MonitorNap Test Suite")
    print("=" * 50)
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Import and run tests
        from test_monitornap import run_tests
        run_tests()
    except ImportError as e:
        print(f"❌ Failed to import test modules: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        return False
    
    return True

def check_dependencies() -> None:
    """Check if required dependencies are available."""
    required_modules = [
        'PyQt6',
        'keyboard',
        'monitorcontrol',
        'screeninfo'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("⚠️  Missing dependencies:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\nInstall missing dependencies with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def main() -> None:
    """Main test runner entry point."""
    print("MonitorNap Test Runner")
    print("=" * 30)
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Run tests
    success = run_tests()
    
    if success:
        print("\n🎉 Test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test suite failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()