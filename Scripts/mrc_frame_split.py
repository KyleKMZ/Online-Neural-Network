#!/usr/bin/env python

import argparse
import mrcfile
import os

def main():
    parser = argparse.ArgumentParser(description = 'Split movie files by number of frames.')
    parser.add_argument('movie_folders', nargs='+')
    args = parser.parse_args()
    folders = args.movie_folders


    movie_extensions = ['.mrcs', '.mrc', '.tiff']
    for folder in folders:
        movies = [movie for movie in os.listdir(folder) if os.path.splitext(movie)[-1] in movie_extensions]
        for movie in movies:
            with mrcfile.open(os.path.join(folder, movie), permissive=True) as movie_file:
                num_frames = int(movie_file.header.nz)
                if not os.path.exists(str(num_frames)):
                    os.mkdir(str(num_frames))
                os.symlink(os.path.join(folder, movie), os.path.join(str(num_frames), movie))






if __name__ == '__main__':
    main()
