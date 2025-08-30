# SWMS MCP Server API Documentation

## Overview

The SWMS MCP Server provides AI-powered analysis of Safe Work Method Statements for Australian construction compliance. It uses Gemini AI with jurisdiction-specific regulatory context from Cloudflare R2 storage.

## Available Tools

### 1. `upload_swms_document`
Upload a SWMS document from base64-encoded content to Gemini API.

**Parameters:**
- `file_content` (string, required): Base64-encoded file content
- `file_name` (string, required): Name of the file (e.g., "safety_plan.pdf")
- `mime_type` (string, optional): MIME type (auto-detected if not provided)

**Supported Formats:**
- PDF files (native support)
- DOCX files (automatically converted to PDF)

**Returns:**
```json
{
  "status": "success",
  "message": "Document uploaded successfully",
  "document_id": "files/abc123...",
  "file_info": {
    "name": "safety_plan.pdf",
    "mime_type": "application/pdf",
    "uri": "https://generativelanguage.googleapis.com/v1beta/files/...",
    "size_bytes": 126600
  },
  "conversion_info": {  // Only present if DOCX was converted
    "original_format": "DOCX",
    "converted_to": "PDF",
    "note": "Document was automatically converted for Gemini compatibility"
  }
}
```

### 2. `upload_swms_from_url`
Upload a SWMS document from a URL to Gemini API.

**Parameters:**
- `url` (string, required): URL of the SWMS document (PDF or DOCX)

**Returns:**
Same as `upload_swms_document`, with additional `source_url` field.

### 3. `analyze_swms_compliance`
Analyze a SWMS document for WHS/OHS compliance using Gemini API with regulatory context.

**Parameters:**
- `document_id` (string, required): ID of the uploaded SWMS document
- `jurisdiction` (string, optional): State/territory code. Default: "nsw"
  - Valid values: "nsw", "vic", "qld", "wa", "sa", "tas", "act", "nt", "national"

**Features:**
- Automatically includes relevant regulatory documents from R2
- Jurisdiction-specific terminology (WHS vs OHS for Victoria)
- Contextual analysis based on local regulations

**Returns:**
```json
{
  "status": "success",
  "project_details": {
    "project_name": "Example Construction Project",
    "principal_contractor": "ABC Builders Pty Ltd",
    "subcontractor": "XYZ Safety Services",
    "swms_title": "Working at Heights SWMS"
  },
  "overall_assessment": "Partially Compliant",
  "summary": "The SWMS addresses most requirements but lacks specific details...",
  "detailed_analysis": {
    "document_control": {
      "status": "Compliant",
      "comments": "Document control section is well-structured..."
    },
    "hrcw_identification": {
      "status": "Partially Compliant",
      "comments": "High-risk activities identified but missing..."
    },
    "hazard_identification": {
      "status": "Compliant",
      "comments": "Comprehensive hazard identification..."
    },
    "control_measures": {
      "status": "Partially Compliant",
      "comments": "Control measures follow hierarchy but..."
    },
    "monitoring_review": {
      "status": "Non-Compliant",
      "comments": "No clear monitoring procedures..."
    },
    "consultation": {
      "status": "Partially Compliant",
      "comments": "Worker consultation mentioned but..."
    }
  },
  "urgent_actions": [
    "Add specific monitoring and review procedures",
    "Include worker sign-off section"
  ],
  "recommendations": [
    "Enhance site-specific hazard details",
    "Add emergency contact information"
  ]
}
```

### 4. `analyze_swms_text`
Analyze SWMS text content directly without file upload.

**Parameters:**
- `document_text` (string, required): The SWMS content as plain text or markdown
- `document_name` (string, optional): Name for reference. Default: "SWMS Document"
- `jurisdiction` (string, optional): State/territory code. Default: "nsw"

**Returns:**
Same structure as `analyze_swms_compliance`.

### 5. `analyze_swms_custom`
Perform custom analysis using a user-provided prompt.

**Parameters:**
- `document_id` (string, required): ID of the uploaded SWMS document
- `analysis_prompt` (string, required): Custom analysis instructions
- `output_format` (string, optional): "json" or "text". Default: "json"
- `jurisdiction` (string, optional): State/territory code. Default: "nsw"

**Example Prompts:**
- "Check if this SWMS adequately addresses mental health and fatigue management"
- "Evaluate the emergency response procedures in this SWMS"
- "Assess if this SWMS is suitable for a residential construction project"

**Returns:**
```json
{
  "status": "success",
  "custom_analysis": {
    // Structure depends on prompt and output_format
  },
  "metadata": {
    "prompt_used": "...",
    "jurisdiction": "nsw",
    "output_format": "json"
  }
}
```

### 6. `get_compliance_score`
Calculate numerical compliance scores for tracking and reporting.

**Parameters:**
- `document_id` (string, required): ID of the uploaded SWMS document
- `weighted` (boolean, optional): Apply importance weighting. Default: true
- `jurisdiction` (string, optional): State/territory code. Default: "nsw"

**Scoring Categories:**
1. Document Control (10% weight)
2. HRCW Identification (20% weight)
3. Hazard Identification (15% weight)
4. Control Measures (25% weight)
5. Monitoring & Review (15% weight)
6. Consultation (15% weight)

