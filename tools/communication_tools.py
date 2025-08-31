"""
SWMS Communication Tools
========================
Tools for creating toolbox talks and worker summaries from SWMS documents.
"""

from typing import Dict, Any, Optional
from google import genai
from google.genai import types

from .utils import (
    format_success,
    format_error,
    validate_document_id,
    check_api_configured
)
from prompts.swms_prompts import (
    TOOLBOX_TALK_PROMPT,
    WORKER_SUMMARY_PROMPT,
    get_visual_instructions,
    get_emoji_symbols,
    HAZARD_SYMBOLS
)


async def generate_toolbox_talk(
    document_id: str,
    duration: str = "5min",
    focus_area: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a toolbox talk from a SWMS document.
    
    Args:
        document_id: ID of the uploaded SWMS document
        duration: Duration of talk (5min, 10min, or 15min)
        focus_area: Specific area to focus on (optional)
    
    Returns:
        Bullet points and talking notes for supervisors
    """
    try:
        # Validate inputs
        if not validate_document_id(document_id):
            return format_error("Invalid document ID format")
        
        if duration not in ["5min", "10min", "15min"]:
            return format_error("Duration must be 5min, 10min, or 15min")
        
        if not check_api_configured():
            return format_error("Gemini API key not configured", "API_KEY_NOT_CONFIGURED")
        
        # Get API client
        import os
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)
        
        # Format the prompt
        prompt = TOOLBOX_TALK_PROMPT.format(
            duration=duration,
            focus_area=focus_area or "general safety for today's work"
        )
        
        # Generate with Gemini
        contents = [
            types.Part.from_uri(
                file_uri=document_id,
                mime_type="application/pdf"
            ),
            prompt
        ]
        
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.5,
                top_p=0.9,
                max_output_tokens=2000,
                response_mime_type="text/plain"
            )
        )
        
        if not response or not response.text:
            return format_error("Failed to generate toolbox talk", "GENERATION_FAILED")
        
        # Parse the response
        talk_content = response.text.strip()
        
        # Extract sections
        sections = {}
        current_section = None
        current_content = []
        
        for line in talk_content.split('\n'):
            if line.strip().startswith('**') and line.strip().endswith('**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.strip('*').strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return {
            "status": "success",
            "message": "Toolbox talk generated successfully",
            "toolbox_talk": {
                "duration": duration,
                "focus_area": focus_area or "general safety",
                "content": talk_content,
                "sections": sections
            },
            "delivery_tips": [
                f"Keep it interactive - ask questions throughout the {duration} talk",
                "Use real examples from the site",
                "Check understanding before starting work",
                "Document attendance and any concerns raised"
            ]
        }
        
    except Exception as e:
        return format_error(
            f"Error generating toolbox talk: {str(e)}",
            "GENERATION_ERROR",
            {"error_type": type(e).__name__}
        )


async def create_worker_summary(
    document_id: str,
    language_level: str = "simple",
    include_symbols: bool = True
) -> Dict[str, Any]:
    """
    Create a simplified worker summary from a SWMS document.
    
    Args:
        document_id: ID of the uploaded SWMS document
        language_level: Language complexity (simple, visual, standard)
        include_symbols: Whether to include emoji symbols for hazards
    
    Returns:
        Simplified safety card format for workers
    """
    try:
        # Validate inputs
        if not validate_document_id(document_id):
            return format_error("Invalid document ID format")
        
        if language_level not in ["simple", "visual", "standard"]:
            return format_error("Language level must be simple, visual, or standard")
        
        if not check_api_configured():
            return format_error("Gemini API key not configured", "API_KEY_NOT_CONFIGURED")
        
        # Get API client
        import os
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)
        
        # Get visual instructions
        visual_instructions = get_visual_instructions(include_symbols)
        
        # Format the prompt
        prompt = WORKER_SUMMARY_PROMPT.format(
            language_level=language_level,
            include_symbols=include_symbols,
            emoji_symbols="Use relevant emoji symbols" if include_symbols else "",
            visual_instructions=visual_instructions
        )
        
        # Generate with Gemini
        contents = [
            types.Part.from_uri(
                file_uri=document_id,
                mime_type="application/pdf"
            ),
            prompt
        ]
        
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.3,  # Lower temperature for consistency
                top_p=0.9,
                max_output_tokens=1500,
                response_mime_type="text/plain"
            )
        )
        
        if not response or not response.text:
            return format_error("Failed to create worker summary", "GENERATION_FAILED")
        
        # Parse the response
        summary_content = response.text.strip()
        
        # Add visual symbols if requested
        if include_symbols:
            # Replace common hazard words with symbols
            for hazard, symbol in HAZARD_SYMBOLS.items():
                summary_content = summary_content.replace(
                    hazard.capitalize(), 
                    f"{symbol} {hazard.capitalize()}"
                )
        
        # Count key metrics
        lines = summary_content.split('\n')
        bullet_points = [line for line in lines if line.strip().startswith('-')]
        
        return {
            "status": "success",
            "message": "Worker summary created successfully",
            "worker_summary": {
                "language_level": language_level,
                "include_symbols": include_symbols,
                "content": summary_content,
                "format": "safety_card",
                "metrics": {
                    "total_lines": len(lines),
                    "bullet_points": len(bullet_points),
                    "estimated_reading_time": "1-2 minutes"
                }
            },
            "usage_instructions": [
                "Print on bright colored paper for visibility",
                "Display at site entry and work areas",
                "Review with workers during induction",
                "Available in multiple languages on request"
            ]
        }
        
    except Exception as e:
        return format_error(
            f"Error creating worker summary: {str(e)}",
            "GENERATION_ERROR",
            {"error_type": type(e).__name__}
        )