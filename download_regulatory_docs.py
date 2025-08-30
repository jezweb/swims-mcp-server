#!/usr/bin/env python3
"""
Script to download publicly available regulatory documents for SWMS compliance
"""

import os
import requests
from pathlib import Path
import time

# Create directory structure
base_dir = Path("regulatory_documents")
base_dir.mkdir(exist_ok=True)

# Document URLs organized by jurisdiction
DOCUMENTS = {
    "national": [
        {
            "name": "safe-work-australia-swms-info-sheet.pdf",
            "url": "https://www.safeworkaustralia.gov.au/system/files/documents/1703/information-sheet-safe-work-method-statement.pdf",
            "description": "Safe Work Australia SWMS Information Sheet"
        },
        {
            "name": "model-code-practice-construction.pdf", 
            "url": "https://www.safeworkaustralia.gov.au/sites/default/files/2022-10/Model Code of Practice - Construction Work - 21102022 .pdf",
            "description": "Model Code of Practice: Construction Work"
        },
        {
            "name": "model-code-practice-construction-alt.pdf",
            "url": "https://www.safeworkaustralia.gov.au/system/files/documents/1705/mcop-construction-work-v2.pdf",
            "description": "Model Code of Practice: Construction Work (Alternative Version)"
        }
    ],
    "nsw": [
        {
            "name": "nsw-swms-template.pdf",
            "url": "https://www.safework.nsw.gov.au/__data/assets/pdf_file/0003/107886/SW08268-0818-427125.pdf",
            "description": "SafeWork NSW SWMS Template"
        },
        {
            "name": "nsw-confined-spaces-cop.pdf",
            "url": "https://www.safework.nsw.gov.au/__data/assets/pdf_file/0015/50073/Confined-spaces-COP.pdf",
            "description": "NSW Code of Practice: Confined Spaces"
        }
    ],
    "qld": [
        {
            "name": "qld-construction-cop.pdf",
            "url": "https://www.worksafe.qld.gov.au/__data/assets/pdf_file/0020/21456/construction-work-cop-2021.pdf",
            "description": "Queensland Code of Practice: Construction Work"
        }
    ],
    "vic": [
        {
            "name": "vic-construction-compliance-code.pdf",
            "url": "https://www.worksafe.vic.gov.au/__data/assets/pdf_file/0019/211334/ISBN-Construction-compliance-code-2016-10.pdf",
            "description": "Victoria Construction Compliance Code"
        }
    ],
    "wa": [
        {
            "name": "wa-construction-cop.pdf",
            "url": "https://www.commerce.wa.gov.au/sites/default/files/atoms/files/221122_cop_construction_work.pdf",
            "description": "WA Code of Practice: Construction Work"
        }
    ],
    "sa": [
        {
            "name": "sa-construction-cop.pdf",
            "url": "https://www.safework.sa.gov.au/__data/assets/pdf_file/0005/136266/Construction-work.pdf",
            "description": "SafeWork SA Code of Practice: Construction Work"
        }
    ]
}

def download_file(url, filepath, description):
    """Download a file from URL to filepath"""
    print(f"Downloading: {description}")
    print(f"  URL: {url}")
    print(f"  Saving to: {filepath}")
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"  ✓ Downloaded successfully ({len(response.content):,} bytes)\n")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed to download: {e}\n")
        return False

def main():
    """Download all available regulatory documents"""
    print("Starting download of regulatory documents for SWMS compliance\n")
    print("=" * 60)
    
    total_files = sum(len(docs) for docs in DOCUMENTS.values())
    downloaded = 0
    failed = []
    
    for jurisdiction, documents in DOCUMENTS.items():
        print(f"\n{jurisdiction.upper()} Documents:")
        print("-" * 40)
        
        jurisdiction_dir = base_dir / jurisdiction
        
        for doc in documents:
            filepath = jurisdiction_dir / doc["name"]
            
            if filepath.exists():
                print(f"  ⚠ {doc['name']} already exists, skipping...")
                downloaded += 1
                continue
            
            if download_file(doc["url"], filepath, doc["description"]):
                downloaded += 1
                time.sleep(1)  # Be respectful to servers
            else:
                failed.append({
                    "jurisdiction": jurisdiction,
                    "file": doc["name"],
                    "url": doc["url"]
                })
    
    print("\n" + "=" * 60)
    print(f"Download Summary:")
    print(f"  Total files: {total_files}")
    print(f"  Downloaded: {downloaded}")
    print(f"  Failed: {len(failed)}")
    
    if failed:
        print("\nFailed downloads:")
        for item in failed:
            print(f"  - {item['jurisdiction']}/{item['file']}")
            print(f"    URL: {item['url']}")
    
    print("\nNote: Some documents may require manual download from official websites")
    print("due to access restrictions or dynamic content generation.")
    
    # Create a README for the documents
    readme_path = base_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write("# Regulatory Documents for SWMS Compliance\n\n")
        f.write("This directory contains publicly available regulatory documents ")
        f.write("for Safe Work Method Statement (SWMS) compliance across Australian jurisdictions.\n\n")
        f.write("## Document Structure\n\n")
        
        for jurisdiction, documents in DOCUMENTS.items():
            f.write(f"### {jurisdiction.upper()}\n")
            for doc in documents:
                f.write(f"- **{doc['name']}**: {doc['description']}\n")
            f.write("\n")
        
        f.write("## Important Notes\n\n")
        f.write("- These documents are sourced from official government websites\n")
        f.write("- Always verify currency of documents with official sources\n")
        f.write("- Some jurisdictions may have updated requirements\n")
        f.write("- For the most current information, visit the relevant regulator's website\n")
    
    print(f"\nREADME created at: {readme_path}")

if __name__ == "__main__":
    main()