#!/usr/bin/env python3
"""
Pipeline Pattern Implementation
Chains processing steps (e.g., preprocessing, inference, post-processing) into a pipeline
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
import logging
import time

logger = logging.getLogger(__name__)

class PipelineStep(ABC):
    """Abstract base class for pipeline steps"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
    
    @abstractmethod
    def process(self, data: Any, **kwargs) -> Any:
        """Process data in this step"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get step information"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "config": self.config
        }

class TokenizationStep(PipelineStep):
    """Tokenization step for text preprocessing"""
    
    def process(self, data: str, **kwargs) -> List[str]:
        """Tokenize input text"""
        if not self.enabled:
            return data
        
        logger.info(f"Tokenizing text: {len(data)} characters")
        
        # Simple tokenization (replace with actual tokenizer)
        tokens = data.split()
        logger.info(f"Tokenization completed: {len(tokens)} tokens")
        
        return tokens

class PreprocessingStep(PipelineStep):
    """Text preprocessing step"""
    
    def process(self, data: List[str], **kwargs) -> List[str]:
        """Preprocess tokens"""
        if not self.enabled:
            return data
        
        logger.info(f"Preprocessing {len(data)} tokens")
        
        # Simple preprocessing (lowercase, remove punctuation)
        processed = []
        for token in data:
            # Remove punctuation and lowercase
            cleaned = ''.join(c for c in token.lower() if c.isalnum())
            if cleaned:
                processed.append(cleaned)
        
        logger.info(f"Preprocessing completed: {len(processed)} tokens")
        return processed

class InferenceStep(PipelineStep):
    """Model inference step"""
    
    def __init__(self, name: str, model: Any, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.model = model
    
    def process(self, data: List[str], **kwargs) -> str:
        """Run model inference"""
        if not self.enabled:
            return "Inference disabled"
        
        logger.info(f"Running inference on {len(data)} tokens")
        
        # Convert tokens back to text for inference
        text = " ".join(data)
        
        # Simulate model inference
        start_time = time.time()
        response = f"[{self.name}] Inference result: {text[:50]}..."
        inference_time = time.time() - start_time
        
        logger.info(f"Inference completed in {inference_time:.2f}s")
        return response

class PostprocessingStep(PipelineStep):
    """Response postprocessing step"""
    
    def process(self, data: str, **kwargs) -> str:
        """Postprocess model response"""
        if not self.enabled:
            return data
        
        logger.info("Postprocessing response")
        
        # Simple postprocessing (formatting, cleaning)
        processed = data.strip()
        if not processed.endswith('.'):
            processed += '.'
        
        logger.info("Postprocessing completed")
        return processed

class ValidationStep(PipelineStep):
    """Input validation step"""
    
    def process(self, data: str, **kwargs) -> str:
        """Validate input data"""
        if not self.enabled:
            return data
        
        logger.info("Validating input")
        
        # Simple validation
        if not data or len(data.strip()) == 0:
            raise ValueError("Input cannot be empty")
        
        if len(data) > 1000:
            logger.warning("Input is very long, may affect performance")
        
        logger.info("Validation completed")
        return data

class Pipeline:
    """Main pipeline class that chains steps together"""
    
    def __init__(self, name: str):
        self.name = name
        self.steps: List[PipelineStep] = []
        self.metrics: Dict[str, Any] = {}
    
    def add_step(self, step: PipelineStep) -> 'Pipeline':
        """Add a step to the pipeline"""
        self.steps.append(step)
        logger.info(f"Added step '{step.name}' to pipeline '{self.name}'")
        return self
    
    def remove_step(self, step_name: str) -> 'Pipeline':
        """Remove a step from the pipeline"""
        self.steps = [step for step in self.steps if step.name != step_name]
        logger.info(f"Removed step '{step_name}' from pipeline '{self.name}'")
        return self
    
    def execute(self, data: Any, **kwargs) -> Any:
        """Execute the entire pipeline"""
        logger.info(f"Executing pipeline '{self.name}' with {len(self.steps)} steps")
        
        start_time = time.time()
        current_data = data
        
        try:
            for i, step in enumerate(self.steps):
                step_start = time.time()
                
                logger.info(f"Executing step {i+1}/{len(self.steps)}: {step.name}")
                current_data = step.process(current_data, **kwargs)
                
                step_time = time.time() - step_start
                self.metrics[f"{step.name}_time"] = step_time
                
                logger.info(f"Step '{step.name}' completed in {step_time:.2f}s")
            
            total_time = time.time() - start_time
            self.metrics["total_time"] = total_time
            self.metrics["success"] = True
            
            logger.info(f"Pipeline '{self.name}' completed successfully in {total_time:.2f}s")
            return current_data
            
        except Exception as e:
            total_time = time.time() - start_time
            self.metrics["total_time"] = total_time
            self.metrics["success"] = False
            self.metrics["error"] = str(e)
            
            logger.error(f"Pipeline '{self.name}' failed after {total_time:.2f}s: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline execution metrics"""
        return self.metrics.copy()
    
    def get_info(self) -> Dict[str, Any]:
        """Get pipeline information"""
        return {
            "name": self.name,
            "steps": [step.get_info() for step in self.steps],
            "metrics": self.metrics
        }

