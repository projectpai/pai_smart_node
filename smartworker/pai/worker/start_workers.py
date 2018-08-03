import os
import sys
from subprocess import Popen


def start_workers(number_of_workers):
    current_directory = os.path.dirname(__file__)
    worker_script_path = os.path.join(current_directory, 'worker.py')
    for i in range(number_of_workers):
        print("Starting worker {}".format(i))
        Popen(['python', worker_script_path, '-e', 'dev', '-w', str(i)])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("You need to provide number of workers you wish to start")

    start_workers(int(sys.argv[1]))
