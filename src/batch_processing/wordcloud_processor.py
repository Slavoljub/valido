#!/usr/bin/env python3
"""
Advanced Word Cloud Processing Module
====================================
Comprehensive word cloud generation and text visualization with batch processing support.
"""

import os
import json
import time
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    import pandas as pd
    from wordcloud import WordCloud, STOPWORDS
    from PIL import Image, ImageDraw, ImageFont
    from tqdm import tqdm
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False
    print("⚠️ Word cloud libraries not available. Install: pip install wordcloud matplotlib seaborn pandas pillow tqdm")

try:
    from textblob import TextBlob
    from langdetect import detect
    import nltk
    # Download required NLTK data
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
    except:
        pass
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    TEXT_PROCESSING_AVAILABLE = True
except ImportError:
    TEXT_PROCESSING_AVAILABLE = False
    print("⚠️ Advanced text processing not available. Install: pip install textblob langdetect nltk")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ Machine learning features not available. Install: pip install scikit-learn")

class AdvancedWordCloudGenerator:
    """Advanced Word Cloud Generator with comprehensive text processing capabilities"""
    
    def __init__(self):
        self.stopwords = set(STOPWORDS) if WORDCLOUD_AVAILABLE else set()
        self.custom_stopwords = set()
        self.sentiment_analyzer = None
        
        # Initialize sentiment analyzer if available
        if TEXT_PROCESSING_AVAILABLE:
            try:
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
            except:
                pass
        
        # Color schemes for different themes
        self.color_schemes = {
            'corporate': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            'ocean': ['#006994', '#3498db', '#5dade2', '#85c1e9', '#aed6f1'],
            'sunset': ['#ff6b6b', '#ffa726', '#ffcc02', '#66bb6a', '#42a5f5'],
            'forest': ['#2e7d32', '#388e3c', '#43a047', '#4caf50', '#66bb6a'],
            'purple': ['#6a1b9a', '#8e24aa', '#ab47bc', '#ba68c8', '#ce93d8'],
            'grayscale': ['#212121', '#424242', '#616161', '#757575', '#9e9e9e']
        }
    
    def add_custom_stopwords(self, words):
        """Add custom stopwords"""
        if isinstance(words, str):
            words = [words]
        self.custom_stopwords.update(words)
        self.stopwords.update(words)
    
    def preprocess_text(self, text, language='english', remove_numbers=True, min_word_length=2):
        """Advanced text preprocessing"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove numbers if requested
        if remove_numbers:
            text = re.sub(r'\d+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove stopwords and filter by length
        if TEXT_PROCESSING_AVAILABLE:
            try:
                stop_words = set(stopwords.words(language))
                stop_words.update(self.stopwords)
                words = word_tokenize(text)
                words = [word for word in words if word not in stop_words and len(word) >= min_word_length]
                text = ' '.join(words)
            except:
                # Fallback if NLTK is not available
                words = text.split()
                words = [word for word in words if word not in self.stopwords and len(word) >= min_word_length]
                text = ' '.join(words)
        else:
            # Simple fallback
            words = text.split()
            words = [word for word in words if word not in self.stopwords and len(word) >= min_word_length]
            text = ' '.join(words)
        
        return text
    
    def detect_language(self, text):
        """Detect the language of the text"""
        if not TEXT_PROCESSING_AVAILABLE:
            return 'english'
            
        try:
            language = detect(text)
            language_map = {
                'en': 'english',
                'es': 'spanish',
                'fr': 'french',
                'de': 'german',
                'it': 'italian',
                'pt': 'portuguese',
                'ru': 'russian',
                'ar': 'arabic',
                'zh': 'chinese',
                'ja': 'japanese'
            }
            return language_map.get(language, 'english')
        except:
            return 'english'
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of the text"""
        if not self.sentiment_analyzer:
            return {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0}
        
        try:
            return self.sentiment_analyzer.polarity_scores(text)
        except:
            return {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0}
    
    def extract_keywords(self, text, max_features=100):
        """Extract keywords using TF-IDF"""
        if not ML_AVAILABLE:
            # Simple word frequency fallback
            words = text.split()
            word_freq = Counter(words)
            return [(word, freq) for word, freq in word_freq.most_common(max_features)]
            
        try:
            vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            keywords = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
            keywords.sort(key=lambda x: x[1], reverse=True)
            
            return keywords
        except Exception as e:
            print(f"⚠️ Keyword extraction failed: {e}")
            return []
    
    def create_mask_from_image(self, image_path, threshold=128):
        """Create a mask from an image for shaped word clouds"""
        if not WORDCLOUD_AVAILABLE:
            return None
            
        try:
            image = Image.open(image_path)
            # Convert to grayscale
            image = image.convert('L')
            # Convert to numpy array
            mask = np.array(image)
            # Create binary mask
            mask = np.where(mask > threshold, 255, 0)
            return mask
        except Exception as e:
            print(f"❌ Error creating mask: {e}")
            return None
    
    def generate_wordcloud(self, text, **kwargs):
        """Generate a word cloud with advanced options"""
        if not WORDCLOUD_AVAILABLE:
            print("❌ Word cloud libraries not available")
            return None
            
        # Default parameters
        params = {
            'width': 1200,
            'height': 600,
            'background_color': 'white',
            'max_words': 100,
            'colormap': 'viridis',
            'relative_scaling': 0.5,
            'min_font_size': 10,
            'max_font_size': 100,
            'prefer_horizontal': 0.7,
            'stopwords': self.stopwords,
            'collocations': False
        }
        
        # Update with user parameters
        params.update(kwargs)
        
        # Create WordCloud object
        wordcloud = WordCloud(**params)
        
        # Generate word cloud
        wordcloud.generate(text)
        
        return wordcloud
    
    def create_comparative_wordcloud(self, texts, labels, figsize=(15, 8)):
        """Create comparative word clouds"""
        if not WORDCLOUD_AVAILABLE:
            print("❌ Word cloud libraries not available")
            return None
            
        fig, axes = plt.subplots(1, len(texts), figsize=figsize)
        if len(texts) == 1:
            axes = [axes]
        
        for i, (text, label) in enumerate(zip(texts, labels)):
            wordcloud = self.generate_wordcloud(text)
            if wordcloud:
                axes[i].imshow(wordcloud, interpolation='bilinear')
                axes[i].set_title(label, fontsize=16, fontweight='bold')
                axes[i].axis('off')
        
        plt.tight_layout()
        return fig
    
    def save_wordcloud(self, wordcloud, filename, dpi=300):
        """Save word cloud to file"""
        if not wordcloud:
            print("❌ No word cloud to save")
            return
            
        try:
            wordcloud.to_file(filename)
            print(f"✅ Word cloud saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving word cloud: {e}")
    
    def generate_report(self, text, filename=None):
        """Generate comprehensive text analysis report"""
        if not TEXT_PROCESSING_AVAILABLE:
            # Basic report without advanced features
            report = {
                'text_length': len(text),
                'word_count': len(text.split()),
                'language': 'english',
                'sentiment': {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0},
                'top_keywords': []
            }
        else:
            report = {
                'text_length': len(text),
                'word_count': len(text.split()),
                'sentence_count': len(sent_tokenize(text)),
                'language': self.detect_language(text),
                'sentiment': self.analyze_sentiment(text),
                'top_keywords': self.extract_keywords(text, max_features=20)
            }
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report

