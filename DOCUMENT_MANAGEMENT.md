# SWMS Regulatory Document Management

This guide explains how to manage regulatory documents for the SWMS MCP Server's R2 integration.

## Overview

The SWMS MCP Server can automatically include relevant regulatory documents as context when analyzing SWMS documents. These documents are stored in a Cloudflare R2 bucket and cached with the Gemini Files API.

## Document Collection

### Available Documents

Successfully downloaded documents include:
- **National**: Safe Work Australia SWMS Information Sheet, Model Code of Practice for Construction Work
- **NSW**: SafeWork NSW SWMS Template, NSW Code of Practice for Confined Spaces  
- **WA**: WA Code of Practice for Construction Work

### Download Script

Use `download_regulatory_docs.py` to download publicly available documents:

```bash
python3 download_regulatory_docs.py
```

This will download documents to the `regulatory_documents/` directory, organized by jurisdiction.

## Uploading to R2

### Prerequisites

1. Create R2 API credentials in Cloudflare Dashboard:
   - Go to R2 > Manage R2 API Tokens
   - Create token with Object Read & Write permissions
   - Note the Access Key ID and Secret Access Key

2. Set environment variables:
```bash
export R2_ACCESS_KEY_ID="your_access_key_id"
export R2_SECRET_ACCESS_KEY="your_secret_access_key"
```

3. Install boto3:
```bash
pip install boto3
```

### Upload Process

Run the upload script:
```bash
python3 upload_to_r2.py
```

This will upload all PDFs from `regulatory_documents/` to the `swms-regulations` R2 bucket.

## R2 Bucket Structure

Documents are organized in R2 as follows:
```
swms-regulations/
├── national/
│   ├── safe-work-australia-swms-info-sheet.pdf
│   ├── model-code-practice-construction.pdf
│   └── model-code-practice-construction-alt.pdf
├── nsw/
│   ├── nsw-swms-template.pdf
│   └── nsw-confined-spaces-cop.pdf
├── vic/
│   └── [Victoria documents]
├── qld/
│   └── [Queensland documents]
└── [other jurisdictions...]
```

## Public Access Configuration

To make documents accessible to the MCP server:

1. **Option A: Public URL** (Recommended for public documents)
   - Go to R2 bucket settings
   - Enable public access
   - Use the public.r2.dev URL

2. **Option B: Custom Domain**
   - Configure a custom domain for the bucket
   - Set `R2_PUBLIC_URL` environment variable

## Adding New Documents

To add new regulatory documents:

1. Add document info to `DOCUMENTS` dict in `download_regulatory_docs.py`
2. Run the download script
3. Upload to R2 using the upload script
4. Documents will automatically be used by the MCP server

## Manual Document Addition

If you have documents not available for automatic download:

1. Place PDFs in appropriate jurisdiction folder under `regulatory_documents/`
2. Follow naming convention: `{jurisdiction}-{document-type}.pdf`
3. Run `upload_to_r2.py` to upload

## Testing R2 Integration

After uploading documents, test the integration:

1. Reconnect the MCP server
2. Use the `list_jurisdictions()` tool to see supported jurisdictions
3. Analyze a SWMS with jurisdiction parameter:
   ```
   analyze_swms_compliance(document_id="...", jurisdiction="nsw")
   ```

## Important Notes

- Only upload publicly available government documents
- Respect copyright and licensing requirements
- Do not upload proprietary or licensed standards (e.g., full Australian Standards)
- Keep documents up to date with latest regulations
- The server will cache Gemini file IDs for 24 hours to avoid re-uploading

## Troubleshooting

### Documents not loading
- Check R2 bucket permissions
- Verify `R2_PUBLIC_URL` environment variable
- Check server logs for fetch errors

### Upload failures
- Verify R2 credentials are correct
- Ensure bucket exists and is accessible
- Check file paths and naming

### Cache issues
- Delete `/tmp/swms-file-cache/file_cache.json` to clear cache
- Files are re-uploaded after 24 hours automatically