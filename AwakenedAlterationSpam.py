import keyboard
import pyautogui
import pyperclip
import time
import re
import sys
import random

safety_limit = 40  # Max number of roll attempts before exiting

running = False
user_regex = ""

# --- Bell curve delay settings ---
MEAN_DELAY = 0.22
STD_DEV = 0.05
MIN_DELAY = 0.05
MAX_DELAY = 0.45

def get_bell_curve_delay():
    """Return a natural human-style delay using a Gaussian curve + micro jitter."""
    delay = random.gauss(MEAN_DELAY, STD_DEV)
    delay = max(MIN_DELAY, min(MAX_DELAY, delay))

    # Add micro jitter (extra small shake)
    jitter = random.uniform(-0.015, 0.015)  # ±15ms
    delay += jitter

    # Clamp again after jitter
    return max(MIN_DELAY, min(MAX_DELAY, delay))


# --- Realistic occasional pauses ---
def maybe_take_human_pause(attempt):
    """Every few clicks, introduce a natural human pause."""
    # About every 8–15 clicks
    if attempt % random.randint(8, 15) == 0:
        # 90% of the time: small pause
        if random.random() < 0.90:
            time.sleep(random.uniform(0.3, 0.6))
        else:
            # 10% of the time: longer natural pause
            time.sleep(random.uniform(1.0, 1.8))


def extract_item_name(text):
    lines = text.splitlines()
    capture = False
    extracted = []

    for line in lines:
        if line.startswith("Rarity:"):
            capture = True
            continue
        if line.strip() == "--------" and capture:
            break
        if capture:
            extracted.append(line)

    return "\n".join(extracted)

def start():
    global running, user_regex
    if not running:
        running = True
        print("Program started.")

        attempts = 0
        attempt_width = len(str(safety_limit))

        while attempts < safety_limit:
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.05)
            raw_text = pyperclip.paste()

            item_name = extract_item_name(raw_text)
            item_name = "".join(line.lstrip() for line in item_name.splitlines())

            if re.search(user_regex, item_name):
                print("Match found. Exiting.")
                keyboard.unhook_all_hotkeys()
                sys.exit(0)

            print(f"Attempt {str(attempts + 1).rjust(attempt_width)}: Regex: {user_regex} Item Name: {item_name}")

            pyautogui.click()
            attempts += 1

            # Realistic pause logic
            maybe_take_human_pause(attempts)

            # Natural human-style timing
            time.sleep(get_bell_curve_delay())

        print(f"Reached safety limit of {safety_limit} attempts. Exiting.")
        running = False

def stop():
    global running
    if running:
        running = False
        print("Program stopped.")

# Ask user for safety limit (default to 40 if invalid)
try:
    user_input = input("Enter safety limit [40] (max attempts before auto-stop): ").strip()
    SAFETY_LIMIT = int(user_input) if user_input else 40
except ValueError:
    SAFETY_LIMIT = 40
print(f"Using safety limit: {SAFETY_LIMIT}")

# Ask user for regex
user_regex = input("Enter regex to match item name: ")

keyboard.add_hotkey('shift+=', start)
keyboard.add_hotkey('shift+-', stop)

print("Waiting for Shift+= to start, Shift+- to stop.")
print("Press Ctrl+C to exit manually if needed.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nExiting on Ctrl+C")
