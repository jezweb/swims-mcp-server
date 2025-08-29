"""
SWMS MCP Server - Safe Work Method Statement Analysis
"""

import os
import json
import base64
import tempfile
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configure Gemini API client
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

# MUST be at module level for FastMCP Cloud
mcp = FastMCP("swms-analysis-server")

@mcp.tool()
async def upload_swms_document(
    file_content: str,
    file_name: str,
    mime_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload a SWMS document from base64-encoded content to Gemini API.
    
    Args:
        file_content: Base64-encoded file content
        file_name: Name of the file (e.g., "safety_plan.pdf")
        mime_type: Optional MIME type (auto-detected if not provided)
        
    Returns:
        Dictionary with upload status and document ID
    """
    try:
        if not client:
            return {
                "status": "error",
                "message": "Gemini API key not configured"
            }
        
        # Decode base64 content
        try:
            file_bytes = base64.b64decode(file_content)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Invalid base64 content: {str(e)}"
            }
        
        # Auto-detect MIME type if not provided
        if not mime_type:
            extension = Path(file_name).suffix.lower()
            if extension == '.pdf':
                mime_type = 'application/pdf'
            elif extension in ['.docx', '.doc']:
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported file format: {extension}. Only PDF and DOCX are supported."
                }
        
        # Create temporary file for upload
        with tempfile.NamedTemporaryFile(suffix=Path(file_name).suffix, delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name
        
        try:
            # Upload file to Gemini
            uploaded_file = client.files.upload(
                path=temp_path,
                config=types.UploadFileConfig(
                    display_name=file_name,
                    mime_type=mime_type
                )
            )
            
            return {
                "status": "success",
                "message": f"Document {file_name} uploaded successfully",
                "document_id": uploaded_file.name,
                "file_info": {
                    "name": uploaded_file.display_name,
                    "mime_type": uploaded_file.mime_type,
                    "uri": uploaded_file.uri,
                    "size_bytes": len(file_bytes)
                }
            }
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Failed to upload document: {str(e)}"
        }

@mcp.tool()
async def upload_swms_from_url(url: str) -> Dict[str, Any]:
    """
    Upload a SWMS document from a URL to Gemini API.
    
    Args:
        url: URL of the SWMS document (PDF or DOCX)
        
    Returns:
        Dictionary with upload status and document ID
    """
    try:
        if not client:
            return {
                "status": "error",
                "message": "Gemini API key not configured"
            }
        
        # Download file from URL
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            return {
                "status": "error",
                "message": f"Failed to download from URL: {str(e)}"
            }
        
        # Determine file name and MIME type from URL and headers
        file_name = url.split('/')[-1].split('?')[0]
        if not file_name or '.' not in file_name:
            file_name = "document.pdf"  # Default name
        
        content_type = response.headers.get('content-type', '')
        if 'pdf' in content_type:
            mime_type = 'application/pdf'
            if not file_name.endswith('.pdf'):
                file_name = file_name.split('.')[0] + '.pdf'
        elif 'wordprocessingml' in content_type or 'msword' in content_type:
            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            if not file_name.endswith('.docx'):
                file_name = file_name.split('.')[0] + '.docx'
        else:
            # Try to detect from file extension
            extension = Path(file_name).suffix.lower()
            if extension == '.pdf':
                mime_type = 'application/pdf'
            elif extension in ['.docx', '.doc']:
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            else:
                return {
                    "status": "error",
                    "message": f"Could not determine file type from URL. Ensure it's a PDF or DOCX file."
                }
        
        # Create temporary file for upload
        with tempfile.NamedTemporaryFile(suffix=Path(file_name).suffix, delete=False) as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        try:
            # Upload file to Gemini
            uploaded_file = client.files.upload(
                path=temp_path,
                config=types.UploadFileConfig(
                    display_name=file_name,
                    mime_type=mime_type
                )
            )
            
            return {
                "status": "success",
                "message": f"Document {file_name} uploaded successfully from URL",
                "document_id": uploaded_file.name,
                "file_info": {
                    "name": uploaded_file.display_name,
                    "mime_type": uploaded_file.mime_type,
                    "uri": uploaded_file.uri,
                    "size_bytes": len(response.content),
                    "source_url": url
                }
            }
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Failed to upload document from URL: {str(e)}"
        }

@mcp.tool()
async def analyze_swms_compliance(document_id: str) -> Dict[str, Any]:
    """
    Analyze a SWMS document for NSW WHS compliance using Gemini API.
    
    Args:
        document_id: ID of the uploaded SWMS document
        
    Returns:
        Detailed compliance assessment report
    """
    try:
        if not client:
            return {
                "status": "error",
                "message": "Gemini API key not configured"
            }
        
        # Get the uploaded file
        try:
            uploaded_file = client.files.get(name=document_id)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Document not found: {document_id}"
            }
        
        # NSW SWMS Assessment Prompt
        assessment_prompt = """
## System Prompt for Assessing Safe Work Method Statements (SWMS) in NSW Construction

**Objective:** Analyze the provided Safe Work Method Statement (SWMS) for completeness and compliance with NSW Work Health and Safety (WHS) Regulation 2017. Generate a detailed compliance report.

**Instructions:**

You are an AI assistant with expertise in NSW Work Health and Safety (WHS) legislation for the construction industry. Assess the SWMS document according to these key areas:

**1. Document Control and Administrative Compliance:**
- Project details (name, address, Principal Contractor, subcontractor, ABN)
- Version control, document numbers, dates
- Personnel identification and responsibilities
- Worker sign-off provisions

**2. Identification of High-Risk Construction Work (HRCW):**
- Explicit identification of HRCW activities
- Correct categorization per NSW WHS Regulation 2017 (18 categories)

**3. Hazard Identification and Risk Assessment:**
- Logical task breakdown
- Site-specific (not generic) hazard identification
- Clear risk descriptions for each hazard

**4. Control Measures:**
- Adherence to hierarchy of controls (Elimination → Substitution → Isolation → Engineering → Administrative → PPE)
- Sufficient detail for worker understanding
- Clear implementation descriptions

**5. Monitoring, Review, and Communication:**
- Defined monitoring responsibilities
- Review triggers (work changes, incidents, ineffective controls)
- Communication plans for workers

**6. Consultation:**
- Evidence of worker consultation
- Sign-off sheets or consultation records

**Output Format Required:**

Return a JSON object with this exact structure:

{
  "status": "success",
  "project_details": {
    "project_name": "[extracted or 'Not specified']",
    "principal_contractor": "[extracted or 'Not specified']",
    "subcontractor": "[extracted or 'Not specified']",
    "swms_title": "[extracted or 'Not specified']"
  },
  "overall_assessment": "Compliant|Partially Compliant|Non-Compliant",
  "summary": "[Brief high-level summary of compliance status]",
  "detailed_analysis": {
    "document_control": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    },
    "hrcw_identification": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    },
    "hazard_identification": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    },
    "control_measures": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    },
    "monitoring_review": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    },
    "consultation": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    }
  },
  "urgent_actions": [
    "[List critical non-compliances that must be addressed before work commences]"
  ],
  "recommendations": [
    "[List other improvements for full compliance]"
  ]
}

