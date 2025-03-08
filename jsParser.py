import re
from html.parser import HTMLParser

class JsParser:
    def metinleri_getir(self, veri, baslangic_metni, bitis_metni):
        baslangic_index = veri.find(baslangic_metni)
        bitis_index = veri.find(bitis_metni, baslangic_index)

        if baslangic_index == -1 or bitis_index == -1:
            return ""

        baslangic_position = baslangic_index + len(baslangic_metni)
        uzunluk = bitis_index - baslangic_position
        return veri[baslangic_position:baslangic_position + uzunluk]

    def parseFunction(self, inputstr, linename):
        line_pattern = f"<strong>{linename}:</strong>([^<]*)"
        
        line_matches = re.findall(line_pattern, inputstr, re.DOTALL)
        
        funcpars = []
        for match in line_matches:
            line_content = match.strip()
            funcpars.append(line_content)
        
        return "\n".join(funcpars)

    def hostname(self, inputstr):
        pattern = "<td class=\"value\">"
        index = inputstr.find(pattern)
        if index == -1:
            return None

        index += len(pattern)

        start_index = inputstr.find('\n', index)
        if start_index == -1:
            return None

        end_index = inputstr.find('\n', start_index + 1)
        if end_index == -1:
            end_index = len(inputstr)

        next_line = inputstr[start_index + 1:end_index].strip()
        kelimeler = next_line.split(' ')
        host1 = kelimeler[-1]
        host = host1.split('/')
        hostname = host[0]
        ip = host[1]

        return hostname

    def fileScanEntryParse(self, inputstr):
        entry_pattern = "<ul class=\"match-strings\">.*?<\\/ul>"
        entry_matches = re.findall(entry_pattern, inputstr, re.DOTALL)
        entry_match_strings = [match for match in entry_matches]
        entry_join = "\n".join(entry_match_strings)

        class MyHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []

            def handle_data(self, data):
                self.text.append(data)

        parser = MyHTMLParser()
        parser.feed(entry_join)
        cleaned_html = ''.join(parser.text)
        return cleaned_html
