from PyQt5.QtWidgets import *
from machine import Machine
import sys
sys.path.append('/')


class Main:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.machine = Machine()
        self.app.exec_()


if __name__ == '__main__':
    Main()
