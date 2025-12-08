import os
import subprocess #provide a way to handle and process like child process
import shlex  #for splittign the command into token. Lexical analysis

def handle_builtin(cmd):
    parts = cmd.split()
    
    if len(parts) == 0:
        return True
    
    command  = parts[0]
    
    if command == 'cd':
        if len(parts) == 1:
            path = os.path.expanduser("~")
        else:
            path = parts[1]
            
        try:
            os.chdir(path)
        except FileNotFoundError:
            print(f"No such file or directory: {path}")
        except NotADirectoryError:
            print(f"Not a directory: {path}")
        except PermissionError:
            print(f"Permission denied: {path}")
            
    if command == "clear":
        os.system("cls" if os.name == "nt" else 'clear')
        return True
    
    if command == "help":
        print ("""
Supported built-in commands:
  cd <path>      Change directory
  clear.         Clear the screen
  help.          Show this help message
  exit.          Quit the Beat 
  
  System commands (ls, pwsd, echo, mkdir...) also work normally.   
""")
        return True
    
    return False
           

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
            
            if handle_builtin(line):
                continue
            
            run_command(line)

            print(f"you typed: {line}")

        except KeyboardInterrupt:
            print("\nuse 'exit' to quit.")
        except EOFError:
            print("\nBye")
            break


if __name__ == "__main__":
    main()
