import subprocess
import os
import platform
import re
import tarfile
import tkinter as tk
from tkinter import scrolledtext
import zipfile

def evaluate_expression(expression):

    tokens = re.findall(r"[+*/()-]|\d+", expression)

    tokens = [float(token) if token.isnumeric() or (token[0] == '-' and token[1:].isnumeric()) else token for token in tokens]

    result = evaluate_bodmas(tokens)
    return result

def evaluate_bodmas(tokens):

    while "(" in tokens:
        start = tokens.index("(")
        end = start + tokens[start:].index(")")
        tokens[start:end+1] = [evaluate_bodmas(tokens[start+1:end])]
    
    while "^" in tokens:
        index = tokens.index("^")
        base = tokens[index-1]
        exponent = tokens[index+1]
        result = base ** exponent
        tokens[index-1:index+2] = [result]

    while "sqrt" in tokens:
        index = tokens.index("sqrt")
        value = tokens[index+1]
        result = value ** 0.5
        tokens[index:index+2] = [result]

    while "*" in tokens or "/" in tokens:
        for i, token in enumerate(tokens):
            if token == "*":
                result = float(tokens[i-1]) * float(tokens[i+1])
                tokens[i-1:i+2] = [result]
                break
            elif token == "/":
                divisor = float(tokens[i+1])
                if divisor == 0:
                    raise ValueError("Cannot divide by zero")
                result = float(tokens[i-1]) / divisor
                tokens[i-1:i+2] = [result]
                break

    while "+" in tokens or "-" in tokens:
        for i, token in enumerate(tokens):
            if token == "+":
                result = float(tokens[i-1]) + float(tokens[i+1])
                tokens[i-1:i+2] = [result]
                break
            elif token == "-":
                result = float(tokens[i-1]) - float(tokens[i+1])
                tokens[i-1:i+2] = [result]
                break

    return tokens[0]


def clear_screen():
    if platform.system() == "Windows":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)

command_history = []
current_history_index = 0

