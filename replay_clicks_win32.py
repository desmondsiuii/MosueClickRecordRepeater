import win32api
import win32con
import time
import csv
import sys
import os

# Virtual key codes
VK_F = 0x46  # Hex for 'F' key

class ClickReplayer:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.clicks = []
        self.running = True
        self.click_delay = 0.5  # Delay between mouse move and click (seconds)
        
    def load_clicks(self):
        """Load clicks from CSV file"""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.clicks.append({
                        'timestamp': float(row['timestamp']),
                        'x': int(float(row['x'])),
                        'y': int(float(row['y'])),
                        'button': row['button'],
                        'action': row.get('action', 'click')
                    })
            print(f"✅ Loaded {len(self.clicks)} clicks from {self.csv_file}")
            
            print("\n📋 First 5 clicks:")
            print("-" * 50)
            for i, click in enumerate(self.clicks[:5]):
                print(f"  {i+1}. ({click['x']}, {click['y']}) - {click['button']} at {click['timestamp']:.2f}s")
            if len(self.clicks) > 5:
                print(f"  ... and {len(self.clicks) - 5} more")
            print("-" * 50)
            return True
            
        except FileNotFoundError:
            print(f"❌ File not found: {self.csv_file}")
            return False
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return False
    
    def click_at(self, x, y, button='left'):
        """Perform a click at the specified position using win32api"""
        # Move mouse to position
        win32api.SetCursorPos((x, y))
        
        # Wait before clicking to prevent dragging
        time.sleep(self.click_delay)
        
        if button.lower() == 'left':
            down_event = win32con.MOUSEEVENTF_LEFTDOWN
            up_event = win32con.MOUSEEVENTF_LEFTUP
        elif button.lower() == 'right':
            down_event = win32con.MOUSEEVENTF_RIGHTDOWN
            up_event = win32con.MOUSEEVENTF_RIGHTUP
        elif button.lower() == 'middle':
            down_event = win32con.MOUSEEVENTF_MIDDLEDOWN
            up_event = win32con.MOUSEEVENTF_MIDDLEUP
        else:
            down_event = win32con.MOUSEEVENTF_LEFTDOWN
            up_event = win32con.MOUSEEVENTF_LEFTUP
        
        win32api.mouse_event(down_event, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(up_event, 0, 0, 0, 0)
    
    def press_f_key(self):
        """Press and release the F key"""
        print("   ⌨️  Pressing 'F' key...")
        
        # Press F key down
        win32api.keybd_event(VK_F, 0, 0, 0)
        time.sleep(0.05)
        
        # Release F key up
        win32api.keybd_event(VK_F, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("   ✅ 'F' key pressed and released")
    
    def wait_with_countdown(self, seconds, message="Waiting"):
        """Wait with countdown display"""
        for i in range(seconds, 0, -1):
            print(f"   ⏳ {message} {i}s...", end='\r')
            time.sleep(1)
        print(f"   ⏳ {message} done!{' ' * 10}")
    
    def replay(self, speed_factor=1.0, pause_before_start=3, loop_count=1):
        """Replay the recorded clicks"""
        if not self.clicks:
            print("❌ No clicks to replay!")
            return
        
        print("\n" + "=" * 60)
        print("CLICK REPLAYER WITH F KEY")
        print("=" * 60)
        print(f"📁 File: {os.path.basename(self.csv_file)}")
        print(f"🚀 Speed: {speed_factor}x")
        print(f"🔄 Loop: {loop_count} time(s)")
        print(f"⏰ Clicks: {len(self.clicks)}")
        print(f"⌨️  F key will be pressed after each loop")
        print(f"⏱️  Click delay: {self.click_delay}s (between move and click)")
        print("=" * 60)
        
        print(f"\n⏳ Starting in {pause_before_start} seconds...")
        for i in range(pause_before_start, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        print("\n🎬 Replaying clicks...")
        print("⚠️  Press Ctrl+C to stop")
        print("-" * 60)
        
        total_replayed = 0
        loop_start_time = time.time()
        
        try:
            for loop in range(loop_count):
                if not self.running:
                    break
                    
                if loop > 0:
                    print(f"\n🔄 Loop {loop + 1}/{loop_count}")
                    self.wait_with_countdown(1, "Before next loop")
                
                first_timestamp = self.clicks[0]['timestamp']
                loop_start = time.time()
                
                for i, click in enumerate(self.clicks, 1):
                    if not self.running:
                        break
                    
                    elapsed_from_first = click['timestamp'] - first_timestamp
                    target_time = loop_start + (elapsed_from_first / speed_factor)
                    
                    sleep_time = target_time - time.time()
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                    x, y = click['x'], click['y']
                    button = click['button']
                    
                    self.click_at(x, y, button)
                    
                    total_replayed += 1
                    current_time = time.time() - loop_start
                    print(f"  [{current_time:.2f}s] Click {total_replayed}: ({x}, {y}) - {button}")
                
                # AFTER COMPLETING ALL CLICKS IN THIS LOOP
                print(f"\n   ✅ Loop {loop + 1} completed")
                
                # WAIT 3 SECONDS
                self.wait_with_countdown(3, "Before F key")
                
                # PRESS F KEY
                self.press_f_key()
                
                # WAIT 3 SECONDS
                self.wait_with_countdown(3, "After F key")

                # If there are more loops, wait is handled at start of next loop
            
            print("\n" + "-" * 60)
            print(f"✅ Replay completed!")
            print(f"📊 Total clicks replayed: {total_replayed}")
            print(f"⏱️  Total duration: {time.time() - loop_start_time:.2f} seconds")
            print(f"⌨️  'F' key pressed {loop_count} time(s)")
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Replay stopped by user")
            print(f"📊 Replayed {total_replayed} clicks")
        except Exception as e:
            print(f"\n❌ Error during replay: {e}")
    
    def replay_with_relative_position(self, speed_factor=1.0, pause_before_start=3, loop_count=1):
        """Replay with relative positioning"""
        if not self.clicks:
            print("❌ No clicks to replay!")
            return
        
        print("\n" + "=" * 60)
        print("CLICK REPLAYER (Relative Mode)")
        print("=" * 60)
        print("⚠️  This mode preserves relative click positions")
        print("    Make sure the target window is in the same position")
        print("=" * 60)
        
        print("\n📌 Choose positioning mode:")
        print("  1. Use absolute positions (as recorded)")
        print("  2. Enter offset (dx, dy)")
        print("  3. Click a reference point to calculate offset")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        offset_x = 0
        offset_y = 0
        
        if choice == '2':
            offset_x = int(input("Enter X offset: "))
            offset_y = int(input("Enter Y offset: "))
        elif choice == '3':
            print("\n🖱️  Click on the reference point (where original (0,0) would be)...")
            time.sleep(2)
            
            def get_mouse_pos():
                print("Click anywhere to set reference...")
                while True:
                    if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                        x, y = win32api.GetCursorPos()
                        print(f"Reference point set to: ({x}, {y})")
                        return x, y
                    time.sleep(0.05)
            
            ref_x, ref_y = get_mouse_pos()
            offset_x = ref_x
            offset_y = ref_y
        
        print(f"\n📐 Offset: ({offset_x}, {offset_y})")
        
        offset_clicks = []
        for click in self.clicks:
            offset_clicks.append({
                'timestamp': click['timestamp'],
                'x': click['x'] + offset_x,
                'y': click['y'] + offset_y,
                'button': click['button']
            })
        
        original_clicks = self.clicks
        self.clicks = offset_clicks
        
        try:
            self.replay(speed_factor, pause_before_start, loop_count)
        finally:
            self.clicks = original_clicks

def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("CLICK REPLAYER WITH F KEY")
        print("=" * 60)
        print("Usage:")
        print(f"  python {sys.argv[0]} <csv_file> [options]")
        print("\nOptions:")
        print("  --speed N   : Playback speed (default: 1.0)")
        print("  --loop N    : Loop count (default: 1)")
        print("  --relative  : Use relative positioning mode")
        print("  --delay N   : Delay before start in seconds (default: 3)")
        print("  --click-delay N : Delay between mouse move and click (default: 0.5)")
        print("\nBehavior:")
        print("  After each loop:")
        print("    1. Wait 3 seconds")
        print("    2. Press 'F' key")
        print("    3. Wait 3 seconds")
        print("\nExamples:")
        print(f"  python {sys.argv[0]} mouse_clicks.csv")
        print(f"  python {sys.argv[0]} mouse_clicks.csv --speed 2.0")
        print(f"  python {sys.argv[0]} mouse_clicks.csv --loop 5")
        print(f"  python {sys.argv[0]} mouse_clicks.csv --click-delay 1.0")
        print("=" * 60)
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    speed_factor = 1.0
    loop_count = 1
    pause_before_start = 3
    use_relative = False
    click_delay = 0.5
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--speed' and i + 1 < len(sys.argv):
            speed_factor = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--loop' and i + 1 < len(sys.argv):
            loop_count = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--delay' and i + 1 < len(sys.argv):
            pause_before_start = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--click-delay' and i + 1 < len(sys.argv):
            click_delay = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--relative':
            use_relative = True
            i += 1
        else:
            i += 1
    
    replayer = ClickReplayer(csv_file)
    replayer.click_delay = click_delay
    
    if not replayer.load_clicks():
        sys.exit(1)
    
    print("\n⚠️  WARNING: This will control your mouse and press F key!")
    print("   Make sure the target window is visible")
    confirm = input("Proceed? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Cancelled")
        sys.exit(0)
    
    if use_relative:
        replayer.replay_with_relative_position(speed_factor, pause_before_start, loop_count)
    else:
        replayer.replay(speed_factor, pause_before_start, loop_count)

if __name__ == "__main__":
    main()