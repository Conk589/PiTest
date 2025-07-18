import os
import zipfile
import tarfile
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# Optional dependencies
try:
    import rarfile
    RAR_SUPPORT = True
except ImportError:
    RAR_SUPPORT = False
    print("Note: RAR support requires 'rarfile'. Install with: pip install rarfile")

try:
    import py7zr
    SEVEN_Z_SUPPORT = True
except ImportError:
    SEVEN_Z_SUPPORT = False
    print("Note: 7z support requires 'py7zr'. Install with: pip install py7zr")


def extract_archive(archive_path, extract_to):
    archive_lower = archive_path.lower()
    try:
        if archive_lower.endswith('.zip'):
            print("📦 Detected ZIP archive.")
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(extract_to)

        elif any(archive_lower.endswith(ext) for ext in ['.tar', '.tar.gz', '.tgz', '.tar.bz2']):
            print("📦 Detected TAR archive.")
            with tarfile.open(archive_path, 'r:*') as tf:
                tf.extractall(extract_to)

        elif archive_lower.endswith('.rar') and RAR_SUPPORT:
            print("📦 Detected RAR archive.")
            with rarfile.RarFile(archive_path, 'r') as rf:
                rf.extractall(extract_to)

        elif archive_lower.endswith('.7z') and SEVEN_Z_SUPPORT:
            print("📦 Detected 7Z archive.")
            with py7zr.SevenZipFile(archive_path, mode='r') as szf:
                szf.extractall(path=extract_to)

        else:
            print("❌ Unsupported archive format.")
            return False

        print("✅ Extraction completed.")
        return True

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False


def extract_all_archives(root_folder):
    supported_extensions = ['.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.rar', '.7z']

    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in supported_extensions):
                archive_path = os.path.join(dirpath, filename)
                print(f"\n🔍 Found archive: {archive_path}")
                print(f"📂 Target extraction folder: {dirpath}")

                if extract_archive(archive_path, dirpath):
                    try:
                        os.remove(archive_path)
                        print(f"🗑️  Successfully deleted: {archive_path}")
                    except Exception as e:
                        print(f"⚠️  Failed to delete {archive_path}: {e}")
                else:
                    print("⏩ Skipped deletion due to failed extraction.")


if __name__ == "__main__":
    folder_to_scan = input("📂 Enter the path to the folder to scan: ").strip()
    if os.path.isdir(folder_to_scan):
        extract_all_archives(folder_to_scan)
    else:
        print("❌ Invalid folder path.")