Analyze the attached SWMS document thoroughly and provide the assessment in the exact JSON format above.
"""
        
        # Generate analysis using Gemini model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                assessment_prompt,
                types.Part.from_uri(
                    file_uri=uploaded_file.uri,
                    mime_type=uploaded_file.mime_type
                )
            ]
        )
        
        # Parse the JSON response
        try:
            # Extract JSON from response text (handle potential markdown formatting)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:-3].strip()
            
            analysis_result = json.loads(response_text)
            
            # Ensure required structure
            if "status" not in analysis_result:
                analysis_result["status"] = "success"
                
            return analysis_result
            
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            return {
                "status": "success",
                "overall_assessment": "Analysis Completed",
                "summary": "Document analyzed but response format needs adjustment",
                "raw_response": response.text[:2000],  # Truncate for safety
                "parse_error": str(e)
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to analyze document: {str(e)}"
        }

@mcp.tool()
async def analyze_swms_text(
    document_text: str,
    document_name: Optional[str] = "SWMS Document"
) -> Dict[str, Any]:
    """
    Analyze SWMS text content directly for NSW WHS compliance.
    
    Args:
        document_text: The SWMS document content as plain text or markdown
        document_name: Optional name for the document
        
    Returns:
        Detailed compliance assessment report
    """
    try:
        if not client:
            return {
                "status": "error",
                "message": "Gemini API key not configured"
            }
        
        # NSW SWMS Assessment Prompt (same as file-based analysis)
        assessment_prompt = """
