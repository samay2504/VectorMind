# PDF Placeholder

This directory should contain 3+ PDF documents for testing the Multimodal RAG System.

## Required PDFs (3+)

To complete the assignment requirements, please add three types of PDFs:

### 1. Text-Only PDF ✅ REQUIRED
A PDF containing only text content (no images).

**Examples:**
- Contract or legal document
- Technical report
- Research paper
- Policy document
- Meeting minutes

**How to create:**
```bash
# Convert text file to PDF
# Option 1: Microsoft Word
# - Open .txt file in Word
# - Save As → PDF

# Option 2: Online converter
# - Use https://www.text2pdf.com/
# - Upload text file
# - Download PDF

# Option 3: Python
pip install fpdf2
python -c "
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', size=12)
with open('sample_data/texts/company_overview.txt', 'r') as f:
    for line in f:
        pdf.cell(200, 10, txt=line, ln=True)
pdf.output('sample_data/pdfs/company_overview.pdf')
"
```

### 2. Image-Only PDF ✅ REQUIRED
A PDF containing only images (scanned document or image-based PDF).

**Examples:**
- Scanned document
- Infographic PDF
- Chart/graph collection
- Photo album
- Hand-written notes (scanned)

**How to create:**
```bash
# Option 1: Scan a document
# - Use scanner or phone camera
# - Save as PDF

# Option 2: Convert images to PDF
# - Use Adobe Acrobat
# - Or online tool: https://www.ilovepdf.com/jpg_to_pdf

# Option 3: Python
pip install Pillow img2pdf
python -c "
import img2pdf
from PIL import Image
# Assuming you have images in sample_data/images/
imgs = ['sample_data/images/chart1.png', 'sample_data/images/diagram.png']
with open('sample_data/pdfs/images_only.pdf', 'wb') as f:
    f.write(img2pdf.convert(imgs))
"
```

### 3. Mixed Content PDF ✅ REQUIRED
A PDF containing both text and embedded images.

**Examples:**
- Product brochure
- Technical documentation with diagrams
- Presentation slides
- User manual with screenshots
- Annual report with charts

**How to create:**
```bash
# Option 1: PowerPoint/Google Slides
# - Create presentation with text and images
# - Export/Save as PDF

# Option 2: Microsoft Word
# - Create document with text and insert images
# - Save As → PDF

# Option 3: LaTeX
# - Create document with \includegraphics
# - Compile to PDF

# Option 4: Python ReportLab
pip install reportlab
python -c "
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

c = canvas.Canvas('sample_data/pdfs/mixed_content.pdf', pagesize=letter)
c.setFont('Helvetica', 16)
c.drawString(100, 750, 'CloudSync Platform Overview')
c.setFont('Helvetica', 12)
c.drawString(100, 720, 'This document contains both text and images.')
# Add image if available
# c.drawImage('sample_data/images/logo.png', 100, 500, width=200, height=100)
c.drawString(100, 450, 'Features:')
c.drawString(120, 430, '• Multi-cloud management')
c.drawString(120, 410, '• Cost optimization')
c.drawString(120, 390, '• Security and compliance')
c.save()
"
```

## PDF Characteristics

### Text-Only PDF
- **Pages:** 2-10 pages
- **Content:** Pure text, no images
- **Searchable:** Yes (text layer present)
- **Processing:** Extract text directly

### Image-Only PDF
- **Pages:** 1-5 pages
- **Content:** Only images/scanned pages
- **Searchable:** No (requires OCR)
- **Processing:** pdf2image → pytesseract OCR

### Mixed Content PDF
- **Pages:** 3-15 pages
- **Content:** Text paragraphs + embedded images
- **Searchable:** Partial (text layer + image content)
- **Processing:** Extract text + extract images + OCR images

## Suggested PDF Content

Based on sample text documents, consider creating:

1. **company_overview.pdf** (Text-only)
   - Convert `company_overview.txt` to PDF
   - Professional formatting

2. **architecture_diagrams.pdf** (Image-only)
   - Collection of architecture diagrams
   - System diagrams
   - Network topology

3. **product_brochure.pdf** (Mixed)
   - Product specifications with screenshots
   - Feature descriptions with charts
   - Customer testimonials with logos

