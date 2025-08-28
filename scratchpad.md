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
2. ⏳ Set up FastMCP server with basic tools
3. ⏳ Integrate Gemini API for document processing
4. ⏳ Implement SWMS assessment logic using draft prompt
5. ⏳ Add error handling and validation
6. ⏳ Test with example files
7. ⏳ Deploy to FastMCP Cloud (GitHub → fastmcp.cloud)
8. ⏳ Git commit and push

## Next Steps
- Verify current directory structure
- Check if git repo exists
- Set up basic FastMCP server structure
- Implement core SWMS processing tools

## Notes
- Keep it simple - no over-engineering
- Modular design for maintainability
- Use environment variables for API keys
- Follow FastMCP Cloud deployment requirements