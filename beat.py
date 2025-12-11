import signal
import readline
import os
import sys
import subprocess  # provide a way to handle and process like child process
import shlex  # for splittign the command into token. Lexical analysis

RESET = "\033[0m"
BOLD = "\033[1m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m" 
CYAN = "\033[36m"
WHITE = "\033[37m"


jobs = {}
job_counter = 1

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
    
    if command == "jobs":
        for jid, job in jobs.items():
            print(f"[{jid}] {job["status"]}    {job['command']} (PID {job['pid']})")
        return True
    
    if command == "kill":
        if len(parts) < 2:
            print("Usage: kill <job_id>")
            return True
        
        jid = int(parts[1])
        if jid not in jobs:
            print(f"No such Job: {jid}")
            return True
        
        
        try:
            os.kill(jobs[jid]["pid"],signal.SIGTERM)
            jobs[jid]["status"] = "Terminated"
            print(f"Killed job {jid}")
        except Exception as e:
            print(f"Process already ended.")
            
        return True
    
    if command == "bg":
        if len(parts) < 2:
            print("Usage: bg <job_id>")
            return False
        
        jid = int(parts[1])
        if jid not in jobs:
            print(f"No such job: {jid}")
            return True
        
        
        job = jobs[jid]
        os.kill(job["pid"], signal.SIGCONT)
        job["status"] = "Running"
        
        print(f"[{jid}] {job["pid"]} resumed in background")
        return True
    
    if command == "fg":
        if len(parts) < 2:
            print("Usage: fg <job_id>")
            return True
        
        jid = int(parts[1])
        if jid not in jobs:
            print(f"No such job: {jid}")
            return True
        
        job = jobs[jid]
        os.kill(job["pid"], signal.SIGCONT)
        job["status"] = "Running"
        
        print(f"[{jid}] {job['command']}")
        job["process"].wait()
        
        del jobs[jid]
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
    
    if command == "which":
        if len(parts) < 2:
            print("Usage: which <command>")
            return True
        
        resolved = resolve_command(parts[1])
        if resolved:
            print(resolved)
        else:
            print(f"{parts[1]} not found")
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
    home = os.path.expanduser("~")
    
    
    if cwd.startswith(home):
        cwd_display = "~" + cwd[len(home):]
    else:
        cwd_display = cwd
        
        user = os.getenv("USER")

    return (
        f"{MAGENTA}{user}{RESET}"
        f"{GREEN}beat{RESET}"
        f"{CYAN}{cwd_display}{RESET} $ "
    )

def run_pipeline(commands):
    processes = []
    prev_pipe = None
    
    for cmd in commands:
        parts = shlex.split(cmd)
        
        if prev_pipe is None:
            proc = subprocess.Popen(parts, stdout=subprocess.PIPE, text=True)
        else:
            proc = subprocess.Popen(
                parts,
                stdin=prev_pipe,
                stdout=subprocess.PIPE,
                text=True
            )
        prev_pipe = proc.stdout
        processes.append(proc)
        
    output, _ = processes[-1].communicate()
    if output:
        print(output, end="")
        
        
def handle_output_redirection(cmd):
    if ">>" in cmd:
        parts = cmd.split(">>")
        filename = parts[1].strip()
        command = shlex.split(parts[0].strip())
        
        with open(filename, "a") as f:
            result = subprocess.run(command, stdout=f, stderr=subprocess.PIPE, text=True)
        return True
    
    elif ">" in cmd:
        parts = cmd.split(">")
        filename = parts[1].strip()
        command = shlex.split(parts[0].strip())
        
        with open(filename, "w") as f:
            result = subprocess.run(command, srdout=f, stderr=subprocess.PIPE, text=True)
        return True
    
    return False

def handle_input_redirection(cmd):
    if "<" in cmd:
        return False
    
    parts = cmd.split("<")
    filename = parts[1].strip()
    command = shlex.split(parts[0].strip())
    
    try:
        with open(filename, "r") as f:
            result = subprocess.run(command, stdin=f, text=True)
    except FileNotFoundError:
        print(f"No such file: {filename}")
        
    return True


background_jobs = []

