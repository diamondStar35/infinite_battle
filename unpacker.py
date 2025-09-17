import os
import sys

# We need to import the ResourceFile class from the ngk library
try:
    from ngk.packfile import ResourceFile, InvalidPackHeader
except ImportError:
    print("Error: Could not import the ngk library.")
    print("Please make sure the ngk folder is in the same directory as this script.")
    sys.exit(1)

# --- Configuration ---
PACK_FILE_NAME = "sounds.dat"
ENCRYPTION_KEY = "yes"
OUTPUT_DIRECTORY = "unpacked_sounds"
# ---------------------

def main():
    print(f"Attempting to unpack '{PACK_FILE_NAME}'...")

    # 1. Check if the pack file exists
    if not os.path.exists(PACK_FILE_NAME):
        print(f"Error: The file '{PACK_FILE_NAME}' was not found in this directory.")
        return

    # 2. Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIRECTORY):
        print(f"Creating output directory: '{OUTPUT_DIRECTORY}'")
        os.makedirs(OUTPUT_DIRECTORY)

    # 3. Load the resource file
    try:
        pack = ResourceFile(ENCRYPTION_KEY)
        pack.load(PACK_FILE_NAME)
        print("Pack file loaded successfully.")
    except InvalidPackHeader:
        print("Error: Invalid pack header. The file might be corrupt or the key is wrong.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while loading the pack file: {e}")
        return

    # 4. Get the list of all files inside the pack
    file_list = pack.list()
    if not file_list:
        print("The pack file is empty. Nothing to extract.")
        return

    print(f"Found {len(file_list)} files to extract.")

    # 5. Loop through, extract, and save each file
    extracted_count = 0
    for internal_name_bytes in file_list:
        try:
            # The file names are stored as bytes, so we decode them to strings
            internal_name_str = internal_name_bytes.decode('utf-8')
            
            # Get the binary content of the file from the pack
            content = pack.get(internal_name_bytes)

            # Construct the full path for the output file
            output_path = os.path.join(OUTPUT_DIRECTORY, internal_name_str)
            
            # Create the necessary subdirectories (e.g., 'sounds/')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Write the content to the new file on disk
            with open(output_path, 'wb') as f:
                f.write(content)
            
            print(f"  -> Extracted: {internal_name_str}")
            extracted_count += 1

        except Exception as e:
            print(f"Error extracting '{internal_name_str}': {e}")

    print("\n-------------------------------------------")
    print(f"Extraction complete. {extracted_count} files were written to the '{OUTPUT_DIRECTORY}' folder.")
    print("-------------------------------------------")

if __name__ == "__main__":
    main()