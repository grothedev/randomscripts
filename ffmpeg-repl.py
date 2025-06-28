#!/bin/python3

import readline # Add this at the top
# ... rest of the code
from datetime import datetime
import subprocess
import sys

cmdConcat='ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" -map "[v]" output.mp4'

#audio from first vid
cmdAudioFromFirst = 'ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v][1:v]hstack[v]" -map "[v]" -map 0:a -c:a copy output.mp4'

#resize videos to same height
cmdResizeToSameHeight = 'ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v]scale=-1:720[v0];[1:v]scale=-1:720[v1];[v0][v1]hstack[v]" -map "[v]" -map 0:a -c:a copy output.mp4'

#padding between vids
cmdPadding = 'ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v]pad=iw+10:ih[v0];[v0][1:v]hstack[v]" -map "[v]" -map 0:a output.mp4'

#shorter duration vid
cmdDurationShorter = 'ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v][1:v]hstack=shortest=1[v]" -map "[v]" -map 0:a output.mp4'

#mix audio from both
cmdAudioMix = 'ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v][1:v]hstack=shortest=1[v]" -map "[v]" -map 0:a output.mp4'

#force same dimensions
cmdForceSameDimension = 'ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v][1:v]hstack[v];[0:a][1:a]amix[a]" -map "[v]" -map "[a]" output.mp4'

#vertical stack
cmdStackVertical = 'ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v]scale=640:480[v0];[1:v]scale=640:480[v1];[v0][v1]hstack[v]" -map "[v]" -map 0:a output.mp4'
cmdStackHorizontal = 'ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex hstack output.mp4'

#3 or more vids sidebyside
cmdMultiVids = 'ffmpeg -i video1.mp4 -i video2.mp4 -i video3.mp4 -filter_complex "[0:v][1:v][2:v]hstack=inputs=3[v]" -map "[v]" -map 0:a output.mp4'



class SimpleREPL:
    def __init__(self):
        self.prompt = ">> "
        self.commands = {
            "help": self._show_help,
            "exit": self._exit_repl,
            "quit": self._exit_repl, # Alias for exit
            "echo": self._echo,
            "stack": self.stack, #vertical or horizontal
        }

    def stack(self):
        return

    def _show_help(self, *args):
        """Displays available commands."""
        print("Available commands:")
        for cmd, func in self.commands.items():
            docstring = func.__doc__ or "No description available."
            print(f"  {cmd:<15} - {docstring.strip().splitlines()[0]}") # Show first line of docstring
        return None # No printable result for help

    def _exit_repl(self, *args):
        """Exits the REPL."""
        print("Exiting REPL. Goodbye!")
        sys.exit(0)

    def _echo(self, *args):
        """Echoes the input arguments back to the user.
        Usage: echo <arg1> <arg2> ...
        """
        if not args:
            return "Echo: Nothing to echo!"
        return "Echo: " + " ".join(args)

    # --- Placeholder for your custom commands ---
    # def _handle_my_command(self, arg1, arg2=None, *other_args):
    #     """
    #     Description of my_command.
    #     Usage: my_command <required_arg> [optional_arg] ...
    #     """
    #     # Your command logic here
    #     # Example:
    #     # self.app_state['something'] = arg1
    #     # return f"Processed {arg1} and {arg2}"
    #     pass


    def evaluate(self, line):
        """Evaluates a single line of input."""
        parts = line.strip().split()
        if not parts:
            return None # Empty line

        command_name = parts[0].lower() # Case-insensitive command matching
        args = parts[1:]

        if command_name in self.commands:
            command_func = self.commands[command_name]
            try:
                return command_func(*args)
            except TypeError as e:
                # Catch errors related to incorrect number of arguments
                return f"Error: Invalid arguments for '{command_name}'. Usage: {command_func.__doc__ or ''}"
            except Exception as e:
                return f"Error executing '{command_name}': {e}"
        else: #todo check for partial str match

            return f"Unknown command: '{command_name}'. Type 'help' for available commands."

    def run(self):
        """Runs the REPL main loop."""
        print("Welcome to SimpleREPL! Type 'help' for commands or 'exit' to quit.")
        while True:
            try:
                line = input(self.prompt)
                if line.strip(): # Process only if line is not empty
                    result = self.evaluate(line)
                    if result is not None: # Print only if there's a result
                        print(result)
            except EOFError: # Ctrl+D
                print("\nExiting REPL (EOF).")
                break
            except KeyboardInterrupt: # Ctrl+C
                print("\nInterrupted. Type 'exit' or 'quit' to exit.")
                # Optionally, you might want to clear any partial input here
                # or reset some state if an operation was interrupted.
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                # Depending on severity, you might want to break or continue

if __name__ == "__main__":
    repl_app = SimpleREPL()
    repl_app.run()
#Common. functions that are frequently used by many utilities


#execute a command
'''def cmd(cmdStr):
    return subprocess.run(cmdStr.join(' '), encoding='utf-8', stdout=subprocess.PIPE).stdout
'''
'''
execute a command using the python subprocess module
params:
    cmdstr (str) : the command to run
return: stdout of command
'''
def cmd(cmdstr,v=False):
    cmdarray = cmdstr.strip().split(' ')
    log(f'runcmd: {cmdstr}')
    '''if '|' in cmdarray:   #TODO handling pipe not yet working
        i = cmdarray.index('|')
        proc0 = subprocess.check_output(cmdstr, shell=True)'''
    proc = subprocess.run(cmdarray, stdout=subprocess.PIPE)
    if proc.returncode == 0:
        res = proc.stdout
    else:
        log(f'returncode = {proc.returncode}')
        res = proc.stderr
    return res

def log(msg, filename=None):
    fn = filename
    if fn == None:
        fn = logfilenamedefault
    t = tnow()
    with open(filename, 'a') as lf:
        lf.write(f'{t}: {msg}\n')
        lf.close()

def tnow():
    '''
    return: current time, formatted as %Y%m%d-%H%M%S
    '''
    return datetime.now().strftime('%Y%m%d-%H%M%S')
