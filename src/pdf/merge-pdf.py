# Importing all libaries and the updated PyPDF2 library codes. 
# If you need to install, type: pip install PyPDF2
import os 
import PyPDF2
from PyPDF2 import PdfReader , PdfWriter, PdfMerger

pdfFiles = [] # variable 

for root, dirs, filenames in os.walk(os.getcwd()+'\pdfs'): # Root and directory pathway.
    for filename in filenames: 
        if filename.lower().endswith('.pdf'):# for loop for all files with .pdf in the name.
            pdfFiles.append(os.path.join(root,filename)) 
            # Appending files to root name from OS (operating system).
            
# Sorting the files by forcing everything to lower case.
pdfFiles.sort(key=str.lower)

print(len(pdfFiles), pdfFiles)

# Assigning the pdfWriter() function to pdfWriter.
pdfWriter = PdfWriter()

for filename in pdfFiles: # Starting a for loop.
    pdfFileObj = open(filename, 'rb') # Opens each of the file paths in filename variable.
    pdfReader = PdfReader(pdfFileObj) # Reads each of the files in the new varaible you've created above and stores into memory.
    print(filename, pdfReader._get_num_pages())
    
    for page in range(pdfReader._get_num_pages()):
        pageObj = pdfReader.pages[page] # Reads only those that are in the varaible.
        pdfWriter.add_page(pageObj) # Adds each of the PDFs it's read to a new page.
    

# Name of the PDF file can be written here.
pdfOutput = open('Desai-Feasi-Report-v2.pdf', 'wb') 

# Writing the output file using the pdfWriter function.
pdfWriter.write(pdfOutput)
pdfOutput.close()