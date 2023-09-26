import sys
import win32gui
import win32con
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QListWidget, QVBoxLayout, QWidget, QHBoxLayout


class TopMostWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Window Manager')
        self.setGeometry(100, 100, 400, 300)

        # 创建Qt界面元素
        self.list_widget = QListWidget()
        self.list_widget_on = QListWidget()
        self.button_set_topmost = QPushButton('顶置窗口')
        self.button_unset_topmost = QPushButton('取消顶置窗口')
        self.button_refresh = QPushButton('刷新')

        # 布局
        layout = QVBoxLayout()  # 垂直布局

        h = QHBoxLayout()  # 水平布局

        # 未顶置局部控件
        w_no = QVBoxLayout()  # 垂直布局
        w_no.addWidget(self.list_widget)
        w_no.addWidget(self.button_set_topmost)
        h.addLayout(w_no)

        # 顶置局部控件
        w_yes = QVBoxLayout()  # 垂直布局
        w_yes.addWidget(self.list_widget_on)
        w_yes.addWidget(self.button_unset_topmost)
        h.addLayout(w_yes)

        layout.addLayout(h)
        layout.addWidget(self.button_refresh)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # 连接按钮点击事件
        self.button_set_topmost.clicked.connect(self.set_selected_window_topmost)
        self.button_unset_topmost.clicked.connect(self.unset_selected_window_topmost)
        self.button_refresh.clicked.connect(self.refresh_window_list)

        # 填充列表框
        self.refresh_window_list()

    def refresh_window_list(self):
        # 清空列表框
        self.list_widget.clear()
        self.list_widget_on.clear()

        # 获取所有顶级窗口
        top_windows = []
        win32gui.EnumWindows(lambda hwnd, top_windows: top_windows.append(hwnd), top_windows)

        # 获取任务栏和托盘程序的窗口以及已顶置的窗口
        taskbar_and_tray_windows = []
        topmost_windows = []
        for hwnd in top_windows:
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text != "":
                    if win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOPMOST:
                        topmost_windows.append((hwnd, window_text))
                    else:
                        taskbar_and_tray_windows.append((hwnd, window_text))

        # 添加窗口信息到列表框中
        for hwnd, window_text in taskbar_and_tray_windows:
            self.list_widget.addItem(f'{window_text} (HWND: {hwnd})')
        for hwnd, window_text in topmost_windows:
            self.list_widget_on.addItem(f'{window_text} (HWND: {hwnd}) - 已顶置')

    def set_selected_window_topmost(self):
        # 获取用户选择的项目
        selected_item = self.list_widget.currentItem()
        if selected_item:
            selected_text = selected_item.text()

            # 从选择的项目中提取窗口句柄
            hwnd = int(selected_text.split('(HWND: ')[1].split(')')[0])

            # 将窗口设置为顶置
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)

    def unset_selected_window_topmost(self):
        # 获取用户选择的项目
        selected_item = self.list_widget_on.currentItem()
        if selected_item:
            selected_text = selected_item.text()

            # 从选择的项目中提取窗口句柄
            hwnd = int(selected_text.split('(HWND: ')[1].split(')')[0])

            # 取消窗口顶置
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TopMostWindow()
    window.show()
    sys.exit(app.exec_())

