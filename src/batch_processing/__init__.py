"""
Batch Processing Package
=======================
Advanced batch processing modules for various file types and operations.

This package provides comprehensive batch processing capabilities for:
- Image processing and favicon generation
- Document processing (PDF, Office, XML, etc.)
- Text analysis and word cloud generation

Main Modules:
- favicon_processor: Batch favicon and icon generation
- document_processor: Multi-format document processing
- wordcloud_processor: Text analysis and word cloud generation

Usage Examples:
    # Favicon processing
    from src.batch_processing.favicon_processor import BatchFaviconProcessor
    processor = BatchFaviconProcessor()
    results = processor.batch_process_directory(Path("images/"))
    
    # Document processing
    from src.batch_processing.document_processor import BatchDocumentProcessor
    doc_processor = BatchDocumentProcessor()
    results = doc_processor.batch_process_directory(Path("documents/"))
    
    # Word cloud generation
    from src.batch_processing.wordcloud_processor import BatchWordCloudProcessor
    wc_processor = BatchWordCloudProcessor()
    results = wc_processor.batch_process_directory(Path("texts/"))
"""

from .favicon_processor import BatchFaviconProcessor, create_sample_images
from .document_processor import BatchDocumentProcessor, create_sample_documents
from .wordcloud_processor import AdvancedWordCloudGenerator, BatchWordCloudProcessor, create_sample_texts

__version__ = "1.0.0"
__author__ = "ValidoAI Team"

__all__ = [
    "BatchFaviconProcessor",
    "BatchDocumentProcessor", 
    "AdvancedWordCloudGenerator",
    "BatchWordCloudProcessor",
    "create_sample_images",
    "create_sample_documents",
    "create_sample_texts"
]

def get_available_processors():
    """Get list of available batch processors with their capabilities"""
    processors = {
        'favicon': {
            'class': BatchFaviconProcessor,
            'description': 'Batch favicon and icon generation',
            'supported_formats': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.svg'],
            'output_formats': ['.png', '.ico', '.webp', '.avif'],
            'features': [
                'Multi-size favicon generation',
                'Platform-specific optimization (iOS, Android, Windows)',
                'Background removal support',
                'Custom shape processing',
                'Web manifest generation',
                'HTML snippet generation'
            ]
        },
        'document': {
            'class': BatchDocumentProcessor,
            'description': 'Multi-format document processing',
            'supported_formats': ['.pdf', '.docx', '.xlsx', '.xml', '.html', '.txt', '.csv', '.zip'],
            'features': [
                'PDF text and table extraction',
                'Office document metadata extraction',
                'XML structure analysis and validation',
                'Archive content analysis',
                'Text encoding detection',
                'Comprehensive metadata extraction'
            ]
        },
        'wordcloud': {
            'class': BatchWordCloudProcessor,
            'description': 'Text analysis and word cloud generation',
            'supported_formats': ['.txt', '.csv', '.json', '.xml', '.html', '.md'],
            'features': [
                'Advanced text preprocessing',
                'Sentiment analysis',
                'Keyword extraction with TF-IDF',
                'Language detection',
                'Custom color schemes',
                'Comparative word clouds',
                'Shaped word clouds with masks'
            ]
        }
    }
    
    return processors

def check_dependencies():
    """Check availability of optional dependencies for each processor"""
    dependencies = {
        'favicon': {
            'required': ['Pillow', 'numpy'],
            'optional': ['rembg', 'cairosvg']
        },
        'document': {
            'required': ['pandas', 'chardet'],
            'optional': ['PyPDF2', 'pdfplumber', 'python-docx', 'openpyxl', 'beautifulsoup4', 'lxml']
        },
        'wordcloud': {
            'required': ['wordcloud', 'matplotlib', 'pandas'],
            'optional': ['textblob', 'nltk', 'scikit-learn', 'langdetect']
        }
    }
    
    status = {}
    
    for processor, deps in dependencies.items():
        status[processor] = {
            'required': {},
            'optional': {}
        }
        
        # Check required dependencies
        for dep in deps['required']:
            try:
                __import__(dep.lower().replace('-', '_'))
                status[processor]['required'][dep] = True
            except ImportError:
                status[processor]['required'][dep] = False
        
        # Check optional dependencies
        for dep in deps['optional']:
            try:
                __import__(dep.lower().replace('-', '_'))
                status[processor]['optional'][dep] = True
            except ImportError:
                status[processor]['optional'][dep] = False
    
    return status

if __name__ == "__main__":
    print("📦 ValidoAI Batch Processing Package")
    print("=" * 40)
    
    processors = get_available_processors()
    
    print("\n🔧 Available Processors:")
    for name, info in processors.items():
        print(f"\n   📂 {name.title()} Processor:")
        print(f"      {info['description']}")
        print(f"      Formats: {', '.join(info['supported_formats'])}")
        print(f"      Features: {len(info['features'])} capabilities")
    
    print(f"\n✅ Package version: {__version__}")
    print(f"👥 Author: {__author__}")
    
    # Check dependencies
    deps = check_dependencies()
    print(f"\n🔍 Dependency Status:")
    for processor, status in deps.items():
        required_ok = all(status['required'].values())
        optional_count = sum(status['optional'].values())
        total_optional = len(status['optional'])
        
        print(f"   {processor}: {'✅' if required_ok else '❌'} Required deps, {optional_count}/{total_optional} optional")
