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

# Checks if a folder is a relion project folder
def is_relion_project(dir_path):
    """
    All Relion project folders have the default_pipeline.star and 
    the .relion_display_gui_settings files.
    """
    files = ['default_pipeline.star', '.relion_display_gui_settings']
    for fname in files:
        if fname not in os.listdir(dir_path):
            return False

    return True

def main():
    # for testing in the command-line as a script
    print(is_relion_project('../../relion30_tutorial'))
    print(is_relion_project('../Test/'))

if __name__ == '__main__':
    main()
                


