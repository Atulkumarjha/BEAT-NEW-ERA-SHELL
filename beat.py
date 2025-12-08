import subprocess #provide a way to handle and process like child process
import shlex  #for splittign the command into token. Lexical analysis


def run_command(cmd):
    try:
        parts = shlex.split(cmd)
        
        if not parts:
            return 
        
        result = subprocess.run(parts, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout, end="")
            
        if result.stderr:
            print(result.stderr, end="")
                
    except FileNotFoundError:
        print(f"Command not found: {cmd}")
    except Exception as e:
        print(f"Error: {e}")
        
        
def main():
    while True:
        try:
            line = input("beat>>> ").strip()

            if not line:
                continue

            if line.lower() == "exit":
                print("Good Bye!")
                break

            print(f"you typed: {line}")

        except KeyboardInterrupt:
            print("\nuse 'exit' to quit.")
        except EOFError:
            print("\nBye")
            break


if __name__ == "__main__":
    main()
