# This file contains functions related to files.
import os


def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_file_name(file_path):
    path, extension = os.path.splitext(file_path)
    path_array = path.split("/")
    name = path_array[len(path_array) - 1]
    return name + extension


