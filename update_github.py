import os
import subprocess

def fetch_remote_file():
    """Fetch the remote index.html file for comparison."""
    remote_file = "/tmp/remote_index.html"
    subprocess.run(
        f"git show origin/main:index.html > {remote_file}",
        shell=True,
        check=True
    )
    return remote_file

def compare_files(local_file, remote_file):
    """Compare local index.html with the remote version."""
    if not os.path.exists(remote_file):
        print("Remote file not found. Skipping comparison.")
        return True  # Treat as changed if remote file is missing

    with open(local_file, "r") as local, open(remote_file, "r") as remote:
        return local.read() != remote.read()

def push_to_github():
    """Push updated content to GitHub."""
    token_path = "/home/dakboard/myenv/credentials/.github_token"

    if not os.path.exists(token_path):
        print("GitHub token file not found!")
        return

    with open(token_path, "r") as token_file:
        github_token = token_file.read().strip()

    remote_url = f"https://{github_token}@github.com/odjopuen/bboi.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)

    subprocess.run(["git", "add", "."], check=True)

    try:
        subprocess.run(["git", "commit", "-m", "Auto-update index.html"], check=True)
    except subprocess.CalledProcessError:
        print("No changes to commit. Skipping push.")
        return

    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("Pushed changes to GitHub.")

def main():
    local_file = "/home/dakboard/myenv/bboi/index.html"
    remote_file = fetch_remote_file()

    if compare_files(local_file, remote_file):
        print("Changes detected. Pushing updates...")
        push_to_github()
    else:
        print("No changes detected. Skipping push.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
