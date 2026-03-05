#!/usr/bin/env python3
"""
Batch Processing Demonstration
============================
Comprehensive demonstration of all batch processing capabilities in ValidoAI.

This notebook-style script demonstrates:
1. Favicon batch processing
2. Document batch processing (PDF, XML, Office files)
3. Word cloud generation and text analysis
4. Integration examples and best practices

Run this script to see all batch processing features in action.
"""

# %% [markdown]
# # 🚀 **ValidoAI Batch Processing Demonstration**
# 
# Welcome to the comprehensive batch processing demonstration! This notebook shows
# how to use all the advanced batch processing capabilities in ValidoAI.
# 
# ## 📋 **What's Covered:**
# - Favicon and icon batch processing
# - Document processing (PDF, XML, Office files)
# - Word cloud generation and text analysis
# - Performance monitoring and reporting
# - Integration examples

# %% Setup and Imports
import sys
import os
from pathlib import Path
import time
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import batch processing modules
try:
    from src.batch_processing import (
        BatchFaviconProcessor, 
        BatchDocumentProcessor, 
        BatchWordCloudProcessor,
        create_sample_images,
        create_sample_documents,
        create_sample_texts,
        get_available_processors,
        check_dependencies
    )
    BATCH_PROCESSING_AVAILABLE = True
    print("✅ Batch processing modules loaded successfully")
except ImportError as e:
    BATCH_PROCESSING_AVAILABLE = False
    print(f"❌ Batch processing modules not available: {e}")

# %% [markdown]
# ## 🔍 **System Check and Capabilities**

# %% System Check
def check_system_capabilities():
    """Check system capabilities and available processors"""
    print("🔍 System Capabilities Check")
    print("=" * 40)
    
    if not BATCH_PROCESSING_AVAILABLE:
        print("❌ Batch processing not available")
        return False
    
    # Check available processors
    processors = get_available_processors()
    print(f"\n📦 Available Processors: {len(processors)}")
    
    for name, info in processors.items():
        print(f"\n   📂 {name.title()} Processor:")
        print(f"      • {info['description']}")
        print(f"      • Formats: {len(info['supported_formats'])} supported")
        print(f"      • Features: {len(info['features'])} capabilities")
    
    # Check dependencies
    print(f"\n🔧 Dependency Status:")
    deps = check_dependencies()
    
    all_good = True
    for processor, status in deps.items():
        required_ok = all(status['required'].values())
        optional_count = sum(status['optional'].values())
        total_optional = len(status['optional'])
        
        status_icon = "✅" if required_ok else "❌"
        print(f"   {status_icon} {processor.title()}: Required deps {'OK' if required_ok else 'MISSING'}, {optional_count}/{total_optional} optional")
        
        if not required_ok:
            all_good = False
            missing = [dep for dep, avail in status['required'].items() if not avail]
            print(f"      Missing: {', '.join(missing)}")
    
    return all_good

system_ok = check_system_capabilities()

# %% [markdown]
# ## 🖼️ **Favicon Batch Processing Demonstration**

# %% Favicon Processing
def demonstrate_favicon_processing():
    """Demonstrate favicon batch processing"""
    print("\n🖼️ Favicon Batch Processing")
    print("=" * 40)
    
    if not BATCH_PROCESSING_AVAILABLE:
        print("❌ Batch processing not available")
        return
    
    try:
        # Create sample images
        print("📁 Creating sample images...")
        sample_images = create_sample_images("demo_images")
        print(f"✅ Created {len(sample_images)} sample images")
        
        # Initialize favicon processor
        favicon_processor = BatchFaviconProcessor("demo_output/favicons")
        
        # Process images
        print("\n🔄 Processing images...")
        start_time = time.time()
        results = favicon_processor.batch_process_directory(
            Path("demo_images"), 
            recursive=True, 
            remove_bg=False,
            max_workers=2
        )
        processing_time = time.time() - start_time
        
        # Generate report
        report = favicon_processor.generate_processing_report(results)
        
        print(f"\n📊 Favicon Processing Results:")
        print(f"   • Processed: {report['summary']['successful']}/{report['summary']['total_processed']}")
        print(f"   • Files created: {report['summary']['total_files_created']}")
        print(f"   • Success rate: {report['summary']['success_rate']:.1f}%")
        print(f"   • Processing time: {processing_time:.2f}s")
        print(f"   • Output: demo_output/favicons/")
        
        return results
        
    except Exception as e:
        print(f"❌ Favicon processing error: {e}")
        return []

