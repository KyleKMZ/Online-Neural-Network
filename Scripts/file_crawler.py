import os
import sys

# Find files ending with the extensions in the list and
# returns a list of paths to such files within the given
# directory and sub directories
def find_file_with_extensions(dir_path, extensions=[]):
    file_list = []
    if not extensions:
        return file_list

    for entry in os.listdir(dir_path):
        subdir_path = os.path.join(dir_path, entry)
        if os.path.isdir(subdir_path):
            # recursively searching sub-directories
            file_list.extend(find_file_with_extensions(subdir_path, extensions))
        else:
            ext = os.path.splitext(entry)[-1]
            if ext in extensions:
                file_list.append(entry)

    return file_list

def main():
    # for testing in the command-line as a script
    print(find_file_with_extensions('../Test/', extensions=['.cs', '.star']))

if __name__ == '__main__':
    main()
                


