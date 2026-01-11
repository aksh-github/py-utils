import PyPDF2

def copy_pages(input_pdf, output_pdf, page_numbers):
    """
    Copy specific pages from input PDF to output PDF.

    Args:
        input_pdf (str): Path to input PDF file.
        output_pdf (str): Path to output PDF file.
        page_numbers (list): List of page numbers to copy (1-indexed).
    """
    with open(input_pdf, 'rb') as input_file:
        pdf_reader = PyPDF2.PdfReader(input_file)
        pdf_writer = PyPDF2.PdfWriter()

        for page_number in page_numbers:
            if page_number <= len(pdf_reader.pages):
                pdf_writer.add_page(pdf_reader.pages[page_number - 1])
            else:
                print(f"Warning: Page {page_number} does not exist in input PDF.")

        with open(output_pdf, 'wb') as output_file:
            pdf_writer.write(output_file)

def main():
    input_pdf = input("Enter input PDF file path: ")
    output_pdf = input("Enter output PDF file path: ")
    page_numbers = [int(x) for x in input("Enter page numbers to copy (comma-separated): ").split(',')]

    copy_pages(input_pdf, output_pdf, page_numbers)
    print("PDF pages copied successfully!")

if __name__ == "__main__":
    main()