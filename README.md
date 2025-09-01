# SWMS MCP Server

A FastMCP server that analyzes Safe Work Method Statements (SWMS) for Australian construction compliance using Gemini AI with jurisdiction-specific regulatory context.

## 🌟 Key Features

### Core Compliance Features
- **🌏 Multi-jurisdictional Support** - All Australian states and territories (NSW, VIC, QLD, WA, SA, TAS, ACT, NT)
- **📚 Regulatory Context** - Automatic inclusion of 25+ official documents from Cloudflare R2
- **📄 Flexible Input** - Base64, URL, text, with automatic DOCX to PDF conversion
- **✅ Comprehensive Analysis** - Based on WHS/OHS regulations for each jurisdiction
- **🎯 Custom Analysis** - Flexible prompts and specialized compliance checks
- **📊 Numerical Scoring** - Weighted compliance scores for tracking improvements
- **🤖 Gemini 2.0 Flash** - Advanced document understanding with regulatory context

### New Business Operation Features
- **🚀 SWMS Generation** - Create complete SWMS from plain English job descriptions
- **🗣️ Toolbox Talks** - Generate 5/10/15 minute safety talks from SWMS
- **👷 Worker Summaries** - Simplified safety cards with visual symbols
- **💡 Improvement Suggestions** - AI-powered recommendations based on best practices
- **📸 Image Hazard Detection** - Identify site hazards from photos using vision AI

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/jezweb/swims-mcp-server.git
cd swims-mcp-server

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running the Server

```bash
# Development
fastmcp dev server.py

# Production
fastmcp run server.py
```

## 📖 Usage Examples

### Basic SWMS Analysis (NSW)

```python
# Upload document
upload_result = await upload_swms_from_url({
    "url": "https://example.com/construction-swms.pdf"
})

# Analyze for NSW compliance (default)
analysis = await analyze_swms_compliance({
    "document_id": upload_result["document_id"]
})
```

### Victoria-Specific Analysis (OHS)

```python
# Victoria uses OHS terminology, not WHS
analysis = await analyze_swms_compliance({
    "document_id": document_id,
    "jurisdiction": "vic"  # Uses OHS regulations
})
```

### Get Compliance Score

```python
# Get numerical score for tracking
score = await get_compliance_score({
    "document_id": document_id,
    "weighted": True,
    "jurisdiction": "qld"
})
# Returns overall score, category breakdowns, and recommendations
```

### Quick Checks

```python
# Quick check for specific aspects
result = await quick_check_swms({
    "document_id": document_id,
    "check_type": "high_risk",  # or "emergency", "ppe", "controls", etc.
    "jurisdiction": "wa"
})
```

### Custom Analysis

```python
# Custom analysis with your own prompt
custom = await analyze_swms_custom({
    "document_id": document_id,
    "analysis_prompt": "Check if this SWMS adequately addresses mental health and fatigue management for night shift workers",
    "jurisdiction": "sa"
})
```

### Generate SWMS from Description (NEW)

```python
# Generate complete SWMS from job description
swms = await generate_swms_from_description_tool({
    "job_description": "Install electrical wiring and outlets on level 3 of commercial building, including running cables through ceiling cavity and installing GPOs in office spaces",
    "trade_type": "electrical",
    "site_type": "commercial",
    "jurisdiction": "nsw"
})
# Returns complete SWMS document ready for review

# Generate toolbox talk from SWMS
talk = await generate_toolbox_talk_tool({
    "document_id": document_id,
    "duration": "5min",
    "focus_area": "electrical safety"
})
# Returns bullet points for morning safety briefing
```

## 🤖 AI Integration Guide

### For AI Assistants Using This MCP Server

This section helps AI assistants understand how to effectively use the SWMS MCP Server tools.

#### Understanding the Workflow

1. **Always Upload First**: Before any analysis, documents must be uploaded using one of:
   - `upload_swms_from_url` (recommended - works with any public URL)
   - `upload_swms_document` (for base64-encoded content)
   - `upload_swms_from_file` (for local files - only works if server has access)

