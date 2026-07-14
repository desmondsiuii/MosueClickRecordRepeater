import win32api
import win32con
import time
import csv
import sys
import os

class ClickReplayer:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.clicks = []
        self.running = True
        
    def load_clicks(self):
        """Load clicks from CSV file"""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.clicks.append({
                        'timestamp': float(row['timestamp']),
                        'x': int(float(row['x'])),  # Convert to float first to handle any format
                        'y': int(float(row['y'])),
                        'button': row['button'],
                        'action': row.get('action', 'click')
                    })
            print(f"✅ Loaded {len(self.clicks)} clicks from {self.csv_file}")
            
            # Show first few clicks for verification
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
        time.sleep(0.01)  # Small delay for mouse movement
        
        # Determine button constants
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
            print(f"⚠️ Unknown button: {button}, using left click")
            down_event = win32con.MOUSEEVENTF_LEFTDOWN
            up_event = win32con.MOUSEEVENTF_LEFTUP
        
        # Perform click using mouse_event (more reliable than click simulation)
        win32api.mouse_event(down_event, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(up_event, 0, 0, 0, 0)
    
    def press_f_key(self):
        """Press the F key using win32api"""
        # Key down
        win32api.keybd_event(win32con.VK_F, 0, 0, 0)
        time.sleep(0.05)  # Small delay between key down and up
        # Key up
        win32api.keybd_event(win32con.VK_F, 0, win32con.KEYEVENTF_KEYUP, 0)
        print("   ⌨️  Pressed 'F' key")
    
    def wait_with_countdown(self, seconds, message="Waiting"):
        """Wait with a countdown display"""
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
        print("=" * 60)
        
        # Countdown
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
                    # Wait 1 second before starting next loop (after F key was pressed)
                    self.wait_with_countdown(1, "Before next loop")
                
                # Get the first click's timestamp as reference
                first_timestamp = self.clicks[0]['timestamp']
                loop_start = time.time()
                
                for i, click in enumerate(self.clicks, 1):
                    if not self.running:
                        break
                    
                    # Calculate when this click should happen
                    elapsed_from_first = click['timestamp'] - first_timestamp
                    target_time = loop_start + (elapsed_from_first / speed_factor)
                    
                    # Wait until it's time for this click
                    sleep_time = target_time - time.time()
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                    # Perform the click
                    x, y = click['x'], click['y']
                    button = click['button']
                    
                    self.click_at(x, y, button)
                    
                    total_replayed += 1
                    current_time = time.time() - loop_start
                    print(f"  [{current_time:.2f}s] Click {total_replayed}: ({x}, {y}) - {button}")
                
                # After completing all clicks in this loop
                print(f"\n   ✅ Loop {loop + 1} completed")
                
                # Wait 2 seconds
                self.wait_with_countdown(2, "Before F key")
                
                # Press F key
                self.press_f_key()
                
                # If there are more loops, wait 1 second (handled at start of next loop)
                if loop < loop_count - 1:
                    print(f"   ⏳ Waiting 1 second before next loop...")
                    # The 1 second wait will happen at the start of the next loop
            
            print("\n" + "-" * 60)
            print(f"✅ Replay completed!")
            print(f"📊 Total clicks replayed: {total_replayed}")
            print(f"⏱️  Total duration: {time.time() - loop_start_time:.2f} seconds")
            print(f"⌨️  'F' key pressed {loop_count} time(s)")
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Replay stopped by user")
            print(f"📊 Replayed {total_replayed} clicks")
            print(f"⌨️  'F' key pressed {loop} time(s)")
        except Exception as e:
            print(f"\n❌ Error during replay: {e}")
    
    def replay_with_relative_position(self, speed_factor=1.0, pause_before_start=3, loop_count=1):
        """
        Replay with relative positioning (useful if window position changed)
        """
        if not self.clicks:
            print("❌ No clicks to replay!")
            return
        
        print("\n" + "=" * 60)
        print("CLICK REPLAYER (Relative Mode)")
        print("=" * 60)
        print("⚠️  This mode preserves relative click positions")
        print("    Make sure the target window is in the same position")
        print("=" * 60)
        
        # Ask for offset
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
            
            # Get click position
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
        
        # Apply offset to all clicks
        offset_clicks = []
        for click in self.clicks:
            offset_clicks.append({
                'timestamp': click['timestamp'],
                'x': click['x'] + offset_x,
                'y': click['y'] + offset_y,
                'button': click['button']
            })
        
        # Temporarily replace clicks with offset versions
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
        print("\nBehavior:")
        print("  After each loop:")
        print("    1. Wait 2 seconds")
        print("    2. Press 'F' key")
        print("    3. Wait 1 second before next loop (if looping)")
        print("\nExamples:")
        print(f"  python {sys.argv[0]} mouse_clicks.csv")
        print(f"  python {sys.argv[0]} mouse_clicks.csv --speed 2.0")
        print(f"  python {sys.argv[0]} mouse_clicks.csv --loop 5")
        print(f"  python {sys.argv[0]} mouse_clicks.csv --relative")
        print("=" * 60)
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # Parse arguments
    speed_factor = 1.0
    loop_count = 1
    pause_before_start = 3
    use_relative = False
    
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
        elif sys.argv[i] == '--relative':
            use_relative = True
            i += 1
        else:
            i += 1
    
    # Create replayer
    replayer = ClickReplayer(csv_file)
    if not replayer.load_clicks():
        sys.exit(1)
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will control your mouse and press F key!")
    print("   Make sure the target window is visible")
    confirm = input("Proceed? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Cancelled")
        sys.exit(0)
    
    # Start replay
    if use_relative:
        replayer.replay_with_relative_position(speed_factor, pause_before_start, loop_count)
    else:
        replayer.replay(speed_factor, pause_before_start, loop_count)

if __name__ == "__main__":
    main()