import glob
import subprocess
import shutil
import shlex
import os

# whatever directory you want to compress other directories from
DATA = 'new_raw'

# Where the directories are compressed to
COMPRESSED = "compressed"

processed_dirs = glob.glob(f"{DATA}/*")

to_compress = []


for processed_dir in processed_dirs:
    print(processed_dir)
    images = glob.glob(f"{processed_dir}/*.jpeg")

    finished = True

    for image in images:
        if "render" not in image:
            finished = False
            break

    if finished:
        command = f"zip -vrj '{processed_dir}.zip' '{processed_dir}' -x '*.DS_Store'"

        try:
            subprocess.check_call(shlex.split(command))
            print(f"compressed {processed_dir}")
        except Exception as e:
            print(f"failed to compress with error: {e}")

        try:
            if not os.path.exists(COMPRESSED):
                os.mkdir(COMPRESSED)
            shutil.move(f"{processed_dir}.zip", f"{COMPRESSED}/")
        except shutil.Error:
            pass

    else:
        print("Not finished")
