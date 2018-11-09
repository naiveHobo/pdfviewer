# PDFViewer
PDFViewer is a GUI tool, written using python3 and tkinter, which lets you view PDF documents.

## Installation
To install PDFViewer along with the dependencies:
```
sudo apt install python3-tk
sudo apt install tesseract-ocr

git clone https://github.com/naiveHobo/pdfviewer.git

cd pdfviewer/

sudo pip3 install .
```

## Instructions
To start PDFViewer:
```
from tkinter import Tk
from pdfviewer import PDFViewer


root = Tk()
PDFViewer()
root.mainloop()
```

## Dependencies

```
python3
tkinter
pdfplumber
PyPDF2
pytesseract
tesseract-ocr
Pillow
```
