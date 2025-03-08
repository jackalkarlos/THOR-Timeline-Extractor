from datetime import datetime

class DateConverter:
    @staticmethod
    def ConvertDate(input_date):
        input_formats = [
            "%a %b %d %H:%M:%S.%f %Y",
            "%a %b %d %H:%M:%S %Y",
            "%a %b %d %H:%M:%S.%f %Y",
        ]

        for fmt in input_formats:
            try:
                datetime_obj = datetime.strptime(input_date, fmt)
                output_format = "%d/%m/%Y %H:%M:%S"
                return datetime_obj.strftime(output_format)
            except ValueError:
                continue

        return "Geçersiz format"
