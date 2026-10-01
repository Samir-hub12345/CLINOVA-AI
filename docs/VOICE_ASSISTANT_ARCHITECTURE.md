# Clinova AI — Patient Voice Assistant Architecture & Specification

## 1. Overview
The Clinova AI Patient Voice Assistant provides a natural, human-friendly, hands-free conversational voice interface for patient symptom intake and triage support across Indian languages (English, Hindi, Odia, Bengali, Tamil, Telugu).

```
IDLE ──► OPEN VOICE ASSISTANT ──► DEDICATED OVERLAY
                                        │
        ┌───────────────────────────────┴───────────────────────────────┐
        ▼                                                               ▼
   CONNECTING                                                        LISTENING
        │                                                               ▲
        ▼                                                               │
  USER SPEAKS ──► REAL-TIME TRANSCRIPTION ──► END-OF-TURN ──► AI RESPONSE ──► TTS SPEECH
                                                                                │
                                              (Barge-in / Tap to Interrupt) ────┘
```

---

## 2. Voice State Machine [CURRENT]

The state machine is implemented as an authoritative single source of truth in `frontend/src/lib/voice-state-machine.ts` with strict transition guards:

| State | Status Description | Next Allowed States |
|---|---|---|
| `CLOSED` | Modal closed, resources released | `REQUESTING_MIC`, `CONNECTING`, `IDLE`, `ERROR` |
| `IDLE` | Microphone muted or standby | `REQUESTING_MIC`, `CONNECTING`, `LISTENING`, `CLOSED`, `ERROR` |
| `REQUESTING_MIC` | Requesting browser audio permission | `CONNECTING`, `LISTENING`, `ERROR`, `CLOSED` |
| `CONNECTING` | Audio analyser initialized, playing greeting | `LISTENING`, `ASSISTANT_SPEAKING`, `ERROR`, `CLOSED` |
| `LISTENING` | Listening for patient speech | `USER_SPEAKING`, `PROCESSING`, `ASSISTANT_THINKING`, `INTERRUPTED`, `ERROR`, `CLOSED`, `IDLE` |
| `USER_SPEAKING` | Capturing streaming interim speech | `PROCESSING`, `ASSISTANT_THINKING`, `LISTENING`, `INTERRUPTED`, `ERROR`, `CLOSED` |
| `PROCESSING` | Utterance frozen, turn ID attached | `ASSISTANT_THINKING`, `ASSISTANT_SPEAKING`, `LISTENING`, `ERROR`, `CLOSED` |
| `ASSISTANT_THINKING` | AI formulating clinical guidance | `ASSISTANT_SPEAKING`, `LISTENING`, `ERROR`, `CLOSED` |
| `ASSISTANT_SPEAKING` | Synthesizing & speaking speech response | `LISTENING`, `USER_SPEAKING`, `INTERRUPTED`, `ERROR`, `CLOSED`, `IDLE` |
| `INTERRUPTED` | Assistant speech halted mid-sentence | `LISTENING`, `USER_SPEAKING`, `PROCESSING`, `ERROR`, `CLOSED` |
| `ERROR` | Microphone denied, network failure, or STT error | `REQUESTING_MIC`, `CONNECTING`, `LISTENING`, `IDLE`, `CLOSED` |

---

## 3. Speech-to-Text & End-of-Turn Detection [CURRENT]

- **Speech Recognition Engine**: Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) with native continuous streaming and interim results.
- **End-of-Turn Heuristics**:
  - Natural speech pause timeout: `1100ms` of silence after speech detection.
  - Sentence boundary pause timeout: `750ms` when terminal punctuation (`.`, `?`, `!`, `।`, `॥`) is recognized.
  - Minimum speech duration check: filters clicks/coughs (`< 2 chars`).
- **Race Condition Immunity**:
  - Browser silence `onend` events while in `USER_SPEAKING` automatically finalize and submit the recognized utterance rather than restarting recognition and dropping the user's words.
  - SpeechRecognition start/stop calls are protected with state locks (`recognitionStartingRef`, `recognitionActiveRef`) preventing `InvalidStateError`.

---

## 4. Text-to-Speech & Multi-Turn Conversation Loop [CURRENT]

- **TTS Engine**: In-browser `SpeechSynthesis` with persona-specific pitch (0.9–1.05) and rate (0.95–1.0).
- **Voice Personas**:
  - `Dr. Clara`: Warm, gentle, reassuring clinical guide.
  - `Dr. Marcus`: Clear, objective clinical triage communicator.
  - `Maya`: Friendly multilingual patient navigator.
  - `Aarav`: Crisp, modern healthcare companion.