**Returns:**
```json
{
  "status": "success",
  "overall_score": 72.5,
  "weighted_score": 68.3,
  "category_scores": {
    "document_control": {
      "score": 85,
      "weight": 0.10,
      "weighted_score": 8.5,
      "status": "Good"
    },
    "hrcw_identification": {
      "score": 70,
      "weight": 0.20,
      "weighted_score": 14.0,
      "status": "Adequate"
    }
    // ... other categories
  },
  "summary": {
    "strengths": ["Good document control", "Clear hazard identification"],
    "improvements_needed": ["Enhance monitoring procedures", "Add consultation records"],
    "critical_gaps": ["Missing review triggers"]
  },
  "compliance_level": "Moderate Compliance",
  "recommendation": "Address critical gaps before commencing work"
}
```

### 7. `quick_check_swms`
Perform rapid checks on specific SWMS aspects.

**Parameters:**
- `document_id` (string, required): ID of the uploaded SWMS document
- `check_type` (string, required): Type of check to perform
  - "completeness": Check for required sections
  - "high_risk": Verify HRCW activities coverage
  - "controls": Assess control measures adequacy
  - "emergency": Check emergency procedures
  - "ppe": Verify PPE requirements
  - "training": Check training requirements
- `jurisdiction` (string, optional): State/territory code. Default: "nsw"

**Returns:**
```json
{
  "status": "success",
  "check_type": "high_risk",
  "result": "PASS with observations",
  "findings": {
    "identified_activities": [
      "Working at heights > 2m",
      "Excavation work > 1.5m",
      "Mobile plant operation"
    ],
    "missing_activities": [
      "Electrical work considerations"
    ],
    "observations": [
      "Fall height threshold correctly identified for jurisdiction",
      "Mobile plant procedures well documented"
    ]
  },
  "recommendations": [
    "Consider electrical hazards if applicable"
  ]
}
```

### 8. `list_jurisdictions`
List all supported jurisdictions with their regulatory details.

**Parameters:** None

**Returns:**
```json
{
  "status": "success",
  "jurisdictions": {
    "nsw": {
      "name": "New South Wales",
      "legislation": "Work Health and Safety Act 2011 (NSW) and Regulation 2017 (NSW)",
      "regulator": "SafeWork NSW",
      "terminology": "WHS"
    },
    "vic": {
      "name": "Victoria",
      "legislation": "Occupational Health and Safety Act 2004 (Vic) and Regulations 2017 (Vic)",
      "regulator": "WorkSafe Victoria",
      "terminology": "OHS",
      "note": "Victoria uses OHS terminology and has not adopted model WHS laws"
    },
    // ... other jurisdictions
  },
  "default": "nsw",
  "note": "All analysis functions support jurisdiction parameter. R2 context documents will be included if available."
}
```

### 9. `get_server_status`
Check server health and configuration status.

**Parameters:** None

**Returns:**
```json
{
  "status": "operational",
  "api_configured": true,
  "api_key_type": "GEMINI_API_KEY",
  "r2_context_available": true,
  "r2_public_url": "https://pub-bb6a39bd73444f4582d3208b2257c357.r2.dev",
  "cached_documents": 5,
  "version": "1.0.0",
  "message": "Server is operational with R2 context support"
}
```

## Jurisdiction-Specific Features

### Victoria (VIC)
- Uses "OHS" terminology instead of "WHS"
- Different penalty structures
- Not harmonized with model WHS laws
- Specific construction regulations under OHS Regulations 2017

### South Australia (SA)
- Fall from height threshold: **3 metres** (vs 2m in other states)
- Otherwise follows model WHS laws

### Western Australia (WA)
- Recently adopted WHS laws in 2022
- Some variations for mining and petroleum sectors
- Transitional arrangements may apply

## R2 Regulatory Context

The server automatically fetches and includes relevant regulatory documents based on jurisdiction:

### Documents Available by Jurisdiction

**National:**
- Safe Work Australia SWMS Information Sheet
- Model Code of Practice: Construction Work (multiple versions)
- Office of Federal Safety Commissioner requirements

**State-Specific:**
- Codes of Practice for construction work
- SWMS templates and examples
- Guidance documents and fact sheets
- Industry-specific requirements

### Caching Strategy
- Documents are cached in Gemini Files API for 24 hours
- Local cache at `/tmp/swms-file-cache/`
- Reduces API calls and improves performance

## Error Handling

All tools return consistent error responses:

```json
{
  "status": "error",
  "message": "Description of the error",
  "error_code": "ERROR_TYPE",
  "details": {
    // Additional error context if available
  }
}
```

Common error codes:
- `API_KEY_NOT_CONFIGURED`: Gemini API key missing
- `DOCUMENT_NOT_FOUND`: Invalid document_id
- `INVALID_JURISDICTION`: Unsupported jurisdiction code
- `CONVERSION_FAILED`: DOCX to PDF conversion error
- `R2_FETCH_FAILED`: Could not retrieve regulatory documents

## Best Practices

1. **Always specify jurisdiction** for accurate compliance checking
2. **Use `get_compliance_score`** for tracking improvements over time
3. **Run `quick_check_swms`** for rapid validation before detailed analysis
4. **Leverage custom analysis** for project-specific requirements
5. **Check server status** if experiencing issues

## Rate Limits

- Gemini API: Subject to your API plan limits
- R2 fetches: Unlimited (public bucket)
- File caching: 24-hour retention

## Support

For issues or questions:
- GitHub: https://github.com/jezweb/swims-mcp-server
- Ensure API keys are properly configured
- Check server status with `get_server_status`
- Verify R2 public access is enabled