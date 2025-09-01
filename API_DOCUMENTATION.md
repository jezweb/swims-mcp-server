# SWMS MCP Server API Documentation

## Overview

The SWMS MCP Server provides AI-powered analysis of Safe Work Method Statements for Australian construction compliance. It uses Gemini AI with jurisdiction-specific regulatory context from Cloudflare R2 storage.

## Quick Start - Common Workflows

### Workflow 1: Analyze Existing SWMS Document
```python
# Step 1: Upload document from URL
upload_result = await upload_swms_from_url(
    url="https://storage.example.com/swms/electrical-work.pdf"
)
document_id = upload_result["document_id"]  # e.g., "files/abc123..."

# Step 2: Get compliance score
score = await get_compliance_score(
    document_id=document_id,
    jurisdiction="nsw",
    weighted=True
)
print(f"Compliance: {score['overall_score']}% - {score['compliance_level']}")

# Step 3: Generate toolbox talk for morning briefing
talk = await generate_toolbox_talk_tool(
    document_id=document_id,
    duration="5min",
    focus_area="electrical safety"
)
```

### Workflow 2: Create New SWMS from Description
```python
# Generate complete SWMS document
result = await generate_swms_from_description_tool(
    job_description="Installing solar panels on warehouse roof with connection to main switchboard",
    trade_type="electrical",
    site_type="industrial",
    jurisdiction="qld"
)

# Save the generated document
with open("solar_installation_swms.md", "w") as f:
    f.write(result["swms_document"])
```

### Workflow 3: Quick Safety Checks
```python
# Upload document
upload = await upload_swms_from_url(url="https://example.com/swms.pdf")
doc_id = upload["document_id"]

# Run multiple quick checks
checks = {
    "hrcw": await quick_check_swms(doc_id, "hrcw"),
    "ppe": await quick_check_swms(doc_id, "ppe"),
    "emergency": await quick_check_swms(doc_id, "emergency")
}

# Review critical findings
for check_type, result in checks.items():
    print(f"{check_type}: {result['quick_summary']}")
```

## Available Tools

### Document Management Tools

#### 1. `upload_swms_document`
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

#### 2. `upload_swms_from_url`
Upload a SWMS document from a URL to Gemini API.

**Parameters:**
- `url` (string, required): URL of the SWMS document (PDF or DOCX)

**Returns:**
Same as `upload_swms_document`, with additional `source_url` field.

### Analysis Tools

#### 3. `analyze_swms_compliance`
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

#### 9. `get_server_status`
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

### Business Operation Tools (NEW)

#### 10. `generate_swms_from_description_tool`
Generate a complete SWMS from a job description using AI.

**Parameters:**
- `job_description` (string, required): Plain English description of the work
- `trade_type` (string, required): Type of trade (electrical, plumbing, carpentry, scaffolding, demolition, concrete, roofing, excavation)
- `site_type` (string, optional): Type of site. Default: "commercial"
  - Options: residential, commercial, industrial, infrastructure, renovation
- `jurisdiction` (string, optional): State/territory code. Default: "nsw"

**Returns:**
```json
{
  "status": "success",
  "message": "SWMS generated successfully",
  "swms_document": "Complete formatted SWMS document text...",
  "metadata": {
    "job_description": "Install electrical wiring...",
    "trade_type": "electrical",
    "site_type": "commercial",
    "jurisdiction": "nsw",
    "terminology": "WHS",
    "regulatory_context_included": true,
    "document_stats": {
      "total_lines": 250,
      "sections": 10,
      "approximate_pages": 8
    }
  },
  "next_steps": [
    "Review and customize for site-specific conditions",
    "Add company logo and contact details",
    "Obtain worker signatures before commencing work",
    "File with principal contractor"
  ]
}
```

#### 11. `generate_toolbox_talk_tool`
Generate a toolbox talk from a SWMS document.

