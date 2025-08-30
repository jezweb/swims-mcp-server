#!/usr/bin/env python3
"""
Script to upload regulatory documents to Cloudflare R2 bucket
Requires: boto3 and Cloudflare R2 credentials
"""

import os
import sys
from pathlib import Path
import boto3
from botocore.config import Config

# R2 Configuration
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "0460574641fdbb98159c98ebf593e2bd")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = "swms-regulations"

def get_r2_client():
    """Create and return an R2 client"""
    if not R2_ACCESS_KEY_ID or not R2_SECRET_ACCESS_KEY:
        print("Error: R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY environment variables must be set")
        print("\nTo set these, you need to:")
        print("1. Go to Cloudflare Dashboard > R2")
        print("2. Manage R2 API Tokens")
        print("3. Create a new API token with Object Read & Write permissions")
        print("4. Export the credentials:")
        print('   export R2_ACCESS_KEY_ID="your_access_key_id"')
        print('   export R2_SECRET_ACCESS_KEY="your_secret_access_key"')
        sys.exit(1)
    
    endpoint_url = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    
    return boto3.client(
        service_name='s3',
        endpoint_url=endpoint_url,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'}
        ),
        region_name='auto'
    )

def upload_file_to_r2(client, local_path, r2_key):
    """Upload a single file to R2"""
    try:
        with open(local_path, 'rb') as f:
            client.put_object(
                Bucket=R2_BUCKET_NAME,
                Key=r2_key,
                Body=f,
                ContentType='application/pdf'
            )
        print(f"  ✓ Uploaded: {r2_key}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to upload {r2_key}: {e}")
        return False

def main():
    """Upload all regulatory documents to R2"""
    print("Uploading regulatory documents to Cloudflare R2")
    print("=" * 60)
    
    # Get R2 client
    client = get_r2_client()
    
    # Check if bucket exists
    try:
        client.head_bucket(Bucket=R2_BUCKET_NAME)
        print(f"✓ Connected to R2 bucket: {R2_BUCKET_NAME}\n")
    except:
        print(f"✗ Could not connect to bucket: {R2_BUCKET_NAME}")
        print("  Make sure the bucket exists and credentials are correct")
        sys.exit(1)
    
    # Find all PDF files in regulatory_documents directory
    base_dir = Path("regulatory_documents")
    if not base_dir.exists():
        print(f"Error: Directory '{base_dir}' not found")
        print("Run download_regulatory_docs.py first to download the documents")
        sys.exit(1)
    
    pdf_files = list(base_dir.glob("**/*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {base_dir}")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF files to upload\n")
    
    uploaded = 0
    failed = []
    
    # Upload each file
    for pdf_path in pdf_files:
        # Get relative path for R2 key
        relative_path = pdf_path.relative_to(base_dir)
        r2_key = str(relative_path).replace('\\', '/')  # Ensure forward slashes
        
        print(f"Uploading: {relative_path}")
        if upload_file_to_r2(client, pdf_path, r2_key):
            uploaded += 1
        else:
            failed.append(relative_path)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Upload Summary:")
    print(f"  Total files: {len(pdf_files)}")
    print(f"  Uploaded: {uploaded}")
    print(f"  Failed: {len(failed)}")
    
    if failed:
        print("\nFailed uploads:")
        for path in failed:
            print(f"  - {path}")
    
    # List objects in bucket to verify
    print("\n" + "=" * 60)
    print("Verifying bucket contents:")
    try:
        response = client.list_objects_v2(Bucket=R2_BUCKET_NAME)
        if 'Contents' in response:
            print(f"\nBucket contains {len(response['Contents'])} objects:")
            for obj in response['Contents']:
                print(f"  - {obj['Key']} ({obj['Size']:,} bytes)")
        else:
            print("Bucket is empty")
    except Exception as e:
        print(f"Could not list bucket contents: {e}")
    
    print("\n✓ Upload complete!")
    print(f"Files are now available in R2 bucket: {R2_BUCKET_NAME}")
    print("\nTo make files publicly accessible:")
    print("1. Go to Cloudflare Dashboard > R2 > swms-regulations bucket")
    print("2. Settings > Public Access")
    print("3. Enable public access or configure custom domain")

if __name__ == "__main__":
    main()