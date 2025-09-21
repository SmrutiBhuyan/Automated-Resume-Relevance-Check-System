import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

@dataclass
class ATSCompatibilityResult:
    is_ats_friendly: bool
    score: float
    main_issues: List[str]
    quick_fixes: List[str]

class ATSCompatibilityChecker:
    """Simplified service to check if resume is ATS friendly"""
    
    def __init__(self):
        # Common ATS-unfriendly elements
        self.ats_problems = {
            'tables': r'<table[^>]*>',
            'complex_formatting': r'<div[^>]*style[^>]*>|<span[^>]*style[^>]*>',
            'special_chars': r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\\]',
            'images': r'<img[^>]*>',
            'columns': r'column-count|column-width|column-gap',
            'headers_footers': r'<header[^>]*>|<footer[^>]*>',
            'text_boxes': r'<input[^>]*>|<textarea[^>]*>'
        }
    
    def check_compatibility(self, resume_text: str, resume_data: Dict) -> ATSCompatibilityResult:
        """Check if resume is ATS friendly - returns simple binary result"""
        issues = []
        score = 100.0
        
        # Check for major ATS problems
        for problem_type, pattern in self.ats_problems.items():
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            if matches:
                if problem_type == 'tables':
                    issues.append("Contains tables")
                    score -= 30
                elif problem_type == 'complex_formatting':
                    issues.append("Complex formatting detected")
                    score -= 20
                elif problem_type == 'special_chars':
                    if len(matches) > 10:  # Only flag if many special chars
                        issues.append("Too many special characters")
                        score -= 15
                elif problem_type == 'images':
                    issues.append("Contains images")
                    score -= 25
                elif problem_type == 'columns':
                    issues.append("Multi-column layout")
                    score -= 20
                elif problem_type == 'headers_footers':
                    issues.append("Headers/footers detected")
                    score -= 15
                elif problem_type == 'text_boxes':
                    issues.append("Interactive elements")
                    score -= 20
        
        # Check for essential content
        if not resume_data.get('skills'):
            issues.append("Missing skills section")
            score -= 20
        
        if not resume_data.get('experience'):
            issues.append("Missing experience section")
            score -= 25
        
        if not resume_data.get('education'):
            issues.append("Missing education section")
            score -= 15
        
        # Check for contact info
        contact_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'  # Phone
        ]
        
        contact_found = sum(1 for pattern in contact_patterns if re.search(pattern, resume_text))
        if contact_found < 2:
            issues.append("Incomplete contact information")
            score -= 10
        
        # Determine if ATS friendly (score >= 70)
        is_ats_friendly = score >= 70
        
        # Generate quick fixes
        quick_fixes = []
        if not is_ats_friendly:
            if "Contains tables" in issues:
                quick_fixes.append("Convert tables to plain text")
            if "Complex formatting detected" in issues:
                quick_fixes.append("Use simple formatting")
            if "Contains images" in issues:
                quick_fixes.append("Remove images and graphics")
            if "Missing skills section" in issues:
                quick_fixes.append("Add a skills section")
            if "Missing experience section" in issues:
                quick_fixes.append("Add work experience")
            if "Missing education section" in issues:
                quick_fixes.append("Add education details")
            if "Incomplete contact information" in issues:
                quick_fixes.append("Add email and phone number")
        
        return ATSCompatibilityResult(
            is_ats_friendly=is_ats_friendly,
            score=max(0, score),
            main_issues=issues[:3],  # Show top 3 issues
            quick_fixes=quick_fixes[:3]  # Show top 3 fixes
        )
