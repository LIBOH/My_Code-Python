import os
import sys

from PyQt5.QtWidgets import QApplication

 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


from cnu_new.src.manager import SlotsBuilder, ThreadsBuilder
from cnu_new.src.mainwindow import MainWindow
from cnu_new.src.Ui_Window import Ui_MainWindow


def main():
    app = QApplication(sys.argv)

    ui = Ui_MainWindow()
    main_window = MainWindow(ui)
    main_window.slot_builder = SlotsBuilder(ui, main_window)
    main_window.thread_builder = ThreadsBuilder()
    main_window.bind()
    main_window.show()

    app.exit(app.exec_())


if __name__ == '__main__':
    main()
