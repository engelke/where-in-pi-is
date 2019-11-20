
import mmap
import time


DIGITS_FILE_NAME = '/pi/Pi.txt'
DIGITS_FILE = open(DIGITS_FILE_NAME, 'r')
DIGITS_MAP = mmap.mmap(DIGITS_FILE.fileno(), 0, access=mmap.ACCESS_READ)


def where_is(digit_bytes):
    location = DIGITS_MAP.find(digit_bytes)
    if location > 0:
        return location - 1
    else:
        return None


def timed_find(digits_bytes):
    started = time.time()
    decimal_place = where_is(digits_bytes)
    elapsed = time.time() - started
    return decimal_place, elapsed


if __name__ == "__main__":
    for run in range(10):
        with open('teststrings.txt', 'r') as strings:
            for line in strings:
                search = line.strip()
                if search.isdigit():
                    location, duration = timed_find(search.encode('utf-8'))
                    print('{},{},{}'.format(search, location, duration), flush=True)
                else:
                    print('Bad input: "{}"'.format(search), flush=True)

