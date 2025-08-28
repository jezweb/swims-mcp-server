# SWMS MCP Server

A FastMCP server that analyzes Safe Work Method Statements (SWMS) for NSW construction compliance using Gemini AI.

## Features

- Upload and process SWMS documents (PDF/DOCX)
- NSW WHS Regulation 2017 compliance assessment
- Detailed compliance reporting with actionable recommendations
- Integration with Gemini API for document understanding

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
python server.py
```

## Tools

### `upload_swms_document`
Upload and analyze a SWMS document file.

### `analyze_swms_compliance` 
Analyze uploaded document for NSW WHS compliance.

### `get_server_status`
Check server status and configuration.

## Deployment

Deploy to FastMCP Cloud by connecting this GitHub repository.