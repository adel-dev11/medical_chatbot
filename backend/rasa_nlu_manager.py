
import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path


class NLUManager:

    def __init__(self):
        """Initialize NLU Manager"""
        self.intents_data = self._load_intents_data()
        print("✓ NLU Manager initialized successfully")

    def _load_intents_data(self) -> Dict[str, Any]:
        """Load intents and entities data from training files"""
        intents_data = {
            "greet": {
                "keywords": ["السلام عليكم", "مرحبا", "صباح", "مساء", "كيف", "hello", "hi", "hey"],
                "confidence_boost": 0.9
            },
            "goodbye": {
                "keywords": ["وداعا", "إلى اللقاء", "سلام", "bye", "goodbye", "farewell"],
                "confidence_boost": 0.9
            },
            "report_symptoms": {
                "keywords": ["أشعر", "عندي", "أعاني", "ألم", "حمى", "صداع", "سعال", "fever", "headache", "pain"],
                "confidence_boost": 0.85
            },
            "ask_medical_advice": {
                "keywords": ["ماذا", "كيف", "ما هو العلاج", "ماذا أفعل", "what should", "how to treat"],
                "confidence_boost": 0.8
            },
            "ask_about_disease": {
                "keywords": ["ما هو", "معلومات", "أخبرني", "tell me about", "information about"],
                "confidence_boost": 0.8
            },
            "ask_medication": {
                "keywords": ["دواء", "أدوية", "medication", "medicine", "drug"],
                "confidence_boost": 0.8
            },
            "emergency": {
                "keywords": ["ساعدني", "حالة طوارئ", "اتصل", "emergency", "help", "urgent"],
                "confidence_boost": 0.95
            },
            "affirm": {
                "keywords": ["نعم", "أيوه", "موافق", "yes", "yeah", "okay", "sure"],
                "confidence_boost": 0.9
            },
            "deny": {
                "keywords": ["لا", "لا شكرا", "no", "nope", "not really"],
                "confidence_boost": 0.9
            },
            "ask_clarification": {
                "keywords": ["هل تقصد", "ماذا تعني", "أعد", "what do you mean", "clarify"],
                "confidence_boost": 0.8
            }
        }
        return intents_data
    
    def parse_message(self, message: str) -> Dict[str, Any]:
        """
        Parse user message to extract intent and entities

        Args:
            message: User input message

        Returns:
            Dictionary with intent, entities, and confidence
        """

        try:
            intent = self.extract_intent(message)
            entities = self.extract_entities(message)

            return {
                "intent": intent,
                "entities": entities,
                "text": message
            }

        except Exception as e:
            print(f"Error parsing message: {str(e)}")
            return {
                "intent": {"name": "nlu_fallback", "confidence": 0.0},
                "entities": [],
                "text": message
            }
    
    def extract_intent(self, message: str) -> Dict[str, Any]:
        """
        Extract intent from message

        Args:
            message: User input message

        Returns:
            Intent information
        """

        message_lower = message.lower()
        best_intent = {"name": "nlu_fallback", "confidence": 0.0}

        for intent_name, intent_data in self.intents_data.items():
            keywords = intent_data["keywords"]
            confidence_boost = intent_data["confidence_boost"]

            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    confidence = min(0.95, confidence_boost)
                    if confidence > best_intent["confidence"]:
                        best_intent = {"name": intent_name, "confidence": confidence}
                    break

        return best_intent
    
    def extract_entities(self, message: str) -> List[Dict[str, Any]]:
        """
        Extract entities from message

        Args:
            message: User input message

        Returns:
            List of extracted entities
        """

        entities = []
        message_lower = message.lower()

        # Medical entities to extract
        medical_entities = {
            "symptom": ["حمى", "صداع", "سعال", "ألم", "غثيان", "إسهال", "fever", "headache", "cough", "pain"],
            "disease": ["السكري", "الربو", "ارتفاع ضغط", "السمنة", "diabetes", "asthma", "hypertension"],
            "medication": ["أسبرين", "باراسيتامول", "أموكسيسيلين", "aspirin", "paracetamol", "amoxicillin"],
            "body_part": ["الرأس", "الصدر", "البطن", "الظهر", "head", "chest", "stomach", "back"]
        }

        for entity_type, keywords in medical_entities.items():
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    entities.append({
                        "entity": entity_type,
                        "value": keyword,
                        "confidence": 0.85
                    })

        return entities
    
    def get_intent_name(self, message: str) -> str:
        """
        Get the intent name for a message
        
        Args:
            message: User input message
        
        Returns:
            Intent name
        """
        
        intent = self.extract_intent(message)
        return intent.get("name", "nlu_fallback")
    
    def get_intent_confidence(self, message: str) -> float:
        """
        Get the confidence score for the detected intent
        
        Args:
            message: User input message
        
        Returns:
            Confidence score (0-1)
        """
        
        intent = self.extract_intent(message)
        return intent.get("confidence", 0.0)
    
    def is_high_confidence(self, message: str, threshold: float = 0.5) -> bool:
        """
        Check if intent confidence is above threshold
        
        Args:
            message: User input message
            threshold: Confidence threshold
        
        Returns:
            True if confidence >= threshold
        """
        
        return self.get_intent_confidence(message) >= threshold
    
    def get_entity_by_type(self, message: str, entity_type: str) -> Optional[str]:
        """
        Get entity value by type
        
        Args:
            message: User input message
            entity_type: Type of entity to extract
        
        Returns:
            Entity value or None
        """
        
        entities = self.extract_entities(message)
        for entity in entities:
            if entity.get("entity") == entity_type:
                return entity.get("value")
        
        return None
    
    def get_all_entities_by_type(self, message: str, entity_type: str) -> List[str]:
        """
        Get all entities of a specific type
        
        Args:
            message: User input message
            entity_type: Type of entity to extract
        
        Returns:
            List of entity values
        """
        
        entities = self.extract_entities(message)
        return [
            entity.get("value")
            for entity in entities
            if entity.get("entity") == entity_type
        ]
    
    def train_model(self, config_path: str = "rasa_config/config.yml"):
        """
        Train NLU model (simplified version without Rasa)

        Args:
            config_path: Path to config file (not used in simplified version)
        """

        try:
            print("✓ NLU model ready (using keyword-based matching)")
            print("  - Intent recognition: Enabled")
            print("  - Entity extraction: Enabled")
            print("  - Confidence scoring: Enabled")

        except Exception as e:
            print(f"Error: {str(e)}")

