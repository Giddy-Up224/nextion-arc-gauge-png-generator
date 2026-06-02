# Packaging Requirements (project-specific)

# 1. Default entrypoint is src/main.py unless explicitly provided.
# 2. Image assets are bundled from img/ via PyInstaller --add-data.
# 3. License and notice files are bundled from licenses/ and THIRD_PARTY_NOTICES.md.
# 4. App icon is expected at img/{PROGRAM_NAME}.ico (if present).
# 5. Python dependencies are installed from requirements.txt.
# 6. Default packaging virtual environment folder is instvenv.

# These are intentional defaults for this project's build workflow.

import subprocess
import shutil
import os
import sys

PROGRAM_NAME = ''
MAIN_PATH    = ''
VENV_DIR     = 'instvenv'

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
        f"--add-data=img{data_sep}img",
        f"--add-data=licenses{data_sep}licenses",
        f"--add-data=THIRD_PARTY_NOTICES.md{data_sep}.",
        f"--name={PROGRAM_NAME}",
        f"{MAIN_PATH}"
    ]

    icon_path = os.path.join("img", f"{PROGRAM_NAME}.ico")
    if os.path.isfile(icon_path):
        cmd.insert(3, f"--icon={icon_path}")

    subprocess.run(cmd, check=True)


def main():
    if '--help' in sys.argv:
        cmd = ''
        if sys.platform == 'win32':
            cmd = 'python'
        else:
            cmd = 'python3'
        print(f"Usage: {cmd} pkg.py [optional]<name-for-your-executable> [optional]<path-to-main.py> [optional]<venv-folder>")
        print(f"Example: {cmd} pkg.py MyApp src/main.py instvenv")
        print("MyApp is simply the name that you wish to be used for your app.")
        print("If no app name is provided, it will default to UNTITLED")
        print("Path to main must be specified if not in default location: src/main.py")
        print("Venv folder defaults to instvenv")
        sys.exit()

    global PROGRAM_NAME
    global MAIN_PATH
    global VENV_DIR
    PROGRAM_NAME = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != '' else 'UNTITLED'
    MAIN_PATH    = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '' else 'src/main.py'
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