## System Prompt for Assessing Safe Work Method Statements (SWMS) in NSW Construction

**Objective:** Analyze the provided Safe Work Method Statement (SWMS) for completeness and compliance with NSW Work Health and Safety (WHS) Regulation 2017. Generate a detailed compliance report.

**Instructions:**

You are an AI assistant with expertise in NSW Work Health and Safety (WHS) legislation for the construction industry. Assess the SWMS document according to these key areas:

**1. Document Control and Administrative Compliance:**
- Project details (name, address, Principal Contractor, subcontractor, ABN)
- Version control, document numbers, dates
- Personnel identification and responsibilities
- Worker sign-off provisions

**2. Identification of High-Risk Construction Work (HRCW):**
- Explicit identification of HRCW activities
- Correct categorization per NSW WHS Regulation 2017 (18 categories)

**3. Hazard Identification and Risk Assessment:**
- Logical task breakdown
- Site-specific (not generic) hazard identification
- Clear risk descriptions for each hazard

**4. Control Measures:**
- Adherence to hierarchy of controls (Elimination → Substitution → Isolation → Engineering → Administrative → PPE)
- Sufficient detail for worker understanding
- Clear implementation descriptions

**5. Monitoring, Review, and Communication:**
- Defined monitoring responsibilities
- Review triggers (work changes, incidents, ineffective controls)
- Communication plans for workers

**6. Consultation:**
- Evidence of worker consultation
- Sign-off sheets or consultation records

**Output Format Required:**

Return a JSON object with this exact structure:

{
  "status": "success",
  "project_details": {
    "project_name": "[extracted or 'Not specified']",
    "principal_contractor": "[extracted or 'Not specified']",
    "subcontractor": "[extracted or 'Not specified']",
    "swms_title": "[extracted or 'Not specified']"
  },
  "overall_assessment": "Compliant|Partially Compliant|Non-Compliant",
  "summary": "[Brief high-level summary of compliance status]",
  "detailed_analysis": {
    "document_control": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    },
    "hrcw_identification": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    },
    "hazard_identification": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    },
    "control_measures": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    },
    "monitoring_review": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    },
    "consultation": {
      "status": "Compliant|Partially Compliant|Non-Compliant",
      "comments": "[Specific findings and recommendations]"
    }
  },
  "urgent_actions": [
    "[List critical non-compliances that must be addressed before work commences]"
  ],
  "recommendations": [
    "[List other improvements for full compliance]"
  ]
}

Analyze the attached SWMS document text thoroughly and provide the assessment in the exact JSON format above.

DOCUMENT NAME: """ + document_name + """

DOCUMENT CONTENT:
""" + document_text
        
        # Generate analysis using Gemini model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=assessment_prompt
        )
        
        # Parse the JSON response
        try:
            # Extract JSON from response text (handle potential markdown formatting)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:-3].strip()
            
            analysis_result = json.loads(response_text)
            
            # Ensure required structure
            if "status" not in analysis_result:
                analysis_result["status"] = "success"
                
            return analysis_result
            
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            return {
                "status": "success",
                "overall_assessment": "Analysis Completed",
                "summary": "Document analyzed but response format needs adjustment",
                "raw_response": response.text[:2000],  # Truncate for safety
                "parse_error": str(e)
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to analyze document: {str(e)}"
        }

@mcp.tool()
async def get_server_status() -> Dict[str, Any]:
    """
    Get the current status of the SWMS analysis server.
    
    Returns:
        Server status and configuration info
    """
    api_configured = bool(api_key)
    
    # Test API connection if configured
    api_status = "not_configured"
    if api_configured and client:
        try:
            # Simple test to verify API connectivity
            models = client.models.list()
            api_status = "active" if models else "connection_failed"
        except Exception as e:
            api_status = f"error: {str(e)}"
    
    return {
        "status": "active",
        "server_name": "SWMS Analysis Server",
        "version": "1.0.0",
        "supported_formats": ["PDF", "DOCX"],
        "gemini_api": {
            "configured": api_configured,
            "status": api_status
        },
        "capabilities": [
            "upload_swms_document",
            "upload_swms_from_url",
            "analyze_swms_text",
            "analyze_swms_compliance", 
            "get_server_status"
        ]
    }

# Remove the if __name__ == "__main__" block for FastMCP Cloud compatibility
# The server should be run using: fastmcp run server.py