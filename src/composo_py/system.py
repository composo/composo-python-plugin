import os
import subprocess
from pathlib import Path


class RealSysInterface:
    def mkdir(self, path: Path, parents=False):
        path.mkdir(exist_ok=True, parents=parents)

    def write(self, path: Path, content, append=False):
        # if not path.is_file():
        #     raise RuntimeError("can only write to a file")

        self.mkdir(path.parent)
        with open(path, 'w') as f:
            f.write(content)

    def read(self, path):
        with open(path, 'r') as f:
            return f.read()

    def git(self, *args):
        return subprocess.check_call(['git'] + list(args))

    def path_exists(self, path: Path):
        return path.exists()


class DrySysInterface:

    def mkdir(self, path, parents=False):
        print(f"mkdir {'-p' if parents else ''} {str(path)}")

    def write(self, path, content, append=False):
        triple_q = '"""'
        print(
            f"""
with open({str(path)}, 'w') as f:
    f.write({triple_q}{content}{triple_q})       
""")

    def git(self, *args):
        return print(['git'] + list(args))

    def path_exists(self, path: Path):
        return path.exists()

