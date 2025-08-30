#!/usr/bin/env python3
"""
Download official SWMS regulatory documents based on comprehensive research
"""

import os
import requests
from pathlib import Path
import time
import csv

# Create directory structure
base_dir = Path("regulatory_documents")
base_dir.mkdir(exist_ok=True)

# Priority documents from the CSV and MD files
PRIORITY_DOCUMENTS = {
    "national": [
        {
            "name": "safe-work-australia-swms-info-sheet.pdf",
            "url": "https://www.safeworkaustralia.gov.au/system/files/documents/1703/information-sheet-safe-work-method-statement.pdf",
            "description": "Safe Work Australia SWMS Information Sheet with template"
        },
        {
            "name": "model-code-practice-construction-v1.pdf",
            "url": "https://www.safeworkaustralia.gov.au/system/files/documents/1705/mcop-construction-work-v1.pdf",
            "description": "Model Code of Practice: Construction Work v1"
        },
        {
            "name": "model-code-practice-construction-v2.pdf",
            "url": "https://www.safeworkaustralia.gov.au/system/files/documents/1705/mcop-construction-work-v2.pdf",
            "description": "Model Code of Practice: Construction Work v2"
        },
        {
            "name": "model-code-practice-construction-nov24.pdf",
            "url": "https://www.safeworkaustralia.gov.au/sites/default/files/2024-11/model_code_of_practice-construction_work-nov24.pdf",
            "description": "Model Code of Practice: Construction Work (Nov 2024)"
        },
        {
            "name": "ofsc-swms-fact-sheet.pdf",
            "url": "https://www.fsc.gov.au/sites/default/files/2020-08/Fact%20Sheet%20%E2%80%93%20Safe%20Work%20Method%20Statements%20(SWMS).pdf",
            "description": "Office of the Federal Safety Commissioner SWMS Fact Sheet"
        }
    ],
    "nsw": [
        {
            "name": "nsw-construction-cop.pdf",
            "url": "https://www.safework.nsw.gov.au/__data/assets/pdf_file/0014/52151/Construction-work-COP.pdf",
            "description": "NSW Code of Practice - Construction Work"
        },
        {
            "name": "nsw-swms-template.pdf",
            "url": "https://www.safework.nsw.gov.au/__data/assets/pdf_file/0003/107886/SW08268-0818-427125.pdf",
            "description": "NSW High Risk Construction Work SWMS Template"
        },
        {
            "name": "nsw-swms-form-5.pdf",
            "url": "https://www.safework.nsw.gov.au/__data/assets/pdf_file/0003/52743/form-5-safe-work-method-statement.pdf",
            "description": "NSW Housing Industry Form 5: SWMS Template"
        }
    ],
    "vic": [
        {
            "name": "vic-swms-guidance.pdf",
            "url": "https://www.worksafe.vic.gov.au/resources/safe-work-method-statements-guidance",
            "description": "Victoria SWMS Guidance Document (8 pages)"
        },
        {
            "name": "vic-swms-template.pdf",
            "url": "https://www.worksafe.vic.gov.au/resources/safe-work-method-statements-swms",
            "description": "Victoria SWMS Template (4 pages)"
        }
    ],
    "qld": [
        {
            "name": "qld-formwork-cop.pdf",
            "url": "https://www.worksafe.qld.gov.au/__data/assets/pdf_file/0019/15823/formwork-cop-2016.pdf",
            "description": "Queensland Formwork Code of Practice 2016"
        },
        {
            "name": "qld-building-construction-cop.pdf",
            "url": "https://www.oir.qld.gov.au/sites/default/files/oir-code-of-practice-building-and-construction_0.pdf",
            "description": "Queensland Building and Construction Code of Practice 2000"
        }
    ],
    "wa": [
        {
            "name": "wa-swms-info-sheet.pdf",
            "url": "https://www.worksafe.wa.gov.au/system/files/migrated/sites/default/files/atoms/files/231293_br_swms-highrisk.pdf",
            "description": "WA SWMS for High Risk Construction Work Information Sheet"
        },
        {
            "name": "wa-swms-template.docx",
            "url": "https://www.worksafe.wa.gov.au/system/files/migrated/sites/default/files/atoms/files/231293_fm_swms-form.docx",
            "description": "WA High Risk Construction Work SWMS Template"
        }
    ],
    "sa": [
        {
            "name": "sa-swms-fact-sheet.pdf",
            "url": "https://dit.sa.gov.au/__data/assets/pdf_file/0011/571727/DOCS_AND_FILES-13976017-v1-Safe_Work_Method_Statement_Fact_Sheet.pdf",
            "description": "SA SWMS Fact Sheet with HRCW activities list"
        },
        {
            "name": "sa-swms-sample-carpentry.docx",
            "url": "https://www.safework.sa.gov.au/__data/assets/word_doc/0007/1056661/Sample-SWMS-first-fix-carpentry.docx",
            "description": "SA Sample SWMS - First Fix Carpentry"
        }
    ],
    "tas": [
        {
            "name": "tas-construction-cop.pdf",
            "url": "https://worksafe.tas.gov.au/__data/assets/pdf_file/0003/806736/model-Code-of-Practice-Construction-Work.PDF",
            "description": "Tasmania Construction Work Code of Practice"
        },
        {
            "name": "tas-swms-template.doc",
            "url": "https://worksafe.tas.gov.au/__data/assets/word_doc/0009/546498/Construction-sample-Safe-work-method-statement-template.doc",
            "description": "Tasmania SWMS Template (Word)"
        }
    ],
    "act": [
        {
            "name": "act-swms-template.pdf",
            "url": "https://www.worksafe.act.gov.au/__data/assets/pdf_file/0003/2191116/Safe-work-method-statement-template-202507.pdf",
            "description": "ACT Safe Work Method Statement Template PDF"
        },
        {
            "name": "act-swms-template.docx",
            "url": "https://www.worksafe.act.gov.au/__data/assets/word_doc/0020/2191115/Safe-work-method-statement-template-202507.docx",
            "description": "ACT Safe Work Method Statement Template DOCX"
        }
    ],
    "nt": [
        {
            "name": "nt-construction-cop.pdf",
            "url": "https://worksafe.nt.gov.au/_resources/documents/pdf/codes-of-practice/code-of-practice-construction-work.pdf",
            "description": "NT Code of Practice - Construction Work"
        },
        {
            "name": "nt-swms-template.docx",
            "url": "https://worksafe.nt.gov.au/_resources/documents/word/checklist/safe-work-method-statement-template.docx",
            "description": "NT Safe Work Method Statement Template"
        },
        {
            "name": "nt-swms-template.pdf",
            "url": "https://worksafe.nt.gov.au/_resources/documents/pdf/checklists/safe-work-method-statement-template.pdf",
            "description": "NT SWMS Template PDF"
        }
    ]
}

