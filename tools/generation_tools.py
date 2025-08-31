"""
SWMS Generation Tools
=====================
Tools for generating SWMS documents from descriptions.
"""

from typing import Dict, Any, Optional
from google import genai
from google.genai import types

from .utils import (
    format_success, 
    format_error, 
    validate_jurisdiction,
    get_jurisdiction_terminology,
    get_trade_context,
    get_site_context,
    check_api_configured
)
from prompts.swms_prompts import GENERATE_SWMS_PROMPT


async def generate_swms_from_description(
    job_description: str,
    trade_type: str,
    site_type: str = "commercial",
    jurisdiction: str = "nsw"
) -> Dict[str, Any]:
    """
    Generate a complete SWMS from a job description.
    
    Args:
        job_description: Plain English description of the work
        trade_type: Type of trade (electrical, plumbing, carpentry, etc.)
        site_type: Type of site (residential, commercial, industrial, etc.)
        jurisdiction: State/territory code (nsw, vic, qld, etc.)
    
    Returns:
        Complete SWMS document ready for review
    """
    try:
        # Validate inputs
        if not job_description:
            return format_error("Job description is required")
        
        if not trade_type:
            return format_error("Trade type is required")
        
        if not validate_jurisdiction(jurisdiction):
            return format_error(f"Invalid jurisdiction: {jurisdiction}")
        
        if not check_api_configured():
            return format_error("Gemini API key not configured", "API_KEY_NOT_CONFIGURED")
        
        # Get context
        trade_context = get_trade_context(trade_type)
        site_context = get_site_context(site_type)
        terminology = get_jurisdiction_terminology(jurisdiction)
        
        # Import dependencies
        import os
        from r2_context import R2ContextManager
        
        # Get API client
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)
        r2_context = R2ContextManager(client)
        
        # Get regulatory context with error handling
        try:
            context_files = await r2_context.get_context_for_jurisdiction(jurisdiction)
        except Exception as e:
            print(f"Warning: Could not load regulatory context: {e}")
            context_files = []
        
        # Format the prompt
        prompt = GENERATE_SWMS_PROMPT.format(
            job_description=job_description,
            trade_type=trade_type,
            site_type=site_type,
            jurisdiction=jurisdiction.upper()
        )
        
        # Add trade and site context
        prompt += f"\n\nTrade Context:\nTypical hazards: {', '.join(trade_context['hazards'])}"
        prompt += f"\nCommon controls: {', '.join(trade_context['controls'])}"
        prompt += f"\n\nSite Context: {site_context}"
        prompt += f"\n\nUse {terminology} terminology for {jurisdiction.upper()}."
        
        # Generate with Gemini
        contents = []
        
        # Add regulatory documents as context (file objects directly)
        for file_obj in context_files:
            if file_obj:  # Only add valid file objects
                contents.append(file_obj)
        
        # Add the prompt
        contents.append(prompt)
        
        # Generate response
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=8000,
                response_mime_type="text/plain"
            )
        )
        
        if not response or not response.text:
            return format_error("Failed to generate SWMS", "GENERATION_FAILED")
        
        # Parse the response
        swms_document = response.text.strip()
        
        # Calculate basic metrics
        lines = swms_document.split('\n')
        sections = [line for line in lines if line.strip().startswith('#')]
        
        return {
            "status": "success",
            "message": "SWMS generated successfully",
            "swms_document": swms_document,
            "metadata": {
                "job_description": job_description,
                "trade_type": trade_type,
                "site_type": site_type,
                "jurisdiction": jurisdiction,
                "terminology": terminology,
                "regulatory_context_included": len(context_files) > 0,
                "document_stats": {
                    "total_lines": len(lines),
                    "sections": len(sections),
                    "approximate_pages": len(swms_document) // 3000  # Rough estimate
                }
            },
            "next_steps": [
                "Review and customize for site-specific conditions",
                "Add company logo and contact details",
                "Obtain worker signatures before commencing work",
                "File with principal contractor"
            ]
        }
        
    except Exception as e:
        return format_error(
            f"Error generating SWMS: {str(e)}",
            "GENERATION_ERROR",
            {"error_type": type(e).__name__}
        )