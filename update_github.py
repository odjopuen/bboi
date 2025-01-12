import os
import subprocess

def push_to_github():
    """Push updated content to GitHub."""
    # Path to the GitHub token
    token_path = "/home/dakboard/myenv/credentials/.github_token"

    # Check if the GitHub token file exists
    if not os.path.exists(token_path):
        print("GitHub token file not found!")
        return

    # Read the GitHub token
    with open(token_path, "r") as token_file:
        github_token = token_file.read().strip()

    # Configure the Git remote URL with the token
    remote_url = f"https://{github_token}@github.com/odjopuen/bboi.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)

    # Stage all changes in the repository
    subprocess.run(["git", "add", "."], check=True)

    # Commit the changes if there are any
    try:
        subprocess.run(["git", "commit", "-m", "Auto-update index.html"], check=True)
    except subprocess.CalledProcessError:
        print("No changes to commit. Exiting.")
        return

    # Push the changes to the GitHub repository
    subprocess.run(["git", "push", "origin", "main"], check=True)

    print("Pushed changes to GitHub.")

if __name__ == "__main__":
    try:
        print("Pushing updates to GitHub...")
        push_to_github()
        print("Process complete!")
    except Exception as e:
        print(f"An error occurred: {e}")
