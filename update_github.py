import os
import subprocess

def fetch_remote_file():
    """Fetch the remote index.html file for comparison."""
    remote_file = "/home/dakboard/myenv/tmp/remote_index.html"
    # Ensure the temporary directory exists
    os.makedirs(os.path.dirname(remote_file), exist_ok=True)

    # Fetch the remote index.html
    try:
        subprocess.run(
            f"git show origin/main:index.html > {remote_file}",
            shell=True,
            check=True
        )
        return remote_file
    except subprocess.CalledProcessError as e:
        print(f"Error fetching remote file: {e}")
        return None

def compare_files(local_file, remote_file):
    """Compare local index.html with the remote version."""
    if not os.path.exists(remote_file):
        print("Remote file not found. Skipping comparison.")
        return True  # Treat as changed if remote file is missing

    try:
        with open(local_file, "r") as local, open(remote_file, "r") as remote:
            return local.read() != remote.read()
    except Exception as e:
        print(f"Error comparing files: {e}")
        return True  # Assume changed if there's an error

def push_to_github():
    """Push updated content to GitHub."""
    token_path = "/home/dakboard/myenv/credentials/.github_token"

    # Check for the GitHub token file
    if not os.path.exists(token_path):
        print("GitHub token file not found!")
        return

    # Read the GitHub token
    with open(token_path, "r") as token_file:
        github_token = token_file.read().strip()

    # Configure the Git remote URL with the token
    remote_url = f"https://{github_token}@github.com/odjopuen/bboi.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)

    # Stage all changes
    subprocess.run(["git", "add", "."], check=True)

    # Commit and push the changes
    try:
        subprocess.run(["git", "commit", "-m", "Auto-update index.html"], check=True)
    except subprocess.CalledProcessError:
        print("No changes to commit. Exiting.")
        return

    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("Pushed changes to GitHub.")

if __name__ == "__main__":
    local_file = "/home/dakboard/myenv/bboi/index.html"

    print("Fetching remote file for comparison...")
    remote_file = fetch_remote_file()

    if remote_file and compare_files(local_file, remote_file):
        print("Changes detected. Updating GitHub...")
        push_to_github()
    else:
        print("No changes detected. Exiting.")
