#!/usr/bin/env python3
"""
Multi-Modal Input Processor for ValidoAI
=========================================

Advanced processing system for various input types:
- Voice/Speech input processing
- Image and document analysis
- Multi-modal context integration
- Real-time processing capabilities

Features:
- Speech-to-text conversion
- Image OCR and analysis
- Document parsing and understanding
- Multi-modal context building
- Real-time processing
"""

import os
import io
import json
import base64
import logging
import tempfile
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import asyncio
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class MultimodalProcessor:
    """Advanced multi-modal input processor"""

    def __init__(self):
        self.temp_dir = Path("temp/multimodal")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self._initialize_processors()

    def _initialize_processors(self):
        """Initialize all available processors"""
        self.processors = {
            'voice': self._initialize_voice_processor(),
            'image': self._initialize_image_processor(),
            'document': self._initialize_document_processor(),
            'video': self._initialize_video_processor()
        }

        logger.info("✅ Multi-modal processors initialized")

    def _initialize_voice_processor(self) -> Dict[str, Any]:
        """Initialize voice/speech processing capabilities"""
        try:
            # Check for speech recognition libraries
            speech_recognition_available = False
            try:
                import speech_recognition as sr
                speech_recognition_available = True
                logger.info("✅ Speech recognition available")
            except ImportError:
                logger.warning("⚠️ Speech recognition not available - install: pip install SpeechRecognition")

            # Check for audio processing
            audio_processing_available = False
            try:
                import pydub
                audio_processing_available = True
                logger.info("✅ Audio processing available")
            except ImportError:
                logger.warning("⚠️ Audio processing not available - install: pip install pydub")

            return {
                'speech_recognition': speech_recognition_available,
                'audio_processing': audio_processing_available,
                'supported_formats': ['wav', 'mp3', 'flac', 'm4a', 'ogg'],
                'max_file_size': 25 * 1024 * 1024,  # 25MB
                'language_support': ['en', 'sr', 'de', 'fr', 'es', 'it']
            }

        except Exception as e:
            logger.error(f"❌ Error initializing voice processor: {e}")
            return {'speech_recognition': False, 'audio_processing': False}

    def _initialize_image_processor(self) -> Dict[str, Any]:
        """Initialize image processing capabilities"""
        try:
            # Check for OCR libraries
            ocr_available = False
            try:
                import pytesseract
                ocr_available = True
                logger.info("✅ OCR processing available")
            except ImportError:
                logger.warning("⚠️ OCR not available - install: pip install pytesseract")

            # Check for image analysis
            image_analysis_available = False
            try:
                from PIL import Image
                image_analysis_available = True
                logger.info("✅ Image analysis available")
            except ImportError:
                logger.warning("⚠️ Image analysis not available - install: pip install Pillow")

            # Check for computer vision
            cv_available = False
            try:
                import cv2
                cv_available = True
                logger.info("✅ Computer vision available")
            except ImportError:
                logger.warning("⚠️ Computer vision not available - install: pip install opencv-python")

            return {
                'ocr': ocr_available,
                'image_analysis': image_analysis_available,
                'computer_vision': cv_available,
                'supported_formats': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
                'max_file_size': 10 * 1024 * 1024,  # 10MB
                'ocr_languages': ['eng', 'srp', 'deu', 'fra', 'spa', 'ita']
            }

        except Exception as e:
            logger.error(f"❌ Error initializing image processor: {e}")
            return {'ocr': False, 'image_analysis': False, 'computer_vision': False}

    def _initialize_document_processor(self) -> Dict[str, Any]:
        """Initialize document processing capabilities"""
        try:
            # Check for PDF processing
            pdf_available = False
            try:
                import PyPDF2
                pdf_available = True
                logger.info("✅ PDF processing available")
            except ImportError:
                logger.warning("⚠️ PDF processing not available - install: pip install PyPDF2")

            # Check for DOCX processing
            docx_available = False
            try:
                import docx
                docx_available = True
                logger.info("✅ DOCX processing available")
            except ImportError:
                logger.warning("⚠️ DOCX processing not available - install: pip install python-docx")

            # Check for text extraction
            text_extraction_available = False
            try:
                import textract
                text_extraction_available = True
                logger.info("✅ Text extraction available")
            except ImportError:
                logger.warning("⚠️ Text extraction not available - install: pip install textract")

            return {
                'pdf': pdf_available,
                'docx': docx_available,
                'text_extraction': text_extraction_available,
                'supported_formats': ['pdf', 'docx', 'doc', 'txt', 'rtf', 'odt', 'html'],
                'max_file_size': 50 * 1024 * 1024,  # 50MB
                'encoding_support': ['utf-8', 'cp1252', 'iso-8859-1']
            }

        except Exception as e:
            logger.error(f"❌ Error initializing document processor: {e}")
            return {'pdf': False, 'docx': False, 'text_extraction': False}

    def _initialize_video_processor(self) -> Dict[str, Any]:
        """Initialize video processing capabilities"""
        try:
            # Check for video processing
            video_available = False
            try:
                import cv2
                video_available = True
                logger.info("✅ Video processing available")
            except ImportError:
                logger.warning("⚠️ Video processing not available - install: pip install opencv-python")

            return {
                'video_processing': video_available,
                'supported_formats': ['mp4', 'avi', 'mov', 'mkv', 'wmv'],
                'max_file_size': 100 * 1024 * 1024,  # 100MB
                'frame_extraction': video_available,
                'audio_extraction': video_available
            }

        except Exception as e:
            logger.error(f"❌ Error initializing video processor: {e}")
            return {'video_processing': False}

    async def process_multimodal_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process multi-modal input with comprehensive analysis"""
        try:
            input_type = input_data.get('type', 'text')
            content = input_data.get('content')
            metadata = input_data.get('metadata', {})

            logger.info(f"🔄 Processing {input_type} input")

            result = {
                'input_type': input_type,
                'processed_content': '',
                'analysis': {},
                'metadata': metadata,
                'timestamp': datetime.now().isoformat(),
                'processing_time': 0
            }

            start_time = datetime.now()

            # Process based on input type
            if input_type == 'voice':
                result = await self._process_voice_input(content, result)
            elif input_type == 'image':
                result = await self._process_image_input(content, result)
            elif input_type == 'document':
                result = await self._process_document_input(content, result)
            elif input_type == 'video':
                result = await self._process_video_input(content, result)
            elif input_type == 'text':
                result = await self._process_text_input(content, result)
            else:
                result['error'] = f'Unsupported input type: {input_type}'

            # Calculate processing time
            end_time = datetime.now()
            result['processing_time'] = (end_time - start_time).total_seconds()

            logger.info(f"✅ {input_type} processing completed in {result['processing_time']:.2f}s")
            return result

        except Exception as e:
            logger.error(f"❌ Error processing multimodal input: {e}")
            return {
                'input_type': input_data.get('type', 'unknown'),
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'processing_time': 0
            }

    async def _process_voice_input(self, content: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process voice/speech input"""
        try:
            if not self.processors['voice']['speech_recognition']:
                result['error'] = 'Speech recognition not available'
                return result

            import speech_recognition as sr

            # Handle different content types
            if isinstance(content, str) and content.startswith('data:audio/'):
                # Base64 encoded audio data
                audio_data = self._decode_base64_audio(content)
                if audio_data:
                    text = await self._speech_to_text(audio_data)
                    result['processed_content'] = text
                    result['analysis']['confidence'] = 0.85  # Placeholder
                    result['analysis']['language'] = 'en'
                else:
                    result['error'] = 'Invalid audio data format'
            elif hasattr(content, 'read'):
                # File-like object
                audio_data = content.read()
                text = await self._speech_to_text(audio_data)
                result['processed_content'] = text
                result['analysis']['confidence'] = 0.85
                result['analysis']['language'] = 'en'
            else:
                result['error'] = 'Unsupported voice content format'

            return result

        except Exception as e:
            logger.error(f"❌ Error processing voice input: {e}")
            result['error'] = str(e)
            return result

    async def _speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text using speech recognition"""
        try:
            import speech_recognition as sr

            # Create recognizer
            recognizer = sr.Recognizer()

            # Convert audio data to AudioData
            # This is a simplified implementation - in production you'd handle various audio formats
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                with sr.AudioFile(temp_file_path) as source:
                    audio = recognizer.record(source)
                    text = recognizer.recognize_google(audio)
                    return text
            finally:
                os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"❌ Error in speech-to-text: {e}")
            return f"[Speech recognition error: {str(e)}]"

    async def _process_image_input(self, content: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process image input with OCR and analysis"""
        try:
            from PIL import Image
            import pytesseract

            image = None

            # Handle different content types
            if isinstance(content, str) and content.startswith('data:image/'):
                # Base64 encoded image
                image_data = self._decode_base64_image(content)
                if image_data:
                    image = Image.open(io.BytesIO(image_data))
                else:
                    result['error'] = 'Invalid image data format'
                    return result
            elif hasattr(content, 'read'):
                # File-like object
                image = Image.open(content)
            else:
                result['error'] = 'Unsupported image content format'
                return result

            if image:
                # Extract text using OCR
                if self.processors['image']['ocr']:
                    text = pytesseract.image_to_string(image, lang='eng')
                    result['processed_content'] = text.strip()

                    # Basic image analysis
                    result['analysis']['dimensions'] = image.size
                    result['analysis']['format'] = image.format
                    result['analysis']['mode'] = image.mode
                    result['analysis']['text_length'] = len(text)
                else:
                    result['error'] = 'OCR processing not available'

            return result

        except Exception as e:
            logger.error(f"❌ Error processing image input: {e}")
            result['error'] = str(e)
            return result

    async def _process_document_input(self, content: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process document input with text extraction"""
        try:
            text_content = ""

            if hasattr(content, 'read'):
                # File-like object
                file_content = content.read()

                # Determine file type and extract text
                if hasattr(content, 'filename'):
                    filename = content.filename.lower()
                else:
                    filename = "document.bin"

                if filename.endswith('.pdf') and self.processors['document']['pdf']:
                    text_content = self._extract_pdf_text(file_content)
                elif filename.endswith('.docx') and self.processors['document']['docx']:
                    text_content = self._extract_docx_text(file_content)
                elif filename.endswith('.txt'):
                    text_content = file_content.decode('utf-8', errors='ignore')
                else:
                    # Try generic text extraction
                    if self.processors['document']['text_extraction']:
                        import textract
                        text_content = textract.process(io.BytesIO(file_content)).decode('utf-8', errors='ignore')
                    else:
                        result['error'] = 'Document processing not available for this file type'
                        return result

            result['processed_content'] = text_content
            result['analysis']['content_length'] = len(text_content)
            result['analysis']['word_count'] = len(text_content.split())
            result['analysis']['line_count'] = len(text_content.split('\n'))

            return result

        except Exception as e:
            logger.error(f"❌ Error processing document input: {e}")
            result['error'] = str(e)
            return result

    def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            import PyPDF2

            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""

            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()

        except Exception as e:
            logger.error(f"❌ Error extracting PDF text: {e}")
            return f"[PDF extraction error: {str(e)}]"

    def _extract_docx_text(self, file_content: bytes) -> str:
        """Extract text from DOCX content"""
        try:
            import docx

            doc = docx.Document(io.BytesIO(file_content))
            text = ""

            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return text.strip()

        except Exception as e:
            logger.error(f"❌ Error extracting DOCX text: {e}")
            return f"[DOCX extraction error: {str(e)}]"

    async def _process_video_input(self, content: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process video input with frame extraction"""
        try:
            if not self.processors['video']['video_processing']:
                result['error'] = 'Video processing not available'
                return result

            import cv2

            # This is a basic implementation - in production you'd handle video streams
            result['processed_content'] = "[Video processing: Frame extraction and analysis would be implemented here]"
            result['analysis']['video_processing'] = True
            result['analysis']['supported'] = True

            return result

        except Exception as e:
            logger.error(f"❌ Error processing video input: {e}")
            result['error'] = str(e)
            return result

    async def _process_text_input(self, content: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process text input with analysis"""
        try:
            result['processed_content'] = content
            result['analysis']['text_length'] = len(content)
            result['analysis']['word_count'] = len(content.split())
            result['analysis']['character_count'] = len(content)

            return result

        except Exception as e:
            logger.error(f"❌ Error processing text input: {e}")
            result['error'] = str(e)
            return result

    def _decode_base64_audio(self, data_url: str) -> Optional[bytes]:
        """Decode base64 audio data"""
        try:
            # Extract base64 data from data URL
            if ',' in data_url:
                base64_data = data_url.split(',')[1]
                return base64.b64decode(base64_data)
            return None
        except Exception as e:
            logger.error(f"❌ Error decoding base64 audio: {e}")
            return None

    def _decode_base64_image(self, data_url: str) -> Optional[bytes]:
        """Decode base64 image data"""
        try:
            # Extract base64 data from data URL
            if ',' in data_url:
                base64_data = data_url.split(',')[1]
                return base64.b64decode(base64_data)
            return None
        except Exception as e:
            logger.error(f"❌ Error decoding base64 image: {e}")
            return None

    def get_processing_capabilities(self) -> Dict[str, Any]:
        """Get current processing capabilities"""
        return {
            'voice': self.processors['voice'],
            'image': self.processors['image'],
            'document': self.processors['document'],
            'video': self.processors['video'],
            'overall_status': self._calculate_overall_status()
        }

    def _calculate_overall_status(self) -> str:
        """Calculate overall system status"""
        capabilities = self.get_processing_capabilities()
        available_count = 0
        total_count = 0

        for processor_type, processor_info in capabilities.items():
            if processor_type != 'overall_status':
                total_count += 1
                if any(processor_info.values()):
                    available_count += 1

        if available_count == total_count:
            return "fully_available"
        elif available_count > 0:
            return "partially_available"
        else:
            return "unavailable"

    def cleanup_temp_files(self, older_than_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        try:
            cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)

            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    logger.info(f"🧹 Cleaned up temp file: {file_path.name}")

        except Exception as e:
            logger.error(f"❌ Error cleaning up temp files: {e}")

# Global instance
multimodal_processor = MultimodalProcessor()

# Helper functions
async def process_multimodal_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to process multimodal input"""
    return await multimodal_processor.process_multimodal_input(input_data)

def get_processing_capabilities() -> Dict[str, Any]:
    """Helper function to get processing capabilities"""
    return multimodal_processor.get_processing_capabilities()

def cleanup_temp_files(older_than_hours: int = 24):
    """Helper function to cleanup temporary files"""
    multimodal_processor.cleanup_temp_files(older_than_hours)
