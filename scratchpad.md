# SWMS MCP Server Development Scratchpad

## Project Overview
Building a FastMCP server that processes Safe Work Method Statements (SWMS) using Gemini API for NSW construction compliance assessment.

## Key Requirements from Analysis
1. **Document Processing**: PDF/DOCX upload via Gemini Files API
2. **SWMS Assessment**: Based on NSW WHS Regulation 2017
3. **Structured Output**: Detailed compliance report
4. **Simple Architecture**: FastMCP + Gemini integration
5. **Cloud Deployment**: FastMCP Cloud + Cloudflare

## Draft Prompt Analysis (from prompt-idea.md)
The prompt is comprehensive and covers:
- Document Control & Administrative Compliance
- High-Risk Construction Work (HRCW) identification  
- Hazard Identification & Risk Assessment
- Control Measures (Hierarchy of Controls)
- Monitoring, Review, and Communication
- Consultation requirements

## Technical Stack Decisions
- **FastMCP**: Latest version 2.12.0+ (`uv pip install fastmcp`)
- **Gemini API**: google-genai SDK for document processing (`pip install google-genai`)
- **Deployment**: FastMCP Cloud (GitHub integration, one-click deploy)
- **Testing**: Simple TDD approach with pytest
- **Validation**: Basic linting/typecheck with ruff

## FastMCP Cloud Deployment Requirements
- **Module-level server object**: `mcp` variable at module level ✅
- **PyPI dependencies only**: All deps in requirements.txt ✅  
- **Public GitHub repository**: Will push to GitHub ✅
- **Environment variables**: GEMINI_API_KEY via FastMCP Cloud dashboard

## Implementation Plan
1. ✅ Create project structure
2. ✅ Set up FastMCP server with basic tools
3. ✅ Integrate Gemini API for document processing (updated to google-genai SDK)
4. ✅ Implement SWMS assessment logic using draft prompt
5. ✅ Add error handling and validation
6. ✅ Test with example files (server runs successfully)
7. ✅ Deploy to FastMCP Cloud (GitHub → fastmcp.cloud) - ready for deployment
8. ✅ Git commit and push successful implementation

## Completed Implementation ✅

### Server Features
- **FastMCP Server**: Module-level `mcp` object for FastMCP Cloud compatibility
- **Document Upload**: `upload_swms_document()` - uploads PDF/DOCX to Gemini API
- **Compliance Analysis**: `analyze_swms_compliance()` - comprehensive NSW WHS assessment
- **Server Status**: `get_server_status()` - health check and API connectivity test

### Technical Stack
- **FastMCP 2.11.3**: Latest stable version
- **google-genai SDK**: Updated from google-generativeai to google-genai per docs
- **Gemini 2.0 Flash**: Latest model for document analysis
- **Python 3.12**: With virtual environment and proper dependency management

### Assessment Features
- NSW WHS Regulation 2017 compliance framework
- 6 key assessment areas: Document Control, HRCW Identification, Hazard Assessment, Control Measures, Monitoring/Review, Consultation  
- Structured JSON output with detailed findings and actionable recommendations
- Hierarchy of controls validation
- Site-specific hazard identification requirements

### Deployment Ready
- All code committed to git
- .gitignore configured for Python/FastMCP projects
- Ready for GitHub push and FastMCP Cloud deployment
- Environment variable configuration documented

## Enhancement Implementation Plan (2024-12-30)

### Completed Features ✅
1. **Custom Analysis Tool** - Flexible analysis with user-provided prompts
2. **Compliance Scoring System** - Numerical scores for tracking
3. **Quick Check Tool** - Fast checks for specific aspects

### R2 + Gemini Context Implementation (2025-01-01)

#### Architecture Design
- **Storage**: Cloudflare R2 bucket for regulatory PDFs
- **Processing**: Gemini Files API for document context
- **Caching**: File ID caching to avoid re-uploads
- **Structure**: Organized by jurisdiction (national, nsw, vic, qld, etc.)

#### Implementation Plan
1. **R2 Integration** - Fetch regulatory documents from R2 bucket
2. **Document Management** - Upload and cache files with Gemini API
3. **Context Injection** - Include relevant docs in analysis based on jurisdiction
4. **Jurisdiction Support** - Add state/territory parameter to analysis tools

#### Document Sources
- Safe Work Australia SWMS information sheets
- State-specific WHS/OHS regulations
- Model Codes of Practice
- State regulator templates and guides

#### Implementation Progress
- [x] R2 document fetching module - ✅ Created `r2_context.py` with R2ContextManager
- [x] Gemini file caching system - ✅ Implemented file ID caching with 24hr expiry
- [x] Jurisdiction-aware analysis - ✅ Added jurisdiction parameter to all analysis functions
- [x] Context injection in prompts - ✅ Regulatory docs included in Gemini context

### Design Principles
- Keep it simple - no over-engineering
- Modular design for maintainability
- Reuse existing code where possible
- Clear function names and documentation
- Proper error handling
- Test each feature before committing

## Notes
- Use environment variables for API keys
- Follow FastMCP Cloud deployment requirements
- Commit working features incrementally
- Keep backward compatibility