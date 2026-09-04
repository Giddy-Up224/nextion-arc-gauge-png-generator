# Packaging Requirements (project-specific)

# 1. Default entrypoint is src/main.py unless explicitly provided.
# 2. Image assets are bundled from img/ via PyInstaller --add-data.
# 3. License and notice files are bundled from licenses/ and THIRD_PARTY_NOTICES.md.
# 4. !!!CHANGE THIS TO YOUR img NAME!!!
ICON_PATH = "img/Arcy.ico"
# 5. Python dependencies are installed from requirements.txt.
# 6. Default packaging virtual environment folder is instvenv.

# These are intentional defaults for this project's build workflow.

import subprocess
import shutil
import os
import sys
import platform

PROGRAM_NAME = ''
MAIN_PATH    = ''
VENV_DIR     = 'instvenv'

def get_platform_suffix():
    os_map = {"Windows": "Win", "Linux": "Linux", "Darwin": "macOS"}
    os_name = os_map.get(platform.system(), platform.system())

    arch_map = {"amd64": "x64", "x86_64": "x64", "aarch64": "arm64", "arm64": "arm64"}
    arch = arch_map.get(platform.machine().lower(), platform.machine().lower())

    return f"{os_name}_{arch}"

def venv_exists():
    if os.name == "nt":
        venv_python = os.path.join(VENV_DIR, "Scripts", "python.exe")
        return os.path.isdir(VENV_DIR) and os.path.isfile(venv_python)
    else:
        venv_python = os.path.join(VENV_DIR, "bin", "python")
        return os.path.isdir(VENV_DIR) and os.path.isfile(venv_python)

def setup_venv():
    python_exe = "python" if os.name == "nt" else "python3"
    subprocess.run([python_exe, "-m", "venv", VENV_DIR], check=True)
    venv_python = os.path.join(VENV_DIR, "Scripts", "python.exe") if os.name == "nt" else os.path.join(VENV_DIR, "bin", "python")
    subprocess.run([venv_python, "-m", "pip", "install", "pyinstaller"], check=True) # PyInstaller is always necessary
    subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)


def ensure_pyinstaller(venv_python: str):
    check = subprocess.run(
        [venv_python, "-c", "import PyInstaller"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if check.returncode != 0:
        subprocess.run([venv_python, "-m", "pip", "install", "pyinstaller"], check=True)

def clean():
    # Remove build directory if it exists
    if os.path.isdir("build"):
        shutil.rmtree("build")
    # Remove .spec file if it exists
    spec_file = f"{PROGRAM_NAME}.spec"
    if os.path.isfile(spec_file):
        os.remove(spec_file)

def build_executable():
    venv_python = os.path.join(VENV_DIR, "Scripts", "python.exe") if os.name == "nt" else os.path.join(VENV_DIR, "bin", "python")
    data_sep = ";" if os.name == "nt" else ":"
    cmd = [
        venv_python, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={PROGRAM_NAME}",
    ]

    # PyInstaller errors out on --add-data paths that don't exist, so only bundle what's present
    for src, dest in (("img", "img"), ("licenses", "licenses"), ("THIRD_PARTY_NOTICES.md", ".")):
        if os.path.exists(src):
            cmd.append(f"--add-data={src}{data_sep}{dest}")

    if os.path.isfile(ICON_PATH):
        cmd.append(f"--icon={ICON_PATH}")

    cmd.append(MAIN_PATH)

    subprocess.run(cmd, check=True)


def main():
    if '--help' in sys.argv:
        cmd = ''
        if sys.platform == 'win32':
            cmd = 'python'
        else:
            cmd = 'python3'
        print(f"Usage: {cmd} pkg.py [optional]<name-for-your-executable> [optional]<path-to-main.py> [optional]<venv-folder>")
        print(f"Example: {cmd} pkg.py MyApp src/ui2/main.py instvenv")
        print("MyApp is simply the name that you wish to be used for your app.")
        print("If no app name is provided, it will default to \'Arcy\'")
        print("Path to main must be specified if not in default location: src/ui2/main.py")
        print("Venv folder defaults to instvenv")
        sys.exit()

    global PROGRAM_NAME
    global MAIN_PATH
    global VENV_DIR
    PROGRAM_NAME = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != '' else 'Arcy'
    PROGRAM_NAME = f"{PROGRAM_NAME}_{get_platform_suffix()}"
    MAIN_PATH    = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '' else 'src/ui2/main.py'
    VENV_DIR     = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '' else 'instvenv'
    
    if not os.path.exists(MAIN_PATH):
        print(f"Invalid script path! {MAIN_PATH}")
        sys.exit(1)

    venv_python = os.path.join(VENV_DIR, "Scripts", "python.exe") if os.name == "nt" else os.path.join(VENV_DIR, "bin", "python")
    if not venv_exists():
        setup_venv()

    ensure_pyinstaller(venv_python)
        
    # If not running inside venv, re-launch script with venv's python
    if os.path.abspath(sys.executable) != os.path.abspath(venv_python):
        subprocess.run([venv_python, __file__, *sys.argv[1:]], check=True)
        return
    
    clean()
    build_executable()
    clean()



if __name__ == "__main__":
    main()