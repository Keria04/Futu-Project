import sys
import platform
import subprocess
import json

def get_conda_env():
    try:
        # 获取当前conda环境名
        env_name = subprocess.check_output(
            ['conda', 'info', '--json'], universal_newlines=True
        )
        info = json.loads(env_name)
        return info.get('active_prefix_name', 'Unknown')
    except Exception:
        return 'Not in a conda environment or conda not found'

def main():
    print("Hello, world!")
    print("Python version:", sys.version)
    print("Platform:", platform.platform())
    print("Conda environment:", get_conda_env())

if __name__ == "__main__":
    main()