2. **Use the Returned document_id**: Upload tools return a `document_id` (format: "files/abc123..."). This ID is required for all analysis tools.

3. **Choose the Right Tool**:
   - **Full compliance check**: Use `analyze_swms_compliance` for comprehensive assessment
   - **Quick validation**: Use `quick_check_swms` for specific aspects (hrcw, ppe, emergency, etc.)
   - **Numerical score**: Use `get_compliance_score` for benchmarking
   - **Create new SWMS**: Use `generate_swms_from_description_tool` (no upload needed)
   - **Daily briefings**: Use `generate_toolbox_talk_tool` after uploading

#### Common Patterns

```python
# Pattern 1: Full Analysis Pipeline
upload = upload_swms_from_url(url="https://example.com/swms.pdf")
doc_id = upload["document_id"]
score = get_compliance_score(doc_id, jurisdiction="nsw")
if score["overall_score"] < 85:
    report = analyze_swms_compliance(doc_id, jurisdiction="nsw")
    improvements = suggest_swms_improvements_tool(doc_id)

# Pattern 2: Morning Safety Briefing
upload = upload_swms_from_url(url="https://company.com/todays-swms.pdf")
talk = generate_toolbox_talk_tool(upload["document_id"], duration="5min")
summary = create_worker_summary_tool(upload["document_id"], language_level="simple")

# Pattern 3: Create New SWMS
swms = generate_swms_from_description_tool(
    job_description="Detailed description of work",
    trade_type="electrical",  # Must be from valid list
    site_type="commercial",   # Must be from valid list
    jurisdiction="nsw"         # Must be valid state code
)
```

#### Parameter Validation

- **jurisdiction**: Must be one of: "nsw", "vic", "qld", "wa", "sa", "tas", "act", "nt", "national"
- **duration**: Must be exactly: "5min", "10min", or "15min"
- **check_type**: Must be one of: "hrcw", "ppe", "emergency", "signatures", "hierarchy", "hazards"
- **trade_type**: See tool description for complete list (electrical, plumbing, carpentry, etc.)
- **site_type**: See tool description for complete list (residential, commercial, industrial, etc.)

#### Error Handling

Common errors and solutions:
- "Document not found" - Ensure you're using the correct document_id from upload
- "Invalid jurisdiction" - Use lowercase state codes (nsw, not NSW)
- "Invalid duration" - Must be exactly "5min", "10min", or "15min"

## 🔧 Available Tools

### Core Analysis Tools
| Tool | Description | Key Parameters |
|------|-------------|---------------|
| `upload_swms_document` | Upload from base64 content | `file_content`, `file_name` |
| `upload_swms_from_url` | Upload from URL | `url` |
| `analyze_swms_compliance` | Full compliance analysis | `document_id`, `jurisdiction` |
| `analyze_swms_text` | Analyze text directly | `document_text`, `jurisdiction` |
| `analyze_swms_custom` | Custom prompt analysis | `document_id`, `analysis_prompt` |
| `get_compliance_score` | Numerical scoring | `document_id`, `weighted` |
| `quick_check_swms` | Rapid specific checks | `document_id`, `check_type` |
| `list_jurisdictions` | Get supported jurisdictions | None |
| `get_server_status` | Check server health | None |

### Business Operation Tools (NEW)
| Tool | Description | Key Parameters |
|------|-------------|---------------|
| `generate_swms_from_description_tool` | Create SWMS from job description | `job_description`, `trade_type`, `site_type` |
| `generate_toolbox_talk_tool` | Generate daily safety talks | `document_id`, `duration`, `focus_area` |
| `create_worker_summary_tool` | Simplified safety cards | `document_id`, `language_level`, `include_symbols` |
| `suggest_swms_improvements_tool` | AI improvement suggestions | `document_id`, `improvement_focus` |
| `extract_hazards_from_image_tool` | Vision-based hazard detection | `image_content`, `work_type` |

