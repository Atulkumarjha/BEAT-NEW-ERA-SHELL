import readline
import os
import subprocess  # provide a way to handle and process like child process
import shlex  # for splittign the command into token. Lexical analysis


def handle_builtin(cmd):
    parts = cmd.split()

    if len(parts) == 0:
        return True

    command = parts[0]

    if command == "cd":
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
        return True

    if command == "clear":
        os.system("cls" if os.name == "nt" else "clear")
        return True

    if command == "help":
        print(
            """
Supported built-in commands:
  cd <path>      Change directory
  clear.         Clear the screen
  help.          Show this help message
  exit.          Quit the Beat 
  
  System commands (ls, pwsd, echo, mkdir...) also work normally.   
"""
        )
        return True

    return False

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


def setup_history():
    histfile = os.path.expanduser("~/.mysh_history")

    try:
        readline.read_history_file(histfile)
    except (FileNotFoundError, PermissionError):
        pass

    import atexit

    atexit.register(readline.write_history_file, histfile)


def completer(text, state):
    options = [f for f in os.listdir(",") if f.startswith(text)]

    if state < len(options):
        return options[state]
    return None


def setup_autocomplete():
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    
def expand_variables(cmd):
    return os.path.expandvars(cmd)

def get_prompt():
    cwd = os.getcwd()
    return f"beat:{cwd}> "

def main():
    setup_history()
    setup_autocomplete()

    while True:
        try:
            line = input(get_prompt()).strip()
            line = expand_variables(line)
            
            if not line:
                continue

            if line.lower() == "exit":
                print("Good Bye!")
                break
            
            if handle_builtin(line):
                continue
            
            run_command(line)

            if handle_builtin(line):
                continue

            run_command(line)

            

        except KeyboardInterrupt:
            print("\nuse 'exit' to quit.")
        except EOFError:
            print("\nBye")
            break


if __name__ == "__main__":
    main()
