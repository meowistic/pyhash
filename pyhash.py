import hashlib
import os
from colorama import Fore, Style
from itertools import cycle
import concurrent.futures

def calculate_hashes(file_path, chunk_size=104857600):  
    available_algorithms = hashlib.algorithms_guaranteed
    hashes = {algo: hashlib.new(algo) for algo in available_algorithms}

    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as file:
            bytes_read = 0
            while chunk := file.read(chunk_size):
                for hash_obj in hashes.values():
                    hash_obj.update(chunk)
                bytes_read += len(chunk)
                progress = (bytes_read / file_size) * 100
                print(f"reading file {progress:.2f}%", end='\r')
        print()  

        def compute_hash(algo, obj):
            try:
                if algo.startswith("shake"):
                    return (algo, obj.hexdigest(64))  
                else:
                    return (algo, obj.hexdigest())
            except Exception as e:
                return (algo, f"Error: {str(e)}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = dict(executor.map(lambda p: compute_hash(*p), hashes.items()))

        return results
    except FileNotFoundError:
        return {"Error": Fore.RED+f"file '{file_path}' not found."}
    except PermissionError:
        return {"Error": Fore.RED+f"permission denied - '{file_path}'."}
    except Exception as e:
        return {"Error": f"An unexpected error occurred - {str(e)}"}

def format_hashes_ascii(hash_results):
    hash_types = {
        "SHA": [algo for algo in hash_results if algo.startswith("sha") and algo != "sha3" and not algo.startswith("shake")],
        "SHA3": [algo for algo in hash_results if algo.startswith("sha3")],
        "SHAKE": [algo for algo in hash_results if algo.startswith("shake")],
        "MD5": [algo for algo in hash_results if algo == "md5"],
        "BLAKE2": [algo for algo in hash_results if algo.startswith("blake2")],
        "Other": [algo for algo in hash_results if not any(algo.startswith(prefix) for prefix in ["sha", "sha3", "shake", "md5", "blake2"])]
    }

    color_map = {
        "SHA": Fore.BLUE,
        "SHA3": Fore.MAGENTA,
        "SHAKE": Fore.CYAN,
        "MD5": Fore.GREEN,
        "BLAKE2": Fore.YELLOW,
        "Other": Fore.WHITE
    }

    for hash_type, algorithms in hash_types.items():
        if algorithms:
            print(Fore.RESET + f"\n===== {hash_type} =====")
            for algo in algorithms:
                print(f"{color_map[hash_type]}[{algo}] {hash_results[algo]}{Style.RESET_ALL}")


if __name__ == "__main__":
    print(Fore.LIGHTMAGENTA_EX+"""$ by kvts
$ ██████  ██    ██ ██   ██  █████  ███████ ██   ██ 
$ ██   ██  ██  ██  ██   ██ ██   ██ ██      ██   ██ 
$ ██████    ████   ███████ ███████ ███████ ███████ 
$ ██         ██    ██   ██ ██   ██      ██ ██   ██ 
$ ██         ██    ██   ██ ██   ██ ███████ ██   ██ 
$ cross-platform file integrity checker                                           
""")
    file_path = input("enter file path: ").strip()

    print(Fore.LIGHTBLACK_EX+"calculating hashes...")
    hash_results = calculate_hashes(file_path)

    if "Error" in hash_results:
        print(hash_results["Error"])
    else:
        format_hashes_ascii(hash_results)
        print()
        user_hash = input("compare hash: ").strip()
        match_found = False

        for algo, value in hash_results.items():
            if user_hash == value:
                print(Fore.GREEN+f"match found: {algo}.")
                match_found = True
                break

        if not match_found:
            print(Fore.RED+"no match found.")
