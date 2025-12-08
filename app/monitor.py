"""
TruLens monitoring and evaluation integration.
This module wraps LLM calls with comprehensive evaluation metrics.
"""
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

# TruLens imports
from trulens_eval import Tru, Feedback, TruChain
from trulens_eval.app import App
from trulens_eval.feedback import Groundedness
from trulens_eval.feedback.provider.openai import OpenAI as OpenAIProvider
import numpy as np

logger = logging.getLogger(__name__)

# Initialize TruLens
tru = Tru(database_url=os.getenv("TRULENS_DATABASE_URL", "sqlite:///./trulens.db"))

# Initialize feedback provider
openai_provider = None
if os.getenv("OPENAI_API_KEY"):
    try:
        openai_provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("TruLens OpenAI provider initialized")
    except Exception as e:
        logger.warning(f"Could not initialize OpenAI provider for TruLens: {e}")


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
        if not self.provider:
            logger.warning("OpenAI provider not available. TruLens evaluations disabled.")
            return
        
        try:
            # 1. Relevance: Does the response address the question?
            f_relevance = Feedback(
                self.provider.relevance,
                name="Relevance"
            ).on_input_output()
            
            # 2. Coherence: Is the response logically consistent?
            f_coherence = Feedback(
                self.provider.coherence,
                name="Coherence"
            ).on_output()
            
            # 3. Groundedness: Is the response grounded in provided context?
            grounded = Groundedness(groundedness_provider=self.provider)
            f_groundedness = Feedback(
                grounded.groundedness_measure,
                name="Groundedness"
            ).on_output()
            
            # 4. Sentiment: Analyze response sentiment
            f_sentiment = Feedback(
                self.provider.sentiment,
                name="Sentiment"
            ).on_output()
            
            # 5. Conciseness: Check if response is appropriately concise
            f_conciseness = Feedback(
                self.provider.conciseness,
                name="Conciseness"
            ).on_output()
            
            self.feedback_functions = [
                f_relevance,
                f_coherence,
                f_groundedness,
                f_sentiment,
                f_conciseness
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
            for feedback in self.feedback_functions:
                try:
                    # Evaluate based on feedback type
                    if feedback.name == "Relevance":
                        score = self.provider.relevance(input_text, output_text)
                    elif feedback.name == "Coherence":
                        score = self.provider.coherence(output_text)
                    elif feedback.name == "Groundedness":
                        score = self.provider.groundedness_measure_with_cot_reasons(output_text)
                        if isinstance(score, tuple):
                            score = score[0]  # Extract score from tuple
                    elif feedback.name == "Sentiment":
                        score = self.provider.sentiment(output_text)
                    elif feedback.name == "Conciseness":
                        score = self.provider.conciseness(output_text)
                    else:
                        score = None
                    
                    # Store score (normalize to 0-1 range if needed)
                    if score is not None:
                        if isinstance(score, (int, float)):
                            results["scores"][feedback.name.lower()] = float(score)
                        else:
                            results["scores"][feedback.name.lower()] = float(score)
                    
                except Exception as e:
                    logger.error(f"Error evaluating {feedback.name}: {e}")
                    results["scores"][feedback.name.lower()] = None
            
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
