"""
PII (Personally Identifiable Information) Detector
Detects and masks sensitive data using pattern matching and NER
"""

import logging
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PIIMatch:
    """Represents a detected PII instance"""
    type: str
    value: str
    start: int
    end: int
    confidence: float


class PIIDetector:
    """Detect and mask PII in text"""
    
    # Regex patterns for common PII
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "passport": r'\b[A-Z]{1,2}\d{6,9}\b',
        "date_of_birth": r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
    }
    
    def __init__(self, enabled_detectors: List[str] = None, use_ner: bool = False):
        """
        Initialize PII detector
        
        Args:
            enabled_detectors: List of detector types to use (default: all)
            use_ner: Whether to use NER for advanced detection
        """
        self.enabled_detectors = enabled_detectors or list(self.PATTERNS.keys())
        self.use_ner = use_ner
        self._ner_model = None
        
        if use_ner:
            self._init_ner()
    
    def _init_ner(self):
        """Initialize NER model for advanced PII detection"""
        try:
            from transformers import pipeline
            self._ner_model = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
            logger.info("NER model initialized for PII detection")
        except Exception as e:
            logger.warning(f"Failed to initialize NER model: {e}")
            self._ner_model = None
    
    def detect(self, text: str) -> List[PIIMatch]:
        """
        Detect PII in text
        
        Args:
            text: Text to analyze
        
        Returns:
            List of detected PII instances
        """
        matches = []
        
        # Pattern-based detection
        for pii_type in self.enabled_detectors:
            if pii_type in self.PATTERNS:
                pattern = self.PATTERNS[pii_type]
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    matches.append(PIIMatch(
                        type=pii_type,
                        value=match.group(),
                        start=match.start(),
                        end=match.end(),
                        confidence=0.9
                    ))
        
        # NER-based detection
        if self.use_ner and self._ner_model:
            ner_matches = self._detect_with_ner(text)
            matches.extend(ner_matches)
        
        # Sort by position
        matches.sort(key=lambda x: x.start)
        
        return matches
    
    def _detect_with_ner(self, text: str) -> List[PIIMatch]:
        """Use NER to detect person names, locations, organizations"""
        matches = []
        
        try:
            entities = self._ner_model(text)
            
            for entity in entities:
                entity_type = entity['entity_group'].lower()
                
                # Map NER labels to PII types
                if entity_type in ['per', 'person']:
                    pii_type = "person_name"
                elif entity_type in ['loc', 'location']:
                    pii_type = "location"
                elif entity_type in ['org', 'organization']:
                    pii_type = "organization"
                else:
                    continue
                
                matches.append(PIIMatch(
                    type=pii_type,
                    value=entity['word'],
                    start=entity['start'],
                    end=entity['end'],
                    confidence=entity['score']
                ))
        
        except Exception as e:
            logger.error(f"NER detection failed: {e}")
        
        return matches
    
    def mask(self, text: str, mask_char: str = "*", preserve_length: bool = True) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Mask PII in text
        
        Args:
            text: Text to mask
            mask_char: Character to use for masking
            preserve_length: Whether to preserve original length
        
        Returns:
            Tuple of (masked_text, metadata about masked items)
        """
        matches = self.detect(text)
        
        if not matches:
            return text, []
        
        # Mask from end to start to preserve indices
        masked_text = text
        metadata = []
        
        for match in reversed(matches):
            if preserve_length:
                replacement = mask_char * (match.end - match.start)
            else:
                replacement = f"[{match.type.upper()}]"
            
            masked_text = masked_text[:match.start] + replacement + masked_text[match.end:]
            
            metadata.append({
                "type": match.type,
                "original_value": match.value,
                "position": (match.start, match.end),
                "confidence": match.confidence
            })
        
        return masked_text, metadata
    
    def redact(self, text: str, redaction_map: Dict[str, str] = None) -> Tuple[str, Dict[str, List[str]]]:
        """
        Redact PII with custom replacements
        
        Args:
            text: Text to redact
            redaction_map: Custom replacement map {pii_type: replacement}
        
        Returns:
            Tuple of (redacted_text, detected_pii_summary)
        """
        default_map = {
            "email": "[EMAIL_REDACTED]",
            "phone": "[PHONE_REDACTED]",
            "ssn": "[SSN_REDACTED]",
            "credit_card": "[CC_REDACTED]",
            "ip_address": "[IP_REDACTED]",
            "passport": "[PASSPORT_REDACTED]",
            "date_of_birth": "[DOB_REDACTED]",
            "person_name": "[NAME_REDACTED]",
            "location": "[LOCATION_REDACTED]",
            "organization": "[ORG_REDACTED]",
        }
        
        redaction_map = {**default_map, **(redaction_map or {})}
        
        matches = self.detect(text)
        redacted_text = text
        summary = {}
        
        for match in reversed(matches):
            replacement = redaction_map.get(match.type, "[REDACTED]")
            redacted_text = redacted_text[:match.start] + replacement + redacted_text[match.end:]
            
            if match.type not in summary:
                summary[match.type] = []
            summary[match.type].append(match.value)
        
        return redacted_text, summary
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for PII without masking
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with PII analysis results
        """
        matches = self.detect(text)
        
        # Group by type
        by_type = {}
        for match in matches:
            if match.type not in by_type:
                by_type[match.type] = []
            by_type[match.type].append({
                "value": match.value,
                "position": (match.start, match.end),
                "confidence": match.confidence
            })
        
        return {
            "total_pii_found": len(matches),
            "pii_types": list(by_type.keys()),
            "by_type": by_type,
            "risk_level": self._assess_risk(matches)
        }
    
    def _assess_risk(self, matches: List[PIIMatch]) -> str:
        """Assess privacy risk level based on detected PII"""
        high_risk_types = {"ssn", "credit_card", "passport"}
        medium_risk_types = {"email", "phone", "date_of_birth"}
        
        if any(m.type in high_risk_types for m in matches):
            return "HIGH"
        elif any(m.type in medium_risk_types for m in matches):
            return "MEDIUM"
        elif matches:
            return "LOW"
        else:
            return "NONE"
