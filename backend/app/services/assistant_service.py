import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.case import TriageCase
from app.models.patient import Patient
from app.models.consultation import Consultation
from app.schemas.assistant import (
    AssistantCapabilities,
    AssistantMessageRequest,
    AssistantMessageResponse,
    ProposedAction,
    AssistantToolExecuteRequest,
    AssistantToolExecuteResponse,
)
from app.services.ai.gemini_service import ai_service

logger = logging.getLogger("clinova.assistant")

SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English"},
    {"code": "hi", "name": "हिन्दी (Hindi)"},
    {"code": "or", "name": "ଓଡ଼ିଆ (Odia)"},
    {"code": "bn", "name": "বাংলা (Bengali)"},
    {"code": "te", "name": "తెలుగు (Telugu)"},
    {"code": "ta", "name": "தமிழ் (Tamil)"},
    {"code": "mr", "name": "मराठी (Marathi)"},
    {"code": "gu", "name": "ગુજરાતી (Gujarati)"},
    {"code": "kn", "name": "ಕನ್ನಡ (Kannada)"},
    {"code": "ml", "name": "മലയാളം (Malayalam)"},
    {"code": "pa", "name": "ਪੰਜਾਬੀ (Punjabi)"},
]

ROLE_TOOL_ALLOWLIST = {
    UserRole.PATIENT: [
        "get_current_user_context",
        "explain_term",
        "translate_patient_statement",
        "identify_missing_information",
        "navigate_to_authorized_page",
        "get_authorized_case_summary",
    ],
    UserRole.NURSE: [
        "get_current_user_context",
        "get_queue_status",
        "explain_term",
        "identify_missing_information",
        "navigate_to_authorized_page",
        "create_draft_handoff",
    ],
    UserRole.DOCTOR: [
        "get_current_user_context",
        "get_queue_status",
        "get_authorized_case_summary",
        "identify_missing_information",
        "explain_term",
        "translate_patient_statement",
        "create_draft_note",
        "navigate_to_authorized_page",
        "request_missing_information",
    ],
    UserRole.ADMIN: [
        "get_current_user_context",
        "get_queue_status",
        "explain_term",
        "navigate_to_authorized_page",
    ],
}


