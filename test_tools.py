#!/usr/bin/env python3
"""
Test script for new SWMS tools
"""

import asyncio
from server import mcp

async def test_tools():
    """Test that all tools are registered."""
    tools = await mcp.get_tools()
    
    print(f"✅ Total tools registered: {len(tools)}")
    print("\nTools list:")
    
    expected_tools = [
        "upload_swms_document",
        "upload_swms_from_url",
        "analyze_swms_text",
        "analyze_swms_compliance",
        "analyze_swms_custom",
        "get_compliance_score",
        "quick_check_swms",
        "list_jurisdictions",
        "get_server_status",
        # New tools
        "generate_swms_from_description_tool",
        "generate_toolbox_talk_tool",
        "create_worker_summary_tool",
        "suggest_swms_improvements_tool",
        "extract_hazards_from_image_tool"
    ]
    
    for tool_name in tools:
        status = "✅" if tool_name in expected_tools else "❓"
        print(f"  {status} {tool_name}")
    
    # Check for missing tools
    registered_names = list(tools)
    missing = [t for t in expected_tools if t not in registered_names]
    
    if missing:
        print(f"\n❌ Missing tools: {missing}")
    else:
        print(f"\n✅ All expected tools are registered!")
    
    return len(missing) == 0

if __name__ == "__main__":
    success = asyncio.run(test_tools())
    exit(0 if success else 1)