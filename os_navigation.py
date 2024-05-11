import os


def find_root(start_path=os.path.dirname(__file__)):
    current_path = os.path.abspath(start_path)
    while True:
        # Check if we have reached the root directory (i.e., path has no parent directory)
        if os.path.dirname(current_path) == current_path:
            break

        # Check if the current path contains certain files/directories that indicate the root
        if "README.md" in os.listdir(current_path):
            return current_path

        # Move one level up the directory tree
        current_path = os.path.dirname(current_path)