class BatchWordCloudProcessor:
    """Batch processor for multiple text files and word cloud generation"""
    
    def __init__(self, output_dir="wordcloud_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.generator = AdvancedWordCloudGenerator()
        
        # Supported text file formats
        self.supported_formats = ['.txt', '.csv', '.json', '.xml', '.html', '.md']
        
        # Processing statistics
        self.stats = {
            'processed': 0,
            'errors': 0,
            'total_words': 0,
            'processing_time': 0
        }
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> List[Path]:
        """Scan directory for supported text files"""
        text_files = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                text_files.append(file_path)
        
        return sorted(text_files)
    
    def extract_text_from_file(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        try:
            if file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_path.suffix.lower() == '.csv':
                # Extract text from CSV file
                if WORDCLOUD_AVAILABLE:
                    try:
                        df = pd.read_csv(file_path)
                        # Combine all string columns
                        text_columns = df.select_dtypes(include=['object']).columns
                        combined_text = ' '.join(df[col].astype(str).str.cat(sep=' ') for col in text_columns)
                        return combined_text
                    except:
                        pass
                
                # Fallback to reading as text
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            
            elif file_path.suffix.lower() in ['.html', '.xml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple tag removal for basic text extraction
                    import re
                    text = re.sub(r'<[^>]+>', ' ', content)
                    return re.sub(r'\s+', ' ', text).strip()
            
            elif file_path.suffix.lower() == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple markdown cleanup
                    import re
                    # Remove headers
                    content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
                    # Remove code blocks
                    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
                    # Remove inline code
                    content = re.sub(r'`[^`]+`', '', content)
                    # Remove links
                    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
                    return content
            
            else:
                # Default to text reading
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return ""
    
    def process_single_file(self, file_path: Path) -> Dict:
        """Process a single text file"""
        try:
            start_time = time.time()
            
            # Extract text
            text = self.extract_text_from_file(file_path)
            if not text:
                return {
                    'success': False,
                    'source': str(file_path),
                    'error': 'No text extracted'
                }
            
            # Preprocess text
            processed_text = self.generator.preprocess_text(text)
            if not processed_text:
                return {
                    'success': False,
                    'source': str(file_path),
                    'error': 'No text after preprocessing'
                }
            
            # Generate word cloud
            output_name = file_path.stem
            wordcloud = self.generator.generate_wordcloud(processed_text)
            
            if not wordcloud:
                return {
                    'success': False,
                    'source': str(file_path),
                    'error': 'Failed to generate word cloud'
                }
            
            # Save word cloud
            output_path = self.output_dir / f"{output_name}_wordcloud.png"
            self.generator.save_wordcloud(wordcloud, output_path)
            
            # Generate analysis report
            report = self.generator.generate_report(processed_text)
            report_path = self.output_dir / f"{output_name}_analysis.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self.stats['processed'] += 1
            self.stats['total_words'] += report['word_count']
            self.stats['processing_time'] += processing_time
            
            return {
                'success': True,
                'source': str(file_path),
                'output_name': output_name,
                'wordcloud_path': str(output_path),
                'report_path': str(report_path),
                'processing_time': processing_time,
                'word_count': report['word_count'],
                'sentiment': report['sentiment']
            }
        
        except Exception as e:
            self.stats['errors'] += 1
            return {
                'success': False,
                'source': str(file_path),
                'error': str(e)
            }
    
    def batch_process_directory(self, input_dir: Path, recursive: bool = True, 
                              max_workers: int = 4) -> List[Dict]:
        """Batch process all text files in directory"""
        # Scan for text files
        text_files = self.scan_directory(input_dir, recursive)
        
        if not text_files:
            print(f"No supported text files found in {input_dir}")
            return []
        
        print(f"Found {len(text_files)} text files to process")
        
        # Reset statistics
        self.stats = {key: 0 for key in self.stats}
        
        results = []
        
        # Process with progress bar
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for file_path in text_files:
                future = executor.submit(self.process_single_file, file_path)
                futures.append(future)
            
            # Collect results with progress bar
            if WORDCLOUD_AVAILABLE:
                try:
                    for future in tqdm(futures, desc="Processing text files"):
                        result = future.result()
                        results.append(result)
                except ImportError:
                    # Fallback without progress bar
                    for future in futures:
                        result = future.result()
                        results.append(result)
            else:
                for future in futures:
                    result = future.result()
                    results.append(result)
        
        return results
    
    def generate_processing_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive processing report"""
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        # Analyze sentiment distribution
        sentiment_analysis = {'positive': 0, 'negative': 0, 'neutral': 0}
        for result in successful:
            sentiment = result.get('sentiment', {})
            compound = sentiment.get('compound', 0)
            if compound > 0.1:
                sentiment_analysis['positive'] += 1
            elif compound < -0.1:
                sentiment_analysis['negative'] += 1
            else:
                sentiment_analysis['neutral'] += 1
        
        report = {
            'summary': {
                'total_processed': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': len(successful) / len(results) * 100 if results else 0,
                'total_words': self.stats['total_words'],
                'average_words_per_file': self.stats['total_words'] / len(successful) if successful else 0,
                'total_processing_time': self.stats['processing_time'],
                'average_processing_time': self.stats['processing_time'] / len(successful) if successful else 0
            },
            'sentiment_analysis': sentiment_analysis,
            'successful_files': [r['source'] for r in successful],
            'failed_files': [(r['source'], r.get('error', 'Unknown error')) for r in failed],
            'statistics': self.stats
        }
        
        # Save report to file
        report_path = self.output_dir / "batch_processing_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report

def create_sample_texts(output_dir="sample_texts"):
    """Create sample text files for testing"""
    sample_dir = Path(output_dir)
    sample_dir.mkdir(exist_ok=True)
    
    samples = {
        'technology.txt': """
        Artificial intelligence and machine learning are transforming the technology landscape.
        Data science, deep learning, neural networks, and algorithms are becoming essential
        for businesses to innovate and compete. Cloud computing, automation, and digital
        transformation enable organizations to scale and adapt to changing market demands.
        Cybersecurity, blockchain, and quantum computing represent the future of secure
        and efficient technological solutions.
        """,
        
        'business.txt': """
        Strategic planning, market analysis, and competitive intelligence drive successful
        business operations. Customer satisfaction, brand loyalty, and revenue growth
        are key performance indicators. Leadership, teamwork, innovation, and agility
        enable organizations to achieve sustainable success. Digital marketing, sales
        optimization, and customer relationship management enhance business performance.
        """,
        
        'positive_reviews.txt': """
        Amazing product! Excellent quality, fantastic service, outstanding performance.
        Highly recommend, brilliant design, wonderful experience, perfect solution.
        Great value, superb features, incredible results, awesome functionality.
        Love it, best choice, remarkable improvement, delighted customer.
        """,
        
        'negative_reviews.txt': """
        Terrible experience, poor quality, awful service, disappointing results.
        Waste of money, horrible design, frustrating problems, unacceptable performance.
        Regret buying, worst purchase, annoying issues, complete failure.
        Avoid this, broken features, useless product, angry customer.
        """
    }
    
    created_files = []
    for filename, content in samples.items():
        file_path = sample_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        created_files.append(file_path)
    
    return created_files

if __name__ == "__main__":
    # Demo usage
    print("🚀 Word Cloud Processor Demo")
    print("=" * 30)
    
    if WORDCLOUD_AVAILABLE:
        # Create sample text files
        sample_files = create_sample_texts()
        print(f"✅ Created {len(sample_files)} sample text files")
        
        # Initialize batch processor
        processor = BatchWordCloudProcessor()
        
        # Process sample files
        results = processor.batch_process_directory(Path("sample_texts"))
        
        # Generate report
        report = processor.generate_processing_report(results)
        
        print(f"\n📊 Processing completed:")
        print(f"   • Processed: {report['summary']['successful']}/{report['summary']['total_processed']}")
        print(f"   • Success rate: {report['summary']['success_rate']:.1f}%")
        print(f"   • Total words: {report['summary']['total_words']:,}")
        print(f"   • Output directory: {processor.output_dir}")
        
        # Show sentiment analysis
        sentiment = report['sentiment_analysis']
        print(f"\n😊 Sentiment Analysis:")
        print(f"   • Positive: {sentiment['positive']} files")
        print(f"   • Negative: {sentiment['negative']} files")
        print(f"   • Neutral: {sentiment['neutral']} files")
    else:
        print("❌ Please install required packages: pip install wordcloud matplotlib pandas pillow")
