import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

print(setuptools.find_packages())

setuptools.setup(name='pdfviewer',
                 version='0.1',
                 description='Tkinter based GUI to view PDF files',
                 url='https://github.com/naiveHobo/pdfviewer.git',
                 author='naiveHobo',
                 author_email='sarthakmittal2608@gmail.com',
                 license='MIT',
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 packages=setuptools.find_packages(),
                 install_requires=[
                     'Pillow',
                     'pdfplumber',
                     'PyPDF2',
                     'pytesseract'
                 ],
                 zip_safe=False)
