import os


class RealSysInterface:
    def mkdir(self, path, parents=False):
        path.mkdir(exist_ok=True, parents=parents)

    def write(self, path, content, append=False):
        with open(path, 'w') as f:
            f.write(content)


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
