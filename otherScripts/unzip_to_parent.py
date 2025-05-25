import os
import zipfile

def unzip_all_in_folder(root_folder):
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith('.zip'):
                zip_path = os.path.join(dirpath, filename)
                extract_to = dirpath  # Extract to the same folder as the zip file
                print(f'\nExtracting {zip_path} to {extract_to}')
                
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_to)
                    print(f'Successfully extracted: {zip_path}')

                    # Ask before deleting
                    confirm = input(f'Delete {filename}? (y/n): ').strip().lower()
                    if confirm == 'y':
                        os.remove(zip_path)
                        print(f'Deleted zip file: {zip_path}')
                    else:
                        print(f'Skipped deleting: {zip_path}')
                except zipfile.BadZipFile:
                    print(f"Error: {zip_path} is not a valid zip file.")
                except Exception as e:
                    print(f"Failed to extract {zip_path}: {e}")

if __name__ == "__main__":
    folder_to_scan = input("Enter the path to the folder: ").strip()
    if os.path.isdir(folder_to_scan):
        unzip_all_in_folder(folder_to_scan)
    else:
        print("Invalid folder path.")