## Quick PDF Creation Scripts

### Create text-only PDF from txt files:

```python
from fpdf import FPDF
import os

def txt_to_pdf(txt_file, pdf_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            pdf.multi_cell(0, 5, txt=line, align='L')
    
    pdf.output(pdf_file)

# Convert text files to PDFs
txt_to_pdf('sample_data/texts/company_overview.txt', 
           'sample_data/pdfs/company_overview.pdf')
txt_to_pdf('sample_data/texts/security_whitepaper.txt', 
           'sample_data/pdfs/security_whitepaper.pdf')
```

### Create image-only PDF:

```python
import img2pdf
from PIL import Image

# Collect all images
images = ['sample_data/images/chart1.png', 
          'sample_data/images/diagram1.png',
          'sample_data/images/screenshot1.png']

# Convert to PDF
with open('sample_data/pdfs/visual_content.pdf', 'wb') as f:
    f.write(img2pdf.convert(images))
```

### Create mixed content PDF:

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_mixed_pdf(output_file):
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    
    # Page 1: Title and text
    c.setFont("Helvetica-Bold", 24)
    c.drawString(inch, height - inch, "CloudSync Platform")
    c.setFont("Helvetica", 12)
    c.drawString(inch, height - 1.5*inch, "Multi-cloud management solution")
    
    # Add image if available
    try:
        c.drawImage('sample_data/images/logo.png', 
                   inch, height - 3*inch, 
                   width=2*inch, height=1*inch)
    except:
        c.rect(inch, height - 3*inch, 2*inch, 1*inch)
        c.drawString(inch, height - 2.5*inch, "[Image placeholder]")
    
    # More text
    c.drawString(inch, height - 4*inch, "Key Features:")
    features = [
        "• Multi-cloud support (AWS, Azure, GCP)",
        "• Cost optimization and monitoring",
        "• Security and compliance",
        "• API and automation"
    ]
    y = height - 4.5*inch
    for feature in features:
        c.drawString(1.2*inch, y, feature)
        y -= 0.3*inch
    
    c.showPage()
    c.save()

create_mixed_pdf('sample_data/pdfs/product_brochure.pdf')
```

## Testing PDFs

After adding PDFs:

```bash
# Upload text-only PDF
curl -X POST "http://localhost:8000/ingest/document" \
  -F "file=@sample_data/pdfs/company_overview.pdf" \
  -F "collection_name=techcorp_docs" \
  -F "user_id=demo_user"

# Upload image-only PDF
curl -X POST "http://localhost:8000/ingest/document" \
  -F "file=@sample_data/pdfs/visual_content.pdf" \
  -F "collection_name=techcorp_docs" \
  -F "user_id=demo_user"

# Upload mixed PDF
curl -X POST "http://localhost:8000/ingest/document" \
  -F "file=@sample_data/pdfs/product_brochure.pdf" \
  -F "collection_name=techcorp_docs" \
  -F "user_id=demo_user"

# Query PDF content
curl -X POST "http://localhost:8000/query/rag" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key features of CloudSync?",
    "collection_name": "techcorp_docs"
  }'
```

## PDF Processing Verification

The system should:
1. Detect PDF type (text-only, image-only, mixed)
2. Extract text using pdfplumber
3. Extract embedded images using pdf2image
4. Apply OCR to images using pytesseract
5. Generate embeddings for all content
6. Store in vector database with metadata
7. Enable retrieval across PDF content

## Common Issues

1. **OCR not working:** Install tesseract-ocr
   ```bash
   # Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   # Ubuntu: sudo apt-get install tesseract-ocr
   # macOS: brew install tesseract
   ```

2. **pdf2image error:** Install poppler
   ```bash
   # Windows: Download from https://github.com/oschwartz10612/poppler-windows
   # Ubuntu: sudo apt-get install poppler-utils
   # macOS: brew install poppler
   ```

3. **Large PDF files:** System handles chunking automatically

## Note

This is a placeholder file. Replace it with actual PDF files to meet the assignment requirement of "at least 3 PDFs with varying content types."

For the full assignment submission, this directory should contain at least 3 PDF files:
- 1x text-only PDF
- 1x image-only PDF
- 1x mixed content PDF
