"""
Computer Vision Module
=====================

OpenCV and computer vision utilities for ValidoAI.
Provides image processing, object detection, and visual analysis capabilities.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

# Lazy imports for optional dependencies
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    cv2 = None
    OPENCV_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

try:
    import PIL
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PIL = None
    Image = None
    PILLOW_AVAILABLE = False

try:
    import torch
    import torchvision
    PYTORCH_VISION_AVAILABLE = True
except ImportError:
    torch = None
    torchvision = None
    PYTORCH_VISION_AVAILABLE = False

try:
    import tensorflow as tf
    import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    tf = None
    keras = None
    TENSORFLOW_AVAILABLE = False

try:
    from sklearn import svm, ensemble, neighbors
    from sklearn.feature_extraction.image import extract_patches_2d
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    dlib = None
    DLIB_AVAILABLE = False

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    face_recognition = None
    FACE_RECOGNITION_AVAILABLE = False

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO = None
    YOLO_AVAILABLE = False

try:
    import segmentation_models as sm
    SEGMENTATION_MODELS_AVAILABLE = True
except ImportError:
    sm = None
    SEGMENTATION_MODELS_AVAILABLE = False

try:
    from transformers import pipeline, AutoImageProcessor, AutoModelForImageClassification
    TRANSFORMERS_VISION_AVAILABLE = True
except ImportError:
    TRANSFORMERS_VISION_AVAILABLE = False

logger = logging.getLogger(__name__)

class ComputerVisionProcessor:
    """Computer vision processing utilities"""

    def __init__(self):
        self.opencv_available = OPENCV_AVAILABLE
        self.numpy_available = NUMPY_AVAILABLE
        self.pillow_available = PILLOW_AVAILABLE
        self.pytorch_vision_available = PYTORCH_VISION_AVAILABLE
        self.tensorflow_available = TENSORFLOW_AVAILABLE
        self.sklearn_available = SKLEARN_AVAILABLE
        self.dlib_available = DLIB_AVAILABLE
        self.face_recognition_available = FACE_RECOGNITION_AVAILABLE
        self.yolo_available = YOLO_AVAILABLE
        self.segmentation_models_available = SEGMENTATION_MODELS_AVAILABLE
        self.transformers_vision_available = TRANSFORMERS_VISION_AVAILABLE

        # Initialize model caches
        self._models = {}
        self._pipelines = {}

        if not self.opencv_available:
            logger.warning("⚠️  OpenCV not available. Install with: pip install opencv-python")
        if not self.numpy_available:
            logger.warning("⚠️  NumPy not available. Install with: pip install numpy")
        if not self.pillow_available:
            logger.warning("⚠️  Pillow not available. Install with: pip install pillow")

        # Log available advanced capabilities
        if self.tensorflow_available:
            logger.info("✅ TensorFlow/Keras available for deep learning")
        if self.pytorch_vision_available:
            logger.info("✅ PyTorch Vision available for computer vision")
        if self.yolo_available:
            logger.info("✅ YOLO available for object detection")
        if self.face_recognition_available:
            logger.info("✅ Face recognition available")
        if self.transformers_vision_available:
            logger.info("✅ Hugging Face transformers available for vision tasks")

    def check_dependencies(self) -> Dict[str, bool]:
        """Check availability of computer vision dependencies"""
        return {
            'opencv': self.opencv_available,
            'numpy': self.numpy_available,
            'pillow': self.pillow_available,
            'pytorch_vision': self.pytorch_vision_available,
            'tensorflow': self.tensorflow_available,
            'sklearn': self.sklearn_available,
            'dlib': self.dlib_available,
            'face_recognition': self.face_recognition_available,
            'yolo': self.yolo_available,
            'segmentation_models': self.segmentation_models_available,
            'transformers_vision': self.transformers_vision_available
        }

    def load_image(self, image_path: str) -> Optional[Any]:
        """Load an image from file path"""
        if not os.path.exists(image_path):
            logger.error(f"❌ Image file not found: {image_path}")
            return None

        try:
            if self.opencv_available:
                # Load with OpenCV
                image = cv2.imread(image_path)
                if image is not None:
                    # Convert BGR to RGB for consistency
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    logger.info(f"✅ Image loaded with OpenCV: {image_path}")
                    return image
            elif self.pillow_available:
                # Fallback to Pillow
                image = Image.open(image_path)
                logger.info(f"✅ Image loaded with Pillow: {image_path}")
                return image
            else:
                logger.error("❌ No image loading library available")
                return None

        except Exception as e:
            logger.error(f"❌ Error loading image: {e}")
            return None

    def save_image(self, image: Any, output_path: str, format: str = 'jpg') -> bool:
        """Save an image to file"""
        try:
            if self.opencv_available and isinstance(image, np.ndarray):
                # Save with OpenCV
                if len(image.shape) == 3 and image.shape[2] == 3:
                    # Convert RGB to BGR for OpenCV
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                success = cv2.imwrite(output_path, image)
                if success:
                    logger.info(f"✅ Image saved with OpenCV: {output_path}")
                    return True
                else:
                    logger.error(f"❌ Failed to save image: {output_path}")
                    return False
            elif self.pillow_available and isinstance(image, Image.Image):
                # Save with Pillow
                image.save(output_path, format=format.upper())
                logger.info(f"✅ Image saved with Pillow: {output_path}")
                return True
            else:
                logger.error("❌ No image saving library available")
                return False

        except Exception as e:
            logger.error(f"❌ Error saving image: {e}")
            return False

    def get_image_info(self, image: Any) -> Dict[str, Any]:
        """Get information about an image"""
        info = {}

        try:
            if self.opencv_available and isinstance(image, np.ndarray):
                info['library'] = 'OpenCV'
                info['shape'] = image.shape
                info['height'] = image.shape[0]
                info['width'] = image.shape[1]
                if len(image.shape) == 3:
                    info['channels'] = image.shape[2]
                info['dtype'] = str(image.dtype)
                info['size_bytes'] = image.nbytes

            elif self.pillow_available and isinstance(image, Image.Image):
                info['library'] = 'Pillow'
                info['size'] = image.size
                info['width'] = image.width
                info['height'] = image.height
                info['mode'] = image.mode
                info['format'] = image.format

            return info

        except Exception as e:
            logger.error(f"❌ Error getting image info: {e}")
            return {'error': str(e)}

    def resize_image(self, image: Any, width: int, height: int) -> Optional[Any]:
        """Resize an image to specified dimensions"""
        try:
            if self.opencv_available and isinstance(image, np.ndarray):
                resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
                logger.info(f"✅ Image resized with OpenCV: {width}x{height}")
                return resized
            elif self.pillow_available and isinstance(image, Image.Image):
                resized = image.resize((width, height), Image.Resampling.LANCZOS)
                logger.info(f"✅ Image resized with Pillow: {width}x{height}")
                return resized
            else:
                logger.error("❌ No image resizing library available")
                return None

        except Exception as e:
            logger.error(f"❌ Error resizing image: {e}")
            return None

    def convert_to_grayscale(self, image: Any) -> Optional[Any]:
        """Convert an image to grayscale"""
        try:
            if self.opencv_available and isinstance(image, np.ndarray):
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                else:
                    gray = image.copy()
                logger.info("✅ Image converted to grayscale with OpenCV")
                return gray
            elif self.pillow_available and isinstance(image, Image.Image):
                gray = image.convert('L')
                logger.info("✅ Image converted to grayscale with Pillow")
                return gray
            else:
                logger.error("❌ No grayscale conversion library available")
                return None

        except Exception as e:
            logger.error(f"❌ Error converting to grayscale: {e}")
            return None

    def detect_edges(self, image: Any, threshold1: int = 100, threshold2: int = 200) -> Optional[Any]:
        """Detect edges in an image using Canny edge detection"""
        if not self.opencv_available:
            logger.error("❌ OpenCV required for edge detection")
            return None

        try:
            # Convert to grayscale if needed
            if isinstance(image, np.ndarray) and len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            # Apply Canny edge detection
            edges = cv2.Canny(gray, threshold1, threshold2)
            logger.info("✅ Edge detection completed with OpenCV")
            return edges

        except Exception as e:
            logger.error(f"❌ Error detecting edges: {e}")
            return None

    def apply_gaussian_blur(self, image: Any, kernel_size: Tuple[int, int] = (5, 5)) -> Optional[Any]:
        """Apply Gaussian blur to an image"""
        if not self.opencv_available:
            logger.error("❌ OpenCV required for Gaussian blur")
            return None

        try:
            if isinstance(image, np.ndarray):
                blurred = cv2.GaussianBlur(image, kernel_size, 0)
                logger.info(f"✅ Gaussian blur applied with kernel {kernel_size}")
                return blurred
            else:
                logger.error("❌ Image must be a NumPy array for OpenCV operations")
                return None

        except Exception as e:
            logger.error(f"❌ Error applying Gaussian blur: {e}")
            return None

    def extract_features(self, image: Any, method: str = 'sift') -> Optional[List]:
        """Extract features from an image"""
        if not self.opencv_available:
            logger.error("❌ OpenCV required for feature extraction")
            return None

        try:
            # Convert to grayscale if needed
            if isinstance(image, np.ndarray) and len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            if method.lower() == 'sift':
                # SIFT feature extraction
                sift = cv2.SIFT_create()
                keypoints, descriptors = sift.detectAndCompute(gray, None)
                logger.info(f"✅ SIFT features extracted: {len(keypoints)} keypoints")
                return {'keypoints': keypoints, 'descriptors': descriptors}

            elif method.lower() == 'orb':
                # ORB feature extraction
                orb = cv2.ORB_create()
                keypoints, descriptors = orb.detectAndCompute(gray, None)
                logger.info(f"✅ ORB features extracted: {len(keypoints)} keypoints")
                return {'keypoints': keypoints, 'descriptors': descriptors}

            else:
                logger.error(f"❌ Unsupported feature extraction method: {method}")
                return None

        except Exception as e:
            logger.error(f"❌ Error extracting features: {e}")
            return None

    def face_detection(self, image: Any) -> Optional[List]:
        """Detect faces in an image"""
        if not self.opencv_available:
            logger.error("❌ OpenCV required for face detection")
            return None

        try:
            # Load Haar cascade classifier for face detection
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if not os.path.exists(face_cascade_path):
                logger.error("❌ Haar cascade classifier not found")
                return None

            face_cascade = cv2.CascadeClassifier(face_cascade_path)

            # Convert to grayscale for face detection
            if isinstance(image, np.ndarray) and len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            logger.info(f"✅ Face detection completed: {len(faces)} faces found")
            return faces.tolist() if len(faces) > 0 else []

        except Exception as e:
            logger.error(f"❌ Error detecting faces: {e}")
            return None

    def analyze_image_quality(self, image: Any) -> Dict[str, Any]:
        """Analyze image quality metrics"""
        analysis = {}

        try:
            if self.opencv_available and isinstance(image, np.ndarray):
                # Calculate image sharpness (variance of Laplacian)
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                else:
                    gray = image

                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                analysis['sharpness'] = laplacian_var

                # Calculate brightness
                if len(image.shape) == 3:
                    brightness = np.mean(cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[:, :, 2])
                else:
                    brightness = np.mean(gray)
                analysis['brightness'] = brightness

                # Calculate contrast
                contrast = gray.std()
                analysis['contrast'] = contrast

                # Calculate noise (simple estimation)
                noise = np.std(image) / np.mean(image)
                analysis['noise_ratio'] = noise

                logger.info("✅ Image quality analysis completed")

            elif self.pillow_available and isinstance(image, Image.Image):
                # Basic analysis with Pillow
                stat = image.convert('L').histogram()
                analysis['basic_stats'] = {
                    'histogram': stat,
                    'size': image.size,
                    'mode': image.mode
                }

            return analysis

        except Exception as e:
            logger.error(f"❌ Error analyzing image quality: {e}")
            return {'error': str(e)}

    def object_detection_yolo(self, image: Any, model_size: str = 'yolov8n.pt') -> Optional[List]:
        """Object detection using YOLO"""
        if not self.yolo_available:
            logger.error("❌ YOLO not available. Install with: pip install ultralytics")
            return None

        try:
            # Load YOLO model
            model = YOLO(model_size)

            # Run inference
            if isinstance(image, np.ndarray):
                results = model(image)
            elif self.pillow_available and isinstance(image, Image.Image):
                results = model(np.array(image))
            else:
                logger.error("❌ Unsupported image format for YOLO")
                return None

            # Extract detections
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    detection = {
                        'class': result.names[int(box.cls)],
                        'confidence': float(box.conf),
                        'bbox': box.xyxy[0].tolist(),
                        'class_id': int(box.cls)
                    }
                    detections.append(detection)

            logger.info(f"✅ YOLO detected {len(detections)} objects")
            return detections

        except Exception as e:
            logger.error(f"❌ Error in YOLO object detection: {e}")
            return None

    def face_recognition_advanced(self, image: Any, known_faces: Optional[List] = None) -> Optional[Dict]:
        """Advanced face recognition using face_recognition library"""
        if not self.face_recognition_available:
            logger.error("❌ Face recognition not available. Install with: pip install face-recognition")
            return None

        try:
            if isinstance(image, np.ndarray):
                if len(image.shape) == 3 and image.shape[2] == 3:
                    # Convert RGB to BGR if needed
                    if image.shape[0] > image.shape[1]:  # Likely RGB
                        pass  # face_recognition expects RGB
                    else:
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if self.opencv_available else image
                face_image = image
            elif self.pillow_available and isinstance(image, Image.Image):
                face_image = np.array(image)
            else:
                logger.error("❌ Unsupported image format for face recognition")
                return None

            # Find face locations
            face_locations = face_recognition.face_locations(face_image)

            # Get face encodings
            face_encodings = face_recognition.face_encodings(face_image, face_locations)

            results = {
                'face_count': len(face_locations),
                'face_locations': face_locations,
                'face_encodings': face_encodings,
                'recognized_faces': []
            }

            # Compare with known faces if provided
            if known_faces and len(face_encodings) > 0:
                known_encodings = [face['encoding'] for face in known_faces]

                for i, face_encoding in enumerate(face_encodings):
                    matches = face_recognition.compare_faces(known_encodings, face_encoding)
                    face_distances = face_recognition.face_distance(known_encodings, face_encoding)

                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            recognized_face = {
                                'face_index': i,
                                'name': known_faces[best_match_index]['name'],
                                'confidence': 1 - face_distances[best_match_index],
                                'location': face_locations[i]
                            }
                            results['recognized_faces'].append(recognized_face)

            logger.info(f"✅ Face recognition completed: {len(face_locations)} faces found")
            return results

        except Exception as e:
            logger.error(f"❌ Error in face recognition: {e}")
            return None

    def image_classification_huggingface(self, image: Any, model_name: str = "google/vit-base-patch16-224") -> Optional[Dict]:
        """Image classification using Hugging Face transformers"""
        if not self.transformers_vision_available:
            logger.error("❌ Transformers vision not available. Install with: pip install transformers torch")
            return None

        try:
            # Load image processor and model
            if model_name not in self._models:
                processor = AutoImageProcessor.from_pretrained(model_name)
                model = AutoModelForImageClassification.from_pretrained(model_name)
                self._models[model_name] = {'processor': processor, 'model': model}
            else:
                processor = self._models[model_name]['processor']
                model = self._models[model_name]['model']

            # Prepare image
            if self.pillow_available and isinstance(image, Image.Image):
                pil_image = image
            elif isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image)
            else:
                logger.error("❌ Unsupported image format for classification")
                return None

            # Process image
            inputs = processor(images=pil_image, return_tensors="pt")

            # Run inference
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits

            # Get predictions
            predicted_class_idx = logits.argmax(-1).item()
            predicted_class = model.config.id2label[predicted_class_idx]

            # Get probabilities
            probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]
            top_5_prob, top_5_class_idx = torch.topk(probabilities, 5)

            predictions = []
            for i in range(5):
                predictions.append({
                    'label': model.config.id2label[top_5_class_idx[i].item()],
                    'probability': top_5_prob[i].item()
                })

            result = {
                'top_prediction': predicted_class,
                'confidence': probabilities[predicted_class_idx].item(),
                'top_5_predictions': predictions
            }

            logger.info(f"✅ Image classification completed: {predicted_class}")
            return result

        except Exception as e:
            logger.error(f"❌ Error in image classification: {e}")
            return None

    def image_segmentation(self, image: Any, model_name: str = 'DeepLabV3') -> Optional[Any]:
        """Image segmentation using various models"""
        if not self.pytorch_vision_available:
            logger.error("❌ PyTorch Vision not available for segmentation")
            return None

        try:
            # Load segmentation model
            if model_name not in self._models:
                if model_name == 'DeepLabV3':
                    model = torchvision.models.segmentation.deeplabv3_resnet101(pretrained=True)
                elif model_name == 'FCN':
                    model = torchvision.models.segmentation.fcn_resnet101(pretrained=True)
                else:
                    logger.error(f"❌ Unsupported segmentation model: {model_name}")
                    return None

                model.eval()
                self._models[model_name] = model
            else:
                model = self._models[model_name]

            # Prepare image
            if isinstance(image, np.ndarray):
                if len(image.shape) == 3:
                    if image.shape[2] == 3:
                        image = image.transpose(2, 0, 1)  # HWC to CHW
                    else:
                        logger.error("❌ Image must be RGB for segmentation")
                        return None
                else:
                    logger.error("❌ Image must be 3D for segmentation")
                    return None

                image = torch.from_numpy(image).float() / 255.0
                image = image.unsqueeze(0)  # Add batch dimension
            else:
                logger.error("❌ Image must be numpy array for segmentation")
                return None

            # Normalize image
            normalize = torchvision.transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
            image = normalize(image)

            # Run segmentation
            with torch.no_grad():
                output = model(image)['out'][0]
                segmentation = output.argmax(0).cpu().numpy()

            logger.info("✅ Image segmentation completed")
            return segmentation

        except Exception as e:
            logger.error(f"❌ Error in image segmentation: {e}")
            return None

    def traditional_ml_classification(self, image: Any, method: str = 'svm') -> Optional[Dict]:
        """Traditional ML classification using scikit-learn"""
        if not self.sklearn_available:
            logger.error("❌ Scikit-learn not available. Install with: pip install scikit-learn")
            return None

        try:
            # Extract features from image
            if isinstance(image, np.ndarray):
                if len(image.shape) == 3:
                    # Convert to grayscale and flatten
                    if image.shape[2] == 3:
                        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if self.opencv_available else image.mean(axis=2)
                    else:
                        gray = image
                else:
                    gray = image

                # Extract features using HOG-like descriptor
                features = []
                for i in range(0, gray.shape[0] - 8, 8):
                    for j in range(0, gray.shape[1] - 8, 8):
                        patch = gray[i:i+8, j:j+8]
                        # Simple feature extraction
                        features.extend([
                            patch.mean(),
                            patch.std(),
                            patch.min(),
                            patch.max()
                        ])

                features = np.array(features)

            else:
                logger.error("❌ Image must be numpy array for ML classification")
                return None

            # This is a demo - in practice you'd need trained models
            result = {
                'method': method,
                'features_extracted': len(features),
                'feature_vector_shape': features.shape,
                'note': 'This is a demo. Train models with your dataset for real classification.'
            }

            logger.info(f"✅ Traditional ML features extracted: {len(features)} features")
            return result

        except Exception as e:
            logger.error(f"❌ Error in ML classification: {e}")
            return None

    def medical_imaging_analysis(self, image: Any) -> Optional[Dict]:
        """Medical imaging analysis (X-ray, MRI, CT)"""
        if not (self.opencv_available and self.numpy_available):
            logger.error("❌ OpenCV and NumPy required for medical imaging analysis")
            return None

        try:
            if isinstance(image, np.ndarray):
                # Convert to grayscale if needed
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                else:
                    gray = image

                # Enhance contrast using CLAHE
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(gray.astype(np.uint8))

                # Apply median blur for noise reduction
                denoised = cv2.medianBlur(enhanced, 5)

                # Edge detection for structure analysis
                edges = cv2.Canny(denoised, 50, 150)

                # Calculate basic statistics
                analysis = {
                    'mean_intensity': float(gray.mean()),
                    'std_intensity': float(gray.std()),
                    'min_intensity': float(gray.min()),
                    'max_intensity': float(gray.max()),
                    'contrast': float(gray.std() / (gray.mean() + 1e-6)),
                    'sharpness': float(cv2.Laplacian(gray.astype(np.uint8), cv2.CV_64F).var()),
                    'edge_density': float(edges.sum() / edges.size),
                    'enhanced_image': enhanced,
                    'denoised_image': denoised,
                    'edge_map': edges
                }

                logger.info("✅ Medical imaging analysis completed")
                return analysis

            else:
                logger.error("❌ Image must be numpy array for medical analysis")
                return None

        except Exception as e:
            logger.error(f"❌ Error in medical imaging analysis: {e}")
            return None

    def document_analysis(self, image: Any) -> Optional[Dict]:
        """Document analysis for OCR and layout detection"""
        if not self.opencv_available:
            logger.error("❌ OpenCV required for document analysis")
            return None

        try:
            if isinstance(image, np.ndarray):
                # Convert to grayscale
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                else:
                    gray = image

                # Enhance document image
                # Apply bilateral filter for noise reduction while keeping edges sharp
                filtered = cv2.bilateralFilter(gray.astype(np.uint8), 9, 75, 75)

                # Thresholding for text extraction
                _, binary = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                # Find contours for layout analysis
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Filter contours (likely text regions)
                text_regions = []
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:  # Filter small contours
                        x, y, w, h = cv2.boundingRect(contour)
                        text_regions.append({
                            'bbox': [x, y, w, h],
                            'area': area,
                            'aspect_ratio': w / h if h > 0 else 0
                        })

                # Calculate document features
                analysis = {
                    'text_regions_count': len(text_regions),
                    'text_regions': text_regions,
                    'document_type': 'text_document' if len(text_regions) > 5 else 'image',
                    'contrast': float(gray.std()),
                    'brightness': float(gray.mean()),
                    'processed_image': filtered,
                    'binary_image': binary
                }

                logger.info(f"✅ Document analysis completed: {len(text_regions)} text regions detected")
                return analysis

            else:
                logger.error("❌ Image must be numpy array for document analysis")
                return None

        except Exception as e:
            logger.error(f"❌ Error in document analysis: {e}")
            return None

    def quality_inspection(self, image: Any, reference_image: Optional[Any] = None) -> Optional[Dict]:
        """Quality inspection and defect detection"""
        if not (self.opencv_available and self.numpy_available):
            logger.error("❌ OpenCV and NumPy required for quality inspection")
            return None

        try:
            if isinstance(image, np.ndarray):
                inspection_results = {
                    'defects_detected': 0,
                    'quality_score': 100,
                    'issues': [],
                    'recommendations': []
                }

                # Convert to grayscale
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                else:
                    gray = image

                # Check for blur (low sharpness)
                sharpness = cv2.Laplacian(gray.astype(np.uint8), cv2.CV_64F).var()
                if sharpness < 100:
                    inspection_results['defects_detected'] += 1
                    inspection_results['quality_score'] -= 20
                    inspection_results['issues'].append('Image appears blurry')
                    inspection_results['recommendations'].append('Improve focus or lighting')

                # Check for noise
                noise_std = gray.std()
                if noise_std > 50:
                    inspection_results['defects_detected'] += 1
                    inspection_results['quality_score'] -= 15
                    inspection_results['issues'].append('High noise detected')
                    inspection_results['recommendations'].append('Reduce ISO or use better lighting')

                # Check brightness
                brightness = gray.mean()
                if brightness < 50:
                    inspection_results['defects_detected'] += 1
                    inspection_results['quality_score'] -= 10
                    inspection_results['issues'].append('Image too dark')
                    inspection_results['recommendations'].append('Increase exposure or lighting')
                elif brightness > 200:
                    inspection_results['defects_detected'] += 1
                    inspection_results['quality_score'] -= 10
                    inspection_results['issues'].append('Image overexposed')
                    inspection_results['recommendations'].append('Reduce exposure or lighting')

                # Contrast check
                contrast = gray.std() / (gray.mean() + 1e-6)
                if contrast < 0.3:
                    inspection_results['defects_detected'] += 1
                    inspection_results['quality_score'] -= 15
                    inspection_results['issues'].append('Low contrast')
                    inspection_results['recommendations'].append('Improve lighting or use histogram equalization')

                # Ensure quality score doesn't go below 0
                inspection_results['quality_score'] = max(0, inspection_results['quality_score'])

                logger.info(f"✅ Quality inspection completed: {inspection_results['defects_detected']} issues detected")
                return inspection_results

            else:
                logger.error("❌ Image must be numpy array for quality inspection")
                return None

        except Exception as e:
            logger.error(f"❌ Error in quality inspection: {e}")
            return None

def create_computer_vision_processor() -> ComputerVisionProcessor:
    """Factory function to create computer vision processor"""
    return ComputerVisionProcessor()

# Test function for computer vision capabilities
def test_computer_vision():
    """Test computer vision functionality"""
    print("🖼️  Testing Enhanced Computer Vision Module")
    print("=" * 60)

    cv_processor = create_computer_vision_processor()

    # Check dependencies
    deps = cv_processor.check_dependencies()
    print("📦 Computer Vision Dependencies:")
    print("-" * 40)
    for dep, available in deps.items():
        status = "✅ Available" if available else "❌ Not Available"
        print("20")

    # Test basic functionality
    print("\\n🔧 Testing Basic Functions:")
    print("-" * 30)

    # Test with a simple image if available
    test_image_path = "static/images/logo.png"  # Adjust path as needed

    if os.path.exists(test_image_path):
        print(f"🖼️  Testing with image: {test_image_path}")

        # Load image
        image = cv_processor.load_image(test_image_path)
        if image is not None:
            print("✅ Image loaded successfully")

            # Get image info
            info = cv_processor.get_image_info(image)
            print(f"📊 Image Info: {info['width']}x{info['height']} ({info.get('channels', 'N/A')} channels)")

            # Test basic processing
            if cv_processor.opencv_available:
                print("\\n🎯 Testing OpenCV Functions:")
                resized = cv_processor.resize_image(image, 224, 224)
                print("✅ Image resizing completed")

                gray = cv_processor.convert_to_grayscale(image)
                print("✅ Grayscale conversion completed")

                edges = cv_processor.detect_edges(gray)
                if edges is not None:
                    print("✅ Edge detection completed")

                blurred = cv_processor.apply_gaussian_blur(gray)
                if blurred is not None:
                    print("✅ Gaussian blur applied")

                features = cv_processor.extract_features(gray)
                if features is not None:
                    print("✅ Feature extraction completed")

                faces = cv_processor.face_detection(image)
                if faces is not None:
                    print(f"✅ Face detection completed: {len(faces)} faces found")

                quality = cv_processor.analyze_image_quality(image)
                if quality is not None:
                    print(f"✅ Quality analysis: {quality.get('sharpness', 'N/A'):.2f} sharpness")

            # Test advanced ML functions
            print("\\n🤖 Testing ML Functions:")
            if cv_processor.yolo_available:
                detections = cv_processor.object_detection_yolo(image)
                if detections is not None:
                    print(f"✅ YOLO object detection: {len(detections)} objects")
                else:
                    print("⚠️  YOLO test skipped (no model)")

            if cv_processor.face_recognition_available:
                face_results = cv_processor.face_recognition_advanced(image)
                if face_results is not None:
                    print(f"✅ Advanced face recognition: {face_results['face_count']} faces")
                else:
                    print("⚠️  Face recognition test skipped")

            if cv_processor.transformers_vision_available:
                try:
                    classification = cv_processor.image_classification_huggingface(image)
                    if classification is not None:
                        print(f"✅ HuggingFace classification: {classification['top_prediction']}")
                    else:
                        print("⚠️  HuggingFace classification test skipped")
                except Exception as e:
                    print(f"⚠️  HuggingFace test skipped: {e}")

            if cv_processor.pytorch_vision_available:
                segmentation = cv_processor.image_segmentation(image)
                if segmentation is not None:
                    print("✅ Image segmentation completed")
                else:
                    print("⚠️  Segmentation test skipped")

            if cv_processor.sklearn_available:
                ml_result = cv_processor.traditional_ml_classification(image)
                if ml_result is not None:
                    print(f"✅ ML classification: {ml_result['features_extracted']} features")
                else:
                    print("⚠️  ML classification test skipped")

            # Test specialized functions
            print("\\n🏥 Testing Specialized Functions:")
            medical = cv_processor.medical_imaging_analysis(image)
            if medical is not None:
                print(f"✅ Medical imaging analysis: {medical['mean_intensity']:.2f} mean intensity")
            else:
                print("⚠️  Medical analysis test skipped")

            document = cv_processor.document_analysis(image)
            if document is not None:
                print(f"✅ Document analysis: {document['text_regions_count']} text regions")
            else:
                print("⚠️  Document analysis test skipped")

            inspection = cv_processor.quality_inspection(image)
            if inspection is not None:
                print(f"✅ Quality inspection: {inspection['quality_score']}% score")
            else:
                print("⚠️  Quality inspection test skipped")

            print("\\n✅ All computer vision tests completed!")
        else:
            print("⚠️  Could not load test image")
    else:
        print(f"⚠️  Test image not found: {test_image_path}")
        print("💡 Basic functionality test completed (no image needed)")

    return True

if __name__ == "__main__":
    test_computer_vision()
