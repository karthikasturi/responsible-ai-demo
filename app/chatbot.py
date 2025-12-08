"""
Simple LLM chatbot implementation.
This module handles the core chat logic using OpenAI/LangChain.
"""
import os
import logging
from datetime import datetime
from typing import Dict, Optional
import uuid

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

# Initialize LLM
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set! Using mock responses.")
    USE_MOCK = True
else:
    USE_MOCK = False
    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY
    )

# System prompt for the chatbot
SYSTEM_PROMPT = """You are a helpful, friendly AI assistant. 
Your goal is to provide accurate, relevant, and coherent responses to user questions.
Be concise but informative. If you don't know something, say so clearly.
Always be respectful and professional."""


async def get_chatbot_response(
    message: str,
    user_id: str = "anonymous",
    session_id: Optional[str] = None,
    context: Optional[Dict] = None
) -> Dict:
    """
    Generate a chatbot response for the given message.
    
    Args:
        message: User's input message
        user_id: User identifier for tracking
        session_id: Session identifier for conversation continuity
        context: Additional context dictionary
        
    Returns:
        Dictionary containing response, metadata, timestamp, and session_id
    """
    start_time = datetime.utcnow()
    
    # Generate session ID if not provided
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    logger.info(f"Processing chat request for user: {user_id}, session: {session_id}")
    
    try:
        if USE_MOCK:
            # Mock response for testing without API key
            response_text = f"Mock response to: '{message}'. This is a test response. Please set OPENAI_API_KEY for real LLM responses."
        else:
            # Create messages for LLM
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=message)
            ]
            
            # Get response from LLM
            response = llm.invoke(messages)
            response_text = response.content
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Build metadata
        metadata = {
            "model": MODEL_NAME,
            "user_id": user_id,
            "processing_time_seconds": processing_time,
            "input_length": len(message),
            "output_length": len(response_text),
            "mock_mode": USE_MOCK
        }
        
        # Add context if provided
        if context:
            metadata["context"] = context
        
        result = {
            "response": response_text,
            "metadata": metadata,
            "timestamp": end_time.isoformat(),
            "session_id": session_id
        }
        
        logger.info(f"Chat response generated in {processing_time:.2f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating chatbot response: {str(e)}")
        raise


def get_mock_response(message: str) -> str:
    """Generate a simple mock response for testing."""
    responses = {
        "hello": "Hello! How can I help you today?",
        "hi": "Hi there! What can I do for you?",
        "help": "I'm here to assist you. Ask me anything!",
        "weather": "I don't have access to real-time weather data, but I can help with other questions!",
        "default": f"I received your message: '{message}'. How can I help you further?"
    }
    
    message_lower = message.lower()
    for key, response in responses.items():
        if key in message_lower:
            return response
    
    return responses["default"]


# Health check for the chatbot module
def check_chatbot_health() -> Dict:
    """Check if the chatbot is properly configured."""
    return {
        "model": MODEL_NAME,
        "api_key_set": bool(OPENAI_API_KEY),
        "mock_mode": USE_MOCK,
        "status": "healthy"
    }
