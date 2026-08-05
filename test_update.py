import asyncio
import os
import shutil
import sys

async def run_test():
    git_bin = shutil.which("git")
    if not git_bin:
        for p in ["/usr/bin/git", "/usr/local/bin/git", "/opt/homebrew/bin/git", "/bin/git"]:
            if os.path.exists(p):
                git_bin = p
                break
    print(f"Git bin: {git_bin}")
    if git_bin:
        try:
            proc_git = await asyncio.create_subprocess_exec(
                git_bin, "pull", "origin", "main",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd()
            )
            stdout_git, stderr_git = await proc_git.communicate()
            print("STDOUT:", stdout_git.decode().strip())
            print("STDERR:", stderr_git.decode().strip())
        except Exception as err:
            print("ERROR EXEC:", err)
    else:
        print("NO GIT BIN")

asyncio.run(run_test())
