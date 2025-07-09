import subprocess
import time
import random
import string
import os
import shutil

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

SERVER_EXEC = './server'
CLIENT_EXEC = './client'
MSG_DELIM = '====='
RESULTS_FILE = 'minitalk_test_results.txt'
VALGRIND_SERVER_LOG = 'valgrind_server.log'

# Check if valgrind is available
VALGRIND = shutil.which('valgrind')
if not VALGRIND:
    print(f"{YELLOW}[WARN]{RESET} Valgrind not found. Leak checks will be skipped.")

def write_result(line):
    with open(RESULTS_FILE, 'a') as f:
        f.write(line + '\n')

def print_header(text):
    print(f"\n{BOLD}{BLUE}=== {text} ==={RESET}")
    write_result(f"\n=== {text} ===")

def print_ok(msg):
    print(f"{GREEN}[OK]{RESET} {msg}")
    write_result(f"[OK] {msg}")

def print_fail(msg):
    print(f"{RED}[FAIL]{RESET} {msg}")
    write_result(f"[FAIL] {msg}")

def print_info(msg):
    print(f"{YELLOW}[INFO]{RESET} {msg}")
    write_result(f"[INFO] {msg}")

def print_time(duration):
    print(f"{BOLD}{YELLOW}[TIME]{RESET} {duration:.4f} seconds")
    write_result(f"[TIME] {duration:.4f} seconds")

def print_leak(leak_str, ok):
    color = GREEN if ok else RED
    status = "[LEAKS OK]" if ok else "[LEAKS FAIL]"
    print(f"{color}{status}{RESET} {leak_str}")
    write_result(f"{status} {leak_str}")

def run_valgrind_client(server_pid, message):
    if not VALGRIND:
        return None, None
    cmd = [VALGRIND, '--leak-check=full', CLIENT_EXEC, str(server_pid), message]
    result = subprocess.run(cmd, capture_output=True)
    out = result.stderr.decode(errors='replace')
    lost = None
    for line in out.splitlines():
        if 'definitely lost:' in line:
            lost = line.strip()
            break
    ok = (lost is not None and '0 bytes' in lost)
    return lost or 'No leak info', ok

def start_server():
    server_proc = subprocess.Popen([SERVER_EXEC], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.2)
    return server_proc

def send_message(server_pid, message, valgrind=False):
    start = time.time()
    if valgrind and VALGRIND:
        leak_str, ok = run_valgrind_client(server_pid, message)
        end = time.time()
        return None, end - start, (leak_str, ok)
    else:
        result = subprocess.run([CLIENT_EXEC, str(server_pid), message], capture_output=True)
        end = time.time()
        return result, end - start, None

def get_server_output(server_proc):
    try:
        time.sleep(0.2)
        server_proc.terminate()
        out, err = server_proc.communicate(timeout=1)
        return out.decode(errors='replace')
    except Exception as e:
        return f"[Error reading server output: {e}]"

