import os

def create_directory(directory):
    """Create a new directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def list_files(directory):
    """List all files in a directory."""
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
