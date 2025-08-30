# SWMS MCP Server Features Guide

## 📋 Complete Feature List

### Core Analysis Features

#### 1. Multi-Jurisdictional Compliance Analysis
- **Coverage**: All Australian states and territories
- **Automatic Terminology**: WHS vs OHS (Victoria)
- **Jurisdiction-Specific Rules**: 
  - SA: 3m fall height threshold
  - VIC: OHS Act 2004 framework
  - WA: Recent 2022 WHS adoption considerations

#### 2. AI-Powered Document Understanding
- **Model**: Gemini 2.0 Flash (latest)
- **Context**: 25+ regulatory documents automatically included
- **Languages**: English (primary), with multi-language support
- **File Types**: PDF, DOCX (auto-converted), plain text

#### 3. Comprehensive Scoring System
- **Weighted Categories**:
  - Document Control (10%)
  - HRCW Identification (20%)
  - Hazard Identification (15%)
  - Control Measures (25%)
  - Monitoring & Review (15%)
  - Consultation (15%)
- **Score Types**: Raw, weighted, percentage
- **Tracking**: Historical comparison support

#### 4. Flexible Input Methods
- **Base64 Upload**: Direct file content
- **URL Upload**: Remote document fetching
- **Text Input**: Direct text analysis
- **Auto-Conversion**: DOCX → PDF

#### 5. Custom Analysis Engine
- **User Prompts**: Custom compliance checks
- **Output Formats**: JSON or plain text
- **Specialized Checks**: Mental health, fatigue, emergency procedures

#### 6. Quick Check System
- **Completeness**: Required sections check
- **High Risk**: HRCW activities verification
- **Controls**: Hierarchy assessment
- **Emergency**: Procedure validation
- **PPE**: Equipment requirements
- **Training**: Competency verification

### Regulatory Context Features

#### 7. R2 Document Integration
- **Storage**: Cloudflare R2 object storage
- **Documents**: 25 official PDFs
- **Auto-Fetch**: Based on jurisdiction
- **Caching**: 24-hour retention

#### 8. Document Categories
- **Codes of Practice**: Construction work guidelines
- **Templates**: Official SWMS examples
- **Information Sheets**: Compliance guides
- **Fact Sheets**: Quick references
- **Regulations**: Full legislative texts

### Technical Features

#### 9. FastMCP Framework
- **Protocol**: Model Context Protocol
- **Transport**: HTTP/SSE
- **Async**: Full async/await support
- **Scaling**: Horizontal scaling ready

#### 10. Error Handling
- **Graceful Degradation**: Continues with available context
- **Detailed Messages**: Actionable error information
- **Recovery**: Automatic retry for transient failures

## 🛠️ Tool Reference

### Document Management Tools

#### `upload_swms_document`
**Purpose**: Upload SWMS from base64 content
```python
result = await upload_swms_document({
    "file_content": base64_string,
    "file_name": "construction-swms.pdf",
    "mime_type": "application/pdf"  # Optional
})
```

**Features**:
- Auto-detect MIME type
- DOCX auto-conversion
- Virus scanning (if configured)
- Size validation

#### `upload_swms_from_url`
**Purpose**: Fetch and upload from URL
```python
result = await upload_swms_from_url({
    "url": "https://example.com/swms.pdf"
})
```

**Features**:
- HTTP/HTTPS support
- Follow redirects
- Content validation
- Auto-retry on failure

### Analysis Tools

#### `analyze_swms_compliance`
**Purpose**: Full compliance assessment
```python
analysis = await analyze_swms_compliance({
    "document_id": "files/abc123",
    "jurisdiction": "nsw"  # Default
})
```

**Returns**:
- Overall assessment
- Detailed category analysis
- Urgent actions required
- Improvement recommendations

#### `analyze_swms_text`
**Purpose**: Direct text analysis
```python
analysis = await analyze_swms_text({
    "document_text": "SWMS content here...",
    "document_name": "Working at Heights",
    "jurisdiction": "vic"
})
```

**Use Cases**:
- Quick drafts review
- Template validation
- Partial document checks

#### `analyze_swms_custom`
**Purpose**: Specialized analysis
```python
custom = await analyze_swms_custom({
    "document_id": "files/abc123",
    "analysis_prompt": "Check mental health provisions",
    "output_format": "json",
    "jurisdiction": "qld"
})
```