def download_file(url, filepath, description):
    """Download a file from URL to filepath"""
    print(f"Downloading: {description}")
    print(f"  URL: {url}")
    print(f"  Saving to: {filepath}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers, allow_redirects=True)
        
        # Some sites may return HTML error pages with 200 status
        if response.status_code == 200:
            # Check if it's actually a PDF or DOCX
            content_type = response.headers.get('content-type', '').lower()
            if filepath.suffix == '.pdf' and 'pdf' not in content_type and len(response.content) < 5000:
                print(f"  ⚠ Warning: May not be a valid PDF (content-type: {content_type})")
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"  ✓ Downloaded successfully ({len(response.content):,} bytes)\n")
            return True
        else:
            print(f"  ✗ HTTP {response.status_code}\n")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed to download: {e}\n")
        return False

def create_index_file():
    """Create an index file of all documents"""
    index_path = base_dir / "INDEX.md"
    with open(index_path, 'w') as f:
        f.write("# SWMS Regulatory Documents Index\n\n")
        f.write("This index lists all downloaded regulatory documents organized by jurisdiction.\n\n")
        
        for jurisdiction, documents in PRIORITY_DOCUMENTS.items():
            f.write(f"## {jurisdiction.upper()}\n\n")
            
            jurisdiction_dir = base_dir / jurisdiction
            if jurisdiction_dir.exists():
                files = list(jurisdiction_dir.glob("*"))
                if files:
                    for doc in documents:
                        filepath = jurisdiction_dir / doc["name"]
                        if filepath.exists():
                            size = filepath.stat().st_size
                            f.write(f"- **{doc['name']}** ({size:,} bytes)\n")
                            f.write(f"  - {doc['description']}\n")
                else:
                    f.write("*No documents downloaded*\n")
            else:
                f.write("*Directory not created*\n")
            f.write("\n")
        
        f.write("## Document Sources\n\n")
        f.write("- Safe Work Australia: National model laws and codes\n")
        f.write("- State/Territory Regulators: Jurisdiction-specific requirements\n")
        f.write("- Office of the Federal Safety Commissioner: Federal contractor requirements\n")
        f.write("\n## Important Notes\n\n")
        f.write("- These are publicly available government documents\n")
        f.write("- Always verify currency with official sources\n")
        f.write("- Some URLs may change or require manual download\n")
        f.write("- Victoria operates under OHS (not WHS) legislation\n")
        f.write("- South Australia has a 3m fall height threshold (vs 2m elsewhere)\n")

def main():
    """Download priority regulatory documents"""
    print("Downloading Official SWMS Regulatory Documents")
    print("=" * 60)
    print("Based on comprehensive research from:")
    print("- Australian SWMS Compliance Documents.md")
    print("- australia_swms_regulatory_documents_templates.csv")
    print("=" * 60 + "\n")
    
    total_files = sum(len(docs) for docs in PRIORITY_DOCUMENTS.values())
    downloaded = 0
    failed = []
    
    for jurisdiction, documents in PRIORITY_DOCUMENTS.items():
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
                    "url": doc["url"],
                    "description": doc["description"]
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
            print(f"    {item['description']}")
            print(f"    URL: {item['url']}")
    
    # Create index file
    create_index_file()
    print(f"\nIndex created at: {base_dir}/INDEX.md")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Review downloaded documents in regulatory_documents/")
    print("2. Manually download any failed documents from official sites")
    print("3. Run upload_to_r2.py to upload to Cloudflare R2")
    print("4. Configure R2 bucket for public access or custom domain")

if __name__ == "__main__":
    main()