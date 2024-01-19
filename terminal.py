import subprocess
import os
import platform

def clear_screen():
    if platform.system() == "Windows":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)

while True:
    user_input = input("Your Command: ")
    if user_input == "exit":
        break
    elif user_input == "clear":
        clear_screen()
    elif user_input.startswith("cd "):  # Check if the command starts with "cd ".
        directory = user_input[3:]  # Extract the directory part.
        try:
            os.chdir(directory)  # Change the current directory.
            print(f"Changed directory to: {directory}")
        except FileNotFoundError:
            print(f"Directory '{directory}' not found.")
    elif user_input == "pwd":
        if platform.system() == "Windows":
            result = subprocess.run("cd", shell=True, stdout=subprocess.PIPE, text=True)
        else:
            result = subprocess.run("pwd", shell=True, stdout=subprocess.PIPE, text=True)
        print("Current Directory:")
        print(result.stdout)
    else:
        try:
            result = subprocess.run(
                user_input, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            print("Output:")
            print(result.stdout)
            print("Errors:")
            print(result.stderr)
        except Exception as e:
            print(f"An error occurred: {e}")
