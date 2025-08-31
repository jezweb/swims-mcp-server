# File Upload Solutions for MCP Servers

## Problem Statement
MCP protocol has no native file upload mechanism (it's JSON-based and cannot transport binary data). Users need to send files to remote MCP servers without complex client-side implementations.

## Final Solution: URL-Based File Access
After exploring multiple approaches, we've settled on URL-based file access as the most practical solution.

## Solution 1: Cloud Storage with Presigned URLs (Recommended)

### Architecture
```
1. User → MCP Tool: get_upload_url → FastMCP Server
2. User → Direct Upload → Cloud Storage (R2/S3)  
3. User → MCP Tool: analyze_cloud_document → FastMCP Server → Gemini
```

### Implementation

#### Step 1: Presigned URL Generator Tool
```python
import boto3
from datetime import datetime, timedelta

# R2 client configuration
r2_client = boto3.client(
    's3',
    endpoint_url='https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com',
    aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
    region_name='auto'
)

@mcp.tool()
async def get_upload_url(
    filename: str,
    content_type: str = "application/octet-stream"
) -> Dict[str, Any]:
    """
    Generate a presigned URL for direct file upload to R2 storage.
    
    Args:
        filename: Name of the file to upload
        content_type: MIME type of the file
    
    Returns:
        Presigned URL and storage URI for the file
    """
    # Generate unique key
    file_key = f"uploads/{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4()}/{filename}"
    
    # Generate presigned POST URL (valid for 1 hour)
    presigned_post = r2_client.generate_presigned_post(
        Bucket='swms-documents',
        Key=file_key,
        Fields={"Content-Type": content_type},
        Conditions=[
            {"Content-Type": content_type},
            ["content-length-range", 0, 52428800]  # Max 50MB
        ],
        ExpiresIn=3600
    )
    
    return {
        "status": "success",
        "upload_url": presigned_post['url'],
        "fields": presigned_post['fields'],
        "storage_uri": f"r2://swms-documents/{file_key}",
        "expires_in": 3600,
        "instructions": "POST to upload_url with fields and file"
    }
```

#### Step 2: Cloud Document Processing Tool
```python
@mcp.tool()
async def analyze_cloud_document(
    storage_uri: str,
    jurisdiction: str = "nsw"
) -> Dict[str, Any]:
    """
    Analyze a SWMS document from cloud storage.
    
    Args:
        storage_uri: Cloud storage URI (e.g., r2://bucket/path/file.pdf)
        jurisdiction: State/territory for compliance checking
    
    Returns:
        Comprehensive SWMS compliance analysis
    """
    # Parse storage URI
    if storage_uri.startswith("r2://"):
        bucket, key = storage_uri[5:].split("/", 1)
        
        # Download from R2 to temp file
        temp_file = TEMP_STORAGE_DIR / f"{uuid.uuid4()}.pdf"
        r2_client.download_file(bucket, key, str(temp_file))
        
        # Upload to Gemini
        gemini_file = client.files.upload(file=str(temp_file))
        
        # Perform analysis (reuse existing logic)
        # ... analysis code ...
        
        # Cleanup
        temp_file.unlink()
        
        return analysis_result
```

### User Workflow

1. **Get Upload URL via MCP**:
```python
upload_info = await mcp.call_tool("get_upload_url", {
    "filename": "construction-swms.pdf",
    "content_type": "application/pdf"
})
```

2. **Upload File Directly to R2**:
```bash
curl -X POST {upload_url} \
  -F "key={key}" \
  -F "Content-Type=application/pdf" \
  -F "file=@/path/to/swms.pdf"
```

3. **Analyze via MCP Tool**:
```python
result = await mcp.call_tool("analyze_cloud_document", {
    "storage_uri": "r2://swms-documents/uploads/20240131/abc-123/construction-swms.pdf",
    "jurisdiction": "nsw"
})
```

### Benefits
- **Pure MCP Workflow** - No web forms needed
- **Scalable** - Direct uploads to cloud storage
- **Secure** - Presigned URLs with expiration
- **Efficient** - Server doesn't handle file bytes
- **Clean Architecture** - Separation of concerns

### Local File Bridge Helper
```python
# local_upload_bridge.py
import requests
from fastmcp import Client
from pathlib import Path

async def upload_local_file(filepath):
    # Get presigned URL from MCP server
    async with Client("https://your-server.fastmcp.app/mcp") as client:
        upload_info = await client.call_tool("get_upload_url", {
            "filename": Path(filepath).name
        })
        
        # Upload file to cloud
        with open(filepath, 'rb') as f:
            requests.post(
                upload_info['upload_url'],
                data=upload_info['fields'],
                files={'file': f}
            )
        
        # Analyze document
        result = await client.call_tool("analyze_cloud_document", {
            "storage_uri": upload_info['storage_uri']
        })
        
        return result
```

---

## Solution 2: In-Protocol MCP File Streaming (Pure MCP)

### Concept
Use MCP tools to stream files in chunks, keeping everything within the MCP protocol.

### Implementation

#### Stateful File Handling Tools
```python
# Dictionary to track active uploads
active_uploads = {}

@mcp.tool()
async def start_file_upload(
    file_name: str,
    file_type: str
) -> Dict[str, Any]:
    """
    Start a file upload session.
    
    Args:
        file_name: Name of the file
        file_type: MIME type of the file
    
    Returns:
        Upload ID for this session
    """
    upload_id = str(uuid.uuid4())
    temp_file = TEMP_STORAGE_DIR / f"{upload_id}_temp"
    
    active_uploads[upload_id] = {
        "file_name": file_name,
        "file_type": file_type,
        "temp_file": temp_file,
        "file_handle": open(temp_file, 'wb'),
        "start_time": time.time(),
        "chunks_received": 0
    }
    
    return {
        "status": "success",
        "upload_id": upload_id,
        "message": f"Upload session started for {file_name}"
    }

@mcp.tool()
async def append_file_chunk(
    upload_id: str,
    data_chunk: str
) -> Dict[str, Any]:
    """
    Append a chunk of data to an active upload.
    
    Args:
        upload_id: ID of the upload session
        data_chunk: Base64-encoded chunk of file data
    
    Returns:
        Status of chunk processing
    """
    if upload_id not in active_uploads:
        return {
            "status": "error",
            "message": "Invalid upload_id"
        }
    
    upload_info = active_uploads[upload_id]
    
    try:
        # Decode base64 chunk and write to file
        chunk_bytes = base64.b64decode(data_chunk)
        upload_info["file_handle"].write(chunk_bytes)
        upload_info["chunks_received"] += 1
        
        return {
            "status": "success",
            "chunks_received": upload_info["chunks_received"],
            "bytes_written": len(chunk_bytes)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool()
async def finish_file_upload(
    upload_id: str
) -> Dict[str, Any]:
    """
    Finalize a file upload session.
    
    Args:
        upload_id: ID of the upload session
    
    Returns:
        Final file ID for processing
    """
    if upload_id not in active_uploads:
        return {
            "status": "error",
            "message": "Invalid upload_id"
        }
    
    upload_info = active_uploads[upload_id]
    
    # Close file handle
    upload_info["file_handle"].close()
    
    # Move to permanent storage
    final_id = str(uuid.uuid4())
    final_path = TEMP_STORAGE_DIR / f"{final_id}_{upload_info['file_name']}"
    upload_info["temp_file"].rename(final_path)
    
    # Upload to Gemini
    gemini_file = client.files.upload(file=str(final_path))
    
    # Store file info
    uploaded_files[final_id] = {
        'document_id': final_id,
        'filename': upload_info['file_name'],
        'file_path': str(final_path),
        'mime_type': upload_info['file_type'],
        'upload_time': time.time(),
        'gemini_file': gemini_file,
        'chunks_received': upload_info['chunks_received']
    }
    
    # Clean up active upload
    del active_uploads[upload_id]
    
    return {
        "status": "success",
        "file_id": final_id,
        "message": f"File uploaded successfully",
        "chunks_processed": upload_info['chunks_received']
    }
```

### Client-Side Orchestration
```python
import base64
from fastmcp import Client

async def stream_file_via_mcp(filepath, mcp_server_url):
    async with Client(mcp_server_url) as client:
        # Start upload
        result = await client.call_tool("start_file_upload", {
            "file_name": Path(filepath).name,
            "file_type": "application/pdf"
        })
        upload_id = result["upload_id"]
        
        # Stream chunks
        chunk_size = 1024 * 1024  # 1MB chunks
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                base64_chunk = base64.b64encode(chunk).decode('utf-8')
                await client.call_tool("append_file_chunk", {
                    "upload_id": upload_id,
                    "data_chunk": base64_chunk
                })
        
        # Finalize upload
        result = await client.call_tool("finish_file_upload", {
            "upload_id": upload_id
        })
        file_id = result["file_id"]
        
        # Analyze document
        analysis = await client.call_tool("analyze_swms_compliance", {
            "document_id": file_id,
            "jurisdiction": "nsw"
        })
        
        return analysis
```

### Trade-offs

#### Pros
- **Purely In-Protocol**: Uses single MCP connection for everything
- **No External Dependencies**: No need for cloud storage or HTTP endpoints
- **Conceptually Clean**: Entire interaction is within MCP conversation

#### Cons
- **High Overhead**: Many round-trips for large files (10MB = 10+ tool calls)
- **Base64 Overhead**: 33% size increase from encoding
- **Complexity**: Client needs to manage chunking and state
- **Inefficiency**: Using control protocol for data transfer
- **Latency**: Sequential chunk processing adds significant delay

---

## Current Implementation

The SWMS MCP Server uses **URL-based file access** through the `upload_swms_from_url` tool:

```python
# Upload a document from any accessible URL
result = await mcp.call_tool("upload_swms_from_url", {
    "url": "https://your-bucket.r2.dev/documents/swms.pdf"
})

# Use the returned document_id for analysis
analysis = await mcp.call_tool("analyze_swms_compliance", {
    "document_id": result["document_id"],
    "jurisdiction": "nsw"
})
```

### Supported URL Sources
- **R2/S3 buckets** (public or presigned URLs)
- **Google Drive** (public share links)
- **Dropbox** (public share links)
- **Direct HTTP/HTTPS** URLs
- **Any publicly accessible file URL**

### Integration Pattern
1. **Web Application**: Handles file upload to cloud storage (R2, S3, etc.)
2. **Storage Service**: Returns a URL for the uploaded file
3. **MCP Server**: Downloads file from URL, uploads to Gemini, analyzes
4. **Results**: Returned through MCP protocol

### Why This Approach?
After testing pure MCP streaming (chunked base64 transfer), we found:
- MCP protocol cannot efficiently transport binary data (33% base64 overhead)
- Token limits make large file transfers impractical (1MB ≈ 350K tokens)
- URL-based access is simpler and more efficient
- Works with existing cloud storage infrastructure
- No client-side complexity required

## Alternative Approaches Considered

### Solution 2: In-Protocol Streaming (Not Recommended)
We implemented and tested pure MCP file streaming with base64 chunks, but removed it due to:
- High token consumption (impractical for files >100KB)
- Requires client-side file handling (defeats the purpose)
- Multiple round-trips add latency
- Complex implementation for minimal benefit

### Key Learning
MCP protocol is designed for control/command operations, not data transport. Use appropriate infrastructure (cloud storage) for file handling and MCP for orchestration.