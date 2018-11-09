import io
import pdfplumber
import PyPDF2
import pytesseract
from tkinter import *
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image

from pdfviewer.config import *
from pdfviewer.hoverbutton import HoverButton
from pdfviewer.helpbox import HelpBox
from pdfviewer.menubox import MenuBox
from pdfviewer.display_canvas import DisplayCanvas


class PDFViewer(Frame):

    def __init__(self, master=None, **kw):
        Frame.__init__(self, master, **kw)
        self.pdf = None
        self.page = None
        self.paths = list()
        self.pathidx = -1
        self.total_pages = 0
        self.pageidx = 0
        self.scale = 1.0
        self.rotate = 0
        self.save_path = None
        self._init_ui()

    def _init_ui(self):
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        h = hs - 100
        w = int(h / 1.414) + 100
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.master.title("PDFViewer")

        self.master.rowconfigure(0, weight=0)
        self.master.rowconfigure(0, weight=0)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)

        self.configure(bg=BACKGROUND_COLOR, bd=0)

        tool_frame = Frame(self, bg=BACKGROUND_COLOR, bd=0, relief=SUNKEN)
        pdf_frame = Frame(self, bg=BACKGROUND_COLOR, bd=0, relief=SUNKEN)

        tool_frame.grid(row=0, column=0, sticky='news')
        pdf_frame.grid(row=0, column=1, sticky='news')

        # Tool Frame
        tool_frame.columnconfigure(0, weight=1)
        tool_frame.rowconfigure(0, weight=0)
        tool_frame.rowconfigure(1, weight=1)
        tool_frame.rowconfigure(2, weight=0)
        tool_frame.rowconfigure(3, weight=2)

        options = MenuBox(tool_frame, image_path=os.path.join(ROOT_PATH, 'widgets/options.png'))
        options.grid(row=0, column=0)

        options.add_item('Open Files...', self._open_file)
        options.add_item('Open Directory...', self._open_dir, seperator=True)
        options.add_item('Next File', self._next_file)
        options.add_item('Previous File', self._prev_file, seperator=True)
        options.add_item('Help...', self._help, seperator=True)
        options.add_item('Exit', self.master.quit)

        tools = Frame(tool_frame, bg=BACKGROUND_COLOR, bd=0, relief=SUNKEN)
        tools.grid(row=2, column=0)

        HoverButton(tools, image_path=os.path.join(ROOT_PATH, 'widgets/clear.png'), command=self._clear,
                    width=50, height=50, bg=BACKGROUND_COLOR, bd=0, tool_tip="Clear",
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(pady=2)
        HoverButton(tools, image_path=os.path.join(ROOT_PATH, 'widgets/open_file.png'), command=self._open_file,
                    width=50, height=50, bg=BACKGROUND_COLOR, bd=0, tool_tip="Open Files",
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(pady=2)
        HoverButton(tools, image_path=os.path.join(ROOT_PATH, 'widgets/open_dir.png'), command=self._open_dir,
                    width=50, height=50, bg=BACKGROUND_COLOR, bd=0, tool_tip="Open Directory",
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(pady=2)
        HoverButton(tools, image_path=os.path.join(ROOT_PATH, 'widgets/search.png'), command=self._search_text,
                    width=50, height=50, bg=BACKGROUND_COLOR, bd=0, tool_tip="Search Text",
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(pady=2)
        HoverButton(tools, image_path=os.path.join(ROOT_PATH, 'widgets/extract.png'), command=self._extract_text,
                    width=50, height=50, bg=BACKGROUND_COLOR, bd=0, tool_tip="Extract Text", keep_pressed=True,
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(pady=2)
        HoverButton(tools, image_path=os.path.join(ROOT_PATH, 'widgets/ocr.png'), command=self._run_ocr,
                    width=50, height=50, bg=BACKGROUND_COLOR, bd=0, tool_tip="Run OCR",
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(pady=2)

        file_frame = Frame(tools, width=50, height=50, bg=BACKGROUND_COLOR, bd=0, relief=SUNKEN)
        file_frame.pack(pady=2)

        file_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(1, weight=1)

        HoverButton(file_frame, image_path=os.path.join(ROOT_PATH, 'widgets/prev_file.png'), command=self._prev_file,
                    width=25, height=50, bg=BACKGROUND_COLOR, bd=0, tool_tip="Previous File",
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).grid(row=0, column=0)
        HoverButton(file_frame, image_path=os.path.join(ROOT_PATH, 'widgets/next_file.png'), command=self._next_file,
                    width=25, height=50, bg=BACKGROUND_COLOR, bd=0, tool_tip="Next File",
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).grid(row=0, column=1)

        HoverButton(tool_frame, image_path=os.path.join(ROOT_PATH, 'widgets/help.png'), command=self._help,
                    width=50, height=50, bg=BACKGROUND_COLOR, bd=0, tool_tip="Help",
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).grid(row=3, column=0, sticky='s')

        # PDF Frame
        pdf_frame.columnconfigure(0, weight=1)
        pdf_frame.rowconfigure(0, weight=0)
        pdf_frame.rowconfigure(1, weight=0)

        page_tools = Frame(pdf_frame, bg=BACKGROUND_COLOR, bd=0, relief=SUNKEN)
        page_tools.grid(row=0, column=0, sticky='news')

        page_tools.rowconfigure(0, weight=1)
        page_tools.columnconfigure(0, weight=1)
        page_tools.columnconfigure(1, weight=0)
        page_tools.columnconfigure(2, weight=2)
        page_tools.columnconfigure(3, weight=0)
        page_tools.columnconfigure(4, weight=1)

        nav_frame = Frame(page_tools, bg=BACKGROUND_COLOR, bd=0, relief=SUNKEN)
        nav_frame.grid(row=0, column=1, sticky='ns')

        HoverButton(nav_frame, image_path=os.path.join(ROOT_PATH, 'widgets/first.png'),
                    command=self._first_page, bg=BACKGROUND_COLOR, bd=0,
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(side=LEFT, expand=True)
        HoverButton(nav_frame, image_path=os.path.join(ROOT_PATH, 'widgets/prev.png'),
                    command=self._prev_page, bg=BACKGROUND_COLOR, bd=0,
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(side=LEFT, expand=True)

        self.page_label = Label(nav_frame, bg=BACKGROUND_COLOR, bd=0, fg='white', font='Arial 8',
                                text="Page {} of {}".format(self.pageidx, self.total_pages))
        self.page_label.pack(side=LEFT, expand=True)

        HoverButton(nav_frame, image_path=os.path.join(ROOT_PATH, 'widgets/next.png'),
                    command=self._next_page, bg=BACKGROUND_COLOR, bd=0,
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(side=LEFT, expand=True)
        HoverButton(nav_frame, image_path=os.path.join(ROOT_PATH, 'widgets/last.png'),
                    command=self._last_page, bg=BACKGROUND_COLOR, bd=0,
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(side=LEFT, expand=True)

        zoom_frame = Frame(page_tools, bg=BACKGROUND_COLOR, bd=0, relief=SUNKEN)
        zoom_frame.grid(row=0, column=3, sticky='ns')

        HoverButton(zoom_frame, image_path=os.path.join(ROOT_PATH, 'widgets/rotate.png'),
                    command=self._rotate, bg=BACKGROUND_COLOR, bd=0,
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(side=RIGHT, expand=True)
        HoverButton(zoom_frame, image_path=os.path.join(ROOT_PATH, 'widgets/fullscreen.png'),
                    command=self._fit_to_screen, bg=BACKGROUND_COLOR, bd=0,
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(side=RIGHT, expand=True)

        self.zoom_label = Label(zoom_frame, bg=BACKGROUND_COLOR, bd=0, fg='white', font='Arial 8',
                                text="Zoom {}%".format(int(self.scale * 100)))
        self.zoom_label.pack(side=RIGHT, expand=True)

        HoverButton(zoom_frame, image_path=os.path.join(ROOT_PATH, 'widgets/zoomout.png'),
                    command=self._zoom_out, bg=BACKGROUND_COLOR, bd=0,
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(side=RIGHT, expand=True)
        HoverButton(zoom_frame, image_path=os.path.join(ROOT_PATH, 'widgets/zoomin.png'),
                    command=self._zoom_in, bg=BACKGROUND_COLOR, bd=0,
                    highlightthickness=0, activebackground=HIGHLIGHT_COLOR).pack(side=RIGHT, expand=True)

        canvas_frame = Frame(pdf_frame, bg=BACKGROUND_COLOR, bd=1, relief=SUNKEN)
        canvas_frame.grid(row=1, column=0, sticky='news')

        self.canvas = DisplayCanvas(canvas_frame, page_height=h-42, page_width=w-70)
        self.canvas.pack()

        self.grid(row=0, column=0, sticky='news')

        self.master.minsize(height=h, width=w)
        self.master.maxsize(height=h, width=w)

    def _reject(self):
        if self.pdf is None:
            return
        self.pathidx = min(self.pathidx + 1, len(self.paths))
        if self.pathidx == len(self.paths):
            self._reset()
            return
        self._load_file()

    def _reset(self):
        self.canvas.clear()
        self.pdf = None
        self.page = None
        self.paths = list()
        self.pathidx = -1
        self.total_pages = 0
        self.pageidx = 0
        self.scale = 1.0
        self.rotate = 0
        self.page_label.configure(text="Page {} of {}".format(self.pageidx, self.total_pages))
        self.zoom_label.configure(text="Zoom {}%".format(int(self.scale * 100)))
        self.master.title("PDFViewer")

    def _clear(self):
        if self.pdf is None:
            return
        self.canvas.reset()
        self._update_page()

    def _zoom_in(self):
        if self.pdf is None:
            return
        if self.scale == 2.5:
            return
        self.scale += 0.1
        self._update_page()

    def _zoom_out(self):
        if self.pdf is None:
            return
        if self.scale == 0.1:
            return
        self.scale -= 0.1
        self._update_page()

    def _fit_to_screen(self):
        if self.pdf is None:
            return
        if self.scale == 1.0:
            return
        self.scale = 1.0
        self._update_page()

    def _rotate(self):
        if self.pdf is None:
            return
        self.rotate = (self.rotate - 90) % 360
        self._update_page()

    def _next_page(self):
        if self.pdf is None:
            return
        if self.pageidx == self.total_pages:
            return
        self.pageidx += 1
        self._update_page()

    def _prev_page(self):
        if self.pdf is None:
            return
        if self.pageidx == 1:
            return
        self.pageidx -= 1
        self._update_page()

    def _last_page(self):
        if self.pdf is None:
            return
        if self.pageidx == self.total_pages:
            return
        self.pageidx = self.total_pages
        self._update_page()

    def _first_page(self):
        if self.pdf is None:
            return
        if self.pageidx == 1:
            return
        self.pageidx = 1
        self._update_page()

    def _next_file(self):
        if self.pdf is None:
            return
        if self.pathidx == len(self.paths) - 1:
            messagebox.showwarning("Warning", "Reached the end of list")
            return
        self.pathidx += 1
        self._load_file()

    def _prev_file(self):
        if self.pdf is None:
            return
        if self.pathidx == 0:
            messagebox.showwarning("Warning", "Reached the end of list")
            return
        self.pathidx -= 1
        self._load_file()

    def _update_page(self):
        page = self.pdf.pages[self.pageidx - 1]
        self.page = page.to_image(resolution=int(self.scale * 80))
        image = self.page.original.rotate(self.rotate)
        self.canvas.update_image(image)
        self.page_label.configure(text="Page {} of {}".format(self.pageidx, self.total_pages))
        self.zoom_label.configure(text="Zoom {}%".format(int(self.scale * 100)))

    def _search_text(self):
        if self.pdf is None:
            return
        text = simpledialog.askstring('Search Text', 'Enter text to search:')
        if text == '' or text is None:
            return
        page = self.pdf.pages[self.pageidx - 1]
        image = page.to_image(resolution=int(self.scale * 80))
        words = [w for w in page.extract_words() if text.lower() in w['text'].lower()]
        image.draw_rects(words)
        image = image.annotated.rotate(self.rotate)
        self.canvas.update_image(image)

    def _extract_text(self):
        if self.pdf is None:
            return
        if not self.canvas.draw:
            self.canvas.draw = True
            self.canvas.configure(cursor='cross')
            return
        self.canvas.draw = False
        self.canvas.configure(cursor='')
        rect = self.canvas.get_rect()
        if rect is None:
            return
        self._clear()
        rect = self._reproject_bbox(rect)
        page = self.pdf.pages[self.pageidx - 1]
        words = page.extract_words()
        min_x = 1000000
        r = None
        for word in words:
            diff = abs(float(word['x0'] - rect[0])) + abs(float(word['top'] - rect[1])) \
                   + abs(float(word['x1'] - rect[2])) + abs(float(word['bottom'] - rect[3]))
            if diff < min_x:
                min_x = diff
                r = word
        image = page.to_image(resolution=int(self.scale * 80))
        image.draw_rect(r)
        image = image.annotated.rotate(self.rotate)
        self.canvas.update_image(image)
        simpledialog.askstring("Extract Text", "Text Extracted:", initialvalue=r['text'])

    def _reproject_bbox(self, bbox):
        bbox = [self.page.decimalize(x) for x in bbox]
        x0, y0, x1, y1 = bbox
        px0, py0 = self.page.page.bbox[:2]
        rx0, ry0 = self.page.root.bbox[:2]
        _x0 = (x0 / self.page.scale) - rx0 + px0
        _y0 = (y0 / self.page.scale) - ry0 + py0
        _x1 = (x1 / self.page.scale) - rx0 + px0
        _y1 = (y1 / self.page.scale) - ry0 + py0
        return [_x0, _y0, _x1, _y1]

    def _run_ocr(self):
        if self.pdf is None:
            return
        pdf_pages = list()
        for page in self.pdf.pages:
            image = page.to_image(resolution=100)
            pdf = pytesseract.image_to_pdf_or_hocr(image.original, extension='pdf')
            pdf_pages.append(pdf)

        pdf_writer = PyPDF2.PdfFileWriter()
        for page in pdf_pages:
            pdf = PyPDF2.PdfFileReader(io.BytesIO(page))
            pdf_writer.addPage(pdf.getPage(0))

        dirname = os.path.dirname(self.paths[self.pathidx])
        filename = os.path.basename(self.paths[self.pathidx])

        path = filedialog.asksaveasfilename(title='Save OCR As', defaultextension='.pdf',
                                            initialdir=dirname, initialfile=filename,
                                            filetypes=[('PDF files', '*.pdf'), ('all files', '.*')])
        if path == '' or path is None:
            return

        with open(path, 'wb') as out:
            pdf_writer.write(out)

        self.paths[self.pathidx] = path
        self._load_file()

    @staticmethod
    def _image_to_pdf(path):
        image = Image.open(path)
        pdf = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')

        filename = '.'.join(os.path.basename(path).split('.')[:-1]) + '.pdf'
        dirname = os.path.dirname(path)

        path = filedialog.asksaveasfilename(title='Save Converted PDF As', defaultextension='.pdf',
                                            initialdir=dirname, initialfile=filename,
                                            filetypes=[('PDF files', '*.pdf'), ('all files', '.*')])
        if path == '' or path is None:
            return
        with open(path, 'wb') as out:
            out.write(pdf)
        return path

    def _load_file(self):
        self._clear()
        path = self.paths[self.pathidx]
        filename = os.path.basename(path)
        if filename.split('.')[-1].lower() in ['jpg', 'png']:
            path = self._image_to_pdf(path)
        try:
            self.pdf = pdfplumber.open(path)
            self.total_pages = len(self.pdf.pages)
            self.pageidx = 1
            self.scale = 1.0
            self.rotate = 0
            self._update_page()
            self.master.title("PDFViewer : {}".format(path))
        except (IndexError, IOError, TypeError):
            self._reject()

    def _open_file(self):
        paths = filedialog.askopenfilenames(filetypes=[('PDF files', '*.pdf'),
                                                       ('JPG files', '*.jpg'),
                                                       ('PNG files', '*.png'),
                                                       ('all files', '.*')],
                                            initialdir=os.getcwd(),
                                            title="Select files", multiple=True)
        if not paths or paths == '':
            return
        paths = [path for path in paths if os.path.basename(path).split('.')[-1].lower() in ['pdf', 'jpg', 'png']]
        self.paths = self.paths[:self.pathidx + 1] + list(paths) + self.paths[self.pathidx + 1:]
        self.total_pages = len(self.paths)
        self.pathidx += 1
        self._load_file()

    def _open_dir(self):
        dir_name = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Directory Containing Invoices")
        if not dir_name or dir_name == '':
            return
        paths = os.listdir(dir_name)
        paths = [os.path.join(dir_name, path) for path in paths
                 if os.path.basename(path).split('.')[-1].lower() in ['pdf', 'jpg', 'png']]
        self.paths.extend(paths)
        if not self.paths:
            return
        self.total_pages = len(self.paths)
        self.pathidx += 1
        self._load_file()

    def _help(self):
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        w, h = 600, 600
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        help_frame = Toplevel(self)
        help_frame.title("Help")
        help_frame.configure(width=w, height=h, bg=BACKGROUND_COLOR, relief=SUNKEN)
        help_frame.geometry('%dx%d+%d+%d' % (w, h, x, y))
        help_frame.minsize(height=h, width=w)
        help_frame.maxsize(height=h, width=w)
        help_frame.rowconfigure(0, weight=1)
        help_frame.columnconfigure(0, weight=1)
        HelpBox(help_frame, width=w, height=h, bg=BACKGROUND_COLOR, relief=SUNKEN).grid(row=0, column=0)
