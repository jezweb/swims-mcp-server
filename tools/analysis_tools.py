"""
SWMS Analysis Tools
===================
Tools for analyzing and improving SWMS documents.
"""

from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types

from .utils import (
    format_success,
    format_error,
    validate_document_id,
    validate_jurisdiction,
    check_api_configured
)
from prompts.swms_prompts import (
    IMPROVEMENT_PROMPT,
    HAZARD_EXTRACTION_PROMPT,
    get_incident_context
)


async def suggest_swms_improvements(
    document_id: str,
    incident_history: Optional[List[str]] = None,
    improvement_focus: str = "safety"
) -> Dict[str, Any]:
    """
    Suggest improvements for an existing SWMS document.
    
    Args:
        document_id: ID of the uploaded SWMS document
        incident_history: List of recent incidents to consider
        improvement_focus: Focus area (safety, efficiency, or compliance)
    
    Returns:
        Prioritized improvement recommendations with explanations
    """
    try:
        # Validate inputs
        if not validate_document_id(document_id):
            return format_error("Invalid document ID format")
        
        if improvement_focus not in ["safety", "efficiency", "compliance"]:
            return format_error("Improvement focus must be safety, efficiency, or compliance")
        
        if not check_api_configured():
            return format_error("Gemini API key not configured", "API_KEY_NOT_CONFIGURED")
        
        # Get API client
        import os
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)
        
        # Format incident context
        incident_context = get_incident_context(incident_history or [])
        
        # Format the prompt
        prompt = IMPROVEMENT_PROMPT.format(
            improvement_focus=improvement_focus.capitalize(),
            incident_context=incident_context
        )
        
        # Get the Gemini file object to get the proper URI
        try:
            gemini_file = client.files.get(name=document_id)
            file_uri = gemini_file.uri
        except Exception as e:
            return format_error(f"Document not found: {document_id}. Error: {str(e)}", "DOCUMENT_NOT_FOUND")
        
        # Generate with Gemini
        contents = [
            types.Part.from_uri(
                file_uri=file_uri,
                mime_type=gemini_file.mime_type or "application/pdf"
            ),
            prompt
        ]
        
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.6,
                top_p=0.95,
                max_output_tokens=3000,
                response_mime_type="text/plain"
            )
        )
        
        if not response or not response.text:
            return format_error("Failed to generate improvement suggestions", "GENERATION_FAILED")
        
        # Parse the response
        suggestions_text = response.text.strip()
        
        # Extract recommendations by category
        categories = {
            "critical_gaps": [],
            "quick_wins": [],
            "best_practices": [],
            f"{improvement_focus}_specific": []
        }
        
        current_category = None
        current_items = []
        
        for line in suggestions_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for category headers
            if "Critical Gaps" in line:
                current_category = "critical_gaps"
                current_items = []
            elif "Quick Wins" in line:
                if current_category and current_items:
                    categories[current_category] = current_items
                current_category = "quick_wins"
                current_items = []
            elif "Best Practice" in line:
                if current_category and current_items:
                    categories[current_category] = current_items
                current_category = "best_practices"
                current_items = []
            elif improvement_focus.capitalize() in line and "Specific" in line:
                if current_category and current_items:
                    categories[current_category] = current_items
                current_category = f"{improvement_focus}_specific"
                current_items = []
            elif current_category and line.startswith('-'):
                current_items.append(line[1:].strip())
        
        # Add last category
        if current_category and current_items:
            categories[current_category] = current_items
        
        # Count total recommendations
        total_recommendations = sum(len(items) for items in categories.values())
        
        return {
            "status": "success",
            "message": "Improvement suggestions generated successfully",
            "improvements": {
                "focus_area": improvement_focus,
                "total_recommendations": total_recommendations,
                "categories": categories,
                "full_analysis": suggestions_text
            },
            "implementation_priority": [
                "1. Address critical gaps immediately",
                "2. Implement quick wins this week",
                "3. Plan best practices for next review",
                f"4. Focus on {improvement_focus} improvements ongoing"
            ],
            "incident_history_considered": len(incident_history) if incident_history else 0
        }
        
    except Exception as e:
        return format_error(
            f"Error generating improvement suggestions: {str(e)}",
            "GENERATION_ERROR",
            {"error_type": type(e).__name__}
        )