def check_server_leaks():
    """Run the server under Valgrind, send a message, kill the server, and parse Valgrind output."""
    if not VALGRIND:
        print_fail("Valgrind not found. Cannot check server leaks.")
        return
    print_header("Server Memory Leak Check (Valgrind)")
    # Remove old log
    if os.path.exists(VALGRIND_SERVER_LOG):
        os.remove(VALGRIND_SERVER_LOG)
    # Start server under Valgrind, output to log
    server_proc = subprocess.Popen([
        VALGRIND, '--leak-check=full', '--log-file=' + VALGRIND_SERVER_LOG, SERVER_EXEC
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.5)  # Give server time to start
    # Send a message from client
    server_pid = server_proc.pid
    test_message = MSG_DELIM + "Server leak test message" + MSG_DELIM
    subprocess.run([CLIENT_EXEC, str(server_pid), test_message], capture_output=True)
    # Wait a bit, then kill server
    time.sleep(1.0)
    server_proc.terminate()
    try:
        server_proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        server_proc.kill()
    # Parse Valgrind log
    if not os.path.exists(VALGRIND_SERVER_LOG):
        print_fail("Valgrind log not found. Server may not have started correctly.")
        return
    with open(VALGRIND_SERVER_LOG, 'r') as f:
        lines = f.readlines()
    lost = None
    for line in lines:
        if 'definitely lost:' in line:
            lost = line.strip()
            break
    ok = (lost is not None and '0 bytes' in lost)
    print_leak(lost or 'No leak info', ok)

def test_normal_message():
    print_header("Test: Normal Message")
    message = "Test `~(*123!@#$%^&*(_+-=][}{';:.></|\\?)"
    server = start_server()
    server_pid = server.pid
    _, duration, client_leak = send_message(server_pid, MSG_DELIM + message + MSG_DELIM, valgrind=True)
    output = get_server_output(server)
    print_info(f"Server output: {output.strip()}")
    print_time(duration)
    if client_leak:
        print_leak(*client_leak)
    if message in output:
        print_ok("Normal message received correctly.")
    else:
        print_fail("Normal message not received correctly.")

def test_giant_message():
    print_header("Test: Giant Message (5000 chars)")
    message = ''.join(random.choices(string.printable, k=5000))
    server = start_server()
    server_pid = server.pid
    _, duration, client_leak = send_message(server_pid, MSG_DELIM + message + MSG_DELIM, valgrind=True)
    output = get_server_output(server)
    print_info(f"Server output (first 200 chars): {output[:200].strip()}...")
    print_time(duration)
    if client_leak:
        print_leak(*client_leak)
    if message in output:
        print_ok("Giant message received correctly.")
    else:
        print_fail("Giant message not received correctly.")

def test_multiple_messages():
    print_header("Test: Multiple Messages")
    messages = ["Hola", "Tudo bien?", "E como vai o tempo?", "vai andando"]
    server = start_server()
    server_pid = server.pid
    total_time = 0.0
    leaks = []
    for msg in messages:
        _, duration, client_leak = send_message(server_pid, MSG_DELIM + msg + MSG_DELIM, valgrind=True)
        total_time += duration
        if client_leak:
            leaks.append(client_leak)
        time.sleep(0.1)
    output = get_server_output(server)
    print_info(f"Server output: {output.strip()}")
    print_time(total_time)
    for leak in leaks:
        print_leak(*leak)
    all_ok = True
    for msg in messages:
        if msg not in output:
            print_fail(f"Message '{msg}' not received.")
            all_ok = False
    if all_ok:
        print_ok("All multiple messages received correctly.")

def test_empty_message():
    print_header("Test: Empty Message")
    message = ""
    server = start_server()
    server_pid = server.pid
    _, duration, client_leak = send_message(server_pid, MSG_DELIM + message + MSG_DELIM, valgrind=True)
    output = get_server_output(server)
    print_info(f"Server output: {output.strip()}")
    print_time(duration)
    if client_leak:
        print_leak(*client_leak)
    if MSG_DELIM in output:
        print_ok("Empty message handled (delimiters found). Check if your server should print nothing or a placeholder.")
    else:
        print_fail("Empty message not handled as expected.")

def test_unicode_message():
    print_header("Test: Unicode Message")
    message = "こんにちは世界 🌍🚀✨"  # "Hello, World" in Japanese + emojis
    server = start_server()
    server_pid = server.pid
    _, duration, client_leak = send_message(server_pid, MSG_DELIM + message + MSG_DELIM, valgrind=True)
    output = get_server_output(server)
    print_info(f"Server output: {output.strip()}")
    print_time(duration)
    if client_leak:
        print_leak(*client_leak)
    if message in output:
        print_ok("Unicode message received correctly.")
    else:
        print_fail("Unicode message not received correctly.")

def test_very_long_message():
    print_header("Test: Very Long Message (50000 chars)")
    message = ''.join(random.choices(string.printable, k=50000))
    server = start_server()
    server_pid = server.pid
    _, duration, client_leak = send_message(server_pid, MSG_DELIM + message + MSG_DELIM, valgrind=True)
    output = get_server_output(server)
    print_info(f"Server output (first 200 chars): {output[:200].strip()}...")
    print_time(duration)
    if client_leak:
        print_leak(*client_leak)
    if message in output:
        print_ok("Very long message received correctly.")
    else:
        print_fail("Very long message not received correctly.")

def test_special_characters():
    print_header("Test: Special Characters Message")
    message = "\n\t\r\b\f\v\a\x1b"  # newline, tab, carriage return, backspace, form feed, vertical tab, bell, escape
    server = start_server()
    server_pid = server.pid
    _, duration, client_leak = send_message(server_pid, MSG_DELIM + message + MSG_DELIM, valgrind=True)
    output = get_server_output(server)
    print_info(f"Server output (escaped): {repr(output.strip())}")
    print_time(duration)
    if client_leak:
        print_leak(*client_leak)
    if MSG_DELIM in output:
        print_ok("Special characters message sent (delimiters found). Check output for correct handling.")
    else:
        print_fail("Special characters message not handled as expected.")

def main():
    # Overwrite results file at start
    with open(RESULTS_FILE, 'w') as f:
        f.write(f"Minitalk Test Results\n{'='*30}\n")
    if not (os.path.exists(SERVER_EXEC) and os.path.exists(CLIENT_EXEC)):
        print_fail("server or client binary not found. Please compile them first.")
        return
    test_normal_message()
    test_giant_message()
    test_multiple_messages()
    test_empty_message()
    test_unicode_message()
    test_very_long_message()
    test_special_characters()
    # Uncomment the next line to run the server leak check after all tests
    # check_server_leaks()

if __name__ == "__main__":
    main() 