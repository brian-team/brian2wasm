import argparse
import sys
import os

def main():

    parser = argparse.ArgumentParser(
        description="Brian2WASM CLI"
    )
    parser.add_argument(
        "script",
        help="Path to the Python script to run"
    )
    parser.add_argument(
        "--no-server",
        action="store_true",
        help="Generate files without starting the web server"
    )
    args = parser.parse_args()

    script_path = args.script

    # Check if the script exists and is a Python file
    if not os.path.isfile(script_path):
        print(f"Error: File '{script_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    if not script_path.endswith(".py"):
        print(f"Error: File '{script_path}' is not a Python script (.py).", file=sys.stderr)
        sys.exit(1)

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

    # Inject the required lines at the top
    if has_html_file:
        print(f"html file found: '{html_file_path}'")
        injection = (
            "from brian2 import set_device\n"
            "import brian2wasm\n"
            f"set_device('wasm_standalone', directory='{script_name}', html_file='{html_file}')\n"
        )
    else:
        print(f"html file not found: using default html template")
        injection = (
            "from brian2 import set_device\n"
            "import brian2wasm\n"
            f"set_device('wasm_standalone', directory='{script_name}')\n"
        )
    modified_script = injection + script_content

    # Set the working directory to the script's directory
    original_cwd = os.getcwd()
    os.chdir(script_dir)

    try:
        # Execute the modified script in memory with __file__ set
        if args.no_server:
            os.environ['BRIAN2WASM_NO_SERVER'] = '1'
        print(f"Script path: {os.path.abspath(script_path)}")
        print(f"Directory: {script_dir}")
        exec_globals = {'__name__': '__main__', '__file__': os.path.abspath(script_path)}
        exec(modified_script, exec_globals)
    except Exception as e:
        print(f"Error running script: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Restore the original working directory
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()