favicon_results = demonstrate_favicon_processing()

# %% [markdown]
# ## 📄 **Document Batch Processing Demonstration**

# %% Document Processing
def demonstrate_document_processing():
    """Demonstrate document batch processing"""
    print("\n📄 Document Batch Processing")
    print("=" * 40)
    
    if not BATCH_PROCESSING_AVAILABLE:
        print("❌ Batch processing not available")
        return
    
    try:
        # Create sample documents
        print("📁 Creating sample documents...")
        sample_docs = create_sample_documents("demo_documents")
        print(f"✅ Created {len(sample_docs)} sample documents")
        
        # Initialize document processor
        doc_processor = BatchDocumentProcessor("demo_output/documents")
        
        # Process documents
        print("\n🔄 Processing documents...")
        start_time = time.time()
        results = doc_processor.batch_process_directory(
            Path("demo_documents"),
            recursive=True,
            max_workers=2
        )
        processing_time = time.time() - start_time
        
        # Generate report
        report = doc_processor.generate_processing_report(results)
        
        print(f"\n📊 Document Processing Results:")
        print(f"   • Processed: {report['summary']['successful']}/{report['summary']['total_processed']}")
        print(f"   • Success rate: {report['summary']['success_rate']:.1f}%")
        print(f"   • Total size: {report['summary']['total_size_mb']:.2f} MB")
        print(f"   • Processing time: {processing_time:.2f}s")
        print(f"   • Output: demo_output/documents/")
        
        # Show format breakdown
        print(f"\n📂 By format:")
        for format_name, info in report['by_format'].items():
            print(f"   • {format_name}: {info['count']} files")
        
        return results
        
    except Exception as e:
        print(f"❌ Document processing error: {e}")
        return []

document_results = demonstrate_document_processing()

# %% [markdown]
# ## 📊 **Word Cloud and Text Analysis Demonstration**

# %% Word Cloud Processing
def demonstrate_wordcloud_processing():
    """Demonstrate word cloud batch processing"""
    print("\n📊 Word Cloud and Text Analysis")
    print("=" * 40)
    
    if not BATCH_PROCESSING_AVAILABLE:
        print("❌ Batch processing not available")
        return
    
    try:
        # Create sample text files
        print("📁 Creating sample text files...")
        sample_texts = create_sample_texts("demo_texts")
        print(f"✅ Created {len(sample_texts)} sample text files")
        
        # Initialize word cloud processor
        wc_processor = BatchWordCloudProcessor("demo_output/wordclouds")
        
        # Process text files
        print("\n🔄 Processing text files...")
        start_time = time.time()
        results = wc_processor.batch_process_directory(
            Path("demo_texts"),
            recursive=True,
            max_workers=2
        )
        processing_time = time.time() - start_time
        
        # Generate report
        report = wc_processor.generate_processing_report(results)
        
        print(f"\n📊 Word Cloud Processing Results:")
        print(f"   • Processed: {report['summary']['successful']}/{report['summary']['total_processed']}")
        print(f"   • Success rate: {report['summary']['success_rate']:.1f}%")
        print(f"   • Total words: {report['summary']['total_words']:,}")
        print(f"   • Processing time: {processing_time:.2f}s")
        print(f"   • Output: demo_output/wordclouds/")
        
        # Show sentiment analysis
        sentiment = report['sentiment_analysis']
        print(f"\n😊 Sentiment Analysis:")
        print(f"   • Positive: {sentiment['positive']} files")
        print(f"   • Negative: {sentiment['negative']} files")
        print(f"   • Neutral: {sentiment['neutral']} files")
        
        return results
        
    except Exception as e:
        print(f"❌ Word cloud processing error: {e}")
        return []