**Example Prompts**:
- "Evaluate COVID-19 safety measures"
- "Check indigenous cultural considerations"
- "Assess environmental impact controls"

### Scoring Tools

#### `get_compliance_score`
**Purpose**: Numerical compliance metrics
```python
score = await get_compliance_score({
    "document_id": "files/abc123",
    "weighted": True,
    "jurisdiction": "wa"
})
```

**Metrics**:
- Overall score (0-100)
- Category breakdowns
- Compliance level rating
- Critical gap identification

#### `quick_check_swms`
**Purpose**: Rapid validation
```python
check = await quick_check_swms({
    "document_id": "files/abc123",
    "check_type": "high_risk",
    "jurisdiction": "sa"
})
```

**Check Types**:
- `completeness`: All sections present
- `high_risk`: 18 HRCW activities
- `controls`: Hierarchy implementation
- `emergency`: Response procedures
- `ppe`: Equipment specifications
- `training`: Competency requirements

### Utility Tools

#### `list_jurisdictions`
**Purpose**: Get supported regions
```python
jurisdictions = await list_jurisdictions()
```

**Returns**:
- All jurisdiction codes
- Legislation details
- Regulator information
- Terminology preferences

#### `get_server_status`
**Purpose**: Health check
```python
status = await get_server_status()
```

**Information**:
- API configuration
- R2 availability
- Cached documents
- Version information

## 🎯 Use Case Examples

### Construction Site Manager
```python
# Morning safety check
async def daily_swms_review(swms_url, site_jurisdiction):
    # Upload latest SWMS
    upload = await upload_swms_from_url({"url": swms_url})
    
    # Quick safety check
    safety = await quick_check_swms({
        "document_id": upload["document_id"],
        "check_type": "emergency",
        "jurisdiction": site_jurisdiction
    })
    
    # Get compliance score
    score = await get_compliance_score({
        "document_id": upload["document_id"],
        "weighted": True,
        "jurisdiction": site_jurisdiction
    })
    
    return {
        "date": datetime.now(),
        "safety_status": safety["result"],
        "compliance_score": score["overall_score"],
        "urgent_actions": safety.get("urgent_actions", [])
    }
```

### Safety Consultant
```python
# Comprehensive audit
async def swms_audit(document_id):
    results = {}
    
    # Check all jurisdictions
    for state in ["nsw", "vic", "qld", "wa", "sa", "tas", "act", "nt"]:
        analysis = await analyze_swms_compliance({
            "document_id": document_id,
            "jurisdiction": state
        })
        results[state] = {
            "compliant": analysis["overall_assessment"],
            "critical_gaps": analysis.get("urgent_actions", [])
        }
    
    # Custom checks
    mental_health = await analyze_swms_custom({
        "document_id": document_id,
        "analysis_prompt": "Assess mental health and wellbeing provisions"
    })
    
    results["special_considerations"] = mental_health
    return results
```

### Compliance Officer
```python
# Track improvement over time
async def track_compliance_progress(swms_versions):
    scores = []
    
    for version in swms_versions:
        upload = await upload_swms_from_url({"url": version["url"]})
        score = await get_compliance_score({
            "document_id": upload["document_id"],
            "weighted": True
        })
        scores.append({
            "version": version["name"],
            "date": version["date"],
            "score": score["overall_score"],
            "improvements": score["summary"]["strengths"]
        })
    
    return {
        "trend": "improving" if scores[-1]["score"] > scores[0]["score"] else "declining",
        "current_score": scores[-1]["score"],
        "improvement_rate": scores[-1]["score"] - scores[0]["score"],
        "history": scores
    }
```

## 🔍 Advanced Features

