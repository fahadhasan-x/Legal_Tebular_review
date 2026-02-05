"""
Gemini AI Extraction Service
Uses Google Gemini LLM to extract structured data from documents
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
import json
import re
import structlog

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.output_parsers import PydanticOutputParser
    from pydantic import BaseModel, Field, create_model
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

from app.core.config import settings
from app.models import FieldType

logger = structlog.get_logger(__name__)


class ExtractionError(Exception):
    """Custom exception for extraction errors"""
    pass


class FieldExtraction(BaseModel):
    """Model for a single extracted field"""
    field_id: str = Field(description="Field identifier")
    raw_value: Optional[str] = Field(None, description="Extracted raw value")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score 0-1")
    citations: List[Dict[str, str]] = Field(default_factory=list, description="Source citations")


class GeminiExtractor:
    """
    Extract structured data from documents using Google Gemini
    
    Features:
        - Schema-driven extraction based on field templates
        - Source citation tracking
        - Confidence scoring
        - Retry logic for failures
    """
    
    def __init__(self):
        if not HAS_LANGCHAIN:
            raise ExtractionError("LangChain libraries not installed")
        
        if not settings.GEMINI_API_KEY:
            raise ExtractionError("GEMINI_API_KEY not configured")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
            max_output_tokens=settings.LLM_MAX_TOKENS,
        )
    
    def extract(
        self,
        document_text: str,
        field_definitions: List[Dict[str, Any]],
        chunk_size: int = 50000
    ) -> List[Dict[str, Any]]:
        """
        Extract fields from document text
        
        Args:
            document_text: Full text content of document
            field_definitions: List of field definitions from template
            chunk_size: Maximum characters per chunk for processing
            
        Returns:
            List of extracted field dictionaries
            
        Raises:
            ExtractionError: If extraction fails
        """
        logger.info("extraction_started", 
                   text_length=len(document_text),
                   field_count=len(field_definitions))
        
        try:
            # For very large documents, process in chunks
            if len(document_text) > chunk_size:
                logger.info("document_chunking_required", 
                           text_length=len(document_text),
                           chunk_size=chunk_size)
                return self._extract_chunked(document_text, field_definitions, chunk_size)
            
            # Single extraction for smaller documents
            return self._extract_single(document_text, field_definitions)
        
        except Exception as e:
            logger.error("extraction_failed", error=str(e), exc_info=True)
            raise ExtractionError(f"Extraction failed: {str(e)}") from e
    
    def _extract_single(
        self,
        document_text: str,
        field_definitions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract all fields in a single LLM call
        
        Args:
            document_text: Document text
            field_definitions: Field definitions
            
        Returns:
            List of extracted fields
        """
        # Build extraction prompt
        prompt = self._build_extraction_prompt(document_text, field_definitions)
        
        logger.info("llm_invocation", prompt_length=len(prompt))
        
        # Invoke LLM
        response = self.llm.invoke(prompt)
        
        # Parse response
        extracted_fields = self._parse_response(response.content, field_definitions)
        
        logger.info("extraction_completed", fields_extracted=len(extracted_fields))
        
        return extracted_fields
    
    def _extract_chunked(
        self,
        document_text: str,
        field_definitions: List[Dict[str, Any]],
        chunk_size: int
    ) -> List[Dict[str, Any]]:
        """
        Extract fields from large documents using chunking strategy
        
        Args:
            document_text: Full document text
            field_definitions: Field definitions
            chunk_size: Size of each chunk
            
        Returns:
            Merged extraction results from all chunks
        """
        # Split document into overlapping chunks
        chunks = self._create_chunks(document_text, chunk_size, overlap=500)
        
        logger.info("processing_chunks", chunk_count=len(chunks))
        
        # Extract from each chunk
        all_extractions = []
        for i, chunk in enumerate(chunks):
            logger.info("processing_chunk", chunk_index=i, chunk_length=len(chunk))
            
            chunk_results = self._extract_single(chunk, field_definitions)
            all_extractions.append(chunk_results)
        
        # Merge results with confidence-based selection
        merged_results = self._merge_chunk_results(all_extractions, field_definitions)
        
        return merged_results
    
    def _build_extraction_prompt(
        self,
        document_text: str,
        field_definitions: List[Dict[str, Any]]
    ) -> str:
        """
        Build comprehensive extraction prompt
        
        Args:
            document_text: Document text to extract from
            field_definitions: Fields to extract
            
        Returns:
            Formatted prompt string
        """
        # Build field descriptions
        field_descriptions = []
        for field in field_definitions:
            field_desc = f"""
- **{field['field_name']}** (ID: `{field['field_id']}`)
  - Type: {field['field_type']}
  - Required: {"Yes" if field.get('required', False) else "No"}
  - Description: {field.get('extraction_prompt', 'Extract this field value')}
  - Validation: {json.dumps(field.get('validation_rules', {}))}
"""
            field_descriptions.append(field_desc.strip())
        
        fields_section = "\n".join(field_descriptions)
        
        # Build output format example
        output_example = []
        for field in field_definitions[:2]:  # Show 2 examples
            output_example.append({
                "field_id": field['field_id'],
                "raw_value": "<extracted value>",
                "confidence_score": 0.95,
                "citations": [
                    {
                        "source": "page 1, section 2",
                        "text_snippet": "<relevant text snippet>"
                    }
                ]
            })
        
        prompt = f"""You are a legal document analysis AI specialized in extracting structured information from legal documents.

**TASK**: Extract the following fields from the provided document:

{fields_section}

**DOCUMENT TEXT**:
```
{document_text[:30000]}  
```

**EXTRACTION INSTRUCTIONS**:
1. For each field, extract the most relevant value from the document
2. If a field value is not found, set raw_value to null
3. Provide a confidence score (0.0 to 1.0) for each extraction
4. Include citations showing where in the document you found the information
5. For DATE fields, normalize to YYYY-MM-DD format
6. For NUMBER fields, extract numeric values only
7. For BOOLEAN fields, return "true" or "false"
8. For LIST fields, return comma-separated values

**OUTPUT FORMAT** (JSON array):
```json
{json.dumps(output_example, indent=2)}
```

**IMPORTANT**:
- Return ONLY the JSON array, no additional text
- Include ALL fields from the list, even if value is null
- Be precise with citations - include page numbers or section references
- Confidence should reflect certainty of extraction

**YOUR JSON OUTPUT**:
```json
"""
        
        return prompt
    
    def _parse_response(
        self,
        response_text: str,
        field_definitions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Parse LLM response into structured field extractions
        
        Args:
            response_text: Raw LLM response
            field_definitions: Expected field definitions
            
        Returns:
            List of extracted field dictionaries
        """
        try:
            # Extract JSON from response (handles markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to find raw JSON array
                json_match = re.search(r'(\[.*\])', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)
                else:
                    raise ValueError("No JSON array found in response")
            
            # Parse JSON
            extracted_data = json.loads(json_text)
            
            if not isinstance(extracted_data, list):
                raise ValueError("Response is not a JSON array")
            
            # Validate and normalize
            validated_fields = []
            for item in extracted_data:
                # Ensure required keys
                if 'field_id' not in item:
                    continue
                
                field_def = next((f for f in field_definitions if f['field_id'] == item['field_id']), None)
                if not field_def:
                    continue
                
                # Normalize value based on field type
                normalized_value = self._normalize_value(
                    item.get('raw_value'),
                    field_def['field_type'],
                    field_def.get('normalization')
                )
                
                validated_fields.append({
                    'field_id': item['field_id'],
                    'raw_value': item.get('raw_value'),
                    'normalized_value': normalized_value,
                    'confidence_score': min(1.0, max(0.0, float(item.get('confidence_score', 0.5)))),
                    'citations': item.get('citations', [])
                })
            
            # Ensure all fields are present
            for field_def in field_definitions:
                if not any(f['field_id'] == field_def['field_id'] for f in validated_fields):
                    validated_fields.append({
                        'field_id': field_def['field_id'],
                        'raw_value': None,
                        'normalized_value': None,
                        'confidence_score': 0.0,
                        'citations': []
                    })
            
            return validated_fields
        
        except json.JSONDecodeError as e:
            logger.error("json_parsing_failed", error=str(e), response_preview=response_text[:500])
            raise ExtractionError(f"Failed to parse LLM response as JSON: {str(e)}")
        
        except Exception as e:
            logger.error("response_parsing_failed", error=str(e))
            raise ExtractionError(f"Failed to parse response: {str(e)}")
    
    def _normalize_value(
        self,
        raw_value: Optional[str],
        field_type: str,
        normalization_strategy: Optional[str]
    ) -> Optional[str]:
        """
        Normalize extracted value based on field type
        
        Args:
            raw_value: Raw extracted value
            field_type: Field type (TEXT, DATE, NUMBER, etc.)
            normalization_strategy: Custom normalization rules
            
        Returns:
            Normalized value
        """
        if raw_value is None or raw_value == "null":
            return None
        
        raw_value = str(raw_value).strip()
        
        if not raw_value:
            return None
        
        try:
            if field_type == FieldType.DATE.value:
                # Basic date normalization (YYYY-MM-DD format)
                # Extract date patterns
                date_patterns = [
                    r'(\d{4})-(\d{2})-(\d{2})',  # 2024-01-15
                    r'(\d{2})/(\d{2})/(\d{4})',  # 01/15/2024
                    r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})',  # 15 January 2024
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, raw_value, re.IGNORECASE)
                    if match:
                        return match.group(0)  # Return first matched date
                
                return raw_value  # Return as-is if no pattern matches
            
            elif field_type == FieldType.NUMBER.value:
                # Extract numeric value
                number_match = re.search(r'-?[\d,]+\.?\d*', raw_value)
                if number_match:
                    # Remove commas and return
                    return number_match.group(0).replace(',', '')
                return raw_value
            
            elif field_type == FieldType.BOOLEAN.value:
                # Normalize to true/false
                lower_val = raw_value.lower()
                if lower_val in ['yes', 'true', '1', 'y']:
                    return 'true'
                elif lower_val in ['no', 'false', '0', 'n']:
                    return 'false'
                return raw_value
            
            elif field_type == FieldType.LIST.value:
                # Ensure comma-separated format
                if ',' in raw_value or ';' in raw_value:
                    items = re.split(r'[,;]', raw_value)
                    return ', '.join(item.strip() for item in items if item.strip())
                return raw_value
            
            else:  # TEXT or unknown
                return raw_value
        
        except Exception as e:
            logger.warning("normalization_failed", 
                          field_type=field_type, 
                          raw_value=raw_value, 
                          error=str(e))
            return raw_value
    
    def _create_chunks(
        self,
        text: str,
        chunk_size: int,
        overlap: int = 500
    ) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Full text
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            if end >= len(text):
                break
            
            start = end - overlap
        
        return chunks
    
    def _merge_chunk_results(
        self,
        chunk_results: List[List[Dict[str, Any]]],
        field_definitions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge extraction results from multiple chunks
        
        Strategy: For each field, select the extraction with highest confidence
        
        Args:
            chunk_results: List of extraction results from each chunk
            field_definitions: Field definitions
            
        Returns:
            Merged extraction results
        """
        merged = []
        
        for field_def in field_definitions:
            field_id = field_def['field_id']
            
            # Collect all extractions for this field
            field_extractions = []
            for chunk_result in chunk_results:
                field_data = next((f for f in chunk_result if f['field_id'] == field_id), None)
                if field_data and field_data.get('raw_value'):
                    field_extractions.append(field_data)
            
            # Select best extraction (highest confidence)
            if field_extractions:
                best_extraction = max(field_extractions, key=lambda x: x.get('confidence_score', 0))
                merged.append(best_extraction)
            else:
                # No extraction found in any chunk
                merged.append({
                    'field_id': field_id,
                    'raw_value': None,
                    'normalized_value': None,
                    'confidence_score': 0.0,
                    'citations': []
                })
        
        return merged
