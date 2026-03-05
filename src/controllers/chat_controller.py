#!/usr/bin/env python3
"""
Chat Controller for managing conversations and AI chat interactions
"""
import os
import logging
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatController:
    """Controller for managing chat conversations and AI interactions"""
    
    def __init__(self):
        self.conversations_file = os.path.join(os.getcwd(), 'data', 'conversations.json')
        self.conversations_dir = os.path.join(os.getcwd(), 'data', 'conversations')
        os.makedirs(self.conversations_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.conversations_file), exist_ok=True)
        
        # Initialize AI Models Controller
        try:
            from src.controllers.ai_models_controller import AIModelsController
            self.ai_models = AIModelsController()
        except ImportError:
            logger.warning("AI Models Controller not available")
            self.ai_models = None
    
    def send_message(self, message: str, model_name: str = None, conversation_id: str = None) -> Dict:
        """Send a message and get AI response"""
        try:
            # Create new conversation if none exists
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Get or create conversation
            conversation = self._get_or_create_conversation(conversation_id)
            
            # Add user message
            user_message = {
                'id': str(uuid.uuid4()),
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat(),
                'model': model_name
            }
            conversation['messages'].append(user_message)
            
            # Generate AI response
            ai_response = self._generate_ai_response(message, model_name, conversation)
            
            # Add AI message
            ai_message = {
                'id': str(uuid.uuid4()),
                'role': 'assistant',
                'content': ai_response,
                'timestamp': datetime.now().isoformat(),
                'model': model_name
            }
            conversation['messages'].append(ai_message)
            
            # Update conversation
            conversation['last_updated'] = datetime.now().isoformat()
            conversation['message_count'] = len(conversation['messages'])
            
            # Save conversation
            self._save_conversation(conversation_id, conversation)
            
            return {
                'conversation_id': conversation_id,
                'user_message': user_message,
                'ai_response': ai_message,
                'conversation': conversation
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    def _generate_ai_response(self, message: str, model_name: str, conversation: Dict) -> str:
        """Generate AI response using the specified model"""
        if not self.ai_models:
            return "AI models are not available. Please check your installation."
        
        try:
            # Auto-load first available model if none specified
            if not model_name:
                available_models = self.ai_models.get_available_models()
                local_models = [m for m in available_models if m['type'] == 'local' and m['is_available']]
                if local_models:
                    model_name = local_models[0]['id']
                    logger.info(f"Auto-loading first available model: {model_name}")
                else:
                    return "No local models available. Please install and configure AI models."
            
            # Load model if not already loaded
            if not self.ai_models.load_model(model_name):
                return f"Failed to load model: {model_name}"
            
            # Create context from conversation history
            context = self._create_conversation_context(conversation, message)
            
            # Generate response
            response = self.ai_models.generate_response(model_name, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return f"Error generating response: {str(e)}"
    
    def _create_conversation_context(self, conversation: Dict, current_message: str) -> str:
        """Create context from conversation history"""
        messages = conversation.get('messages', [])
        
        # Build context from recent messages (last 10 messages)
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        
        context_parts = []
        
        # Add system message if available
        if conversation.get('system_message'):
            context_parts.append(f"System: {conversation['system_message']}")
        
        # Add conversation history
        for msg in recent_messages:
            role = "User" if msg['role'] == 'user' else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        # Add current message
        context_parts.append(f"User: {current_message}")
        context_parts.append("Assistant:")
        
        return "\n".join(context_parts)
    
    def get_conversations(self) -> List[Dict]:
        """Get all conversations"""
        try:
            if not os.path.exists(self.conversations_file):
                return []
            
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            
            # Sort by last updated
            conversations.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []
    
    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """Get messages for a specific conversation"""
        try:
            conversation = self._get_conversation(conversation_id)
            if not conversation:
                return []
            
            return conversation.get('messages', [])
            
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []
    
    def _get_or_create_conversation(self, conversation_id: str) -> Dict:
        """Get existing conversation or create new one"""
        conversation = self._get_conversation(conversation_id)
        
        if not conversation:
            conversation = {
                'id': conversation_id,
                'title': f"Conversation {conversation_id[:8]}",
                'messages': [],
                'system_message': "You are a helpful AI assistant. Provide clear, accurate, and helpful responses.",
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'message_count': 0,
                'model': None
            }
        
        return conversation
    
    def _get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation"""
        try:
            conversations = self.get_conversations()
            
            for conv in conversations:
                if conv['id'] == conversation_id:
                    return conv
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {e}")
            return None
    
    def _save_conversation(self, conversation_id: str, conversation: Dict):
        """Save conversation to file"""
        try:
            conversations = self.get_conversations()
            
            # Update or add conversation
            found = False
            for i, conv in enumerate(conversations):
                if conv['id'] == conversation_id:
                    conversations[i] = conversation
                    found = True
                    break
            
            if not found:
                conversations.append(conversation)
            
            # Save to file
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
            
            # Also save individual conversation file
            conv_file = os.path.join(self.conversations_dir, f"{conversation_id}.json")
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            raise
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        try:
            conversations = self.get_conversations()
            
            # Remove from conversations list
            conversations = [conv for conv in conversations if conv['id'] != conversation_id]
            
            # Save updated list
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
            
            # Delete individual conversation file
            conv_file = os.path.join(self.conversations_dir, f"{conversation_id}.json")
            if os.path.exists(conv_file):
                os.remove(conv_file)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {e}")
            return False
    
    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title"""
        try:
            conversation = self._get_conversation(conversation_id)
            if not conversation:
                return False
            
            conversation['title'] = title
            conversation['last_updated'] = datetime.now().isoformat()
            
            self._save_conversation(conversation_id, conversation)
            return True
            
        except Exception as e:
            logger.error(f"Error updating conversation title: {e}")
            return False
    
    def set_system_message(self, conversation_id: str, system_message: str) -> bool:
        """Set system message for conversation"""
        try:
            conversation = self._get_or_create_conversation(conversation_id)
            conversation['system_message'] = system_message
            conversation['last_updated'] = datetime.now().isoformat()
            
            self._save_conversation(conversation_id, conversation)
            return True
            
        except Exception as e:
            logger.error(f"Error setting system message: {e}")
            return False
    
    def get_conversation_stats(self) -> Dict:
        """Get conversation statistics"""
        try:
            conversations = self.get_conversations()
            
            total_conversations = len(conversations)
            total_messages = sum(conv.get('message_count', 0) for conv in conversations)
            
            # Count messages by model
            model_stats = {}
            for conv in conversations:
                for msg in conv.get('messages', []):
                    model = msg.get('model', 'unknown')
                    model_stats[model] = model_stats.get(model, 0) + 1
            
            return {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'model_stats': model_stats,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation stats: {e}")
            return {
                'total_conversations': 0,
                'total_messages': 0,
                'model_stats': {},
                'last_updated': datetime.now().isoformat()
            }