### Batch Processing
```python
async def batch_analyze(document_urls):
    tasks = []
    for url in document_urls:
        task = asyncio.create_task(process_document(url))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### Multi-Format Support
```python
async def process_any_format(file_path):
    if file_path.endswith('.docx'):
        # Auto-converts to PDF
        with open(file_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode()
        return await upload_swms_document({
            "file_content": content,
            "file_name": os.path.basename(file_path)
        })
    elif file_path.endswith('.txt'):
        with open(file_path, 'r') as f:
            text = f.read()
        return await analyze_swms_text({
            "document_text": text
        })
    else:
        # PDF or other supported format
        return await upload_swms_from_url({
            "url": f"file://{file_path}"
        })
```

### Comparison Analysis
```python
async def compare_swms(doc_id_1, doc_id_2):
    # Analyze both documents
    doc1 = await analyze_swms_compliance({"document_id": doc_id_1})
    doc2 = await analyze_swms_compliance({"document_id": doc_id_2})
    
    # Compare scores
    score1 = await get_compliance_score({"document_id": doc_id_1})
    score2 = await get_compliance_score({"document_id": doc_id_2})
    
    return {
        "better_document": doc_id_1 if score1["overall_score"] > score2["overall_score"] else doc_id_2,
        "score_difference": abs(score1["overall_score"] - score2["overall_score"]),
        "doc1_strengths": doc1["detailed_analysis"],
        "doc2_strengths": doc2["detailed_analysis"]
    }
```

## 🎨 Customization Options

### Custom Prompts Library
```python
CUSTOM_PROMPTS = {
    "indigenous": "Evaluate indigenous cultural safety considerations and consultation requirements",
    "environment": "Assess environmental protection measures and sustainability practices",
    "mental_health": "Check mental health support, fatigue management, and wellbeing initiatives",
    "covid": "Verify COVID-19 safety measures and infection control procedures",
    "women": "Evaluate provisions for women in construction including facilities and PPE",
    "apprentices": "Check training, supervision, and safety provisions for apprentices and trainees"
}

async def specialized_check(document_id, check_type):
    return await analyze_swms_custom({
        "document_id": document_id,
        "analysis_prompt": CUSTOM_PROMPTS[check_type]
    })
```

### Jurisdiction-Specific Templates
```python
def get_jurisdiction_template(state):
    templates = {
        "nsw": "Follow SafeWork NSW SWMS template structure",
        "vic": "Use WorkSafe Victoria OHS format",
        "qld": "Apply WHSQ guidelines and format",
        # ... etc
    }
    return templates.get(state, "Use national Safe Work Australia template")
```

## 📊 Reporting Features

### Generate Compliance Report
```python
async def generate_full_report(document_id, jurisdiction="nsw"):
    report = {
        "timestamp": datetime.now().isoformat(),
        "jurisdiction": jurisdiction,
        "analysis": await analyze_swms_compliance({
            "document_id": document_id,
            "jurisdiction": jurisdiction
        }),
        "score": await get_compliance_score({
            "document_id": document_id,
            "weighted": True,
            "jurisdiction": jurisdiction
        }),
        "quick_checks": {}
    }
    
    # Run all quick checks
    for check_type in ["completeness", "high_risk", "controls", "emergency", "ppe", "training"]:
        report["quick_checks"][check_type] = await quick_check_swms({
            "document_id": document_id,
            "check_type": check_type,
            "jurisdiction": jurisdiction
        })
    
    return report
```

### Export Results
```python
def export_to_csv(report):
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Category", "Status", "Score", "Comments"])
    
    # Data
    for category, details in report["analysis"]["detailed_analysis"].items():
        writer.writerow([
            category,
            details["status"],
            report["score"]["category_scores"].get(category, {}).get("score", "N/A"),
            details["comments"]
        ])
    
    return output.getvalue()
```

## 🔐 Security Features

- **API Key Protection**: Environment variables only
- **Input Validation**: All inputs sanitized
- **File Size Limits**: Configurable max upload size
- **Rate Limiting**: Built-in throttling support
- **Audit Logging**: Full request/response logging
- **Data Privacy**: No permanent storage of documents

## 🚀 Performance Features

- **Async Processing**: Non-blocking operations
- **Caching Layer**: 24-hour document cache
- **Connection Pooling**: Efficient API usage
- **Batch Operations**: Process multiple documents
- **Streaming Responses**: For large documents
- **CDN Integration**: R2 with Cloudflare CDN

## 📈 Future Enhancements

### Planned Features
- [ ] Multi-language SWMS support
- [ ] Industry-specific templates
- [ ] Automated improvement suggestions
- [ ] Historical compliance tracking
- [ ] Integration with safety management systems
- [ ] Mobile app support
- [ ] Real-time collaboration
- [ ] Digital signatures
- [ ] Automated notifications
- [ ] Custom branding options

### API Roadmap
- GraphQL endpoint
- WebSocket support for real-time updates
- Webhook notifications
- Bulk import/export
- Template marketplace

---

For implementation details, see [API Documentation](./API_DOCUMENTATION.md) and [Deployment Guide](./DEPLOYMENT_GUIDE.md).