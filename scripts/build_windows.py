#!/usr/bin/env python3
"""Build script for Windows Packaging (v0.9.0).

This script performs the following actions:
1. Runs PyInstaller using pushbox.spec in onedir mode.
2. Copies README.md, LICENSE, and RELEASE_NOTES.md to the package.
3. Generates a 'quick-start.txt' guide inside the packaged application folder.
4. Packages the compiled folder into a clean ZIP archive.
5. Outputs the SHA256 checksum of the created ZIP archive.
"""

import hashlib
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# Package settings
APP_NAME = "Pushbox-Pygame"
VERSION = "1.0.0"
ZIP_NAME = f"{APP_NAME}-v{VERSION}-windows-x64.zip"


def calculate_sha256(file_path: Path) -> str:
    """Calculate the SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def main() -> None:
    """Main build process."""
    print("==================================================")
    print(f"Starting build and packaging for {APP_NAME} v{VERSION}")
    print("==================================================")

    project_root = Path(__file__).parent.parent.resolve()
    os.chdir(project_root)

    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    release_dir = project_root / "release"
    spec_file = project_root / "pushbox.spec"
    app_dir = dist_dir / APP_NAME

    # 1. Clean previous build/dist outputs
    print("\n[1/5] Cleaning previous builds...")
    for path in [dist_dir, build_dir]:
        if path.exists():
            print(f"Removing: {path}")
            shutil.rmtree(path)
    release_dir.mkdir(exist_ok=True)

    # Check that the icon file exists as defined in the spec to prevent build errors
    icon_file = project_root / "src" / "pushbox" / "assets" / "icon" / "pushbox.ico"
    if not icon_file.exists():
        print(f"Error: Application icon not found at {icon_file}")
        print("Please run 'uv run python scripts/generate_icon.py' first.")
        sys.exit(1)

    try:
        subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--noconfirm", str(spec_file)],
            check=True,
        )
        print("PyInstaller compilation completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: PyInstaller build failed with exit code {e.returncode}")
        sys.exit(1)

    # 3. Verify built output structure and copy resources
    print("\n[3/5] Generating documentation and verifying asset folders...")
    if not app_dir.exists():
        print(f"Error: Packed application folder not found at {app_dir}")
        sys.exit(1)

    # Ensure assets directory exists in the output folder
    output_assets = app_dir / "assets"
    output_assets.mkdir(parents=True, exist_ok=True)
    (output_assets / "images").mkdir(parents=True, exist_ok=True)
    (output_assets / "sounds").mkdir(parents=True, exist_ok=True)
    (output_assets / "themes").mkdir(parents=True, exist_ok=True)

    # Copy metadata files
    metadata_files = ["README.md", "LICENSE", "RELEASE_NOTES.md"]
    for filename in metadata_files:
        src_path = project_root / filename
        if src_path.exists():
            shutil.copy2(src_path, app_dir / filename)
            print(f"Copied {filename} to packaged app folder.")
        else:
            print(f"Warning: {filename} not found at project root.")

    # Write quick-start.txt
    quick_start_path = app_dir / "quick-start.txt"
    quick_start_content = """Pushbox-Pygame 快速開始指南 (Quick Start Guide)
==============================================

歡迎遊玩 Pushbox-Pygame！這是一部現代化的推箱子經典益智遊戲。

【如何開始遊戲】
1. 在本資料夾中，尋找並雙擊「Pushbox-Pygame.exe」即可啟動遊戲。
2. 第一次啟動時，遊戲會自動在與「Pushbox-Pygame.exe」同級的目錄下建立：
   - 「data/」（儲存設定、進度、最高記錄）
   - 「levels/」（存放自訂關卡）資料夾。

【基本操作控制】
- 移動角色：方向鍵 (↑↓←→) 或 WASD
- 撤銷上一步 (Undo)：按 Z 鍵 或 Backspace 鍵
- 重做下一步 (Redo)：按 Y 鍵
- 重置目前關卡 (Reset)：按 F5 鍵 或 Delete 鍵
- 返回主選單：按 M 鍵
- 開啟/關閉說明面板 (Help)：按 H 鍵 或 F1 鍵
- 💡 智能提示：按 I 鍵 (會調用 BFS 求解器給出前三步移動提示)

【安全性提示】
- 當您第一次執行 Pushbox-Pygame.exe 時，Windows SmartScreen
  可能會彈出「已保護您的電腦」的 unsigned exe 警告。
- 這是因為此執行檔是使用 PyInstaller 打包且尚未進行數位簽章。
- 請放心，本軟體完全安全。您可以點擊「其他資訊」，
  然後點擊「仍要執行」來啟動遊戲。

【更多資訊與自訂關卡】
- 若要了解更多資訊，請參閱主目錄下的 README.md，或造訪官方 GitHub：
  https://github.com/YI-TING-EE13/Pushbox-Pygame

祝您遊戲愉快！
- Pushbox-Pygame 開發團隊
"""

    with open(quick_start_path, "w", encoding="utf-8") as f:
        f.write(quick_start_content)
    print(f"Generated quick-start.txt at: {quick_start_path.relative_to(project_root)}")

    # 4. Packaging into a ZIP archive
    zip_path = release_dir / ZIP_NAME
    print(f"\n[4/5] Creating ZIP archive at {zip_path.relative_to(project_root)}...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Walk through dist/Pushbox-Pygame/ directory recursively
        for root, _dirs, files in os.walk(app_dir):
            for file in files:
                file_path = Path(root) / file
                # Define arcname to preserve a top-level APP_NAME folder
                rel_path = file_path.relative_to(dist_dir)
                zipf.write(file_path, arcname=rel_path)

    # 5. Output SHA256 checksum
    print("\n[5/5] Calculating SHA256 checksum...")
    sha256_checksum = calculate_sha256(zip_path)
    sha256_file = release_dir / f"{ZIP_NAME}.sha256"
    with open(sha256_file, "w", encoding="utf-8") as f:
        f.write(f"{sha256_checksum}  {ZIP_NAME}\n")

    print("\nZIP archive created successfully!")
    print(f"Archive file size: {zip_path.stat().st_size / (1024 * 1024):.2f} MB")
    print(f"SHA256: {sha256_checksum}")
    print(f"Saved checksum to {sha256_file.relative_to(project_root)}")
    print("\n==================================================")
    print("Build and Windows Packaging completed successfully!")
    print("==================================================")


if __name__ == "__main__":
    main()