def execute_command():
    global current_history_index
    user_input = entry.get()

    if user_input == "exit":
        command_history.append(user_input)
        root.destroy()

    elif user_input == "clear":
        command_history.append(user_input)
        text.delete("1.0", tk.END)

    elif user_input.startswith("cd "):
        command_history.append(user_input)
        directory = user_input[3:]
        try:
            os.chdir(directory)
            text.insert(tk.END, f"Changed directory to: {directory}\n")
        except FileNotFoundError:
            text.insert(tk.END, f"Directory '{directory}' not found.\n")

    elif user_input == "pwd":
        command_history.append(user_input)
        if platform.system() == "Windows":
            result = subprocess.run("cd", shell=True, stdout=subprocess.PIPE, text=True)
        else:
            result = subprocess.run("pwd", shell=True, stdout=subprocess.PIPE, text=True)
        text.insert(tk.END, f"Current Directory:\n{result.stdout}\n")

    elif user_input.startswith("mkdir "):
        command_history.append(user_input)
        directory = user_input[6:]
        try:
            os.mkdir(directory)
            text.insert(tk.END, f"Created directory: {directory}\n")
        except FileExistsError:
            text.insert(tk.END, f"Directory '{directory}' already exists.\n")

    elif user_input.startswith("touch "):
        command_history.append(user_input)
        file_name = user_input[6:]
        try:
            with open(file_name, "w"):
                pass  # Create an empty file
            text.insert(tk.END, f"Created file: {file_name}\n")
        except FileExistsError:
            text.insert(tk.END, f"File '{file_name}' already exists.\n")

    elif user_input.startswith("rm "):
        command_history.append(user_input)
        target = user_input[3:]
        if os.path.exists(target):
            if os.path.isdir(target):
                os.rmdir(target)
                text.insert(tk.END, f"Removed directory: {target}\n")
            else:
                os.remove(target)
                text.insert(tk.END, f"Removed file: {target}\n")
        else:
            text.insert(tk.END, f"File or directory '{target}' not found.\n")

    elif user_input.startswith("start "):
        command_history.append(user_input)
        file_path = user_input[6:]
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            else:
                subprocess.Popen(["xdg-open", file_path])
            text.insert(tk.END, f"Opened: {file_path}\n")
        except FileNotFoundError:
            text.insert(tk.END, f"File not found: {file_path}\n")

    elif user_input.startswith("cat "):
        command_history.append(user_input)
        file_names = user_input[4:].split()
        target1 = file_names[0]
        concatenated_contents = ""
        for file_name in file_names:
            try:
                with open(file_name, "r") as file:
                    file_contents = file.read()
                    concatenated_contents += f"\n{file_contents}\n"
            except FileNotFoundError:
                text.insert(tk.END, f"File not found: {file_name}\n")

        os.remove(target1)
        with open(file_names[0], "w") as file:
            file.write(concatenated_contents)
        text.insert(tk.END, concatenated_contents)

    elif user_input.startswith("find "):
        command_history.append(user_input)
        pattern = user_input[5:]
        try:
            matches = find_files(pattern, os.getcwd())
            if matches:
                text.insert(tk.END, f"Files and directories matching '{pattern}':\n")
                for match in matches:
                    text.insert(tk.END, f"{match}\n")
            else:
                text.insert(tk.END, f"No files or directories matching '{pattern}' found.\n")
        except Exception as e:
            text.insert(tk.END, f"An error occurred: {str(e)}\n")

    elif user_input.startswith("chmod "):
        # Parse the chmod command to get the file and permission values
        command_parts = user_input.split()
        if len(command_parts) != 3:
            text.insert(tk.END, "Invalid chmod command. Usage: chmod <permissions> <file>\n")
        else:
            permissions = command_parts[1]
            file_path = command_parts[2]
            try:
                command_history.append(user_input)
                os.chmod(file_path, int(permissions, 8))
                text.insert(tk.END, f"Changed permissions of '{file_path}' to {permissions}\n")
            except FileNotFoundError:
                text.insert(tk.END, f"File '{file_path}' not found.\n")
            except ValueError:
                text.insert(tk.END, "Invalid permissions. Permissions must be in octal format.\n")

    elif user_input.startswith("whoami"):
        command_history.append(user_input)
        try:
            username = os.getlogin()
            text.insert(tk.END, f"Current user: {username}\n")
        except Exception as e:
            text.insert(tk.END, f"An error occurred: {str(e)}\n")

    elif user_input.startswith("tar "):
        command_history.append(user_input)
        tar_command = user_input.split()[1:]
        try:
            with tarfile.open(tar_command[0], "w") as tar:
                for file_name in tar_command[1:]:
                    tar.add(file_name)
            text.insert(tk.END, f"Created tar archive: {tar_command[0]}\n")
        except Exception as e:
            text.insert(tk.END, f"An error occurred: {str(e)}\n")

    elif user_input.startswith("zip "):
        command_history.append(user_input)
        zip_command = user_input.split()[1:]
        try:
            with zipfile.ZipFile(zip_command[0], "w") as zipf:
                for file_name in zip_command[1:]:
                    zipf.write(file_name)
            text.insert(tk.END, f"Created zip archive: {zip_command[0]}\n")
        except Exception as e:
            text.insert(tk.END, f"An error occurred: {str(e)}\n")

    elif user_input.startswith("unzip "):
        command_history.append(user_input)
        unzip_command = user_input.split()[1:]
        try:
            zip_file = unzip_command[0]
            destination = "."  # Extract to the current working directory
            with zipfile.ZipFile(zip_file, "r") as zipf:
                zipf.extractall(destination)
            text.insert(tk.END, f"Unzipped archive: {zip_file}\n")
        except Exception as e:
            text.insert(tk.END, f"An error occurred: {str(e)}\n")

    elif user_input.startswith("help"):
        command_history.append(user_input)
        text.insert(tk.END, "Available commands:\n\n")
        text.insert(tk.END, "  exit --> Exit the terminal\n\n")
        text.insert(tk.END, "  clear --> Clear the terminal screen\n\n")
        text.insert(tk.END, "  cd <directory> --> Change the current directory\n\n")
        text.insert(tk.END, "  pwd --> Display the current directory\n\n")
        text.insert(tk.END, "  mkdir <directory> --> Create a new directory\n\n")
        text.insert(tk.END, "  touch <file> --> Create a new file\n\n")
        text.insert(tk.END, "  rm <file or directory> --> Remove a file or directory\n\n")
        text.insert(tk.END, "  start <file> --> Open a file\n\n")
        text.insert(tk.END, "  cat <file1> [file2 file3 ...] --> Concatenate and display file contents\n\n")
        text.insert(tk.END, "  find <pattern> --> Search for files and directories matching a pattern\n\n")
        text.insert(tk.END, "  chmod <permissions> <file> --> Change file permissions\n\n")
        text.insert(tk.END, "  whoami --> Display the current user\n\n")
        text.insert(tk.END, "  tar <archive.tar> <file1 file2 ...> --> Create a tar archive\n\n")
        text.insert(tk.END, "  zip <archive.zip> <file1 file2 ...> --> Create a zip archive\n\n")
        text.insert(tk.END, "  unzip <archive.zip> --> Extract files from a zip archive\n\n")
        text.insert(tk.END, "  math <num1> <operation> <num2> --> Perform basic math operations\n\n")     
        text.insert(tk.END, "  help --> Display this help message\n\n")


    elif user_input.startswith("math "):
        command_history.append(user_input)
        try:
            expression = user_input[5:]
            result = evaluate_expression(expression)
            text.insert(tk.END, f"Result: {result}\n")
        except Exception as e:
            text.insert(tk.END, f"Error: {str(e)}\n")


    else:
        if user_input:
            command_history.append(user_input)
            current_history_index = len(command_history)
        if user_input == "history":
            for idx, command in enumerate(command_history):
                text.insert(tk.END, f"{idx+1}: {command}\n")
        else:
            try:
                result = subprocess.run(
                    user_input, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                text.insert(tk.END, f"Output:\n{result.stdout}\nErrors:\n{result.stderr}\n")
            except Exception as e:
                text.insert(tk.END, f"An error occurred: {str(e)}\n")

    text.see("end")
    entry.delete(0, tk.END)

def handle_up_key(event):
    global current_history_index
    if current_history_index > 0:
        current_history_index -= 1
        entry.delete(0, tk.END)
        entry.insert(0, command_history[current_history_index])

def handle_down_key(event):
    global current_history_index
    if current_history_index < len(command_history) - 1:
        current_history_index += 1
        entry.delete(0, tk.END)
        entry.insert(0, command_history[current_history_index])

def find_files(pattern, directory):
    matches = []
    for root, dirs, files in os.walk(directory):
        for item in dirs + files:
            if pattern in item:
                matches.append(os.path.join(root, item))
    return matches

root = tk.Tk()
root.title("Terminal Prototype")

frame = tk.Frame(root, bg="white")
frame.pack(fill=tk.BOTH, expand=True)

entry = tk.Entry(frame, font=("Arial", 12), fg="green", bg="white")
entry.pack(fill=tk.X, padx=5, pady=5)
entry.bind("<Return>", lambda event: execute_command())
entry.bind("<Up>", handle_up_key)
entry.bind("<Down>", handle_down_key)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Courier New", 12), yscrollcommand=scrollbar.set, fg="green", bg="lavender")
text.pack(fill=tk.BOTH, expand=True)
text.configure(insertbackground='green')
scrollbar.config(command=text.yview)

entry.focus()

root.mainloop()