async def extract_hazards_from_image(
    image_content: str,
    work_type: str,
    jurisdiction: str = "nsw"
) -> Dict[str, Any]:
    """
    Extract and identify hazards from a construction site image.
    
    Args:
        image_content: Base64 encoded image content
        work_type: Type of work being performed
        jurisdiction: State/territory for specific requirements
    
    Returns:
        List of identified hazards with risk ratings
    """
    try:
        # Validate inputs
        if not image_content:
            return format_error("Image content is required")
        
        if not work_type:
            return format_error("Work type is required")
        
        if not validate_jurisdiction(jurisdiction):
            return format_error(f"Invalid jurisdiction: {jurisdiction}")
        
        if not check_api_configured():
            return format_error("Gemini API key not configured", "API_KEY_NOT_CONFIGURED")
        
        # Get API client
        import os
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)
        
        # Format the prompt
        prompt = HAZARD_EXTRACTION_PROMPT.format(
            work_type=work_type,
            jurisdiction=jurisdiction.upper()
        )
        
        # Create image part
        image_part = types.Part.from_bytes(
            data=image_content.encode() if isinstance(image_content, str) else image_content,
            mime_type="image/jpeg"  # Adjust based on actual image type
        )
        
        # Generate with Gemini
        contents = [image_part, prompt]
        
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.4,  # Lower temperature for factual analysis
                top_p=0.9,
                max_output_tokens=2500,
                response_mime_type="text/plain"
            )
        )
        
        if not response or not response.text:
            return format_error("Failed to analyze image for hazards", "GENERATION_FAILED")
        
        # Parse the response
        hazards_text = response.text.strip()
        
        # Extract hazard categories
        hazard_categories = {
            "immediate_dangers": [],
            "high_risk_hazards": [],
            "general_hazards": [],
            "work_specific_hazards": []
        }
        
        current_category = None
        
        for line in hazards_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check for category headers
            if "Immediate Danger" in line:
                current_category = "immediate_dangers"
            elif "High Risk" in line:
                current_category = "high_risk_hazards"
            elif "General Hazard" in line:
                current_category = "general_hazards"
            elif "Work-Specific" in line or work_type in line:
                current_category = "work_specific_hazards"
            elif current_category and line.startswith('-'):
                # Parse hazard entry
                hazard_text = line[1:].strip()
                
                # Try to extract risk level
                risk_level = "Medium"  # Default
                if "High" in hazard_text or "high" in hazard_text:
                    risk_level = "High"
                elif "Low" in hazard_text or "low" in hazard_text:
                    risk_level = "Low"
                
                hazard_entry = {
                    "description": hazard_text,
                    "risk_level": risk_level,
                    "category": current_category.replace('_', ' ').title()
                }
                
                hazard_categories[current_category].append(hazard_entry)
        
        # Count total hazards
        total_hazards = sum(len(hazards) for hazards in hazard_categories.values())
        high_risk_count = sum(
            1 for category in hazard_categories.values() 
            for hazard in category 
            if hazard.get("risk_level") == "High"
        )
        
        return {
            "status": "success",
            "message": "Image analyzed successfully for hazards",
            "hazard_analysis": {
                "work_type": work_type,
                "jurisdiction": jurisdiction,
                "total_hazards_identified": total_hazards,
                "high_risk_count": high_risk_count,
                "hazard_categories": hazard_categories,
                "full_analysis": hazards_text
            },
            "recommended_actions": [
                "Address immediate dangers before any work proceeds",
                "Implement controls for all high-risk hazards",
                "Update SWMS to include identified site-specific hazards",
                "Brief all workers on hazards visible in work area"
            ],
            "image_metadata": {
                "analyzed": True,
                "work_type": work_type,
                "jurisdiction": jurisdiction
            }
        }
        
    except Exception as e:
        return format_error(
            f"Error analyzing image: {str(e)}",
            "IMAGE_ANALYSIS_ERROR",
            {"error_type": type(e).__name__}
        )