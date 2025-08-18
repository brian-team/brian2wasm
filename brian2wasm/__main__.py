import argparse
import shutil
import sys
import os
import platform
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Brian2WASM CLI")
    parser.add_argument("script", help="Path to the Python script to run")
    parser.add_argument("--no-server", action="store_true", help="Generate files without starting the web server")
    parser.add_argument("--skip-install", action="store_true", help="Run Brian2WASM without installing/activating EMSDK")
    args = parser.parse_args()

    script_path = args.script

    # Check if the script exists and is a Python file
    if not os.path.isfile(script_path):
        full_path = os.path.abspath(script_path)
        print(f"❌ Error: File '{full_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    if not script_path.endswith(".py"):
        print(f"❌ Error: File '{script_path}' is not a Python script (.py).", file=sys.stderr)
        sys.exit(1)

    if not args.skip_install:
        # Check emsdk setup
        check_emsdk()

    # Read the original script
    with open(script_path, 'r') as f:
        script_content = f.read()

    # Get the script's directory and name
    script_dir = os.path.dirname(script_path) or '.'
    script_name = os.path.splitext(os.path.basename(script_path))[0]

    # Check if an HTML file with the same name exists
    html_file = f"{script_name}.html"
    html_file_path = os.path.join(script_dir, html_file)
    has_html_file = os.path.isfile(html_file_path)

    # Inject required lines at the top
    if has_html_file:
        print(f"✅ HTML file found: '{html_file_path}'")
        injection = (
            "from brian2 import set_device\n"
            "import brian2wasm\n"
            f"set_device('wasm_standalone', directory='{script_name}', html_file='{html_file}')\n"
        )
    else:
        print("ℹ️  HTML file not found: using default HTML template.")
        injection = (
            "from brian2 import set_device\n"
            "import brian2wasm\n"
            f"set_device('wasm_standalone', directory='{script_name}')\n"
        )

    modified_script = injection + script_content

    # Set working directory to script's directory
    original_cwd = os.getcwd()
    os.chdir(script_dir)

    try:
        if args.no_server:
            os.environ['BRIAN2WASM_NO_SERVER'] = '1'

        print(f"📄 Script path: {os.path.abspath(script_path)}")
        print(f"📁 Directory: {script_dir}")
        exec_globals = {'__name__': '__main__', '__file__': os.path.abspath(script_path)}
        compiled_script = compile(modified_script, script_path, 'exec')
        exec(compiled_script, exec_globals)

    except Exception as e:
        print(f"❌ Error running script: {e}", file=sys.stderr)
        sys.exit(1)

    finally:
        os.chdir(original_cwd)


def check_emsdk():
    emsdk = shutil.which("emsdk")
    conda_emsdk_dir = os.environ.get("CONDA_EMSDK_DIR")

    if not emsdk and not conda_emsdk_dir:
        print("❌ EMSDK and CONDA_EMSDK_DIR not found. That means EMSDK is not installed.")
        print("   ➤ If you are using **Pixi**, run:")
        print("     pixi add emsdk && pixi install")
        print("   ➤ If you are using **Conda**, run:")
        print("     conda install emsdk -c conda-forge")
        print("   ➤ Else refer to Emscripten documentation:")
        print("     https://emscripten.org/index.html#")
        sys.exit(1)

    print(f"✅ EMSDK is installed and CONDA_EMSDK_DIR is found")

    try:
        print("🔧 Attempting to activate EMSDK with: emsdk activate latest")
        result = subprocess.run(["./emsdk", "activate", "latest"], cwd=conda_emsdk_dir, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to activate EMSDK:")
            choice = input("Do you want to install and activate EMSDK now? (y/n) ")
            if choice == 'y':
                try:
                    subprocess.run(["./emsdk", "install", "latest"], cwd=conda_emsdk_dir, check=True)
                    print("✅ EMSDK install & activation succeeded. You can run the script now.")
                except subprocess.CalledProcessError as e:
                    print("❌ Failed to activate EMSDK:")
                    print("   ➤ Please run the following manually in your terminal and try again:")
                    print("       cd $CONDA_EMSDK_DIR && ./emsdk install latest && ./emsdk activate latest")
            else:
                print("   ➤ Please run the following manually in your terminal and try again:")
                print("       cd $CONDA_EMSDK_DIR && ./emsdk install latest && ./emsdk activate latest")

            sys.exit(1)
        else:
            print("✅ EMSDK activation succeeded.")
    except Exception as e:
        print(f"❌ Error while running EMSDK activation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()