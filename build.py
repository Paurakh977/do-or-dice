import os
import sys
import subprocess
import platform
from PIL import Image


def build():
 
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_png = os.path.join(base_dir, "assets", "images", "logo.png")
    logo_ico = os.path.join(base_dir, "assets", "images", "logo.ico")
    assets_src = os.path.join(base_dir, "assets")
    assets_dst = "assets"
    
    if os.path.exists(logo_png):
        print(f"Converting {logo_png} to .ico format...")
        try:
            img = Image.open(logo_png)
            img.save(logo_ico, format='ICO', sizes=[(256, 256)])
            print(f"Icon saved to {logo_ico}")
        except Exception as e:
            print(f"Failed to convert icon: {e}")
            logo_ico = None
    else:
        print(f"Warning: Logo not found at {logo_png}")
        logo_ico = None

    sep = ";" if platform.system() == "Windows" else ":"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name", "DoOrDice",
        "--add-data", f"{assets_src}{sep}{assets_dst}",
        "--clean",
    ]
    
    if logo_ico and os.path.exists(logo_ico):
        cmd.extend(["--icon", logo_ico])
        
    cmd.append("main.py")

    print(f"Executing: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*30)
        print("BUILD SUCCESSFUL")
        print(f"Executable is located in: {os.path.join(base_dir, 'dist')}")
        print("="*30)
    except subprocess.CalledProcessError as e:
        print(f"\nBUILD FAILED with error code {e.returncode}")

if __name__ == "__main__":
    build()
