import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFrame, QLabel, QPushButton,
    QLineEdit, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QSpacerItem, QSizePolicy, QMessageBox, QDialog, QFileDialog, QRadioButton
)
from PyQt5.QtCore import Qt, QDateTime, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from jsParser import JsParser
from dateconverter import DateConverter
from buildexcel import BuildExcelFile
import http.server
import json
from datetime import datetime
import re

class ServerThread(QThread):
    data_received = pyqtSignal(str)  # Veri alındığında sinyal gönder

    def run(self):
        server_address = ('', 8171)
        httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)
        httpd.main_window = self  # Thread'i main_window olarak ata
        httpd.serve_forever()

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(content_length).decode('utf-8')
        
        # Ana thread'e veriyi sinyal ile gönder
        self.server.main_window.data_received.emit(request_body)
        
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response_message = json.dumps({"message": "Veri Alindi"})
        self.wfile.write(response_message.encode('utf-8'))

    def log_message(self, format, *args):
        return
    
class EditDialog(QDialog):
    def __init__(self, current_data):
        super().__init__()
        self.setWindowTitle("Edit")
        self.setGeometry(100, 100, 300, 200)

        self.layout = QVBoxLayout()
        self.input_fields = []

        for label in ["Time", "Activity", "Hostname", "Source", "Note"]:
            field_layout = QHBoxLayout()
            field_label = QLabel(label)
            field_input = QLineEdit(current_data[label])
            field_layout.addWidget(field_label)
            field_layout.addWidget(field_input)
            self.layout.addLayout(field_layout)
            self.input_fields.append(field_input)

        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_data)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_data(self):
        self.accept()

    def get_data(self):
        return [field.text() for field in self.input_fields]

class ManualAddDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manual Ekleme")
        self.setGeometry(100, 100, 300, 200)

        self.layout = QVBoxLayout()
        self.input_fields = []

        for label in ["Edit", "Activity", "Hostname", "Source", "Note"]:
            field_layout = QHBoxLayout()
            field_label = QLabel(label)
            field_input = QLineEdit()
            field_layout.addWidget(field_label)
            field_layout.addWidget(field_input)
            self.layout.addLayout(field_layout)
            self.input_fields.append(field_input)

        self.add_button = QPushButton("Ekle")
        self.add_button.clicked.connect(self.add_data)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def add_data(self):
        self.accept()

    def get_data(self):
        return [field.text() for field in self.input_fields]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('favicon.ico'))  # Favicon'u ayarla

        self.setWindowTitle("Thor To Timeline - Timeline Extractor (Made by. Mehmet Demir)")
        self.setGeometry(100, 100, 1600, 800)

        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: rgb(46, 51, 73);")
        self.frame.setGeometry(0, 0, self.width(), self.height())

        self.left_panel = QFrame(self)
        self.left_panel.setStyleSheet("background-color: rgb(30, 35, 50);")
        self.left_panel.setGeometry(0, 0, int(self.width() * 0.2), self.height())

        left_layout = QVBoxLayout(self.left_panel)

        self.image_label = QLabel(self)
        left_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        self.text_label = QLabel("Hello, Analyst", self)
        self.text_label.setStyleSheet("color: white; font-size: 22px; margin-top: 20px;")
        left_layout.addWidget(self.text_label, alignment=Qt.AlignCenter)

        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        radio_layout = QVBoxLayout()
        self.windows_radio = QRadioButton("Windows", self)
        self.linux_radio = QRadioButton("Linux", self)
        self.windows_radio.setStyleSheet("color: white; font-size: 11px;")
        self.linux_radio.setStyleSheet("color: white; font-size: 11px;")
        self.windows_radio.setChecked(True)
        radio_layout.addWidget(self.windows_radio, alignment=Qt.AlignCenter)
        radio_layout.addWidget(self.linux_radio, alignment=Qt.AlignCenter)
        left_layout.addLayout(radio_layout)

        self.selected_os = "Windows"
        self.windows_radio.toggled.connect(self.update_selected_os)
        self.linux_radio.toggled.connect(self.update_selected_os)

        button_style = "background-color: rgb(60, 65, 85); color: white; font-size: 11px; padding: 10px;"
        self.button1 = QPushButton("Export Activity List to Excel", self)
        self.button1.clicked.connect(self.exceleaktar)
        self.button1.setStyleSheet(button_style)
        left_layout.addWidget(self.button1, alignment=Qt.AlignCenter)


        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Analyst Name")
        self.text_input.setStyleSheet("background-color: rgb(60, 65, 85); color: white; font-size: 16px; margin-top: 20px; padding: 10px;")
        left_layout.addWidget(self.text_input, alignment=Qt.AlignCenter)
        self.text_input.setFixedWidth(int(self.left_panel.width() * 0.8))
        self.text_input.textChanged.connect(self.update_greeting)

        self.right_panel = QFrame(self)
        self.right_panel.setGeometry(int(self.width() * 0.2), 0, int(self.width() * 0.8), self.height())

        right_layout = QVBoxLayout(self.right_panel)

        top_layout = QHBoxLayout()
        left_box = QFrame(self)
        left_box.setStyleSheet("background-color: rgb(60, 65, 85); padding: 15px; border: 2px solid white;")
        left_box.setFixedSize(350, 220)
        left_box_layout = QVBoxLayout(left_box)
        left_box_layout.addWidget(QLabel("HTML to App Server 8171", self, styleSheet="color: white; font-size: 16px; border: none;"), alignment=Qt.AlignCenter)

        self.server_status_label = QLabel("Server Status: Stopped", self)
        self.server_status_label.setStyleSheet("color: white; font-size: 16px; border: none;")
        left_box_layout.addWidget(self.server_status_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start", self)
        self.start_button.setStyleSheet(button_style)
        self.start_button.clicked.connect(self.start_server)
        button_layout.addWidget(self.start_button, alignment=Qt.AlignLeft)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setStyleSheet(button_style)
        self.stop_button.clicked.connect(self.stop_server)
        button_layout.addWidget(self.stop_button, alignment=Qt.AlignRight)

        left_box_layout.addLayout(button_layout)
        top_layout.addWidget(left_box)

        center_layout = QVBoxLayout()
        self.runtime_label = QLabel("Program Run Time: 00:00:00", self)
        self.runtime_label.setStyleSheet("color: white; font-size: 20px;")
        center_layout.addWidget(self.runtime_label, alignment=Qt.AlignCenter)

        self.datetime_label = QLabel(QDateTime.currentDateTime().toString(), self)
        self.datetime_label.setStyleSheet("color: white; font-size: 20px;")
        center_layout.addWidget(self.datetime_label, alignment=Qt.AlignCenter)

        top_layout.addLayout(center_layout)

        right_box = QFrame(self)
        right_box.setStyleSheet("background-color: rgb(60, 65, 85); padding: 15px; border: 2px solid white;")
        right_box.setFixedSize(350, 220)
        right_box_layout = QVBoxLayout(right_box)
        right_box_layout.addWidget(QLabel("JS Injection", self, styleSheet="color: white; font-size: 16px; border: none;"), alignment=Qt.AlignCenter)

        self.folder_path_label = QLabel("Folder Path: ", self)
        self.folder_path_label.setStyleSheet("color: white; font-size: 8px;")
        right_box_layout.addWidget(self.folder_path_label, alignment=Qt.AlignCenter)

        right_button_layout = QHBoxLayout()
        self.select_button = QPushButton("Select Folder", self)
        self.select_button.setStyleSheet(button_style)
        self.select_button.clicked.connect(self.select_folder)
        right_button_layout.addWidget(self.select_button, alignment=Qt.AlignLeft)

        self.inject_button = QPushButton("Inject", self)
        self.inject_button.setStyleSheet(button_style)
        self.inject_button.clicked.connect(self.inject_js)
        right_button_layout.addWidget(self.inject_button, alignment=Qt.AlignRight)

        right_box_layout.addLayout(right_button_layout)
        top_layout.addWidget(right_box)

        right_layout.addLayout(top_layout)

        self.table = QTableWidget(self)
        self.table.setRowCount(0)
        self.table.setWordWrap(True)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Activity", "Hostname", "Source", "Note"])
        self.table.setStyleSheet("background-color: rgba(211, 221, 229, 255); gridline-color: white; font-size: 14px;")
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnWidth(0, int(self.right_panel.width() * 0.15))
        self.table.setColumnWidth(1, int(self.right_panel.width() * 0.50))
        self.table.setColumnWidth(2, int(self.right_panel.width() * 0.15))
        self.table.setColumnWidth(3, int(self.right_panel.width() * 0.10))
        self.table.setColumnWidth(4, int(self.right_panel.width() * 0.10))


        right_layout.addWidget(self.table)

        bottom_layout = QHBoxLayout()
        delete_button = QPushButton("Delete Selected Activity", self)
        delete_button.setStyleSheet(button_style)
        delete_button.clicked.connect(self.delete_selected_activity)
        bottom_layout.addWidget(delete_button)

        edit_button = QPushButton("Edit", self)
        edit_button.setStyleSheet(button_style)
        edit_button.clicked.connect(self.open_edit_dialog)
        bottom_layout.addWidget(edit_button)

        manual_add_button = QPushButton("Manual Addition", self)
        manual_add_button.setStyleSheet(button_style)
        manual_add_button.clicked.connect(self.open_manual_add_dialog)
        bottom_layout.addWidget(manual_add_button)

        exit_button = QPushButton("Exit", self)
        exit_button.setStyleSheet("background-color: red; color: white; font-size: 11px; padding: 10px;")
        exit_button.clicked.connect(self.close)
        bottom_layout.addWidget(exit_button)

        right_layout.addLayout(bottom_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

        self.runtime_timer = QTimer(self)
        self.runtime_timer.timeout.connect(self.update_runtime)
        self.runtime_timer.start(1000)
        self.start_time = QDateTime.currentDateTime()

        self.server_thread = ServerThread()
        self.server_thread.data_received.connect(self.jsParse)  # Sinyali bağla
        self.server_thread.start()

        self.selected_folder_path = ""

        self.jsParser = JsParser()

        self.httpServer = SimpleHTTPRequestHandler

    def update_greeting(self):
        name = self.text_input.text()
        self.text_label.setText(f"Hello, {name}" if name else "Hello, Analyst")

    def update_datetime(self):
        self.datetime_label.setText(QDateTime.currentDateTime().toString())

    def exceleaktar(self):
        BuildExcelFile.buildExcel(self.table)

    def update_runtime(self):
        elapsed_time = self.start_time.secsTo(QDateTime.currentDateTime())
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.runtime_label.setText(f"Program Running Time: {hours:02}:{minutes:02}:{seconds:02}")

    def start_server(self):
        self.server_status_label.setText("Server Status: Running")
        if self.server_thread is None:
            self.server_thread = threading.Thread(target=self.run_server, daemon=True)
            self.server_thread.start()

    def stop_server(self):
        if self.server_thread is not None:
            self.server_status_label.setText("Server Status: Stopped")
            self.server_thread = None

    def delete_selected_activity(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            self.table.removeRow(selected_row)

    def open_edit_dialog(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            current_data = {
                "Time": self.table.item(selected_row, 0).text(),
                "Activity": self.table.item(selected_row, 1).text(),
                "Hostname": self.table.item(selected_row, 2).text(),
                "Source": self.table.item(selected_row, 3).text(),
                "Note": self.table.item(selected_row, 4).text(),
            }
            dialog = EditDialog(current_data)
            if dialog.exec_() == QDialog.Accepted:
                new_data = dialog.get_data()
                for i, value in enumerate(new_data):
                    self.table.setItem(selected_row, i, QTableWidgetItem(value))

    def open_manual_add_dialog(self):
        dialog = ManualAddDialog()
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            self.table.insertRow(self.table.rowCount())
            for i, value in enumerate(new_data):
                self.table.setItem(self.table.rowCount() - 1, i, QTableWidgetItem(value))

    def select_folder(self):
        QMessageBox.information(self, "Information", "Injected files cannot be reverted in any way. The folder you select should only contain a copy of the relevant reports. Original copies or folders with other files should not be processed.")
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.selected_folder_path = folder_path  # Global değişkene ata
            self.folder_path_label.setText(f"Folder Path: {self.selected_folder_path}")  # Etiketi güncelle

    def inject_js(self):
        #bunu bu şekilde yaptığım için bana küfrettiğinizi biliyorum <3
        pattern = '-key">'
        pattern2="-key'>"
        pattern3="ajax.googleapis.com"
        replacement_pattern = '-key"><strong><button style=\"background-color: #4CAF50; /* Yeşil */\n  border: none;\n  color: white;\n  padding: 15px 32px;\n  text-align: center;\n  text-decoration: none;\n  display: inline-block;\n  font-size: 16px;\n  margin: 4px 2px;\n  cursor: pointer;\n  border-radius: 10px;\n  box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19);\" onclick=\"uniqthortoofficefunction(this)\">Add To List\n  </button><br/>\n'
        replacement_pattern2 = "-key'><strong><button style=\"background-color: #4CAF50; /* Yeşil */\n  border: none;\n  color: white;\n  padding: 15px 32px;\n  text-align: center;\n  text-decoration: none;\n  display: inline-block;\n  font-size: 16px;\n  margin: 4px 2px;\n  cursor: pointer;\n  border-radius: 10px;\n  box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19);\" onclick=\"uniqthortoofficefunction(this)\">Add To List\n  </button><br/>\n"

        if hasattr(self, 'selected_folder_path') and self.selected_folder_path:
            import os
            for root, dirs, files in os.walk(self.selected_folder_path):
                for file in files:
                    if file.endswith(".html"):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()

                        last_script_index = html_content.rfind("</script>")
                        if last_script_index != -1:
                            if "uniqthortoofficefunction" not in html_content:
                                new_html_content = html_content[:last_script_index] + """
function uniqthortoofficefunction(button) {
    var trElement = button.closest('tr');
    var trHtml = trElement.outerHTML.trim();

    var formData = new FormData();
    formData.append('tr', trHtml);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:8171", true);

    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                console.log('Response:', xhr.responseText);
            } else {
                console.error('There was a problem with the POST request:', xhr.statusText);
            }
        }
    };
    xhr.send(formData);
}
""" + html_content[last_script_index:]

                                new_html_content = new_html_content.replace(pattern, replacement_pattern)
                                new_html_content = new_html_content.replace(pattern2, replacement_pattern2)

                                # pattern3, pattern4 veya pattern5 içeren satırları sil, google csp bypass, thor lite'da oluyor
                                lines = new_html_content.splitlines()
                                filtered_lines = [
                                    line for line in lines
                                    if not (re.search(pattern3, line))
                                ]
                                new_html_content = "\n".join(filtered_lines)

                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(new_html_content)
                            else:
                                QMessageBox.information(self, "Information", f"{file_path} file has already been processed, or there is an error. Upload the original file.")
        else:
            QMessageBox.warning(self, "Uyarı", "Please select a folder first.")

    def update_selected_os(self):
        if self.windows_radio.isChecked():
            self.selected_os = "Windows"
        elif self.linux_radio.isChecked():
            self.selected_os = "Linux"

    def resizeEvent(self, event):
        self.frame.setGeometry(0, 0, self.width(), self.height())
        self.left_panel.setGeometry(0, 0, int(self.width() * 0.2), self.height())
        self.right_panel.setGeometry(int(self.width() * 0.2), 0, int(self.width() * 0.8), self.height())

        pixmap = QPixmap('resim.png').scaled(self.left_panel.width(), self.left_panel.width(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.table.setColumnWidth(4, int(self.right_panel.width() * 0.10))
        super().resizeEvent(event)

    def jsParse(self, inputstr):
        import json
        from datetime import datetime

        with open("windows.json", "r") as f:
            windowsJsonData = f.read()
        windowsModules = json.loads(windowsJsonData)
        with open("linux.json", "r") as f:
            linuxJsonData = f.read()
        linuxModules = json.loads(linuxJsonData)

        moduleName = self.jsParser.parseFunction(inputstr, "MODULE")
        message = self.jsParser.parseFunction(inputstr, "MESSAGE")
        formattedDateTime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        isFound = False
        messageFound = False

        if self.selected_os == "Windows":
            for module in windowsModules["WindowsModules"]:
                if module["name"].strip().lower() in moduleName.lower().strip():
                    isFound = True
                    for condition in module["conditions"]:
                        if condition["messageContains"] in message:
                            messageFound = True
                            parameters = condition["parameters"]

                            for i in range(len(parameters)):
                                param_type = parameters[i][1]
                                if "date" in param_type:
                                    result = DateConverter.ConvertDate(self.jsParser.parseFunction(inputstr, parameters[i][0]).strip())
                                    parameters[i][0] = result
                                elif "normal" in param_type:
                                    result = self.jsParser.parseFunction(inputstr, parameters[i][0])
                                    parameters[i][0] = result
                                elif "hostname" in param_type:
                                    result = self.jsParser.hostname(inputstr)
                                    parameters[i][0] = result
                                elif "datenow" in param_type:
                                    result = formattedDateTime
                                    parameters[i][0] = result
                                elif param_type == "filescanentry":
                                    result = self.jsParser.fileScanEntryParse(inputstr)
                                    parameters[i][0] = result

                            # Tabloya ekle
                            self.table.insertRow(self.table.rowCount())
                            for j in range(5):
                                self.table.setItem(self.table.rowCount() - 1, j, QTableWidgetItem(parameters[j][0]))
                                self.table.resizeColumnsToContents()

            if not messageFound or not isFound:
                QMessageBox.information(self, "Information", "The module is not supported yet. If you send the report with the related alarm or alert to mdmrrr.34@gmail.com or create an Issue on Github, we can update the app.")
                print(inputstr)
        elif self.selected_os == "Linux":
            for module in linuxModules["LinuxModules"]:
                if module["name"].strip().lower() in moduleName.lower().strip():
                    isFound = True
                    for condition in module["conditions"]:
                        if condition["messageContains"] in message:
                            messageFound = True
                            parameters = condition["parameters"]
                            for i in range(len(parameters)):
                                param_type = parameters[i][1]
                                if "date" in param_type:
                                    result = DateConverter.ConvertDate(self.jsParser.parseFunction(inputstr, parameters[i][0]).strip())
                                    parameters[i][0] = result
                                elif "normal" in param_type:
                                    result = self.jsParser.parseFunction(inputstr, parameters[i][0])
                                    parameters[i][0] = result
                                elif "hostname" in param_type:
                                    result = self.jsParser.hostname(inputstr)
                                    parameters[i][0] = result
                                elif "datenow" in param_type:
                                    result = formattedDateTime
                                    parameters[i][0] = result
                                elif param_type == "filescanentry":
                                    result = self.jsParser.fileScanEntryParse(inputstr)
                                    parameters[i][0] = result

                            self.table.insertRow(self.table.rowCount())
                            for j in range(5):
                                self.table.setItem(self.table.rowCount() - 1, j, QTableWidgetItem(parameters[j][0]))

            if not messageFound or not isFound:
                QMessageBox.information(self, "Bilgi", "The module is not supported yet. If you send the report with the related alarm or alert to mdmrrr.34@gmail.com or create an Issue on Github, we can update the app.")

        else:
            QMessageBox.warning(self, "Uyarı", "Please select the operating system type of the processed report from the application interface.")

    def run_server(self):
        server_address = ('', 8171)
        httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)
        httpd.main_window = self
        self.server_status_label.setText("Server Status: Running")
        httpd.serve_forever()

    def sirala(self):
        rows = []
        for i in range(self.table.rowCount()):
            time_item = self.table.item(i, 0)
            if time_item:
                try:
                    time_value = datetime.strptime(time_item.text(), "%d.%m.%Y %H:%M:%S")
                    rows.append((time_value, i))
                except ValueError:
                    rows.append((None, i)) 

        rows.sort(key=lambda x: x[0] if x[0] is not None else datetime.max)

        sorted_rows = [row[1] for row in rows]

        for i, row_index in enumerate(sorted_rows):
            for col in range(self.table.columnCount()):
                item = self.table.takeItem(row_index, col)
                self.table.setItem(i, col, item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