**Parameters:**
- `document_id` (string, required): ID of the uploaded SWMS document
- `duration` (string, optional): Duration of talk. Default: "5min"
  - Options: "5min", "10min", "15min"
- `focus_area` (string, optional): Specific area to focus on

**Returns:**
```json
{
  "status": "success",
  "message": "Toolbox talk generated successfully",
  "toolbox_talk": {
    "duration": "5min",
    "focus_area": "working at heights",
    "content": "Full toolbox talk text...",
    "sections": {
      "Today's Key Risks": "...",
      "Critical Controls": "...",
      "PPE Reminder": "...",
      "Watch Out For": "...",
      "Emergency Info": "..."
    }
  },
  "delivery_tips": [
    "Keep it interactive - ask questions",
    "Use real examples from the site",
    "Check understanding before starting work",
    "Document attendance and concerns raised"
  ]
}
```

#### 12. `create_worker_summary_tool`
Create a simplified worker summary from a SWMS document.

**Parameters:**
- `document_id` (string, required): ID of the uploaded SWMS document
- `language_level` (string, optional): Language complexity. Default: "simple"
  - Options: "simple", "visual", "standard"
- `include_symbols` (boolean, optional): Include emoji symbols. Default: true

**Returns:**
```json
{
  "status": "success",
  "message": "Worker summary created successfully",
  "worker_summary": {
    "language_level": "simple",
    "include_symbols": true,
    "content": "Safety card content with visual symbols...",
    "format": "safety_card",
    "metrics": {
      "total_lines": 20,
      "bullet_points": 15,
      "estimated_reading_time": "1-2 minutes"
    }
  },
  "usage_instructions": [
    "Print on bright colored paper",
    "Display at site entry",
    "Review during induction",
    "Available in multiple languages"
  ]
}
```

#### 13. `suggest_swms_improvements_tool`
Suggest improvements for an existing SWMS document.

**Parameters:**
- `document_id` (string, required): ID of the uploaded SWMS document
- `incident_history` (array, optional): List of recent incidents to consider
- `improvement_focus` (string, optional): Focus area. Default: "safety"
  - Options: "safety", "efficiency", "compliance"

**Returns:**
```json
{
  "status": "success",
  "message": "Improvement suggestions generated successfully",
  "improvements": {
    "focus_area": "safety",
    "total_recommendations": 12,
    "categories": {
      "critical_gaps": ["Add emergency assembly point", "..."],
      "quick_wins": ["Include site-specific hazards", "..."],
      "best_practices": ["Implement permit system", "..."],
      "safety_specific": ["Add fatigue management", "..."]
    },
    "full_analysis": "Detailed analysis text..."
  },
  "implementation_priority": [
    "1. Address critical gaps immediately",
    "2. Implement quick wins this week",
    "3. Plan best practices for next review",
    "4. Focus on safety improvements ongoing"
  ]
}
```

#### 14. `extract_hazards_from_image_tool`
Extract and identify hazards from a construction site image.

**Parameters:**
- `image_content` (string, required): Base64 encoded image content
- `work_type` (string, required): Type of work being performed
- `jurisdiction` (string, optional): State/territory code. Default: "nsw"

**Returns:**
```json
{
  "status": "success",
  "message": "Image analyzed successfully for hazards",
  "hazard_analysis": {
    "work_type": "scaffolding",
    "jurisdiction": "nsw",
    "total_hazards_identified": 8,
    "high_risk_count": 3,
    "hazard_categories": {
      "immediate_dangers": [
        {
          "description": "Missing edge protection at 3m height",
          "risk_level": "High",
          "category": "Immediate Dangers"
        }
      ],
      "high_risk_hazards": [...],
      "general_hazards": [...],
      "work_specific_hazards": [...]
    },
    "full_analysis": "Detailed hazard analysis..."
  },
  "recommended_actions": [
    "Address immediate dangers before work proceeds",
    "Implement controls for high-risk hazards",
    "Update SWMS with site-specific hazards",
    "Brief workers on identified hazards"
  ]
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