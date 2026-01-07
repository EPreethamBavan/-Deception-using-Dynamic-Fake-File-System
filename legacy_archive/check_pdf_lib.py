try:
    from pypdf import PdfReader
    print("pypdf is installed")
except ImportError:
    try:
        import PyPDF2
        print("PyPDF2 is installed")
    except ImportError:
        print("No PDF library found")