class PipelineBuilder:
    """Builder pattern for creating pipelines"""
    
    def __init__(self, name: str):
        self.pipeline = Pipeline(name)
    
    def add_validation(self, config: Dict[str, Any] = None) -> 'PipelineBuilder':
        """Add validation step"""
        step = ValidationStep("validation", config)
        self.pipeline.add_step(step)
        return self
    
    def add_tokenization(self, config: Dict[str, Any] = None) -> 'PipelineBuilder':
        """Add tokenization step"""
        step = TokenizationStep("tokenization", config)
        self.pipeline.add_step(step)
        return self
    
    def add_preprocessing(self, config: Dict[str, Any] = None) -> 'PipelineBuilder':
        """Add preprocessing step"""
        step = PreprocessingStep("preprocessing", config)
        self.pipeline.add_step(step)
        return self
    
    def add_inference(self, model: Any, config: Dict[str, Any] = None) -> 'PipelineBuilder':
        """Add inference step"""
        step = InferenceStep("inference", model, config)
        self.pipeline.add_step(step)
        return self
    
    def add_postprocessing(self, config: Dict[str, Any] = None) -> 'PipelineBuilder':
        """Add postprocessing step"""
        step = PostprocessingStep("postprocessing", config)
        self.pipeline.add_step(step)
        return self
    
    def build(self) -> Pipeline:
        """Build and return the pipeline"""
        return self.pipeline

class PipelineManager:
    """Manager for multiple pipelines"""
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
    
    def create_pipeline(self, name: str) -> PipelineBuilder:
        """Create a new pipeline builder"""
        return PipelineBuilder(name)
    
    def add_pipeline(self, pipeline: Pipeline):
        """Add a pipeline to the manager"""
        self.pipelines[pipeline.name] = pipeline
        logger.info(f"Added pipeline '{pipeline.name}' to manager")
    
    def get_pipeline(self, name: str) -> Optional[Pipeline]:
        """Get a pipeline by name"""
        return self.pipelines.get(name)
    
    def execute_pipeline(self, name: str, data: Any, **kwargs) -> Any:
        """Execute a specific pipeline"""
        pipeline = self.get_pipeline(name)
        if not pipeline:
            raise ValueError(f"Pipeline '{name}' not found")
        
        return pipeline.execute(data, **kwargs)
    
    def list_pipelines(self) -> Dict[str, Dict[str, Any]]:
        """List all pipelines"""
        return {
            name: pipeline.get_info()
            for name, pipeline in self.pipelines.items()
        }
