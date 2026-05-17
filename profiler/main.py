from colorama import Fore, Style, init
from api import start_server

init(autoreset=True)

print(Fore.CYAN + """
╔══════════════════════════════════════════╗
║      Dynamic Behavior Profiler v3.0      ║
║      Stage 3 — ML & Diagnostics          ║
╚══════════════════════════════════════════╝
""")

print(Fore.YELLOW + "Checklist before starting:")
print("  1. Android emulator is running")
print("  2. BehaviorTestApp is installed and open")
print("  3. ADB can see the device (adb devices)")
print()

start_server()