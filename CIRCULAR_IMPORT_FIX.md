# Circular Import Fix - MonitorNap

## Problem
The application was experiencing a circular import error when packaged with PyInstaller:

```
ImportError: cannot import name 'MonitorController' from partially initialized module 'monitor_controller' 
(most likely due to a circular import)
```

### Root Cause
The circular dependency chain was:
1. `monitornap.py` (line 187) → imports `MonitorController` from `monitor_controller.py`
2. `monitor_controller.py` (line 15) → imports `log_message` from `monitornap.py`
3. `ui_components.py` (line 15) → also imports `log_message` from `monitornap.py`

This created a circular dependency where `monitornap` and `monitor_controller` depended on each other.

## Solution
Created a new independent logging module (`logging_utils.py`) that contains the logging functionality. This allows all other modules to import logging utilities without creating circular dependencies.

### Changes Made

1. **Created `/workspace/logging_utils.py`**
   - Extracted `log_message()` function
   - Extracted `LOG_CACHE` deque
   - Extracted `DEBUG_MODE` flag
   - Added `set_debug_mode()` helper function

2. **Updated `/workspace/monitornap.py`**
   - Removed logging function definitions
   - Changed: `from logging_utils import log_message, LOG_CACHE, set_debug_mode`
   - Updated debug mode setting to use `set_debug_mode()` instead of global variable

3. **Updated `/workspace/monitor_controller.py`**
   - Changed: `from logging_utils import log_message` (was `from monitornap import log_message`)

4. **Updated `/workspace/ui_components.py`**
   - Changed: `from logging_utils import log_message` (was `from monitornap import log_message`)

### New Import Structure

```
logging_utils.py (no dependencies on other app modules)
    ↑
    ├── monitornap.py
    ├── monitor_controller.py
    └── ui_components.py
```

Now:
- `logging_utils.py` has no dependencies on other app modules
- All modules import logging from `logging_utils.py`
- `monitornap.py` imports from `monitor_controller.py` and `ui_components.py`
- No circular dependencies exist

## Verification
The fix has been verified to eliminate the circular import issue. The application can now be imported successfully without circular dependency errors.

## Files Modified
- ✅ Created: `logging_utils.py`
- ✅ Modified: `monitornap.py`
- ✅ Modified: `monitor_controller.py`
- ✅ Modified: `ui_components.py`
