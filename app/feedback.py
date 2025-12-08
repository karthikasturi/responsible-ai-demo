"""
Feedback loop system for continuous improvement.
Collects user/operator feedback and uses it to improve the system.
"""
import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)

FEEDBACK_LOG_FILE = "/app/data/feedback.jsonl"
THRESHOLDS_PATH = "/app/config/thresholds.json"


class FeedbackProcessor:
    """
    Processes user feedback to improve the LLM system.
    """
    
    def __init__(self):
        """Initialize feedback processor."""
        self.feedback_history = deque(maxlen=500)
        self.reference_dataset = []
        self._load_existing_feedback()
    
    def _load_existing_feedback(self):
        """Load existing feedback from file."""
        try:
            if os.path.exists(FEEDBACK_LOG_FILE):
                with open(FEEDBACK_LOG_FILE, 'r') as f:
                    for line in f:
                        feedback = json.loads(line.strip())
                        self.feedback_history.append(feedback)
                logger.info(f"Loaded {len(self.feedback_history)} feedback entries")
        except Exception as e:
            logger.error(f"Error loading feedback: {e}")
    
    def submit_feedback(
        self,
        session_id: str,
        feedback_type: str,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Submit feedback for a chat interaction.
        
        Args:
            session_id: Session identifier
            feedback_type: Type of feedback (quality, relevance, helpful, etc.)
            rating: Numeric rating (1-5)
            comment: Text comment
            metadata: Additional metadata
            
        Returns:
            Feedback record
        """
        feedback = {
            "session_id": session_id,
            "feedback_type": feedback_type,
            "rating": rating,
            "comment": comment,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in memory
        self.feedback_history.append(feedback)
        
        # Store in file
        self._save_feedback(feedback)
        
        # Process feedback for improvements
        self._process_feedback(feedback)
        
        logger.info(f"Feedback submitted: {feedback_type} - Rating: {rating}")
        
        return feedback
    
    def _save_feedback(self, feedback: Dict):
        """Save feedback to file."""
        try:
            os.makedirs(os.path.dirname(FEEDBACK_LOG_FILE), exist_ok=True)
            with open(FEEDBACK_LOG_FILE, 'a') as f:
                f.write(json.dumps(feedback) + "\n")
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
    
    def _process_feedback(self, feedback: Dict):
        """Process feedback for system improvements."""
        try:
            # Update thresholds based on feedback
            if feedback.get("rating") is not None:
                self._update_thresholds(feedback)
            
            # Add to reference dataset if high quality
            if feedback.get("rating", 0) >= 4:
                self._add_to_reference_dataset(feedback)
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
    
    def _update_thresholds(self, feedback: Dict):
        """
        Dynamically adjust alert thresholds based on feedback.
        
        Logic:
        - Low ratings (1-2): Increase sensitivity (lower thresholds)
        - High ratings (4-5): Maintain or slightly relax thresholds
        """
        rating = feedback.get("rating", 3)
        feedback_type = feedback.get("feedback_type")
        
        try:
            # Load current thresholds
            if os.path.exists(THRESHOLDS_PATH):
                with open(THRESHOLDS_PATH, 'r') as f:
                    thresholds = json.load(f)
            else:
                return
            
            # Adjustment factor based on rating
            if rating <= 2:
                # Increase sensitivity for low ratings
                adjustment = 0.95  # Reduce threshold by 5%
            elif rating >= 4:
                # Slightly relax for high ratings
                adjustment = 1.02  # Increase threshold by 2%
            else:
                return  # No change for neutral ratings
            
            # Update relevant threshold
            threshold_map = {
                "quality": "quality_threshold",
                "relevance": "relevance_threshold",
                "coherence": "coherence_threshold"
            }
            
            threshold_key = threshold_map.get(feedback_type)
            if threshold_key and threshold_key in thresholds:
                old_value = thresholds[threshold_key]
                new_value = max(0.3, min(0.95, old_value * adjustment))  # Clamp to reasonable range
                
                if abs(new_value - old_value) > 0.001:  # Only update if significant change
                    thresholds[threshold_key] = round(new_value, 3)
                    
                    # Save updated thresholds
                    with open(THRESHOLDS_PATH, 'w') as f:
                        json.dump(thresholds, f, indent=2)
                    
                    logger.info(
                        f"Threshold updated: {threshold_key} "
                        f"{old_value:.3f} -> {new_value:.3f}"
                    )
        
        except Exception as e:
            logger.error(f"Error updating thresholds: {e}")
    
    def _add_to_reference_dataset(self, feedback: Dict):
        """Add high-quality examples to reference dataset."""
        metadata = feedback.get("metadata", {})
        
        if "input" in metadata and "output" in metadata:
            reference = {
                "input": metadata["input"],
                "output": metadata["output"],
                "rating": feedback.get("rating"),
                "timestamp": feedback.get("timestamp")
            }
            
            self.reference_dataset.append(reference)
            
            # Keep only recent 100 references
            if len(self.reference_dataset) > 100:
                self.reference_dataset = self.reference_dataset[-100:]
            
            logger.info("Added example to reference dataset")
    
    def get_feedback_summary(self) -> Dict:
        """Get summary statistics of feedback."""
        if not self.feedback_history:
            return {"total_feedback": 0}
        
        total = len(self.feedback_history)
        
        # Calculate average rating
        ratings = [f.get("rating") for f in self.feedback_history if f.get("rating") is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        
        # Count by type
        by_type = {}
        for f in self.feedback_history:
            ftype = f.get("feedback_type", "unknown")
            by_type[ftype] = by_type.get(ftype, 0) + 1
        
        # Rating distribution
        rating_dist = {}
        for r in ratings:
            rating_dist[r] = rating_dist.get(r, 0) + 1
        
        return {
            "total_feedback": total,
            "average_rating": round(avg_rating, 2) if avg_rating else None,
            "rating_distribution": rating_dist,
            "feedback_by_type": by_type,
            "reference_dataset_size": len(self.reference_dataset)
        }
    
    def get_recent_feedback(self, limit: int = 20) -> List[Dict]:
        """Get recent feedback entries."""
        return list(self.feedback_history)[-limit:]
    
    def get_low_rating_feedback(self, threshold: int = 2) -> List[Dict]:
        """Get feedback with low ratings for analysis."""
        return [
            f for f in self.feedback_history
            if f.get("rating") is not None and f.get("rating") <= threshold
        ]
    
    def export_reference_dataset(self) -> List[Dict]:
        """Export the reference dataset for fine-tuning."""
        return self.reference_dataset.copy()


# Global feedback processor
feedback_processor = FeedbackProcessor()


def get_feedback_processor() -> FeedbackProcessor:
    """Get the global feedback processor instance."""
    return feedback_processor
