"""
R2 Context Module - Manages regulatory documents from Cloudflare R2
"""

import os
import json
import time
import hashlib
import requests
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from google import genai
from google.genai import types

# R2 Configuration
R2_BUCKET_NAME = "swms-regulations"
# Public R2 URL for accessing regulatory documents
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL", "https://pub-bb6a39bd73444f4582d3208b2257c357.r2.dev")

# Cache configuration
CACHE_DIR = Path("/tmp/swms-file-cache")
CACHE_EXPIRY_HOURS = 24

# Document mapping by jurisdiction
REGULATORY_DOCUMENTS = {
    "national": [
        "safe-work-australia-swms-info-sheet.pdf",
        "model-code-practice-construction.pdf",
        "high-risk-construction-work-list.pdf"
    ],
    "nsw": [
        "nsw-whs-regulation-2017.pdf",
        "safework-nsw-swms-template.pdf",
        "nsw-construction-cop.pdf"
    ],
    "vic": [
        "vic-ohs-regulations-2017.pdf",
        "worksafe-vic-construction-cop.pdf"
    ],
    "qld": [
        "qld-whs-regulation-2011.pdf",
        "worksafe-qld-swms-guide.pdf"
    ],
    "wa": [
        "wa-whs-regulations-2022.pdf",
        "worksafe-wa-construction-cop.pdf"
    ],
    "sa": [
        "sa-whs-regulations-2012.pdf",
        "safework-sa-swms-template.pdf"
    ],
    "tas": [
        "tas-whs-regulations-2012.pdf",
        "worksafe-tas-swms-guide.pdf"
    ],
    "act": [
        "act-whs-regulation-2011.pdf",
        "worksafe-act-swms-guide.pdf"
    ],
    "nt": [
        "nt-whs-regulations-2011.pdf",
        "nt-worksafe-construction-cop.pdf"
    ]
}

