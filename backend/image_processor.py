import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageStat
import imagehash
from typing import List, Tuple, Dict
import os


class ImageProcessor:
    """AI-powered image quality assessment and processing"""
    
    def __init__(self, quality_threshold: float = 0.6, blur_threshold: float = 100, 
                 duplicate_threshold: int = 5):
        self.quality_threshold = quality_threshold
        self.blur_threshold = blur_threshold
        self.duplicate_threshold = duplicate_threshold
        self.image_hashes = {}
    
    def assess_quality(self, image_path: str) -> Dict[str, float]:
        """
        Assess image quality based on multiple metrics
        Returns dict with quality scores
        """
        # Load image with OpenCV
        img_cv = cv2.imread(image_path)
        if img_cv is None:
            return {"error": "Could not load image"}
        
        # Load with PIL for additional analysis
        img_pil = Image.open(image_path)
        
        # Calculate metrics
        sharpness = self._calculate_sharpness(img_cv)
        brightness = self._calculate_brightness(img_pil)
        contrast = self._calculate_contrast(img_pil)
        
        # Normalize scores to 0-1 range
        sharpness_score = min(sharpness / 500, 1.0)  # Normalize to 0-1
        brightness_score = self._normalize_brightness(brightness)
        contrast_score = min(contrast / 80, 1.0)
        
        # Calculate overall quality score (weighted average)
        quality_score = (
            sharpness_score * 0.4 +
            brightness_score * 0.3 +
            contrast_score * 0.3
        )
        
        # Convert numpy booleans to Python booleans for JSON serialization
        return {
            "quality_score": round(float(quality_score), 3),
            "sharpness_score": round(float(sharpness_score), 3),
            "brightness_score": round(float(brightness_score), 3),
            "contrast_score": round(float(contrast_score), 3),
            "is_blur": bool(sharpness < self.blur_threshold),
            "is_high_quality": bool(quality_score >= self.quality_threshold)
        }
    
    def _calculate_sharpness(self, img_cv: np.ndarray) -> float:
        """
        Calculate image sharpness using Laplacian variance
        Higher values indicate sharper images
        """
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var
    
    def _calculate_brightness(self, img_pil: Image.Image) -> float:
        """
        Calculate average brightness (luminance)
        Returns value between 0-255
        """
        greyscale = img_pil.convert('L')
        stat = ImageStat.Stat(greyscale)
        return stat.mean[0]
    
    def _normalize_brightness(self, brightness: float) -> float:
        """
        Normalize brightness to 0-1 score
        Optimal brightness is around 128 (middle gray)
        """
        # Penalize images that are too dark or too bright
        optimal = 128
        deviation = abs(brightness - optimal)
        score = 1.0 - (deviation / optimal)
        return max(0.0, score)
    
    def _calculate_contrast(self, img_pil: Image.Image) -> float:
        """
        Calculate image contrast using standard deviation
        Higher values indicate more contrast
        """
        greyscale = img_pil.convert('L')
        stat = ImageStat.Stat(greyscale)
        return stat.stddev[0]
    
    def detect_duplicates(self, image_paths: List[str]) -> List[Tuple[str, str]]:
        """
        Detect duplicate images using perceptual hashing
        Returns list of (original, duplicate) tuples
        """
        duplicates = []
        hashes = {}
        
        for img_path in image_paths:
            try:
                img = Image.open(img_path)
                img_hash = imagehash.average_hash(img)
                
                # Check for similar hashes
                for existing_path, existing_hash in hashes.items():
                    if img_hash - existing_hash <= self.duplicate_threshold:
                        duplicates.append((existing_path, img_path))
                        break
                else:
                    hashes[img_path] = img_hash
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
        
        return duplicates
    
    def enhance_image(self, image_path: str, output_path: str = None) -> str:
        """
        Apply basic enhancements to image
        Returns path to enhanced image
        """
        if output_path is None:
            base, ext = os.path.splitext(image_path)
            output_path = f"{base}_enhanced{ext}"
        
        img = Image.open(image_path)
        
        # Auto-adjust brightness if too dark or too bright
        brightness = self._calculate_brightness(img)
        if brightness < 100:  # Too dark
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.2)
        elif brightness > 180:  # Too bright
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.9)
        
        # Slightly boost contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        # Boost color saturation slightly
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.05)
        
        # Sharpen
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)
        
        img.save(output_path, quality=95)
        return output_path
    
    def detect_faces(self, image_path: str) -> int:
        """
        Detect number of faces in image
        Returns count of faces detected
        """
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Load face cascade classifier
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(face_cascade_path)
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            return len(faces)
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return 0
    
    def select_best_images(self, image_scores: List[Dict], max_count: int = 10) -> List[Dict]:
        """
        Select the best images based on quality scores
        Prioritizes high-quality, non-blurry, non-duplicate images
        """
        # Filter out blurry and duplicate images
        valid_images = [
            img for img in image_scores 
            if not img.get('is_blur', False) and not img.get('is_duplicate', False)
        ]
        
        # Sort by quality score (descending)
        sorted_images = sorted(
            valid_images, 
            key=lambda x: x.get('quality_score', 0), 
            reverse=True
        )
        
        # Return top N images
        return sorted_images[:max_count]
    
    def batch_process(self, image_paths: List[str]) -> Dict[str, any]:
        """
        Process multiple images in batch
        Returns comprehensive analysis
        """
        results = []
        
        # Assess quality for all images
        for img_path in image_paths:
            quality_metrics = self.assess_quality(img_path)
            quality_metrics['path'] = img_path
            quality_metrics['filename'] = os.path.basename(img_path)
            results.append(quality_metrics)
        
        # Detect duplicates
        duplicates = self.detect_duplicates(image_paths)
        duplicate_paths = set([dup[1] for dup in duplicates])
        
        # Mark duplicates in results
        for result in results:
            result['is_duplicate'] = result['path'] in duplicate_paths
        
        # Select best images
        best_images = self.select_best_images(results)
        
        return {
            'total_images': len(image_paths),
            'all_results': results,
            'duplicates': duplicates,
            'selected_images': best_images,
            'summary': {
                'total': len(image_paths),
                'high_quality': len([r for r in results if r.get('is_high_quality', False)]),
                'blurry': len([r for r in results if r.get('is_blur', False)]),
                'duplicates': len(duplicates),
                'selected': len(best_images)
            }
        }
