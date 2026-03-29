import difflib
import time
from pathlib import Path

PROMPT_FILE = Path(__file__).parent / "system_prompt.txt"
POLL_INTERVAL = 0.2

GREEN = "\033[92m"
CYAN = "\033[96m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_with_highlights(prev_lines, curr_lines, turn):
    print(f"\n{CYAN}{'─' * 50}{RESET}")
    print(f"{BOLD}{CYAN}  ◆ System Prompt (v{turn}){RESET}")
    print(f"{CYAN}{'─' * 50}{RESET}")

    changed = set()
    matcher = difflib.SequenceMatcher(None, prev_lines, curr_lines)
    for tag, _, _, j1, j2 in matcher.get_opcodes():
        if tag in ("replace", "insert"):
            changed.update(range(j1, j2))

    for i, line in enumerate(curr_lines):
        if i in changed:
            print(f"{BOLD}{GREEN}  {line}{RESET}")
        else:
            print(f"{DIM}  {line}{RESET}")

def display_prompt_loop():
    prev_lines = []
    turn = 0

    print(f"\n{BOLD}{CYAN}{'=' * 50}")
    print(f"  System Prompt Monitor")
    print(f"{'=' * 50}{RESET}")
    print(f"{DIM}  Watching: {PROMPT_FILE.name}")
    print(f"  Press Ctrl+C to stop.{RESET}")

    try:
        while True:
            if PROMPT_FILE.exists():
                current = PROMPT_FILE.read_text(encoding="utf-8").strip()
                curr_lines = current.splitlines()
            else:
                curr_lines = []

            if curr_lines != prev_lines:
                print_with_highlights(prev_lines, curr_lines, turn)
                turn += 1
                prev_lines = curr_lines

            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print(f"\n{DIM}모니터링 종료. (총 {turn}개 버전 감지됨){RESET}\n")

if __name__ == "__main__":
    display_prompt_loop()
