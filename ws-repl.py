import asyncio
import sys
import websockets # For WebSocket client functionality
import json # For potentially sending/receiving JSON

class WebsocketREPL:
    def __init__(self):
        self.prompt_prefix = "ws-repl"
        self.ws_client = None
        self.listener_task = None
        self.is_connected = False
        self.current_url = None

        self.commands = {
            "help": self._show_help,
            "exit": self._exit_repl,
            "quit": self._exit_repl,
            "connect": self._connect_to_server,
            "disconnect": self._disconnect_from_server,
            "send": self._send_message,
            "status": self._show_status,
            # Add more commands like 'sendjson', 'ping', etc.
        }

    def _get_prompt(self):
        """Generates the current prompt string."""
        status_indicator = f" ({self.current_url})" if self.is_connected else " (disconnected)"
        return f"{self.prompt_prefix}{status_indicator} >> "

    async def _show_help(self, *args):
        """Displays available commands."""
        print("Available commands:")
        for cmd, func in self.commands.items():
            docstring = func.__doc__ or "No description available."
            # Show first line of docstring
            print(f"  {cmd:<15} - {docstring.strip().splitlines()[0]}")
        return None

    async def _exit_repl(self, *args):
        """Exits the REPL, disconnecting if necessary."""
        print("Exiting REPL...")
        if self.is_connected and self.ws_client:
            await self._disconnect_from_server()
        # To stop the asyncio event loop properly from within an async function,
        # we can cancel the main task or use a more structured shutdown.
        # For simplicity here, we'll rely on the run loop ending.
        # Alternatively, raise a custom exception that the main loop catches to exit.
        # For now, we'll just print and let the loop terminate naturally if it can,
        # or the user can Ctrl+C if this method is called from a command.
        # A more robust way is to have run() check a flag set by _exit_repl.
        print("Goodbye!")
        # Get the current running loop and stop it.
        # This is a bit forceful but works for a simple REPL.
        loop = asyncio.get_running_loop()
        loop.stop() # This will stop the loop after the current iteration
        return "Exiting..." # This return might not be seen if loop stops immediately

    async def _listen_for_messages(self):
        """Continuously listens for messages from the WebSocket server."""
        if not self.ws_client:
            return
        try:
            print(f"\n[Listener] Started for {self.current_url}")
            async for message in self.ws_client:
                # The `\r` and `end=''` try to clear the current input line
                # and reprint the prompt after the message. This is tricky
                # with standard input() and works best with libraries like prompt_toolkit.
                sys.stdout.write('\r' + ' ' * (len(self._get_prompt()) + 20) + '\r') # Clear line
                print(f"<-- RECV: {message}")
                sys.stdout.write(self._get_prompt()) # Reprint prompt
                sys.stdout.flush()
        except websockets.exceptions.ConnectionClosedOK:
            sys.stdout.write('\r' + ' ' * (len(self._get_prompt()) + 20) + '\r')
            print(f"<-- INFO: Connection to {self.current_url} closed gracefully.")
            self.is_connected = False # Ensure state is updated
            self.current_url = None
        except websockets.exceptions.ConnectionClosedError as e:
            sys.stdout.write('\r' + ' ' * (len(self._get_prompt()) + 20) + '\r')
            print(f"<-- ERROR: Connection to {self.current_url} closed with error: {e}")
            self.is_connected = False
            self.current_url = None
        except Exception as e:
            sys.stdout.write('\r' + ' ' * (len(self._get_prompt()) + 20) + '\r')
            print(f"<-- ERROR: Listener error: {e}")
            self.is_connected = False # Assume connection is lost
        finally:
            self.is_connected = False # Double ensure
            if self.ws_client and not self.ws_client.closed:
                 # This might happen if listener exits due to non-connection error
                await self.ws_client.close()
            self.ws_client = None
            self.listener_task = None # Clear the task reference
            sys.stdout.write(self._get_prompt()) # Reprint prompt
            sys.stdout.flush()
            print("[Listener] Stopped.")


    async def _connect_to_server(self, url=None, *args):
        """Connects to a WebSocket server.
        Usage: connect <ws_url> (e.g., connect ws://localhost:8000/ws)
        """
        if not url:
            return "Error: No URL provided. Usage: connect <ws_url>"
        if self.is_connected:
            return f"Error: Already connected to {self.current_url}. Disconnect first."

        try:
            print(f"Attempting to connect to {url}...")
            # You can add timeout to connect:
            # self.ws_client = await asyncio.wait_for(websockets.connect(url), timeout=10.0)
            self.ws_client = await websockets.connect(url)
            self.is_connected = True
            self.current_url = url
            # Start the listener task
            self.listener_task = asyncio.create_task(self._listen_for_messages())
            return f"Successfully connected to {url}."
        except asyncio.TimeoutError:
            self.is_connected = False
            self.ws_client = None
            return f"Error: Connection to {url} timed out."
        except websockets.exceptions.InvalidURI:
            return f"Error: Invalid WebSocket URI: {url}"
        except ConnectionRefusedError:
            return f"Error: Connection refused by server at {url}."
        except Exception as e:
            self.is_connected = False
            self.ws_client = None
            return f"Error connecting to {url}: {e}"

    async def _disconnect_from_server(self, *args):
        """Disconnects from the current WebSocket server."""
        if not self.is_connected or not self.ws_client:
            return "Not currently connected."

        print(f"Disconnecting from {self.current_url}...")
        try:
            # Signal the listener to stop
            if self.listener_task and not self.listener_task.done():
                self.listener_task.cancel()
                try:
                    await self.listener_task # Wait for listener to finish cleanup
                except asyncio.CancelledError:
                    print("[Listener] Cancelled by disconnect command.")
                except Exception as e: # Catch other exceptions if listener fails during cancel
                    print(f"[Listener] Error during cancellation: {e}")


            if self.ws_client and not self.ws_client.closed:
                await self.ws_client.close()
            
            self.is_connected = False
            # Listener's finally block should also set ws_client to None
            # but we do it here as well to be sure.
            self.ws_client = None
            self.listener_task = None # Ensure task reference is cleared
            url_disconnected = self.current_url
            self.current_url = None
            return f"Disconnected from {url_disconnected}."
        except Exception as e:
            # Force state update even on error
            self.is_connected = False
            self.ws_client = None
            self.listener_task = None
            old_url = self.current_url
            self.current_url = None
            return f"Error during disconnection from {old_url}: {e}"


    async def _send_message(self, *message_parts):
        """Sends a message to the connected WebSocket server.
        Usage: send <message content>
        """
        if not self.is_connected or not self.ws_client:
            return "Error: Not connected to any server. Use 'connect <url>' first."
        if not message_parts:
            return "Error: No message content provided. Usage: send <message>"

        message = " ".join(message_parts)
        try:
            await self.ws_client.send(message)
            return f"--> SENT: {message}"
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False # Connection might have dropped
            self.current_url = None
            if self.listener_task and not self.listener_task.done():
                self.listener_task.cancel() # Attempt to clean up listener
            return "Error: Connection closed. Message not sent. Please reconnect."
        except Exception as e:
            return f"Error sending message: {e}"

    async def _show_status(self, *args):
        """Shows the current connection status."""
        if self.is_connected and self.current_url:
            return f"Status: Connected to {self.current_url}"
        else:
            return "Status: Not connected."

    async def evaluate_line(self, line):
        """Evaluates a single line of input."""
        parts = line.strip().split()
        if not parts:
            return None

        command_name = parts[0].lower()
        args = parts[1:]

        if command_name in self.commands:
            command_func = self.commands[command_name]
            try:
                # All command handlers are now async
                return await command_func(*args)
            except TypeError as e:
                # Check if it's an argument count error
                import inspect
                sig = inspect.signature(command_func)
                num_required_params = len([
                    p for p in sig.parameters.values()
                    if p.default == inspect.Parameter.empty and p.kind != inspect.Parameter.VAR_POSITIONAL
                ])
                # This logic is a bit simplified for TypeError; proper arg parsing is better
                if "required positional argument" in str(e) or "missing" in str(e) or "takes" in str(e) :
                     return f"Error: Invalid arguments for '{command_name}'. Usage: {getattr(command_func, '__doc__', '').strip().splitlines()[1] if getattr(command_func, '__doc__', '') else 'No usage info.'}"
                else:
                    return f"Error executing '{command_name}': {e}" # Other TypeErrors
            except Exception as e:
                return f"Error executing '{command_name}': {e}"
        else:
            # Default behavior: if connected, try to send the whole line as a message
            if self.is_connected:
                print(f"(Interpreting '{line}' as a message to send)")
                return await self._send_message(*parts) # Send the whole line
            else:
                return f"Unknown command: '{command_name}'. Type 'help' for available commands."

    async def run(self):
        """Runs the REPL main loop."""
        print("Welcome to WebsocketREPL! Type 'help' for commands.")
        loop = asyncio.get_running_loop()

        try:
            while not loop.is_closed(): # Check if loop is still running
                try:
                    # Use asyncio.to_thread to run blocking input() in a separate thread
                    # This allows the asyncio event loop (and our WebSocket listener) to keep running.
                    line = await asyncio.to_thread(input, self._get_prompt())

                    if line.strip():
                        result = await self.evaluate_line(line)
                        if result is not None:
                            print(result)
                    if loop.is_closed(): # Check again, _exit_repl might have stopped it
                        break
                except KeyboardInterrupt: # Ctrl+C
                    # Gracefully stop the listener if it's running
                    if self.listener_task and not self.listener_task.done():
                        print("\nCtrl+C detected. Stopping listener if active...")
                        self.listener_task.cancel()
                        try:
                            await self.listener_task
                        except asyncio.CancelledError:
                            print("[Listener] Cancelled due to Ctrl+C.")
                        except Exception as e:
                            print(f"[Listener] Error during cancellation: {e}")
                    print("\nInterrupted. Type 'exit' or 'quit' to exit the REPL.")
                    # Optionally, clear partial input or reset state
                except EOFError: # Ctrl+D
                    print("\nExiting REPL (EOF).")
                    await self._exit_repl() # Ensure cleanup and loop stop
                    break # Exit while loop
                except Exception as e: # Catch-all for unexpected errors in the loop
                    print(f"An unexpected REPL error occurred: {e}")
                    # Depending on severity, you might want to break or attempt to continue
        finally:
            print("REPL session ended.")
            # Final cleanup, ensuring the WebSocket is closed if it was somehow left open
            if self.ws_client and not self.ws_client.closed:
                print("Performing final cleanup: closing WebSocket connection...")
                await self.ws_client.close()
            if self.listener_task and not self.listener_task.done():
                self.listener_task.cancel() # Cancel if still running
                try:
                    await self.listener_task
                except asyncio.CancelledError:
                    pass # Expected
            print("All tasks should be cleaned up.")


async def main():
    repl_app = WebsocketREPL()
    await repl_app.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nREPL terminated by user (Ctrl+C at global scope).")
    finally:
        print("Application shut down.")