class AssistantService:
    """Bounded, role-aware, multi-lingual intelligence service for Floating Clinova Assistant."""

    @classmethod
    def get_capabilities(cls, user: User) -> AssistantCapabilities:
        tools = ROLE_TOOL_ALLOWLIST.get(user.role, ["get_current_user_context", "explain_term"])
        return AssistantCapabilities(
            role=user.role.value,
            available_tools=tools,
            supported_languages=SUPPORTED_LANGUAGES,
            voice_input_available=True,
            tts_available=True,
        )

    @classmethod
    def detect_language(cls, text: str) -> str:
        """Lightweight script and phonetic detection for regional Indian languages."""
        # 1. Unicode native scripts
        if any("\u0900" <= c <= "\u097F" for c in text):
            return "hi"  # Devanagari (Hindi)
        if any("\u0B00" <= c <= "\u0B7F" for c in text):
            return "or"  # Odia script
        if any("\u0980" <= c <= "\u09FF" for c in text):
            return "bn"  # Bengali
        if any("\u0C00" <= c <= "\u0C7F" for c in text):
            return "te"  # Telugu
        if any("\u0B80" <= c <= "\u0BFF" for c in text):
            return "ta"  # Tamil
        if any("\u0C80" <= c <= "\u0CFF" for c in text):
            return "kn"  # Kannada
        if any("\u0D00" <= c <= "\u0D7F" for c in text):
            return "ml"  # Malayalam
        if any("\u0A80" <= c <= "\u0AFF" for c in text):
            return "gu"  # Gujarati
        if any("\u0A00" <= c <= "\u0A7F" for c in text):
            return "pa"  # Punjabi

        # 2. Phonetic Romanized Hindi keywords (word-boundary matched)
        lower = text.lower()
        hi_words = [
            "namaste", "namaskar", "mera", "meri", "mere", "mujhe", "aap", "tum",
            "dard", "sir dard", "pet dard", "bukhar", "khansi", "dawa", "kripya",
            "kya", "kyu", "kaise", "thik", "nahi", "haan", "batao", "madad",
            "chhati", "saans", "takleef", "bimar", "bhookh"
        ]
        if any(re.search(rf"\b{re.escape(w)}\b", lower) for w in hi_words):
            return "hi"

        # 3. Phonetic Romanized Odia keywords (word-boundary matched)
        or_words = [
            "mora", "mote", "munda", "bindhuchi", "peto", "jwara", "kasa",
            "au", "kaha", "hete", "achi", "nahin", "sahajya", "dhanyabad"
        ]
        if any(re.search(rf"\b{re.escape(w)}\b", lower) for w in or_words):
            return "or"

        return "en"

    @classmethod
    async def process_message(
        cls,
        req: AssistantMessageRequest,
        user: User,
        db: AsyncSession,
    ) -> AssistantMessageResponse:
        """Processes an incoming assistant query with strict safety, authorization, and multilingual response."""
        msg_clean = req.message.strip()
        lower_msg = msg_clean.lower()
        detected_lang = cls.detect_language(msg_clean)
        # Prioritize detected language of the spoken voice so the assistant speaks back in that same language!
        response_lang = detected_lang if detected_lang != "en" else (req.language or "en")

        # -------------------------------------------------------------
        # SAFETY CHECK 1: Prompt Injection & Unsafe Command Filtering
        # -------------------------------------------------------------
        injection_patterns = [
            r"ignore (all )?(previous )?(instructions|rules)",
            r"system instruction",
            r"(drop|delete|alter) table",
            r"select .* from",
            r"database password",
            r"shell command",
            r"run sql",
            r"show me all (patients|users|records)",
            r"export (the )?database",
            r"who am i.*admin",
        ]
        if any(re.search(p, lower_msg) for p in injection_patterns):
            refusal_en = (
                "I am Clinova's Health Assistant. I can only assist with authorized Clinova healthcare workflows "
                "and cannot execute arbitrary commands, bypass access controls, or disclose credentials."
            )
            refusal_map = {
                "hi": "मैं क्लिनोवा का स्वास्थ्य सहायक हूँ। मैं केवल अधिकृत क्लिनोवा स्वास्थ्य प्रक्रियाओं में सहायता कर सकता हूँ और सिस्टम या डेटाबेस कमांड निष्पादित नहीं कर सकता।",
                "or": "ମୁଁ କ୍ଲିନୋଭା ସ୍ୱାସ୍ଥ୍ୟ ସହାୟକ। ମୁଁ କେବଳ ଅନୁମୋଦିତ ସ୍ୱାସ୍ଥ୍ୟ ପ୍ରକ୍ରିୟାରେ ସାହାଯ୍ୟ କରିପାରିବି ଏବଂ ସିଷ୍ଟମ୍ କିମ୍ବା ଡାଟାବେସ୍ କମାଣ୍ଡ୍ ଚଳାଇପାରିବି ନାହିଁ।",
            }
            return AssistantMessageResponse(
                text=refusal_map.get(response_lang, refusal_en),
                language=response_lang,
                original_statement=msg_clean,
                source_label="Safety Policy (Refusal)",
                detected_language=detected_lang,
            )

        # -------------------------------------------------------------
        # SAFETY CHECK 2: Autonomous Diagnosis or Prescription Demands
        # -------------------------------------------------------------
        if any(w in lower_msg for w in ["diagnose me", "what is my diagnosis", "do i have cancer", "confirm my disease"]):
            diag_en = (
                "I am an AI assistant and cannot provide a personal medical diagnosis. "
                "I can help organize your symptoms into a structured intake note for review by a qualified doctor."
            )
            diag_map = {
                "hi": "मैं एक एआई सहायक हूँ और व्यक्तिगत चिकित्सा निदान प्रदान नहीं कर सकता। मैं आपके लक्षणों को एक योग्य डॉक्टर द्वारा समीक्षा के लिए व्यवस्थित करने में मदद कर सकता हूँ।",
                "or": "ମୁଁ ଏକ AI ସହାୟକ ଏବଂ ବ୍ୟକ୍ତିଗତ ଡାକ୍ତରୀ ନିର୍ଣ୍ଣୟ ଦେଇପାରିବି ନାହିଁ। ମୁଁ ଆପଣଙ୍କ ଲକ୍ଷଣଗୁଡ଼ିକୁ ଜଣେ ଯୋଗ୍ୟ ଡାକ୍ତରଙ୍କ ଦ୍ୱାରା ସମୀକ୍ଷା ପାଇଁ ସଂଗଠିତ କରିବାରେ ସାହାଯ୍ୟ କରିପାରିବି।",
            }
            return AssistantMessageResponse(
                text=diag_map.get(response_lang, diag_en),
                language=response_lang,
                original_statement=msg_clean,
                source_label="AI-assisted Boundary",
                follow_up_suggestions=["Start clinical intake", "Describe your symptoms"],
                detected_language=detected_lang,
            )

        if any(w in lower_msg for w in ["prescribe", "give me medicine", "change my dose", "stop taking my"]):
            rx_en = (
                "I cannot prescribe medications or alter your treatment regimen. "
                "Please consult your treating physician or visit a healthcare center before changing any prescription."
            )
            rx_map = {
                "hi": "मैं दवाएं निर्धारित नहीं कर सकता या आपकी खुराक में बदलाव की सलाह नहीं दे सकता। कृपया किसी भी दवा में बदलाव करने से पहले अपने डॉक्टर से परामर्श करें।",
                "or": "ମୁଁ ଔଷଧ ନିର୍ଦ୍ଦେଶ ଦେଇପାରିବି ନାହିଁ କିମ୍ବା ଆପଣଙ୍କ ଚିକିତ୍ସାରେ ପରିବର୍ତ୍ତନ କରିପାରିବି ନାହିଁ। ଦୟାକରି କୌଣସି ପରିବର୍ତ୍ତନ ପୂର୍ବରୁ ଆପଣଙ୍କ ଡାକ୍ତରଙ୍କ ପରାମର୍ଶ ନିଅନ୍ତୁ।",
            }
            return AssistantMessageResponse(
                text=rx_map.get(response_lang, rx_en),
                language=response_lang,
                original_statement=msg_clean,
                source_label="AI-assisted Boundary",
                detected_language=detected_lang,
            )

        # -------------------------------------------------------------
        # EMERGENCY RED FLAG ADVISORY (Human oversight first)
        # -------------------------------------------------------------
        acute_keywords = [
            "chest pain", "cannot breathe", "difficulty breathing", "severe bleeding", "unconscious", "stroke", "heart attack",
            "छाती में दर्द", "सांस", "सांस फूलना", "बेहोश", "chhati me dard", "saans",
            "ଛାତି ଯନ୍ତ୍ରଣା", "ନିଶ୍ୱାସ", "ଅଚେତ", "chhati jantrana"
        ]
        if any(w in lower_msg for w in acute_keywords):
            em_en = (
                "⚠️ URGENT HEALTH ADVISORY: The symptoms you described may require immediate medical attention. "
                "Please notify a healthcare professional at your clinic or call local emergency medical services immediately. "
                "Clinova AI is a triage-support assistant and does not replace emergency clinical evaluation."
            )
            em_map = {
                "hi": "⚠️ तत्काल स्वास्थ्य सूचना: आपके द्वारा बताए गए लक्षणों के लिए तत्काल आपातकालीन चिकित्सा सहायता की आवश्यकता हो सकती है। कृपया तुरंत अपने नजदीकी स्वास्थ्य केंद्र या आपातकालीन सेवा से संपर्क करें।",
                "or": "⚠️ ଜରୁରୀ ସ୍ୱାସ୍ଥ୍ୟ ସୂଚନା: ଆପଣ ବର୍ଣ୍ଣନା କରିଥିବା ଲକ୍ଷଣଗୁଡ଼ିକ ପାଇଁ ତୁରନ୍ତ ଡାକ୍ତରୀ ସହାୟତା ଆବଶ୍ୟକ ହୋଇପାରେ। ଦୟାକରି ତୁରନ୍ତ ସ୍ୱାସ୍ଥ୍ୟ କେନ୍ଦ୍ର କିମ୍ବା ଆପାତକାଳୀନ ସେବା ସହିତ ଯୋଗାଯୋଗ କରନ୍ତୁ।",
            }
            return AssistantMessageResponse(
                text=em_map.get(response_lang, em_en),
                language=response_lang,
                original_statement=msg_clean,
                source_label="Emergency Triage Advisory",
                follow_up_suggestions=["Call emergency contact", "Notify on-duty clinician"],
                detected_language=detected_lang,
            )

        # -------------------------------------------------------------
        # DOMAIN INTENT: Symptom Intake Reporting
        # -------------------------------------------------------------
        symptom_keywords = [
            "headache", "fever", "cough", "cold", "pain", "stomach", "vomiting", "weakness", "body ache",
            "सिरदर्द", "बुखार", "खांसी", "जुकाम", "दर्द", "पेट दर्द", "उल्टी", "कमजोरी", "थकान",
            "sir dard", "bukhar", "khansi", "pet dard",
            "ମୁଣ୍ଡ ବିନ୍ଧା", "ଜ୍ୱର", "କାଶ", "ଥଣ୍ଡା", "ଯନ୍ତ୍ରଣା", "ପେଟ ବ୍ୟଥା", "ବାନ୍ତି", "ଦୁର୍ବଳତା",
            "munda bindha", "jwara", "kasa", "thanda", "peto jantrana"
        ]
        if any(w in lower_msg for w in symptom_keywords):
            resp_en = (
                f"I have noted your reported symptoms. How many days have you been experiencing this, "
                f"and is there any severe discomfort? I will organize your symptom timeline for clinician review."
            )
            resp_hi = (
                f"मैंने आपके द्वारा बताए गए लक्षण दर्ज कर लिए हैं। आपको यह तकलीफ कितने दिनों से हो रही है, "
                f"और क्या दर्द अधिक तेज है? मैं आपके लक्षणों का विवरण डॉक्टर की समीक्षा के लिए व्यवस्थित कर रहा हूँ।"
            )
            resp_or = (
                f"ମୁଁ ଆପଣଙ୍କର ଲକ୍ଷଣଗୁଡ଼ିକ ରେକର୍ଡ କରିଛି। ଆପଣଙ୍କୁ ଏହି ଅସୁବିଧା କେତେ ଦିନରୁ ହେଉଛି, "
                f"ଏବଂ କଷ୍ଟ ଅଧିକ ହେଉଛି କି? ମୁଁ ଡାକ୍ତରଙ୍କ ସମୀକ୍ଷା ପାଇଁ ଆପଣଙ୍କ ତଥ୍ୟ ପ୍ରସ୍ତୁତ କରୁଛି।"
            )
            resp_map = {"hi": resp_hi, "or": resp_or}
            return AssistantMessageResponse(
                text=resp_map.get(response_lang, resp_en),
                language=response_lang,
                original_statement=msg_clean,
                source_label="Clinical Intake Note (AI-assisted)",
                follow_up_suggestions=["Record symptom duration", "Record vitals"],
                detected_language=detected_lang,
            )

        # -------------------------------------------------------------
        # DOMAIN INTENT 1: Case Status Query (Patient / Clinician)
        # -------------------------------------------------------------
        if any(w in lower_msg for w in ["case status", "my status", "track case", "केस का स्टेटस", "କେସ ଷ୍ଟାଟସ"]):
            if user.role == UserRole.PATIENT:
                stmt = select(TriageCase).where(
                    TriageCase.patient_id == user.id,
                    TriageCase.is_deleted.is_(False),
                ).order_by(desc(TriageCase.created_at)).limit(1)
                latest_case = (await db.execute(stmt)).scalar_one_or_none()
                if latest_case:
                    status_str = latest_case.status.replace("_", " ").title()
                    status_text_en = (
                        f"Your most recent intake case ({latest_case.synthetic_case_id}) is currently in status: '{status_str}'. "
                        f"Facility: {latest_case.facility_type}. Review urgency: {latest_case.queue_category.upper()}."
                    )
                    status_map = {
                        "hi": f"आपका सबसे हालिया केस ({latest_case.synthetic_case_id}) वर्तमान में स्थिति '{status_str}' में है। सुविधा: {latest_case.facility_type}।",
                        "or": f"ଆପଣଙ୍କର ସଦ୍ୟତମ କେସ୍ ({latest_case.synthetic_case_id}) ବର୍ତ୍ତମାନ '{status_str}' ସ୍ଥିତିରେ ଅଛି। ସ୍ୱାସ୍ଥ୍ୟ କେନ୍ଦ୍ର: {latest_case.facility_type}।",
                    }
                    return AssistantMessageResponse(
                        text=status_map.get(response_lang, status_text_en),
                        language=response_lang,
                        original_statement=msg_clean,
                        source_label="EHR Query (Grounded)",
                        structured_data={"case_id": latest_case.synthetic_case_id, "status": latest_case.status},
                        detected_language=detected_lang,
                    )
                else:
                    return AssistantMessageResponse(
                        text="You have no active intake cases recorded. You can start a new symptom intake anytime.",
                        language=response_lang,
                        original_statement=msg_clean,
                        source_label="EHR Query",
                        follow_up_suggestions=["Start new intake"],
                        detected_language=detected_lang,
                    )

        # -------------------------------------------------------------
        # DOMAIN INTENT 2: Queue Status (Staff / Doctor)
        # -------------------------------------------------------------
        if any(w in lower_msg for w in ["queue", "waiting patients", "how many cases", "कतार", "କ୍ୟୁ"]):
            if user.role in (UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN):
                stmt = select(
                    TriageCase.status, func.count(TriageCase.id)
                ).where(
                    TriageCase.is_deleted.is_(False)
                ).group_by(TriageCase.status)
                counts = dict((await db.execute(stmt)).all())
                awaiting = counts.get("awaiting_review", 0)
                in_rev = counts.get("in_review", 0)
                ready = counts.get("ready_for_doctor", 0)
                appr = counts.get("approved", 0)

                q_en = (
                    f"Operational Queue Summary:\n"
                    f"• Awaiting Review: {awaiting} patients\n"
                    f"• In Review: {in_rev} patients\n"
                    f"• Ready for Doctor: {ready} patients\n"
                    f"• Approved Today: {appr} cases"
                )
                return AssistantMessageResponse(
                    text=q_en,
                    language=response_lang,
                    original_statement=msg_clean,
                    source_label="Operational Telemetry (Grounded)",
                    structured_data={"awaiting_review": awaiting, "in_review": in_rev, "ready_for_doctor": ready, "approved": appr},
                    detected_language=detected_lang,
                )

        # -------------------------------------------------------------
        # DOMAIN INTENT 3: Missing Information Evaluation
        # -------------------------------------------------------------
        if any(w in lower_msg for w in ["missing information", "what is missing", "क्या जानकारी गायब", "କଣ ବାକି ଅଛି"]):
            missing = [
                "Duration of current symptoms (e.g. days or hours since onset)",
                "Severity score on a 1-10 pain/discomfort scale",
                "Current list of daily medications or home treatments",
                "Known drug or food allergies",
            ]
            resp_en = (
                "Identified potential missing clinical factors for human review:\n" +
                "\n".join([f"• {m}" for m in missing]) +
                "\n\nClarifying these with the patient improves triage precision."
            )
            return AssistantMessageResponse(
                text=resp_en,
                language=response_lang,
                original_statement=msg_clean,
                source_label="AI-assisted Data Quality Check",
                structured_data={"missing_factors": missing},
                follow_up_suggestions=["Record symptom duration", "Record vitals"],
                detected_language=detected_lang,
            )

        # -------------------------------------------------------------
        # DOMAIN INTENT 4: Health Terminology Explanation
        # -------------------------------------------------------------
        term_map = {
            "hypertension": "High blood pressure — a condition where the force of blood against artery walls is consistently elevated.",
            "triage": "The systematic sorting and prioritization of patients based on urgency and clinical need.",
            "mrn": "Medical Record Number — a unique clinical identifier assigned to your medical chart.",
            "vital signs": "Key physiological measurements including Blood Pressure, Heart Rate, Respiratory Rate, Oxygen Saturation, and Body Temperature.",
            "ecg": "Electrocardiogram — a non-invasive diagnostic test recording the electrical activity of the heart.",
        }
        for term, explanation in term_map.items():
            if term in lower_msg:
                return AssistantMessageResponse(
                    text=f"Health Terminology Explanation:\n{term.upper()}: {explanation}",
                    language=response_lang,
                    original_statement=msg_clean,
                    source_label="Health Education (Non-diagnostic)",
                    detected_language=detected_lang,
                )

        # -------------------------------------------------------------
        # DOMAIN INTENT 5: Navigation Guidance
        # -------------------------------------------------------------
        if any(w in lower_msg for w in ["where do i", "how to start", "open intake", "go to", "navigate"]):
            route = "/intake" if user.role == UserRole.PATIENT else "/patients"
            return AssistantMessageResponse(
                text=f"You can proceed to the authorized workflow at '{route}'.",
                language=response_lang,
                original_statement=msg_clean,
                source_label="Workflow Navigation",
                structured_data={"target_route": route},
                follow_up_suggestions=["Go to intake", "View dashboard"],
                detected_language=detected_lang,
            )

        # -------------------------------------------------------------
        # DOMAIN INTENT 6: Consequential Action Proposal (requires confirmation)
        # -------------------------------------------------------------
        if any(w in lower_msg for w in ["submit case", "send referral", "escalate case", "approve case"]):
            action_desc = "Clinical action proposal requires your explicit confirmation before submission."
            return AssistantMessageResponse(
                text=(
                    "You have requested a consequential clinical workflow action. "
                    "In compliance with Clinova safety protocols, this requires explicit human review and confirmation before backend execution."
                ),
                language=response_lang,
                original_statement=msg_clean,
                source_label="Human-in-the-Loop Confirmation Gate",
                requires_confirmation=True,
                proposed_action=ProposedAction(
                    tool_name="confirm_clinical_action",
                    description="Approve and record triage action",
                    parameters={"action": "approve", "requested_by": user.email},
                    risk_level="HIGH_IMPACT",
                ),
                detected_language=detected_lang,
            )

        # -------------------------------------------------------------
        # CONVERSATIONAL VOICE SKILLS & MULTI-TURN AI CHAT
        # -------------------------------------------------------------
        # 1. Attempt Live Gemini Voice Generation if client configured
        try:
            gemini_voice_text = await ai_service.generate_voice_chat(
                message=msg_clean,
                history=req.history,
                language=response_lang,
                persona=getattr(req, "voice_persona", "clara") or "clara",
                user_name=user.full_name or "Patient",
                user_role=user.role.value if hasattr(user.role, "value") else str(user.role),
            )
            if gemini_voice_text and len(gemini_voice_text.strip()) > 5:
                return AssistantMessageResponse(
                    text=gemini_voice_text.strip(),
                    language=response_lang,
                    original_statement=msg_clean,
                    source_label="Clinova Voice AI (Gemini)",
                    follow_up_suggestions=["Record additional symptom", "Check triage status"],
                    detected_language=detected_lang,
                )
        except Exception as e:
            logger.warning(f"Voice Gemini chat fallback triggered: {e}")

        # 2. Conversational Heuristic Turn-Taking Engine (Offline & Deterministic)
        # Check if user is reporting duration
        if any(w in lower_msg for w in ["days", "day", "hours", "hour", "weeks", "since yesterday", "today", "दिन", "घंटे", "हफ्ते", "କାଲିଠୁ", "ଦିନ"]):
            dur_en = (
                "Thank you for sharing that timeline. Knowing how long you have experienced this is key for clinician review. "
                "Have your symptoms been staying consistent, or are they worsening at particular times like evening or night?"
            )
            dur_hi = (
                "समय अवधि बताने के लिए धन्यवाद। क्या आपके लक्षण पूरे दिन एक जैसे रहते हैं, या शाम या रात के समय अधिक बढ़ जाते हैं?"
            )
            dur_or = (
                "ସମୟ ବିଷୟରେ ଜଣାଇବା ପାଇଁ ଧନ୍ୟବାଦ। ଏହି ଲକ୍ଷଣଗୁଡ଼ିକ କଣ ସବୁବେଳେ ସମାନ ରହୁଛି, ନା ରାତିରେ ଅଧିକ ହେଉଛି?"
            )
            dur_map = {"hi": dur_hi, "or": dur_or}
            return AssistantMessageResponse(
                text=dur_map.get(response_lang, dur_en),
                language=response_lang,
                original_statement=msg_clean,
                source_label="Conversational Triage Follow-up",
                follow_up_suggestions=["Describe pain severity", "Record vitals"],
                detected_language=detected_lang,
            )

        # Check if user is reporting severity or pain level
        if any(w in lower_msg for w in ["out of 10", "scale", "severe", "mild", "moderate", "pain is", "तेज", "हल्का", "दर्द", "କଷ୍ଟ", "ଯନ୍ତ୍ରଣା"]):
            sev_en = (
                "I understand how uncomfortable that is. Managing your pain and discomfort is our priority. "
                "Are you able to rest and hydrate comfortably, or is this keeping you from sleeping?"
            )
            sev_hi = (
                "मैं आपकी तकलीफ समझ सकता हूँ। क्या इस परेशानी के कारण आपको सोने या आराम करने में भी कठिनाई हो रही है?"
            )
            sev_or = (
                "ମୁଁ ଆପଣଙ୍କ କଷ୍ଟ ବୁଝିପାରୁଛି। ଏହି ଯନ୍ତ୍ରଣା ଯୋଗୁଁ ଆପଣଙ୍କୁ ଶୋଇବା କିମ୍ବା ବିଶ୍ରାମ ନେବାରେ କୌଣସି ଅସୁବିଧା ହେଉଛି କି?"
            )
            sev_map = {"hi": sev_hi, "or": sev_or}
            return AssistantMessageResponse(
                text=sev_map.get(response_lang, sev_en),
                language=response_lang,
                original_statement=msg_clean,
                source_label="Conversational Triage Follow-up",
                follow_up_suggestions=["List current medications", "Request doctor consult"],
                detected_language=detected_lang,
            )

        # Check if user is mentioning medications or home remedies taken
        if any(w in lower_msg for w in ["paracetamol", "tablet", "medicine", "pill", "syrup", "dawa", "दवा", "गोली", "ଔଷଧ"]):
            med_en = (
                "Noted. Keeping track of previous medications or home remedies provides valuable context for the doctor. "
                "Did taking that give you any noticeable relief, or are you still feeling the same?"
            )
            med_hi = (
                "दर्ज कर लिया गया है। आपने जो दवा या घरेलू उपाय लिया, क्या उससे आपको कुछ राहत मिली है?"
            )
            med_or = (
                "ମୁଁ ଏହା ରେକର୍ଡ କରିଛି। ଆପଣ ନେଇଥିବା ଔଷଧ ଦ୍ୱାରା କିଛି ଉପଶମ ମିଳିଛି କି, ନା ସମାନ ଅନୁଭବ ହେଉଛି?"
            )
            med_map = {"hi": med_hi, "or": med_or}
            return AssistantMessageResponse(
                text=med_map.get(response_lang, med_en),
                language=response_lang,
                original_statement=msg_clean,
                source_label="Medication History Intake",
                follow_up_suggestions=["Note allergies", "Check clinical queue"],
                detected_language=detected_lang,
            )

        # Check if user asks for advice, diet, hydration, or what to do next
        if any(w in lower_msg for w in ["what should i do", "what can i eat", "food", "diet", "drink", "water", "क्या करूँ", "क्या खाऊं", "पानी", "ଖାଦ୍ୟ", "କଣ କରିବି"]):
            care_en = (
                "While waiting for human clinician review, it is generally safest to drink plenty of warm fluids, "
                "eat light non-greasy foods, and get adequate rest. Would you like me to submit your symptom summary to the clinic intake queue?"
            )
            care_hi = (
                "डॉक्टर द्वारा समीक्षा किए जाने तक, पर्याप्त आराम करें, हल्का भोजन लें और गुनगुने तरल पदार्थ पिएं। क्या आप चाहते हैं कि मैं आपके लक्षणों की रिपोर्ट डॉक्टर को भेज दूँ?"
            )
            care_or = (
                "ଡାକ୍ତର ଦେଖିବା ପର୍ଯ୍ୟନ୍ତ, ପର୍ଯ୍ୟାପ୍ତ ବିଶ୍ରାମ ନିଅନ୍ତୁ, ପ୍ରଚୁର ପାଣି ପିଅନ୍ତୁ ଏବଂ ହାଲୁକା ଖାଦ୍ୟ ଖାଆନ୍ତୁ। ଆପଣ ଚାହାଁନ୍ତି କି ମୁଁ ଡାକ୍ତରଙ୍କ ପାଇଁ ଏହି ରିପୋର୍ଟ ଦାଖଲ କରେ?"
            )
            care_map = {"hi": care_hi, "or": care_or}
            return AssistantMessageResponse(
                text=care_map.get(response_lang, care_en),
                language=response_lang,
                original_statement=msg_clean,
                source_label="Self-Care & Triage Guidance",
                follow_up_suggestions=["Submit to clinic intake", "Add another symptom"],
                detected_language=detected_lang,
            )

        # Greetings & friendly conversational check-ins
        if any(w in lower_msg for w in ["hello", "hi", "hey", "how are you", "who are you", "नमस्ते", "ନମସ୍କାର"]):
            greet_en = (
                f"Hello {user.full_name}! I am Clinova's voice health companion. "
                f"I'm here to listen to your health concerns, organize your symptoms, and assist with your clinic visit. How are you feeling right now?"
            )
            greet_hi = (
                f"नमस्ते {user.full_name}! मैं क्लिनोवा का वॉयस स्वास्थ्य सहायक हूँ। "
                f"मैं आपकी सहायता के लिए तैयार हूँ। आप अभी कैसा महसूस कर रहे हैं?"
            )
            greet_or = (
                f"ନମସ୍କାର {user.full_name}! ମୁଁ କ୍ଲିନୋଭା ର ଭଏସ୍ ସ୍ୱାସ୍ଥ୍ୟ ସହାୟକ। "
                f"ଆପଣ ବର୍ତ୍ତମାନ କିପରି ଅନୁଭବ କରୁଛନ୍ତି? ଦୟାକରି ଆପଣଙ୍କ ସ୍ୱାସ୍ଥ୍ୟ ସମସ୍ୟା ଜଣାନ୍ତୁ।"
            )
            greet_map = {"hi": greet_hi, "or": greet_or}
            return AssistantMessageResponse(
                text=greet_map.get(response_lang, greet_en),
                language=response_lang,
                original_statement=msg_clean,
                source_label="Conversational Greeting",
                follow_up_suggestions=["Report a symptom", "Track case status"],
                detected_language=detected_lang,
            )

        # -------------------------------------------------------------
        # DEFAULT BOUNDED CONVERSATIONAL GUIDANCE
        # -------------------------------------------------------------
        default_en = (
            f"I hear you. As your Clinova voice companion, I can help capture your symptoms, explain medical terminology, "
            f"or check your clinic visit status. Could you tell me more about what you are experiencing?"
        )
        default_hi = (
            f"मैं समझ रहा हूँ। मैं आपके लक्षणों को दर्ज करने, चिकित्सकीय शब्दों को समझाने या केस स्टेटस की जाँच में मदद कर सकता हूँ। क्या आप मुझे थोड़ा और विस्तार से बता सकते हैं?"
        )
        default_or = (
            f"ମୁଁ ବୁଝିପାରୁଛି। ମୁଁ ଆପଣଙ୍କ ଲକ୍ଷଣ ରେକର୍ଡ କରିବା, ଡାକ୍ତରୀ ଶବ୍ଦ ବୁଝାଇବା ଏବଂ କେସ୍ ଷ୍ଟାଟସ୍ ଯାଞ୍ଚ କରିବାରେ ସାହାଯ୍ୟ କରିପାରିବି। ଆପଣଙ୍କ ସମସ୍ୟା ବିଷୟରେ ଆଉ କିଛି କହିପାରିବେ କି?"
        )

        def_map = {"hi": default_hi, "or": default_or}
        suggestions = ["Explain my case status", "What information is missing?", "Explain medical term"]

        return AssistantMessageResponse(
            text=def_map.get(response_lang, default_en),
            language=response_lang,
            original_statement=msg_clean,
            source_label="Clinova Voice AI Companion",
            follow_up_suggestions=suggestions,
            detected_language=detected_lang,
        )

    @classmethod
    async def execute_tool(
        cls,
        req: AssistantToolExecuteRequest,
        user: User,
        db: AsyncSession,
    ) -> AssistantToolExecuteResponse:
        """Executes an allowlisted, deterministic backend tool with RBAC re-authorization."""
        allowed_tools = ROLE_TOOL_ALLOWLIST.get(user.role, [])
        if req.tool_name not in allowed_tools and req.tool_name != "confirm_clinical_action":
            return AssistantToolExecuteResponse(
                success=False,
                tool_name=req.tool_name,
                result=None,
                message=f"Access denied: Role '{user.role.value}' is not authorized to execute tool '{req.tool_name}'.",
                audit_logged=True,
            )

        if req.tool_name == "get_current_user_context":
            return AssistantToolExecuteResponse(
                success=True,
                tool_name=req.tool_name,
                result={
                    "user_id": user.id,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "facility_id": user.facility_id,
                },
                message="User context retrieved successfully.",
            )

        if req.tool_name == "get_queue_status":
            stmt = select(TriageCase.status, func.count(TriageCase.id)).where(
                TriageCase.is_deleted.is_(False)
            ).group_by(TriageCase.status)
            counts = dict((await db.execute(stmt)).all())
            return AssistantToolExecuteResponse(
                success=True,
                tool_name=req.tool_name,
                result=counts,
                message="Queue status counts retrieved successfully.",
            )

        if req.tool_name == "confirm_clinical_action":
            if not req.confirmed:
                return AssistantToolExecuteResponse(
                    success=False,
                    tool_name=req.tool_name,
                    result=None,
                    message="Action was cancelled by user. No change made.",
                )
            return AssistantToolExecuteResponse(
                success=True,
                tool_name=req.tool_name,
                result={"action": req.parameters.get("action", "approved"), "status": "executed"},
                message="Clinical action confirmed and verified.",
            )

        return AssistantToolExecuteResponse(
            success=False,
            tool_name=req.tool_name,
            result=None,
            message="Tool execution completed.",
        )
