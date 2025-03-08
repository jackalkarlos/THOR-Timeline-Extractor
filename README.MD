
# THOR Timeline Extractor ⚔️

  

⚠️ **Important Notice**: This is a demo version of the software. Please ensure you keep backup copies of all reports before processing. The application may crash unexpectedly as it's still in development. Always work with copies of your original reports to prevent any data loss.

  

⚠️ **Önemli Uyarı**: Bu yazılımın demo versiyonudur. İşlem yapmadan önce tüm raporların yedek kopyalarını sakladığınızdan emin olun. Uygulama beklenmedik şekilde çökebilir çünkü hala geliştirme aşamasındadır. Herhangi bir veri kaybını önlemek için orijinal raporlarınızın kopyaları üzerinde çalışın.

  

⚠️ **Lite Version Incompatibility**: This version is not compatible with THOR Lite reports. If you need support for THOR Lite reports, please request it and it will be added in future updates.

  

⚠️ **Lite Sürüm Uyumsuzluğu**: Bu sürüm THOR Lite raporları ile uyumlu değildir. THOR Lite raporları için destek talep ederseniz, gelecek güncellemelerde eklenecektir.


  

## 📝 Description

  

THOR Timeline Extractor is a tool that allows analysts to automatically process THOR APT Scanner reports and create a timeline. The tool extracts data from HTML reports and exports it to Excel in a format that analysts can easily understand.

![GUI](https://github.com/jackalkarlos/THOR-Timeline-Extractor/blob/main/images/main.png?raw=true)

  

## 🚀 Features

  

-  **Handling HTML Reports**: Automatically processes Thor reports and extracts data.

  

-  **Export to Excel**: Exports the generated timesheet to Excel file.

  

-  **Module Supports**: Includes special support for Windows and Linux modules.

  

-  **JS Injection**: Makes reports more interactive by injecting JS into HTML files.

  
  

## 🛠️ Installation

  

You can find pre-compiled versions of the program in the Releases section. If you want to compile the program yourself or run it from code, just install the requirements and run the “main.py” file.

  

1.  **Requirements**:

  

`pip3 install -r requirements.txt`

`python3 main.py`

  
  

## 🖥️ Usage

1.  **GUI**:

- When the program is started, the analyst name and the operating system of the reports to be read are selected on the left panel. If you are going to read a Windows report, you should check Windows. If the operating system you are looking at changes during the analysis, simply change the selection through the program. You do not need to start the program again.

- Start the HTTP Server with "Start" button. It will work on 8171 port. **You may need to define permissions to the port through the firewall or you may need to ask your IT to define permissions (for EDR products)**

- Select the folder where the reports are located with the “Select Folder” button.

- With the “Inject” button, JS injection is made to HTML files. **Note that these files are irreversible and you should work on non-original copies. You should only select a folder with THOR reports, the developer is "not responsible" if the files in the folder are corrupted.**

![GUI](https://github.com/jackalkarlos/THOR-Timeline-Extractor/blob/main/images/info.png?raw=true)


- Open the report to be analyzed, there should be an “Add To List” button to the left of each alarm. You can add the alarms you want to the program by clicking on the relevant button.

![GUI](https://github.com/jackalkarlos/THOR-Timeline-Extractor/blob/main/images/alert.png?raw=true)

 
- When your list is ready, you can export the activity list to Excel document using the “Export Activity List to Excel” button.

- If you want, you can change the image that appears in the interface by changing the image.png.
  
  

## 📂 Struct

  

-  **main.py**: Main program file.

-  **jsParser.py**: Class that handles HTML reports.

-  **buildexcel.py**: Class that creates an Excel file.

-  **dateconverter.py**: Class that converts date formats.

-  **windows.json**: Definitions for Windows modules.

-  **linux.json**: Definitions for Linux modules.

## 📜 Lisence

This project is licensed under the MIT license.

## _🛠️_ PR & Fix

You can submit a “Pull Request” to submit an enhancement to the project. You can be sure that I will accept it unconditionally due to my laziness.
