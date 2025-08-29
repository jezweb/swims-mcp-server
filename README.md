# SWMS MCP Server

A FastMCP server that analyzes Safe Work Method Statements (SWMS) for NSW construction compliance using Gemini AI.

## Features

- Multiple document input methods (base64, URL, text)
- NSW WHS Regulation 2017 compliance assessment
- Detailed compliance reporting with actionable recommendations
- Integration with Gemini 2.5 Flash for document understanding

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

3. Run the server:
```bash
fastmcp run server.py
```

## Tools

### `upload_swms_document`
Upload a SWMS document from base64-encoded content.

**Parameters:**
- `file_content` (string): Base64-encoded file content
- `file_name` (string): Name of the file (e.g., "safety_plan.pdf")
- `mime_type` (string, optional): MIME type (auto-detected if not provided)

**Example:**
```json
{
  "file_content": "JVBERi0xLjQKJdPr6...",
  "file_name": "construction_swms.pdf"
}
```

### `upload_swms_from_url`
Upload a SWMS document from a URL.

**Parameters:**
- `url` (string): URL of the SWMS document (PDF or DOCX)

**Example:**
```json
{
  "url": "https://example.com/documents/swms.pdf"
}
```

### `analyze_swms_text`
Analyze SWMS text content directly without file upload.

**Parameters:**
- `document_text` (string): The SWMS document content as plain text or markdown
- `document_name` (string, optional): Name for the document

**Example:**
```json
{
  "document_text": "SAFE WORK METHOD STATEMENT\n\nProject: Construction Site...",
  "document_name": "Site Safety SWMS"
}
```

### `analyze_swms_compliance`
Analyze an uploaded document for NSW WHS compliance.

**Parameters:**
- `document_id` (string): ID returned from upload tools

**Returns:**
Detailed compliance assessment with:
- Overall compliance status
- Six assessment areas analysis
- Urgent actions required
- Recommendations for improvement

### `get_server_status`
Check server status and API connectivity.

## How AI Agents Use This Server

AI agents can interact with this MCP server in three ways:

1. **Base64 Upload**: Convert the document to base64 and send it directly
2. **URL Upload**: Provide a URL where the document is hosted
3. **Text Analysis**: Send document text directly for analysis

The server handles all file processing internally and returns structured compliance reports.

## Deployment

Deploy to FastMCP Cloud:
1. Connect this GitHub repository to [FastMCP Cloud](https://fastmcp.cloud)
2. Add `GEMINI_API_KEY` environment variable
3. Deploy

## Compliance Framework

The server assesses SWMS documents against NSW WHS Regulation 2017:
- Document Control & Administrative Compliance
- High-Risk Construction Work (HRCW) identification
- Hazard Identification & Risk Assessment
- Control Measures (Hierarchy of Controls)
- Monitoring, Review, and Communication
- Consultation requirements