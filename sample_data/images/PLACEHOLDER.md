# Image Placeholder

This directory should contain 5+ images for testing the Multimodal RAG System.

## Required Images (5+)

To complete the assignment requirements, please add the following types of images:

### 1. Architecture Diagrams
- System architecture diagrams
- Network topology diagrams
- Data flow diagrams
- Component diagrams

### 2. Charts and Graphs
- Sales data charts
- Performance metrics graphs
- Cost comparison charts
- Usage statistics visualizations

### 3. Screenshots
- Product UI screenshots
- Dashboard screenshots
- Configuration screenshots
- Report examples

### 4. Infographics
- Process flow infographics
- Feature comparison infographics
- Timeline infographics
- Statistics infographics

### 5. Logos and Branding
- Company logos
- Product logos
- Partner logos
- Certification badges

## Supported Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif) - limited support

## Image Requirements

- Resolution: Minimum 800x600 pixels
- Maximum file size: 10MB
- Clear, readable text if present
- High contrast for better OCR results

## How to Add Images

1. Create or download appropriate images
2. Save them in this directory
3. Use descriptive filenames:
   - `architecture_diagram_cloudplatform.png`
   - `sales_chart_2024.jpg`
   - `dashboard_screenshot.png`
   - `company_logo.png`

## Sample Image Sources

You can create images from:
- **Diagrams:** draw.io, Lucidchart, Visio
- **Charts:** Excel, Google Sheets, matplotlib, Chart.js
- **Screenshots:** Your own applications or demo sites
- **Infographics:** Canva, Piktochart, Adobe Illustrator

## Image Content Suggestions

Based on the text documents in `sample_data/texts/`, consider creating:

1. **CloudSync Architecture Diagram**
   - Show multi-cloud connectivity
   - Display core components
   - Illustrate data flow

2. **Cost Savings Chart**
   - Bar chart showing GlobalRetail's 32% cost reduction
   - Before/after comparison
   - Monthly savings trend

3. **Performance Dashboard Screenshot**
   - Real-time metrics display
   - Resource utilization graphs
   - Alert status

4. **Security Architecture Diagram**
   - Defense-in-depth layers
   - Encryption points
   - Network segmentation

5. **Certification Badges**
   - SOC 2 Type II badge
   - ISO 27001 badge
   - GDPR compliance badge

## Testing with Images

Once images are added:

```bash
# Upload single image
curl -X POST "http://localhost:8000/ingest/document" \
  -F "file=@sample_data/images/architecture_diagram.png" \
  -F "collection_name=techcorp_docs" \
  -F "user_id=demo_user"

# Query for image content
curl -X POST "http://localhost:8000/query/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find diagrams showing system architecture",
    "collection_name": "techcorp_docs"
  }'
```

## Image Processing

The system will:
1. Extract text using OCR (pytesseract)
2. Generate image embeddings
3. Store in vector database
4. Enable cross-modal search (text query → find images)

## Quick Image Creation

If you need placeholder images quickly:

```python
# Python script to create simple placeholder images
from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder(filename, text, size=(800, 600)):
    img = Image.new('RGB', size, color='white')
    d = ImageDraw.Draw(img)
    d.text((size[0]//2, size[1]//2), text, fill='black', anchor='mm')
    img.save(f"sample_data/images/{filename}")

create_placeholder("architecture_diagram.png", "CloudSync Architecture\n[Placeholder]")
create_placeholder("sales_chart.png", "Sales Data Chart\n[Placeholder]")
create_placeholder("dashboard.png", "Dashboard Screenshot\n[Placeholder]")
create_placeholder("logo.png", "TechCorp Logo\n[Placeholder]")
create_placeholder("security_diagram.png", "Security Architecture\n[Placeholder]")
```

## Note

This is a placeholder file. Replace it with actual images to meet the assignment requirement of "at least 5 images."

For the full assignment submission, this directory should contain at least 5 image files.
