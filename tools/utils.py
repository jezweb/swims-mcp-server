"""
Shared Utilities for SWMS Tools
================================
Common functions used across multiple tools.
"""

from typing import Dict, Any, Optional
import os

def format_success(message: str, data: Any = None) -> Dict[str, Any]:
    """Format a successful response."""
    response = {
        "status": "success",
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response

def format_error(message: str, error_code: str = "ERROR", details: Any = None) -> Dict[str, Any]:
    """Format an error response."""
    response = {
        "status": "error",
        "message": message,
        "error_code": error_code
    }
    if details is not None:
        response["details"] = details
    return response

def validate_jurisdiction(jurisdiction: str) -> bool:
    """Validate jurisdiction code."""
    valid_jurisdictions = ["nsw", "vic", "qld", "wa", "sa", "tas", "act", "nt", "national"]
    return jurisdiction.lower() in valid_jurisdictions

def get_jurisdiction_terminology(jurisdiction: str) -> str:
    """Get correct terminology for jurisdiction (WHS vs OHS)."""
    if jurisdiction.lower() == "vic":
        return "OHS"
    return "WHS"

def validate_document_id(document_id: str) -> bool:
    """Validate Gemini document ID format."""
    return document_id and document_id.startswith("files/")

def get_trade_context(trade_type: str) -> Dict[str, Any]:
    """Get context information for a trade type."""
    from prompts.swms_prompts import TRADE_TYPES
    return TRADE_TYPES.get(trade_type.lower(), {
        "hazards": ["general construction hazards"],
        "controls": ["standard controls"]
    })

def get_site_context(site_type: str) -> str:
    """Get description for a site type."""
    from prompts.swms_prompts import SITE_TYPES
    return SITE_TYPES.get(site_type.lower(), "general construction site")

def check_api_configured() -> bool:
    """Check if Gemini API is configured."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    return bool(api_key)

def create_file_metadata(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Create metadata for uploaded file."""
    return {
        "document_id": file_info.get("name", ""),
        "mime_type": file_info.get("mimeType", "application/pdf"),
        "size_bytes": file_info.get("sizeBytes", 0),
        "uri": file_info.get("uri", ""),
        "create_time": file_info.get("createTime", ""),
        "expiration_time": file_info.get("expirationTime", "")
    }