## 🏛️ Jurisdiction Support

| State/Territory | Code | Legislation | Regulator | Notes |
|----------------|------|-------------|-----------|--------|
| New South Wales | `nsw` | WHS Act 2011 | SafeWork NSW | Default jurisdiction |
| Victoria | `vic` | OHS Act 2004 | WorkSafe Victoria | Uses OHS terminology |
| Queensland | `qld` | WHS Act 2011 | WHSQ | Model laws |
| Western Australia | `wa` | WHS Act 2020 | WorkSafe WA | Adopted 2022 |
| South Australia | `sa` | WHS Act 2012 | SafeWork SA | 3m fall height |
| Tasmania | `tas` | WHS Act 2012 | WorkSafe Tasmania | Model laws |
| ACT | `act` | WHS Act 2011 | WorkSafe ACT | Model laws |
| Northern Territory | `nt` | WHS Act 2011 | NT WorkSafe | Model laws |
| National | `national` | Model Laws | Safe Work Australia | Model framework |

## 📚 Regulatory Document Context

The server automatically includes relevant regulatory documents from R2:

- **Codes of Practice** - Construction work guidelines for each jurisdiction
- **SWMS Templates** - Official templates and examples
- **Information Sheets** - Guidance on SWMS requirements
- **Fact Sheets** - Quick reference materials

Documents are fetched from: `https://pub-bb6a39bd73444f4582d3208b2257c357.r2.dev`

## 🎯 Compliance Assessment Areas

The server evaluates SWMS against six key areas:

1. **Document Control** (10% weight)
   - Project details, version control, responsibilities

2. **HRCW Identification** (20% weight)
   - 18 categories of high-risk construction work

3. **Hazard Identification** (15% weight)
   - Site-specific hazards, risk descriptions

4. **Control Measures** (25% weight)
   - Hierarchy of controls implementation

5. **Monitoring & Review** (15% weight)
   - Review triggers, monitoring procedures

6. **Consultation** (15% weight)
   - Worker consultation, sign-off records

## ☁️ Deployment

### FastMCP Cloud

1. Push to GitHub
2. Connect repository to [FastMCP Cloud](https://fastmcp.cloud)
3. Add environment variables:
   - `GEMINI_API_KEY` (required)
   - `R2_PUBLIC_URL` (optional, defaults to configured URL)
4. Deploy

### Local Development

```bash
# Install FastMCP
pip install fastmcp

# Run in development mode
fastmcp dev server.py

# Access at default MCP endpoint
```

## 🔐 Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (defaults provided)
R2_PUBLIC_URL=https://pub-bb6a39bd73444f4582d3208b2257c357.r2.dev
```

## 📁 Project Structure

```
swms-mcp-server/
├── server.py                 # Main MCP server
├── r2_context.py            # R2 document management
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── regulatory_documents/    # Local document cache
│   ├── national/          # Safe Work Australia docs
│   ├── nsw/              # NSW specific docs
│   ├── vic/              # Victoria OHS docs
│   └── ...               # Other jurisdictions
└── docs/                   # Documentation
    ├── API_DOCUMENTATION.md
    ├── DOCUMENT_MANAGEMENT.md
    └── R2_DEPLOYMENT_STATUS.md
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/jezweb/swims-mcp-server/issues)
- **Documentation**: See `/docs` folder
- **API Reference**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## 🏗️ Built With

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Gemini AI](https://ai.google.dev/) - Document analysis
- [Cloudflare R2](https://www.cloudflare.com/products/r2/) - Document storage
- Python 3.11+ - Runtime environment

## 📈 Version History

- **v1.0.0** - Initial release with multi-jurisdictional support
- **v1.1.0** - Added R2 integration and regulatory context
- **v1.2.0** - Custom analysis and scoring features
- **v2.0.0** - Added 5 business operation tools for SME workflow management

---

Made with ❤️ for Australian construction safety compliance