wordcloud_results = demonstrate_wordcloud_processing()

# %% [markdown]
# ## 📈 **Performance Analysis and Comparison**

# %% Performance Analysis
def analyze_performance():
    """Analyze performance across all processors"""
    print("\n📈 Performance Analysis")
    print("=" * 40)
    
    if not all([favicon_results, document_results, wordcloud_results]):
        print("⚠️ Not all processors completed successfully")
        return
    
    # Collect performance data
    performance_data = {
        'favicon': {
            'files_processed': len([r for r in favicon_results if r.get('success')]),
            'total_time': sum(r.get('processing_time', 0) for r in favicon_results if r.get('success')),
            'files_created': sum(r.get('total_files_created', 0) for r in favicon_results if r.get('success'))
        },
        'document': {
            'files_processed': len([r for r in document_results if r.get('success')]),
            'total_time': sum(r.get('processing_time', 0) for r in document_results if r.get('success')),
            'formats_supported': len(set(r.get('file_info', {}).get('category') for r in document_results if r.get('success')))
        },
        'wordcloud': {
            'files_processed': len([r for r in wordcloud_results if r.get('success')]),
            'total_time': sum(r.get('processing_time', 0) for r in wordcloud_results if r.get('success')),
            'total_words': sum(r.get('word_count', 0) for r in wordcloud_results if r.get('success'))
        }
    }
    
    print("⚡ Processing Performance:")
    for processor, data in performance_data.items():
        files = data['files_processed']
        time_taken = data['total_time']
        avg_time = time_taken / files if files > 0 else 0
        
        print(f"\n   📂 {processor.title()}:")
        print(f"      • Files processed: {files}")
        print(f"      • Total time: {time_taken:.2f}s")
        print(f"      • Average time per file: {avg_time:.3f}s")
        
        if processor == 'favicon':
            print(f"      • Total files created: {data['files_created']}")
        elif processor == 'document':
            print(f"      • Formats supported: {data['formats_supported']}")
        elif processor == 'wordcloud':
            print(f"      • Total words processed: {data['total_words']:,}")
    
    # Calculate overall statistics
    total_files = sum(data['files_processed'] for data in performance_data.values())
    total_time = sum(data['total_time'] for data in performance_data.values())
    
    print(f"\n🎯 Overall Performance:")
    print(f"   • Total files processed: {total_files}")
    print(f"   • Total processing time: {total_time:.2f}s")
    print(f"   • Average throughput: {total_files / total_time:.2f} files/second")

analyze_performance()

# %% [markdown]
# ## 💡 **Integration Examples and Best Practices**