class R2ContextManager:
    """Manages regulatory document context from R2 storage"""
    
    def __init__(self, client: genai.Client):
        """Initialize with Gemini client"""
        self.client = client
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True)
        self.file_cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load file cache from disk"""
        cache_file = self.cache_dir / "file_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save file cache to disk"""
        cache_file = self.cache_dir / "file_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(self.file_cache, f)
    
    def _get_cache_key(self, doc_path: str) -> str:
        """Generate cache key for document"""
        return hashlib.md5(doc_path.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry:
            return False
        
        cache_time = cache_entry.get("timestamp", 0)
        current_time = time.time()
        hours_elapsed = (current_time - cache_time) / 3600
        
        return hours_elapsed < CACHE_EXPIRY_HOURS
    
    def fetch_from_r2(self, doc_path: str) -> Optional[bytes]:
        """Fetch document from R2 bucket"""
        url = f"{R2_PUBLIC_URL}/{doc_path}"
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to fetch {doc_path}: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching {doc_path}: {e}")
            return None
    
    def upload_to_gemini(self, doc_bytes: bytes, doc_name: str) -> Optional[str]:
        """Upload document to Gemini Files API and return file ID"""
        try:
            # Save to temp file for upload
            temp_path = self.cache_dir / f"temp_{doc_name}"
            with open(temp_path, 'wb') as f:
                f.write(doc_bytes)
            
            # Upload to Gemini
            uploaded_file = self.client.files.upload(file=str(temp_path))
            
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
            
            return uploaded_file.name
        except Exception as e:
            print(f"Error uploading {doc_name} to Gemini: {e}")
            return None
    
    def get_context_files(self, jurisdiction: str = "nsw") -> List[str]:
        """Get list of Gemini file IDs for jurisdiction context"""
        file_ids = []
        
        # Always include national documents
        docs_to_fetch = REGULATORY_DOCUMENTS.get("national", [])
        
        # Add jurisdiction-specific documents
        if jurisdiction.lower() != "national":
            docs_to_fetch.extend(REGULATORY_DOCUMENTS.get(jurisdiction.lower(), []))
        
        for doc_name in docs_to_fetch:
            doc_path = f"{jurisdiction.lower()}/{doc_name}" if jurisdiction.lower() != "national" else f"national/{doc_name}"
            cache_key = self._get_cache_key(doc_path)
            
            # Check cache
            cache_entry = self.file_cache.get(cache_key, {})
            if self._is_cache_valid(cache_entry):
                file_ids.append(cache_entry["file_id"])
                continue
            
            # Fetch from R2
            doc_bytes = self.fetch_from_r2(doc_path)
            if not doc_bytes:
                continue
            
            # Upload to Gemini
            file_id = self.upload_to_gemini(doc_bytes, doc_name)
            if file_id:
                # Update cache
                self.file_cache[cache_key] = {
                    "file_id": file_id,
                    "timestamp": time.time(),
                    "doc_name": doc_name,
                    "doc_path": doc_path
                }
                self._save_cache()
                file_ids.append(file_id)
        
        return file_ids
    
    def get_jurisdiction_context(self, jurisdiction: str = "nsw") -> Dict[str, Any]:
        """Get jurisdiction-specific context information"""
        jurisdiction = jurisdiction.lower()
        
        context = {
            "jurisdiction": jurisdiction.upper(),
            "legislation": self._get_legislation_info(jurisdiction),
            "regulatory_body": self._get_regulator_info(jurisdiction),
            "specific_requirements": self._get_specific_requirements(jurisdiction)
        }
        
        return context
    
    def _get_legislation_info(self, jurisdiction: str) -> str:
        """Get legislation information for jurisdiction"""
        legislation_map = {
            "nsw": "Work Health and Safety Act 2011 (NSW) and Work Health and Safety Regulation 2017 (NSW)",
            "vic": "Occupational Health and Safety Act 2004 (Vic) and Occupational Health and Safety Regulations 2017 (Vic)",
            "qld": "Work Health and Safety Act 2011 (Qld) and Work Health and Safety Regulation 2011 (Qld)",
            "wa": "Work Health and Safety Act 2020 (WA) and Work Health and Safety (General) Regulations 2022 (WA)",
            "sa": "Work Health and Safety Act 2012 (SA) and Work Health and Safety Regulations 2012 (SA)",
            "tas": "Work Health and Safety Act 2012 (Tas) and Work Health and Safety Regulations 2012 (Tas)",
            "act": "Work Health and Safety Act 2011 (ACT) and Work Health and Safety Regulation 2011 (ACT)",
            "nt": "Work Health and Safety (National Uniform Legislation) Act 2011 (NT) and Regulations 2011 (NT)",
            "national": "Model Work Health and Safety Act and Model Work Health and Safety Regulations"
        }
        return legislation_map.get(jurisdiction, "Model WHS Laws")
    
    def _get_regulator_info(self, jurisdiction: str) -> str:
        """Get regulator information for jurisdiction"""
        regulator_map = {
            "nsw": "SafeWork NSW",
            "vic": "WorkSafe Victoria",
            "qld": "Workplace Health and Safety Queensland",
            "wa": "WorkSafe Western Australia",
            "sa": "SafeWork SA",
            "tas": "WorkSafe Tasmania",
            "act": "WorkSafe ACT",
            "nt": "NT WorkSafe",
            "national": "Safe Work Australia"
        }
        return regulator_map.get(jurisdiction, "Safe Work Australia")
    
    def _get_specific_requirements(self, jurisdiction: str) -> List[str]:
        """Get jurisdiction-specific requirements"""
        if jurisdiction == "vic":
            return [
                "Uses OHS terminology instead of WHS",
                "Different penalty structures",
                "Specific construction regulations under OHS Regulations 2017",
                "Different consultation requirements"
            ]
        elif jurisdiction == "wa":
            return [
                "Recently adopted WHS laws in 2022",
                "Specific provisions for mining and petroleum sectors",
                "Transitional arrangements may apply"
            ]
        else:
            return [
                "Follows harmonized Model WHS Laws",
                "18 prescribed high-risk construction work activities",
                "SWMS required before work commences",
                "Principal contractor coordination requirements"
            ]