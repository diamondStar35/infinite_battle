import sys
import os
from ngk.packfile import ResourceFile

def get_list_of_files(dirName):
    """Recursively gets all file paths within a directory."""
    listOfFile = os.listdir(dirName)
    allFiles = []
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles.extend(get_list_of_files(fullPath))
        else:
            allFiles.append(fullPath)
    return allFiles

def real_main():
    if len(sys.argv) != 3:
        print("Usage: python packer.py <output_filename> <encryption_key>")
        print("Example: python packer.py sounds.dat yes")
        sys.exit(1)

    packfilename = sys.argv[1]
    encryptionkey = sys.argv[2]
    
    source_directory = "sounds"
    if not os.path.isdir(source_directory):
        print(f"Error: The source directory '{source_directory}' was not found.")
        print("Please make sure you are running this script from your main project folder.")
        sys.exit(1)

    pack = ResourceFile(encryptionkey)
    files_to_pack = get_list_of_files(source_directory)
    
    print(f"Processing {len(files_to_pack)} files from '{source_directory}'...")

    for full_path in files_to_pack:
        internal_name = os.path.relpath(full_path, source_directory)
        
        # Normalize path separators to forward slashes for consistency inside the pack
        internal_name = internal_name.replace(os.path.sep, '/')

        print(f"  Adding: {full_path}  ->  Internal name: {internal_name}")
        pack.add_file(name=full_path, internalname=internal_name)
    
    print("Done processing files.")
    print(f"Saving pack to disk as '{packfilename}'. This can take some time...")
    
    output_path = os.path.join(os.getcwd(), packfilename)
    pack.save(output_path)
    
    print(f"Done! The pack file can be found at: {output_path}")

def clean_on_abort():
    """Cleans up an unfinished packfile if the script is interrupted."""
    if len(sys.argv) > 1:
        packfilename = sys.argv[1]
        output_path = os.path.join(os.getcwd(), packfilename)
        if os.path.exists(output_path):
            print(f"Deleting unfinished packfile: {output_path}")
            os.remove(output_path)
            print("Cleanup done.")

def main():
    try:
        real_main()
    except KeyboardInterrupt:
        print("\nAborted by user. Cleaning up.")
        clean_on_abort()
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        clean_on_abort()

if __name__ == "__main__":
    main()
