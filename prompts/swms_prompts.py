"""
SWMS Prompt Templates
=====================
Reusable prompt templates for SWMS generation and analysis.
"""

# Trade types with typical hazards and controls
TRADE_TYPES = {
    "electrical": {
        "hazards": ["electrical shock", "arc flash", "working at heights", "confined spaces"],
        "controls": ["lockout/tagout", "test before touch", "insulated tools", "PPE"]
    },
    "plumbing": {
        "hazards": ["confined spaces", "hot work", "manual handling", "slips/trips"],
        "controls": ["ventilation", "hot work permits", "mechanical aids", "housekeeping"]
    },
    "carpentry": {
        "hazards": ["power tools", "manual handling", "falls", "struck by objects"],
        "controls": ["tool guards", "lifting techniques", "edge protection", "exclusion zones"]
    },
    "scaffolding": {
        "hazards": ["falls from height", "falling objects", "structural collapse", "manual handling"],
        "controls": ["harness points", "toe boards", "load limits", "inspection tags"]
    },
    "demolition": {
        "hazards": ["structural collapse", "asbestos", "noise", "dust", "falling debris"],
        "controls": ["exclusion zones", "asbestos survey", "hearing protection", "dust suppression"]
    },
    "concrete": {
        "hazards": ["concrete burns", "manual handling", "vibration", "dust"],
        "controls": ["skin protection", "mechanical aids", "anti-vibration gloves", "wet cutting"]
    },
    "roofing": {
        "hazards": ["falls from height", "fragile surfaces", "weather conditions", "hot materials"],
        "controls": ["edge protection", "roof ladders", "weather monitoring", "heat protection"]
    },
    "excavation": {
        "hazards": ["cave-ins", "underground services", "mobile plant", "confined spaces"],
        "controls": ["shoring/benching", "service location", "spotters", "gas monitoring"]
    }
}

# Site types with specific requirements
SITE_TYPES = {
    "residential": "domestic construction site with public interface",
    "commercial": "commercial building site with controlled access",
    "industrial": "industrial facility with specialized hazards",
    "infrastructure": "civil/infrastructure project with traffic management",
    "renovation": "existing building with ongoing operations"
}

# Prompt for generating SWMS from description
GENERATE_SWMS_PROMPT = """
You are an expert safety consultant creating a Safe Work Method Statement (SWMS) for Australian construction work.

Job Description: {job_description}
Trade Type: {trade_type}
Site Type: {site_type}
Jurisdiction: {jurisdiction}

Using the regulatory context provided and your knowledge of {jurisdiction} WHS/OHS requirements, create a comprehensive SWMS that includes:

1. **Document Control Section**
   - SWMS title and reference number
   - Date of creation and version
   - Principal contractor details
   - Subcontractor/PCBU details
   - Project name and location
   - Scope of works

2. **High Risk Construction Work (HRCW) Identification**
   - Identify which of the 18 HRCW categories apply
   - Note specific threshold requirements for {jurisdiction}

3. **Task Breakdown**
   - List all work tasks in sequence
   - Include preparation, execution, and cleanup phases

4. **Hazard Identification and Risk Assessment**
   - For each task, identify specific hazards
   - Include site-specific hazards based on {site_type} environment
   - Rate risks (before controls)

5. **Control Measures**
   - Apply hierarchy of controls (elimination to PPE)
   - Include specific controls for {trade_type} work
   - Reference relevant codes of practice

6. **PPE Requirements**
   - List mandatory PPE for each task
   - Include specific PPE for {trade_type} hazards

7. **Training and Competency**
   - Required licenses/tickets
   - Trade qualifications
   - Site inductions

8. **Emergency Procedures**
   - Emergency contacts
   - First aid arrangements
   - Evacuation procedures
   - Incident reporting

9. **Monitoring and Review**
   - Review triggers
   - Inspection requirements
   - Update procedures

10. **Consultation and Sign-off**
    - Worker consultation record
    - Signature section for workers

Format the SWMS professionally with clear sections and practical, actionable content.
Focus on real safety outcomes, not just compliance.
"""

