import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, QHBoxLayout, \
    QComboBox
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
import subprocess
import os
import signal
import platform


class ServerControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setFocus()
        self.initUI()

    def mousePressEvent(self, a0) -> None:
        self.setFocus()

    def closeEvent(self, a0) -> None:
        self.stop_server()

    def initUI(self):
        self.setGeometry(100, 100, 400, 150)
        self.setWindowTitle('Django Server Control')

        # 创建文本域控件
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)  # 将 QTextEdit 设置为只读模式

        # 选择项目路径按钮
        self.select_path_button = QPushButton('选择Django项目路径', self)
        self.select_path_button.setGeometry(50, 50, 200, 30)
        self.select_path_button.clicked.connect(self.select_project_path)

        # 选择py文件
        self.folder_combo = QComboBox(self)
        self.folder_combo.setEditable(False)
        self.folder_combo.setInsertPolicy(QComboBox.InsertAtBottom)

        # 启动服务器按钮
        self.start_button = QPushButton('启动服务器', self)
        self.start_button.setGeometry(50, 90, 100, 30)
        self.start_button.clicked.connect(self.start_server)
        self.start_button.setEnabled(False)  # 初始禁用启动按钮

        # 关闭服务器按钮
        self.stop_button = QPushButton('关闭服务器', self)
        self.stop_button.setGeometry(200, 90, 100, 30)
        self.stop_button.clicked.connect(self.stop_server)
        self.stop_button.setEnabled(False)  # 初始禁用关闭按钮

        # 将按钮放置在水平布局中
        hbox = QHBoxLayout()
        hbox.addWidget(self.select_path_button)
        hbox.addWidget(self.folder_combo)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.start_button)
        hbox2.addWidget(self.stop_button)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.text_edit)

        # 将水平布局放置在垂直布局中
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        self.setLayout(vbox)

        # 保存Django项目路径
        self.project_path = None

        # 进程服务
        self.server_process = None

    def select_project_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.DirectoryOnly
        project_path = QFileDialog.getExistingDirectory(self, "选择Django项目路径", options=options)
        if project_path:
            self.project_path = project_path
            self.start_button.setEnabled(True)  # 启用启动按钮
            self.stop_button.setEnabled(True)  # 启用关闭按钮
            self.populate_file_list(project_path)

    def populate_file_list(self, folder):
        self.folder_combo.clear()
        self.folder_combo.addItem("选择运行文件")
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith('.py'):
                    self.folder_combo.addItem(file)

    def start_server(self):
        if self.folder_combo.currentText() == "选择运行文件":
            format = QTextCharFormat()
            format.setForeground(QColor("red"))
            self.text_edit.textCursor().insertText("运行文件未选择\n", format)
            return False
        if self.project_path:
            if self.server_process is None:
                # 启动Django开发服务器，使用用户提供的项目路径
                try:
                    if platform.system() == 'Windows':
                        # Windows系统下使用start启动新进程，并将进程设置为一个新的进程组
                        self.server_process = subprocess.Popen(
                            ['python', os.path.join(self.project_path, self.folder_combo.currentText()), 'runserver'],
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                        )
                    else:
                        self.server_process = subprocess.Popen(
                            ['python', os.path.join(self.project_path, self.folder_combo.currentText()), 'runserver'],
                            preexec_fn=os.setpgrp  # 分离服务器进程
                        )

                    # 检查运行是否成功
                    if self.server_process.returncode != 0:
                        format = QTextCharFormat()
                        format.setForeground(QColor("bleak"))
                        self.text_edit.textCursor().insertText(self.folder_combo.currentText() + "文件运行成功\n",
                                                               format)
                    else:
                        format = QTextCharFormat()
                        format.setForeground(QColor("bleak"))
                        self.text_edit.textCursor().insertText(self.folder_combo.currentText() + "文件运行失败\n",
                                                               format)
                except Exception as e:
                    format = QTextCharFormat()
                    format.setForeground(QColor("red"))
                    self.text_edit.textCursor().insertText("Error：" + str(e) + "\n", format)
            else:
                format = QTextCharFormat()
                format.setForeground(QColor("bleak"))
                self.text_edit.textCursor().insertText("django已运行\n", format)
        else:
            # 如果未选择项目路径，显示错误消息或采取其他操作
            format = QTextCharFormat()
            format.setForeground(QColor("bleak"))
            self.text_edit.textCursor().insertText("项目路径未选择\n", format)

    def stop_server(self):
        if self.project_path:
            if self.server_process is not None:
                try:
                    if platform.system() == 'Windows':
                        # Windows系统下使用taskkill命令杀死服务器进程及其子进程
                        result = subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.server_process.pid)])

                    else:
                        # 其他系统发送SIGTERM信号给服务器进程
                        self.server_process.terminate()
                        result = self.server_process.returncode

                    if result.returncode == 0:
                        format = QTextCharFormat()
                        format.setForeground(QColor("bleak"))
                        self.text_edit.textCursor().insertText("结束成功 pid为：" + str(self.server_process.pid) + "\n",
                                                               format)
                        self.server_process = None
                    else:
                        format = QTextCharFormat()
                        format.setForeground(QColor("bleak"))
                        self.text_edit.textCursor().insertText("结束失败 pid为：" + str(self.server_process.pid) + "\n",
                                                               format)
                        self.text_edit.append("结束 pid为：" + str(self.server_process.pid))
                        print("结束失败 pid为：", self.server_process.pid)
                except Exception as e:
                    format = QTextCharFormat()
                    format.setForeground(QColor("red"))
                    self.text_edit.textCursor().insertText("Error：" + str(e), format)
            else:
                format = QTextCharFormat()
                format.setForeground(QColor("bleak"))
                self.text_edit.textCursor().insertText("无进程", format)
        else:
            # 如果未选择项目路径，显示错误消息或采取其他操作
            format = QTextCharFormat()
            format.setForeground(QColor("bleak"))
            self.text_edit.textCursor().insertText("项目路径未选择\n", format)


def main():
    app = QApplication(sys.argv)
    window = ServerControlApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

