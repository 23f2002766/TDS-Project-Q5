import subprocess
import tempfile
import os
import os
import subprocess
import tempfile
import uuid


def run_python(code: str):
    try:
        os.makedirs("outputs", exist_ok=True)
        
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as f:
            f.write(code)
            temp_file = f.name

        result = subprocess.run(
            ["python", temp_file],
            capture_output=True,
            text=True,
            timeout=60
        )

        os.remove(temp_file)

        if result.returncode == 0:
            return result.stdout.strip()

        return result.stderr.strip()

    except Exception as e:
        return str(e)