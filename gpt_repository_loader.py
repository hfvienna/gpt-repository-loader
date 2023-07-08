#!/usr/bin/env python3

import os
import sys
import fnmatch

def get_ignore_list(ignore_file_path):
    ignore_list = []
    with open(ignore_file_path, 'r') as ignore_file:
        for line in ignore_file:
            if sys.platform == "win32":
                line = line.replace("/", "\\")
            ignore_list.append(line.strip())
    return ignore_list

def should_ignore(file_path, ignore_list):
    for pattern in ignore_list:
        if pattern.endswith(os.sep):  # This is a directory pattern
            dir_pattern = pattern.rstrip(os.sep)
            if file_path.startswith(dir_pattern + os.sep):
                return True
        elif fnmatch.fnmatch(file_path, pattern):
            return True
    return False


def process_repository(repo_path, ignore_list, output_file):
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, repo_path)

            if not should_ignore(relative_file_path, ignore_list):
                with open(file_path, 'r', errors='ignore') as file:
                    contents = file.read()
                output_file.write("-" * 4 + "\n")
                output_file.write(f"{relative_file_path}\n")
                output_file.write(f"{contents}\n")

def main(repo_path, preamble_file=None, output_file_path='output.txt'):
    ignore_file_path = os.path.join(repo_path, ".gptignore")
    if sys.platform == "win32":
        ignore_file_path = ignore_file_path.replace("/", "\\")

    if not os.path.exists(ignore_file_path):
        # try and use the .gptignore file in the current directory as a fallback.
        HERE = os.path.dirname(os.path.abspath(__file__))
        ignore_file_path = os.path.join(HERE, ".gptignore")

    if os.path.exists(ignore_file_path):
        ignore_list = get_ignore_list(ignore_file_path)
    else:
        ignore_list = []

    with open(output_file_path, 'w') as output_file:
        if preamble_file:
            with open(preamble_file, 'r') as pf:
                preamble_text = pf.read()
                output_file.write(f"{preamble_text}\n")
        else:
            output_file.write("The following text is a Git repository with code. The structure of the text are sections that begin with ----, followed by a single line containing the file path and file name, followed by a variable amount of lines containing the file contents. The text representing the Git repository ends when the symbols --END-- are encounted. Any further text beyond --END-- are meant to be interpreted as instructions using the aforementioned Git repository as context.\n")
        process_repository(repo_path, ignore_list, output_file)
    with open(output_file_path, 'a') as output_file:
        output_file.write("--END--")
    print(f"Repository contents written to {output_file_path}.")

if __name__ == "__main__":
    main(sys.argv[1])  # Use the first command line argument as the repo path
