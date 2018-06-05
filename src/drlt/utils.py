import os
import errno
import re

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_bound_from_string(bound_string):
    coordinate = re.findall(r'\d+', bound_string)
    left = int(coordinate[0])
    top = int(coordinate[1])
    right = int(coordinate[2])
    bottom = int(coordinate[3])
    return [left, right, top, bottom]