def run_single_command(cmd):
    cmd = cmd.strip()
    
    if handle_builtin(cmd):
        return 0
    
    if "|" in cmd:
        commands = [c.strip() for c in cmd.split("|")]
        run_pipeline(commands)
        return 0
    
    if handle_input_redirection(cmd) or handle_output_redirection(cmd):
        return 0
    
    if cmd.endswith("&"):
        run_in_background(cmd[:-1].strip())
        return 0
    
    parts = shlex.split(cmd)
    command_name = parts[0]
    
    program = resolve_command(command_name)
    if not program:
        print(f"beat: command not found: {command_name}")
        return 1
    
    parts[0] = program
    
    result = subprocess.run(parts)
    return result.returncode
        
    
    
def handle_chaining(line):
    if ";" in line:
        commands = [c.strip() for c in line.split(";")]
        for cmd in commands:
            run_single_command(cmd)
            
    if "&&" in line:
        parts = [c.strip() for c in line.split("&&")]
        
        for i, cmd in enumerate(parts):
            status = run_single_command(cmd)
            if status != 0:
                
                break
        return True
    
    if "||" in line:
        parts = [c.strip() for c in line.split("||")]
        
        for cmd in parts:
            status = run_single_command(cmd)
            if status == 0:
                break
        return True
    
    return False

def run_in_background(cmd):
    global job_counter
    
    parts = shlex.split(cmd)
    proc = subprocess.Popen(parts)
    
    jobs[job_counter] = {
        "pid": proc.pid,
        "process": proc,
        "command": cmd,
        "status": "Running"
    }
    
    print(f"[{job_counter}] {proc.pid}")
    job_counter += 1
    
    
def setup_readline():
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind('"\\C-r": reverse-search-history')
    
    
class ReverseSearch:
    def __init__(self):
        self.search_term = ""
        self.history_index = readline.get_current_history_length()
        
    def activate(self):
        print("\n(reverse-i-search)`':", end="", flush=True)
        self.search_term = ""
        self.history_index = readline.get_current_history_length() - 1
        
        while True:
            ch = sys.stdin.read(1)
            
            if ch == "\n":
                print()
                return readline.get_history_item(self.history_index + 1)
            
            if ch == "\x7f":
                if self.search_term:
                    self.search_term = self.search_term[:1]
                    
            elif ch == "\x1b":
                print()
                return ""
            
            else:
                self.search_term += ch
                
            self.history_index = self.find_match(self.search_term)
            
            
            match = readline.get_history_item(self.history_index + 1)
            print(f"\r(reverse-i-search)`{self.search_term}`: {match}", end="", flush=True)
            
    def find_match(self, term):
        for i in range(readline.get_current_history_length() -1, -1, -1):
            item = readline.get_history_item(i + 1)
            if term in item:
                return i 
        return -1
    
    
def trigger_reverse_search():
    search = ReverseSearch()
    result = search.activate()
    if result:
        readline.insert_text(result)
        readline.redisplay()
        
def setup_history_search():
    readline.parse_and_bind('"\\C-r": "reverse-search"')
    readline.set_pre_input_hook(trigger_reverse_search)
    
    
def resolve_command(cmd):
    if "/" in cmd:
        return cmd if os.path.isfile(cmd) and os.access(cmd, os.X_OK) else None
    
    path_dirs = os.getenv("PATH", "").split(":")
    
    for directory in path_dirs:
        full_path = os.path.join(directory, cmd)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
        
    return None
    
def main():
    setup_history()
    setup_autocomplete()
    setup_history_search()
    
    finished = []
    for jid, job in jobs.items():
        if job["process"].poll() is not None:
            job["status"] = "Done"
            finished.append(jid)
            
    for jid in finished:
        del jobs[jid]

    while True:
        try:
            line = input(get_prompt()).strip()
            line = expand_variables(line)
            
            if not line:
                continue

            if line.lower() == "exit":
                print("Good Bye!")
                break
            
            if handle_input_redirection(line):
                continue
            
            if handle_output_redirection(line):
                continue
            
            if "|" in line:
                commands = line.split("|")
                run_pipeline([cmd.strip() for cmd in commands])
                continue
            
            if handle_chaining(line):
                continue
            
            if handle_builtin(line):
                continue
            
            run_command(line)
            
            if line.endswith("&"):
                cmd = line[:-1].strip()
                run_in_background(cmd)
                continue
            

        except KeyboardInterrupt:
            print("\nuse 'exit' to quit.")
        except EOFError:
            print("\nBye")
            break


if __name__ == "__main__":
    main()
