from PyQt5.QtWidgets import QApplication, QFileDialog
from openpyxl import Workbook
from openpyxl.styles import Font
from datetime import datetime

class BuildExcelFile:
    @staticmethod
    def buildExcel(table):
        file_path, _ = QFileDialog.getSaveFileName(
            None,  
            "Save The Excel File", 
            "",
            "Excel Files (*.xlsx)"
        )

        if file_path:
            valid_items = []
            invalid_items = []

            for i in range(table.rowCount()):
                item = table.item(i, 0)
                try:
                    datetime.strptime(item.text(), "%d.%m.%Y %H:%M:%S")
                    valid_items.append(i)
                except ValueError:
                    invalid_items.append(i)

            valid_items.sort(key=lambda x: datetime.strptime(table.item(x, 0).text(), "%d.%m.%Y %H:%M:%S"))

            sorted_items = valid_items + invalid_items

            wb = Workbook()
            ws = wb.active
            ws.title = "Timeline"

            ws.append(["Time", "Activity", "Hostname", "Source", "Note"])

            for row in sorted_items:
                row_data = [table.item(row, col).text() for col in range(table.columnCount())]
                ws.append(row_data)

            for row in ws.iter_rows():
                for cell in row:
                    cell.font = Font(name="Ubuntu", size=12)

            wb.save(file_path)