# Prompt for generating toolbox talk
TOOLBOX_TALK_PROMPT = """
Based on this SWMS document, create a {duration} toolbox talk for site workers.

Focus Area: {focus_area}

Extract the most critical safety information and format it as:

1. **Today's Key Risks** (2-3 main hazards)
2. **Critical Controls** (must-do safety measures)
3. **PPE Reminder** (what to wear)
4. **Watch Out For** (specific things to observe)
5. **Emergency Info** (key contacts/procedures)
6. **Questions to Ask Workers** (engagement prompts)

Keep language simple and direct. Use bullet points.
Make it practical and relevant to today's work.
Duration should be approximately {duration}.
"""

# Prompt for creating worker summary
WORKER_SUMMARY_PROMPT = """
Create a simplified safety summary of this SWMS for workers.

Language Level: {language_level}
Include Visual Symbols: {include_symbols}

Format as a single-page safety card with:

1. **Job:** What we're doing today
2. **Main Dangers:** {emoji_symbols}
   - List 5 key hazards with simple descriptions
3. **Stay Safe:** 
   - 5 must-do safety rules in simple language
4. **Wear This:** PPE requirements with symbols
5. **If Something Goes Wrong:**
   - Who to tell
   - Where to go
   - Emergency number

Use short sentences. One idea per line.
{visual_instructions}
Make it easy to understand for all literacy levels.
"""

# Visual symbols for hazards
HAZARD_SYMBOLS = {
    "electrical": "⚡",
    "fall": "⬇️",
    "chemical": "☣️",
    "fire": "🔥",
    "cutting": "✂️",
    "crushing": "🔨",
    "noise": "🔊",
    "dust": "💨",
    "heat": "🌡️",
    "cold": "❄️",
    "radiation": "☢️",
    "biological": "🦠",
    "manual": "💪",
    "slip": "⚠️",
    "vehicle": "🚗",
    "confined": "📦"
}

# Prompt for suggesting improvements
IMPROVEMENT_PROMPT = """
Analyze this SWMS and suggest improvements based on best practices and {improvement_focus}.

{incident_context}

Provide recommendations in these categories:

1. **Critical Gaps** (must fix immediately)
   - Safety issues that need urgent attention
   
2. **Quick Wins** (easy improvements)
   - Simple changes with high impact
   
3. **Best Practice Enhancements**
   - Industry-leading practices to adopt
   
4. **{improvement_focus} Specific**
   - Targeted improvements for the focus area

For each recommendation:
- Explain WHY it's important
- Describe HOW to implement
- Note expected BENEFIT

Prioritize practical, actionable improvements that will make real difference to safety outcomes.
Reference relevant standards and codes where applicable.
"""

# Prompt for extracting hazards from image
HAZARD_EXTRACTION_PROMPT = """
Analyze this construction site image for safety hazards relevant to {work_type} work.

Jurisdiction: {jurisdiction}

Identify and categorize hazards:

1. **Immediate Dangers** (stop work required)
   - Life-threatening hazards needing immediate action

2. **High Risk Hazards** 
   - Related to 18 HRCW categories
   - Include specific {jurisdiction} threshold considerations

3. **General Hazards**
   - Common construction site hazards
   - Environmental conditions
   - Housekeeping issues

4. **Work-Specific Hazards**
   - Hazards specific to {work_type} activities
   - Tool and equipment issues
   - Access and egress problems

For each hazard:
- Describe what you see
- Explain the risk
- Suggest immediate control measures
- Rate the risk level (High/Medium/Low)

Also note any good safety practices visible in the image.
"""

def get_visual_instructions(include_symbols: bool) -> str:
    """Get instructions for visual formatting."""
    if include_symbols:
        return "Use emoji symbols for hazards: ⚡ electrical, ⬇️ falls, 🔥 hot work, etc."
    return "Use CAPITAL LETTERS for emphasis on key dangers."

def get_incident_context(incident_history: list) -> str:
    """Format incident history for context."""
    if not incident_history:
        return "Consider general industry incident trends."
    
    context = "Recent incidents to consider:\n"
    for incident in incident_history:
        context += f"- {incident}\n"
    return context

def get_emoji_symbols(hazards: list) -> str:
    """Get emoji symbols for hazards."""
    symbols = []
    for hazard in hazards:
        for key, symbol in HAZARD_SYMBOLS.items():
            if key in hazard.lower():
                symbols.append(symbol)
                break
    return " ".join(symbols) if symbols else "⚠️"