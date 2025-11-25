
from typing import Dict, Any, Optional, List
from datetime import datetime
from rasa_nlu_manager import NLUManager
from response_generator import ResponseGenerator
import json
import os

class DialogueManager:
    def __init__(self, llm_provider: str = "gemini"):
        self.nlu_manager = NLUManager()
        self.response_generator = ResponseGenerator()
        self.conversation_history: List[Dict[str, str]] = []
        self.user_context: Dict[str, Any] = {}
        self.session_id = datetime.now().isoformat()

       
        self.quick_keywords = {
            "المدة": "ask_duration",
            "العلاج": "ask_medication",
            "الاعراض": "report_symptoms",
            "اعراض": "report_symptoms",
            "السبب": "ask_about_disease",
            "الاسباب": "ask_about_disease",
            "دواء": "ask_medication",
            "دوائي": "ask_medication",
        }

    def process_message(self, user_message: str) -> Dict[str, Any]:
        intent = self.nlu_manager.extract_intent(user_message)
        entities = self.nlu_manager.extract_entities(user_message)

        
        if intent.get("confidence", 0.0) < 0.3:
            for keyword, fixed_intent in self.quick_keywords.items():
                if keyword in user_message:
                    intent = {"name": fixed_intent, "confidence": 0.9}
                    break

        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        self._update_context(entities)
        response = self._generate_response(user_message, intent, entities)

        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "response": response,
            "intent": intent,
            "entities": entities,
            "context": self.user_context
        }

    def _update_context(self, entities: List[Dict[str, Any]]):
        context_map = {
            "symptom": "symptoms",
            "disease": "diseases",
            "medication": "medications",
            "body_part": "body_parts",
        }
        for entity in entities:
            e_type = entity.get("entity")
            e_value = entity.get("value")
            if e_type in context_map:
                key = context_map[e_type]
                if key not in self.user_context:
                    self.user_context[key] = []
                if e_value not in self.user_context[key]:
                    self.user_context[key].append(e_value)

    def _generate_response(self, user_message: str, intent: Dict[str, Any], entities: List[Dict[str, Any]]) -> str:
        intent_name = intent.get("name", "nlu_fallback")
        confidence = intent.get("confidence", 0.0)

        if confidence < 0.3:
            return "عذرًا، ممكن توضح سؤالك أكتر؟"

        handlers = {
            "greet": self._handle_greet,
            "goodbye": self._handle_goodbye,
            "report_symptoms": self._handle_symptoms,
            "ask_medical_advice": self._handle_medical_advice,
            "ask_about_disease": self._handle_disease_info,
            "ask_medication": self._handle_medication_info,
            "ask_duration": self._handle_duration,
            "emergency": self._handle_emergency,
            "affirm": lambda: "تمام 😊، إزاي ممكن أساعدك أكتر؟",
            "deny": lambda: "ماشي 👌، تحب تسأل عن حاجة تانية؟",
            "ask_clarification": lambda: "أكيد! ممكن توضح أكتر؟",
        }

        handler = handlers.get(intent_name)
        if handler:
            return handler() if callable(handler) else handler

        return self.response_generator.generate_response(
            user_message,
            intent_name,
            context=self.user_context
        )

    def _handle_greet(self) -> str:
        return self.response_generator.generate_response("", "greet", self.user_context)

    def _handle_goodbye(self) -> str:
        return self.response_generator.generate_response("", "goodbye", self.user_context)

    def _handle_symptoms(self) -> str:
        return self.response_generator.generate_response("", "report_symptoms", self.user_context)

    def _handle_medical_advice(self) -> str:
        return self.response_generator.generate_response("", "ask_medical_advice", self.user_context)

    def _handle_disease_info(self) -> str:
        return self.response_generator.generate_response("", "ask_about_disease", self.user_context)

    def _handle_medication_info(self) -> str:
        return self.response_generator.generate_response("", "ask_medication", self.user_context)

    def _handle_duration(self) -> str:
        return self.response_generator.generate_response("", "ask_duration", self.user_context)

    def _handle_emergency(self) -> str:
        return (" حالة طوارئ!\n"
                "يرجى الاتصال برقم الطوارئ فوراً:\n"
                " 911 أو 123\n\n"
                "أو توجه إلى أقرب مستشفى فوراً!")

    def get_conversation_history(self):
        return self.conversation_history

    def get_user_context(self):
        return self.user_context

    def clear_context(self):
        self.user_context = {}
        self.conversation_history = []

    def set_context(self, context: Dict[str, Any]):
        self.user_context.update(context)

    def get_session_id(self):
        return self.session_id
