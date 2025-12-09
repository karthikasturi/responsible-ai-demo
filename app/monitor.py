"""
TruLens monitoring and evaluation integration.
This module wraps LLM calls with comprehensive evaluation metrics.
"""
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# TruLens imports - Using deprecated but working trulens_eval for 2.5.1
TRULENS_AVAILABLE = False
Tru = None
Feedback = None
OpenAIProvider = None

try:
    from trulens_eval import Tru, Feedback
    from trulens.providers.openai import OpenAI as OpenAIProvider
    TRULENS_AVAILABLE = True
    logger.info("TruLens (trulens_eval) loaded successfully")
except ImportError as e:
    logger.warning(f"TruLens not available. Evaluations will be disabled. Error: {e}")

import numpy as np

# Initialize TruLens
tru = None
openai_provider = None

logger.info(f"TRULENS_AVAILABLE={TRULENS_AVAILABLE}, Tru={Tru}, OpenAIProvider={OpenAIProvider}")
logger.info(f"OPENAI_API_KEY set: {bool(os.getenv('OPENAI_API_KEY'))}")

if TRULENS_AVAILABLE and Tru is not None:
    try:
        tru = Tru(database_url=os.getenv("TRULENS_DATABASE_URL", "sqlite:///./trulens.db"))
        logger.info("TruLens initialized successfully")
        
        # Initialize feedback provider
        if os.getenv("OPENAI_API_KEY") and OpenAIProvider is not None:
            try:
                logger.info("Attempting to initialize OpenAI provider...")
                openai_provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
                logger.info(f"TruLens OpenAI provider initialized: {type(openai_provider)}")
            except Exception as e:
                logger.error(f"Could not initialize OpenAI provider for TruLens: {e}", exc_info=True)
        else:
            logger.warning(f"Cannot initialize OpenAI provider: API_KEY={bool(os.getenv('OPENAI_API_KEY'))}, Provider={OpenAIProvider}")
    except Exception as e:
        logger.error(f"Could not initialize TruLens: {e}", exc_info=True)
        TRULENS_AVAILABLE = False
else:
    logger.warning(f"TruLens module not available. TRULENS_AVAILABLE={TRULENS_AVAILABLE}, Tru={Tru}")


class TruLensMonitor:
    """
    Manages TruLens monitoring and evaluation for the chatbot.
    """
    
    def __init__(self):
        """Initialize TruLens monitor with feedback functions."""
        self.tru = tru
        self.provider = openai_provider
        self.feedback_functions = []
        self.evaluation_results = []
        
        # Initialize feedback functions
        self._setup_feedback_functions()
    
    def _setup_feedback_functions(self):
        """Set up TruLens feedback functions for evaluation."""
        if not TRULENS_AVAILABLE:
            logger.warning("TruLens not available. Evaluations disabled.")
            return
        
        if not self.provider:
            logger.warning("OpenAI provider not available. TruLens evaluations disabled.")
            return
        
        try:
            # Store feedback function references with their names
            # For trulens-eval 2.5.1, we'll call these directly during evaluation
            self.feedback_functions = [
                ("relevance", "Relevance"),
                ("coherence", "Coherence"),
                ("sentiment", "Sentiment"),
                ("conciseness", "Conciseness")
            ]
            
            logger.info(f"Initialized {len(self.feedback_functions)} feedback functions")
            
        except Exception as e:
            logger.error(f"Error setting up feedback functions: {e}")
            self.feedback_functions = []
    
    def evaluate_response(
        self,
        input_text: str,
        output_text: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Evaluate a chatbot response using TruLens feedback functions.
        
        Args:
            input_text: User's input message
            output_text: Chatbot's response
            context: Optional context dictionary
            
        Returns:
            Dictionary containing evaluation scores
        """
        if not self.feedback_functions:
            logger.warning("No feedback functions available for evaluation")
            return {
                "evaluations_available": False,
                "message": "TruLens evaluations not configured"
            }
        
        results = {
            "evaluations_available": True,
            "timestamp": datetime.utcnow().isoformat(),
            "scores": {}
        }
        
        try:
            # Create a simple record for evaluation
            record = {
                "input": input_text,
                "output": output_text,
                "context": context or {}
            }
            
            # Run each feedback function
            for method_name, display_name in self.feedback_functions:
                try:
                    # Get the method from the provider
                    method = getattr(self.provider, method_name, None)
                    if method is None:
                        logger.warning(f"Method {method_name} not found on provider")
                        results["scores"][display_name.lower()] = None
                        continue
                    
                    # Call the method with appropriate arguments
                    if method_name == "relevance":
                        score = method(input_text, output_text)
                    else:
                        # coherence, sentiment, conciseness take only output
                        score = method(output_text)
                    
                    # Store score (normalize to 0-1 range if needed)
                    if score is not None:
                        if isinstance(score, (int, float)):
                            results["scores"][display_name.lower()] = float(score)
                        else:
                            results["scores"][display_name.lower()] = float(score)
                    
                except Exception as e:
                    logger.error(f"Error evaluating {display_name}: {e}")
                    results["scores"][display_name.lower()] = None
            
            # Calculate overall quality score (average of available scores)
            valid_scores = [s for s in results["scores"].values() if s is not None]
            if valid_scores:
                results["overall_quality"] = sum(valid_scores) / len(valid_scores)
            else:
                results["overall_quality"] = None
            
            # Store evaluation result
            self.evaluation_results.append(results)
            
            logger.info(f"Evaluation completed. Overall quality: {results.get('overall_quality', 'N/A')}")
            
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            results["error"] = str(e)
        
        return results
    
    def get_recent_evaluations(self, limit: int = 10) -> List[Dict]:
        """Get recent evaluation results."""
        return self.evaluation_results[-limit:]
    
    def get_evaluation_statistics(self) -> Dict:
        """Get statistics from all evaluations."""
        if not self.evaluation_results:
            return {"message": "No evaluations yet"}
        
        # Collect all scores by metric
        metrics = {}
        for result in self.evaluation_results:
            for metric, score in result.get("scores", {}).items():
                if score is not None:
                    if metric not in metrics:
                        metrics[metric] = []
                    metrics[metric].append(score)
        
        # Calculate statistics
        stats = {}
        for metric, scores in metrics.items():
            stats[metric] = {
                "mean": np.mean(scores),
                "std": np.std(scores),
                "min": np.min(scores),
                "max": np.max(scores),
                "count": len(scores)
            }
        
        # Overall statistics
        overall_scores = [r.get("overall_quality") for r in self.evaluation_results 
                         if r.get("overall_quality") is not None]
        
        if overall_scores:
            stats["overall"] = {
                "mean": np.mean(overall_scores),
                "std": np.std(overall_scores),
                "min": np.min(overall_scores),
                "max": np.max(overall_scores),
                "count": len(overall_scores)
            }
        
        stats["total_evaluations"] = len(self.evaluation_results)
        
        return stats
    
    def reset_evaluations(self):
        """Clear evaluation history."""
        self.evaluation_results = []
        logger.info("Evaluation history cleared")


# Global monitor instance
monitor = TruLensMonitor()


def get_monitor() -> TruLensMonitor:
    """Get the global TruLens monitor instance."""
    return monitor


async def evaluate_chat_response(
    input_text: str,
    output_text: str,
    context: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to evaluate a chat response.
    
    Args:
        input_text: User's input
        output_text: Chatbot's response
        context: Optional context
        
    Returns:
        Evaluation results dictionary
    """
    return monitor.evaluate_response(input_text, output_text, context)
