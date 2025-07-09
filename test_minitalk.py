import subprocess
import random
import string
import time

def generate_random_string(length):
	characters = string.ascii_letters + string.digits
	return ''.join(random.choice(characters) for _ in range(length))

def execute_client_and_wait(pid_server, input_str):
	subprocess.run(['./client', str(pid_server), input_str], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	time.sleep(0.1)  # Give the server a bit of time

def check_input_in_file(input_str, log_file):
	with open(log_file, 'r', encoding='utf-8') as f:
		return input_str in f.read()

def start_server():
	log_file = 'server_output.log'
	return subprocess.Popen(['./server'], stdout=open(log_file, 'w', encoding='utf-8'), stderr=subprocess.DEVNULL).pid

def kill_server(pid):
	try:
		subprocess.Popen(['kill', '-9', str(pid)])
	except Exception as e:
		print(f"Error: {e}")

def test_with_lengths(pid_server, log_file, num_runs=1):
	input_lengths = [1, 10, 100, 1000, 10000, 50000, 100000]
	for length in input_lengths:
		print(f"Testing ASCII+digits with length {length}")
		print(f"-------------------")
		for _ in range(10):
			input_str = generate_random_string(length)
			execute_client_and_wait(pid_server, input_str)
			if check_input_in_file(input_str, log_file):
				print(f"\033[1;32m[OK] \033[0m", end='', flush=True)
			else:
				print(f"\033[0;31m[KO] \033[0m", end='', flush=True)
		print(f"\n-------------------")

def test_with_unicode(pid_server, log_file, num_runs=1):
	unicode_tests = [
		"Hello 😊",
		"¡Hola, señorita!",
		"你好，世界",
		"Привет мир",
		"こんにちは世界",
		"안녕하세요 세계",
		"🌍🚀✨🔥💻📱",
		"éèêëēėę",
		"𝔘𝔫𝔦𝔠𝔬𝔡𝔢 𝔱𝔢𝔰𝔱"
	]

	print(f"\nTesting Unicode inputs")
	print(f"======================")
	for test_str in unicode_tests:
		for _ in range(1):
			print(f"Testing: {repr(test_str)}")
			execute_client_and_wait(pid_server, test_str)
			if check_input_in_file(test_str, log_file):
				print(f"\033[1;32m[OK] \033[0m", end='', flush=True)
			else:
				print(f"\033[0;31m[KO] \033[0m", end='', flush=True)
			print()
	print(f"======================\n")

def main():
	pid_server = start_server()
	log_file = 'server_output.log'
	time.sleep(1)  # Let server warm up

	test_with_lengths(pid_server, log_file, num_runs=1)
	test_with_unicode(pid_server, log_file, num_runs=1)

	kill_server(pid_server)

if __name__ == "__main__":
	main()


# valgrind --leak-check=full --show-leak-kinds=all ./server
# valgrind --leak-check=full --show-leak-kinds=all ./client

# ps aux | grep server
# pkill -f "./server"
# ./server > server.log