- **Hands-Free Turn-Taking**:
  - Upon completion of `SpeechSynthesisUtterance.onend`, the assistant automatically transitions back to `LISTENING` and re-engages speech recognition.
  - Patients do not need to click "Send", "Talk", or "Listen" between conversational turns.

---

## 5. Interruption (Barge-In) [CURRENT]

- While `ASSISTANT_SPEAKING`:
  - **Speech Barge-in**: User speech detected by `SpeechRecognition` immediately halts speech synthesis via `window.speechSynthesis.cancel()`.
  - **Touch/Click Barge-in**: Tapping the living orb or clicking the pause button cancels playback.
  - **Keyboard Barge-in**: Pressing `Space` cancels playback.
  - **Acoustic Self-Interruption Prevention**: Raw microphone RMS energy thresholds were removed from the interruption loop to prevent the computer's speakers from self-interrupting the assistant's voice. Hardware acoustic echo cancellation (`echoCancellation: true`) is enforced.

---

## 6. Language & Script Support [CURRENT]

- Supported Indic and English Languages:
  - English (`en-IN`)
  - Hindi (`hi-IN` — Devanagari script range `\u0900-\u097F`)
  - Odia (`or-IN` — Odia script range `\u0B00-\u0B7F`)
  - Bengali (`bn-IN` — Bengali script range `\u0980-\u09FF`)
  - Tamil (`ta-IN` — Tamil script range `\u0B80-\u0BFF`)
  - Telugu (`te-IN` — Telugu script range `\u0C00-\u0C7F`)
- Script detection dynamically determines the language of spoken utterances in `auto` mode and updates the recognition locale.

---

## 7. Medical Safety & Human-in-the-Loop [CURRENT]

- **Non-Diagnostic Educational Boundaries**: Explicitly refuses to issue autonomous personal medical diagnoses or prescribe medications (`AssistantService.process_message`).
- **Emergency Red Flag Escalation**: Recognizes acute emergency terms ("chest pain", "cannot breathe", "severe bleeding", "छाती में दर्द", "chhati me dard") and outputs immediate emergency escalation notices.
- **Consequential Actions**: Actions affecting patient records or triage cases require explicit verbal confirmation ("Confirm" / "Cancel") before execution.

---

## 8. Feature Status Matrix

| Feature | Status | Notes |
|---|---|---|
| Authoritative Finite State Machine | **CURRENT** | Enforced via `frontend/src/lib/voice-state-machine.ts` |
| Dedicated Voice Modal | **CURRENT** | Voice-first overlay; persistent navbar ON/OFF toggle removed |
| Hands-Free Auto Turn-Taking | **CURRENT** | Automatic transition to `LISTENING` upon TTS completion |
| End-of-Turn Pause Debouncing | **CURRENT** | 1100ms conversational pause; 750ms sentence boundary |
| Speech Interruption (Barge-in) | **CURRENT** | Speech recognition, touch-orb, and keyboard barge-in |
| Acoustic Echo Cancellation | **CURRENT** | Enforced via `getUserMedia` constraints |
| Multi-turn Context Memory | **CURRENT** | Recent turns preserved and passed in AI payload |
| Indic Multilingual Detection | **CURRENT** | Unicode script ranges for Hindi, Odia, Bengali, Tamil, Telugu |
| Prompt Injection Defense | **CURRENT** | Strict pattern matching and safety refusal |
| Emergency Red Flag Triage | **CURRENT** | Urgent clinical escalation advisory |
| WebSocket Full-Duplex Audio | **PLANNED** | Server-side bidirectional WebSocket streaming |
| Offline On-Device Neural STT (Whisper WASM)| **PLANNED** | Client-side fallback when browser Web Speech API is absent |
| Custom Neural TTS Voice Cloning | **NOT IMPLEMENTED** | Standard browser regional synthesis voices used |

---

## 9. Test Verification Results

- `test-voice-state-machine.js`: **6 / 6 passed (100%)**
- `test-speech-recognition.js`: **13 / 13 passed (100%)**
- `test-voice-conversation-e2e.js`: **8 / 8 passed (100%)**
- Backend `test_assistant.py` & `test_speech_service.py`: **8 / 8 passed (100%)**
- Next.js Production Build (`npm run build`): **0 errors, all 23 static pages generated successfully**.
