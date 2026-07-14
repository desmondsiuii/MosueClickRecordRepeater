import win32api
import win32con
import time

# Virtual key codes
VK_F = 0x46  # Hex for 'F' key (70 in decimal)

print("Press F key in 3 seconds...")
time.sleep(3)

# Press F key down
win32api.keybd_event(VK_F, 0, 0, 0)
time.sleep(0.1)

# Release F key up
win32api.keybd_event(VK_F, 0, win32con.KEYEVENTF_KEYUP, 0)
print("✅ F key pressed!")