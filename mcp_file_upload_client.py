#!/usr/bin/env python3
"""
MCP File Upload Client - Pure MCP Protocol File Streaming
==========================================================

This script demonstrates how to upload files to the SWMS MCP Server
using pure MCP protocol - no HTTP endpoints or curl commands needed!

Perfect for files under 1MB (typical SWMS documents).

Usage:
    python mcp_file_upload_client.py <file_path> [server_url]

Example:
    python mcp_file_upload_client.py "construction-swms.pdf"
    python mcp_file_upload_client.py "electrical-work.docx" "https://your-server.fastmcp.app/mcp"
"""

import asyncio
import base64
import sys
from pathlib import Path
from typing import Optional
from fastmcp import Client


async def stream_file_via_mcp(
    filepath: str,
    server_url: str = "http://localhost:3000/mcp",
    chunk_size: int = 256 * 1024  # 256KB chunks for <1MB files
) -> dict:
    """
    Upload a file to MCP server using pure MCP protocol streaming.
    
    Args:
        filepath: Path to the file to upload
        server_url: MCP server URL (default: local development server)
        chunk_size: Size of each chunk in bytes (default: 256KB)
    
    Returns:
        Analysis result from the server
    """
    file_path = Path(filepath)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    file_size = file_path.stat().st_size
    print(f"📁 Uploading: {file_path.name}")
    print(f"📏 File size: {file_size:,} bytes")
    
    # Determine MIME type
    mime_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else \
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    async with Client(server_url) as client:
        print(f"🔗 Connected to: {server_url}")
        
        # Step 1: Start upload session
        print("\n1️⃣ Starting upload session...")
        result = await client.call_tool("start_file_upload", {
            "file_name": file_path.name,
            "file_type": mime_type
        })
        
        if result.get("status") != "success":
            raise Exception(f"Failed to start upload: {result.get('message')}")
        
        upload_id = result["upload_id"]
        print(f"✅ Upload session started: {upload_id}")
        
        # Step 2: Stream file in chunks
        print(f"\n2️⃣ Streaming file in {chunk_size // 1024}KB chunks...")
        chunks_sent = 0
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                # Base64 encode the chunk
                base64_chunk = base64.b64encode(chunk).decode('utf-8')
                
                # Send chunk
                result = await client.call_tool("append_file_chunk", {
                    "upload_id": upload_id,
                    "data_chunk": base64_chunk,
                    "chunk_index": chunks_sent
                })
                
                if result.get("status") != "success":
                    raise Exception(f"Failed to upload chunk {chunks_sent}: {result.get('message')}")
                
                chunks_sent += 1
                bytes_sent = result.get("total_bytes", 0)
                progress = (bytes_sent / file_size) * 100
                print(f"  📤 Chunk {chunks_sent}: {len(chunk):,} bytes ({progress:.1f}% complete)")
        
        # Step 3: Finalize upload
        print(f"\n3️⃣ Finalizing upload...")
        result = await client.call_tool("finish_file_upload", {
            "upload_id": upload_id
        })
        
        if result.get("status") != "success":
            raise Exception(f"Failed to finalize upload: {result.get('message')}")
        
        document_id = result["document_id"]
        print(f"✅ Upload complete! Document ID: {document_id}")
        print(f"   • Chunks processed: {result.get('chunks_processed')}")
        print(f"   • Total size: {result.get('file_size'):,} bytes")
        print(f"   • Gemini uploaded: {result.get('gemini_uploaded')}")
        
        # Step 4: Analyze the document
        print(f"\n4️⃣ Analyzing SWMS compliance...")
        analysis = await client.call_tool("analyze_swms_compliance", {
            "document_id": document_id,
            "jurisdiction": "nsw"
        })
        
        if analysis.get("status") == "success":
            print("\n✅ Analysis complete!")
            return analysis
        else:
            print(f"\n⚠️ Analysis failed: {analysis.get('message')}")
            return analysis


async def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    filepath = sys.argv[1]
    server_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:3000/mcp"
    
    try:
        result = await stream_file_via_mcp(filepath, server_url)
        
        # Display summary of results
        if result.get("status") == "success":
            print("\n" + "="*60)
            print("📊 SWMS COMPLIANCE ANALYSIS RESULTS")
            print("="*60)
            
            if "overall_assessment" in result:
                assessment = result["overall_assessment"]
                print(f"\n🎯 Overall Score: {assessment.get('score', 'N/A')}/100")
                print(f"📈 Compliance Level: {assessment.get('compliance_level', 'N/A')}")
                
            if "summary" in result:
                print(f"\n📝 Summary:\n{result['summary']}")
            
            if "key_findings" in result:
                print("\n🔍 Key Findings:")
                for finding in result["key_findings"][:3]:  # Show top 3
                    print(f"  • {finding}")
            
            if "critical_issues" in result:
                print("\n⚠️ Critical Issues:")
                for issue in result["critical_issues"][:3]:  # Show top 3
                    print(f"  • {issue}")
            
            print("\n✅ Full analysis available in the result object")
        else:
            print(f"\n❌ Analysis failed: {result.get('message', 'Unknown error')}")
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())