# %% Integration Examples
def show_integration_examples():
    """Show integration examples and best practices"""
    print("\n💡 Integration Examples and Best Practices")
    print("=" * 50)
    
    print("""
🔧 **Production Integration Examples:**

1. **Web Application Favicon Generation:**
   ```python
   from src.batch_processing import BatchFaviconProcessor
   
   processor = BatchFaviconProcessor("static/favicons")
   results = processor.batch_process_directory(
       Path("uploaded_logos/"),
       remove_bg=True,  # Remove backgrounds
       max_workers=4    # Parallel processing
   )
   ```

2. **Document Management System:**
   ```python
   from src.batch_processing import BatchDocumentProcessor
   
   doc_processor = BatchDocumentProcessor("processed_docs")
   results = doc_processor.batch_process_directory(
       Path("incoming_documents/"),
       recursive=True,
       max_workers=6
   )
   ```

3. **Content Analysis Pipeline:**
   ```python
   from src.batch_processing import BatchWordCloudProcessor
   
   wc_processor = BatchWordCloudProcessor("analysis_output")
   results = wc_processor.batch_process_directory(
       Path("content/articles/"),
       max_workers=8
   )
   ```

📋 **Best Practices:**

• **Performance Optimization:**
  - Use SSD storage for better I/O performance
  - Adjust max_workers based on CPU cores (typically CPU count - 1)
  - Monitor memory usage for large files
  - Implement file size limits if needed

• **Error Handling:**
  - Always check processing results for errors
  - Implement retry logic for failed files
  - Log errors for debugging and monitoring
  - Validate input files before processing

• **Resource Management:**
  - Clean up temporary files after processing
  - Implement proper exception handling
  - Use context managers for file operations
  - Monitor disk space usage

• **Security Considerations:**
  - Validate file types and extensions
  - Scan uploaded files for malware
  - Implement file size limits
  - Use secure temporary directories

🚀 **Production Deployment:**

1. **Docker Integration:**
   ```dockerfile
   FROM python:3.9-slim
   RUN pip install -r requirements.txt
   COPY src/ /app/src/
   WORKDIR /app
   ```

2. **API Endpoint Example:**
   ```python
   @app.route('/api/process-favicons', methods=['POST'])
   def process_favicons():
       files = request.files.getlist('images')
       processor = BatchFaviconProcessor()
       results = processor.process_uploaded_files(files)
       return jsonify(results)
   ```

3. **Background Task Integration:**
   ```python
   from celery import Celery
   
   @celery.task
   def process_documents_async(directory_path):
       processor = BatchDocumentProcessor()
       return processor.batch_process_directory(Path(directory_path))
   ```
""")

show_integration_examples()

# %% [markdown]
# ## 📋 **Summary and Next Steps**

# %% Summary
def generate_final_summary():
    """Generate final summary of the demonstration"""
    print("\n📋 Final Summary")
    print("=" * 30)
    
    print("🎉 **Demonstration Complete!**")
    print(f"✅ System check: {'PASSED' if system_ok else 'FAILED'}")
    print(f"✅ Favicon processing: {'COMPLETED' if favicon_results else 'FAILED'}")
    print(f"✅ Document processing: {'COMPLETED' if document_results else 'FAILED'}")
    print(f"✅ Word cloud processing: {'COMPLETED' if wordcloud_results else 'FAILED'}")
    
    print(f"\n📁 **Output Locations:**")
    print(f"   • Favicons: demo_output/favicons/")
    print(f"   • Documents: demo_output/documents/")
    print(f"   • Word clouds: demo_output/wordclouds/")
    
    print(f"\n🚀 **Ready for Production Use:**")
    capabilities = [
        "Multi-threaded parallel processing",
        "Comprehensive error handling and reporting",
        "Support for 15+ file formats",
        "Advanced image processing and optimization",
        "Text analysis and sentiment detection",
        "Automated metadata extraction",
        "Scalable batch operations",
        "Production-ready API integration"
    ]
    
    for i, capability in enumerate(capabilities, 1):
        print(f"   {i:2d}. {capability}")
    
    print(f"\n💡 **Next Steps:**")
    next_steps = [
        "Install optional dependencies for enhanced features",
        "Configure production environment settings",
        "Implement custom processing workflows",
        "Set up monitoring and logging",
        "Scale with distributed processing",
        "Integrate with existing applications"
    ]
    
    for i, step in enumerate(next_steps, 1):
        print(f"   {i}. {step}")
    
    print(f"\n🎯 **ValidoAI Batch Processing Suite is ready for enterprise use!**")

generate_final_summary()

# %% Cleanup
def cleanup_demo_files():
    """Clean up demonstration files"""
    import shutil
    
    print("\n🧹 Cleaning up demo files...")
    
    demo_dirs = ["demo_images", "demo_documents", "demo_texts"]
    for demo_dir in demo_dirs:
        if Path(demo_dir).exists():
            shutil.rmtree(demo_dir)
            print(f"   ✅ Removed {demo_dir}/")
    
    print("🎉 Cleanup complete!")

# Uncomment the next line to clean up demo files
# cleanup_demo_files()

if __name__ == "__main__":
    print("🎉 ValidoAI Batch Processing Demonstration Complete!")
    print("📝 Check the output directories for generated files")
    print("🚀 Ready for production deployment!")
