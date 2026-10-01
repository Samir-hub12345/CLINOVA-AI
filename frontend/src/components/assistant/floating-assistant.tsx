"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  Mic,
  MicOff,
  X,
  Volume2,
  Sparkles,
  Radio,
  Pause,
  FileText,
  ChevronDown,
  Minimize2,
  Copy,
  Check,
  Globe,
  AlertCircle,
  Send,
  RefreshCw,
} from "lucide-react";
import { assistantApi } from "@/lib/api";
import { ProposedAction } from "@/types";
import { useAuth } from "@/lib/auth";
import { ClinovaLogo } from "@/components/common/clinova-logo";
import {
  VoiceState,
  DEFAULT_VOICE_CONFIG,
  isValidVoiceTransition,
  generateTurnId,
  hasSentenceTerminalPunctuation,
} from "@/lib/voice-state-machine";
import {
  detectScriptFromText,
  isSpeechRecognitionSupported,
} from "@/lib/speech-recognition";

export interface LanguageOption {
  code: string;
  name: string;
  locale: string;
}

export const LANGUAGE_OPTIONS: LanguageOption[] = [
  { code: "auto", name: "Auto-Detect (Multilingual)", locale: "en-IN" },
  { code: "en", name: "English", locale: "en-IN" },
  { code: "hi", name: "हिन्दी (Hindi)", locale: "hi-IN" },
  { code: "or", name: "ଓଡ଼ିଆ (Odia)", locale: "or-IN" },
  { code: "bn", name: "বাংলা (Bengali)", locale: "bn-IN" },
  { code: "ta", name: "தமிழ் (Tamil)", locale: "ta-IN" },
  { code: "te", name: "తెలుగు (Telugu)", locale: "te-IN" },
];

export interface ConversationTurn {
  id: string;
  role: "user" | "assistant";
  text: string;
  language: string;
  timestamp: string;
  sourceLabel?: string;
  persona?: string;
}

export interface VoicePersona {
  id: string;
  name: string;
  roleTitle: string;
  description: string;
  pitch: number;
  rate: number;
  gender: "female" | "male";
  accent: string;
}

export const VOICE_PERSONAS: VoicePersona[] = [
  {
    id: "clara",
    name: "Dr. Clara",
    roleTitle: "Empathetic Clinical Guide",
    description: "Warm, gentle, reassuring tone tailored for patient comfort and active listening.",
    pitch: 1.05,
    rate: 0.95,
    gender: "female",
    accent: "en-IN / hi-IN",
  },
  {
    id: "marcus",
    name: "Dr. Marcus",
    roleTitle: "Medical Officer",
    description: "Clear, authoritative, objective clinical communicator for fast clinical triage.",
    pitch: 0.9,
    rate: 0.95,
    gender: "male",
    accent: "en-IN / hi-IN",
  },
  {
    id: "maya",
    name: "Maya",
    roleTitle: "Patient Navigator",
    description: "Friendly, supportive multilingual guide with natural regional cadence.",
    pitch: 1.0,
    rate: 0.95,
    gender: "female",
    accent: "en-IN / or-IN / hi-IN",
  },
  {
    id: "aarav",
    name: "Aarav",
    roleTitle: "Care Specialist",
    description: "Crisp, concise, encouraging modern healthcare companion.",
    pitch: 0.98,
    rate: 1.0,
    gender: "male",
    accent: "en-IN / hi-IN",
  },
];

// Synthesized Browser Chimes
function playChime(type: "connect" | "disconnect" | "interrupt") {
  try {
    const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    if (ctx.state === "suspended") ctx.resume();

    if (type === "connect") {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(523.25, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(783.99, ctx.currentTime + 0.16);
      gain.gain.setValueAtTime(0.1, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } else if (type === "disconnect") {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(783.99, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(523.25, ctx.currentTime + 0.16);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.3);
    } else if (type === "interrupt") {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(440, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(300, ctx.currentTime + 0.1);
      gain.gain.setValueAtTime(0.06, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.12);
    }
  } catch {}
}

export const FloatingAssistant: React.FC = () => {
  const { user } = useAuth();

  // Authoritative Voice State Machine
  const [voiceState, setVoiceStateInternal] = useState<VoiceState>("CLOSED");
  const voiceStateRef = useRef<VoiceState>("CLOSED");

  // Synchronized State Setter with Transition Guard
  const setVoiceState = useCallback((target: VoiceState) => {
    const current = voiceStateRef.current;
    if (isValidVoiceTransition(current, target)) {
      voiceStateRef.current = target;
      setVoiceStateInternal(target);
    } else {
      console.warn(`[VoiceStateMachine] Rejected transition: ${current} -> ${target}`);
    }
  }, []);

  // Modal display states
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [showTranscript, setShowTranscript] = useState<boolean>(false);
  const [showPersonaPicker, setShowPersonaPicker] = useState<boolean>(false);
  const [showLanguagePicker, setShowLanguagePicker] = useState<boolean>(false);

  // Settings & Personas
  const [selectedPersona, setSelectedPersona] = useState<VoicePersona>(VOICE_PERSONAS[0]);
  const [speechRate, setSpeechRate] = useState<number>(1.0);
  const [language, setLanguage] = useState<string>("en");
  const [selectedLanguageCode, setSelectedLanguageCode] = useState<string>("auto");
  const [isManualLanguageOverride, setIsManualLanguageOverride] = useState<boolean>(false);
  const [detectedLanguageLabel, setDetectedLanguageLabel] = useState<string>("Auto-Detect (Active)");
  const [recognitionLocale, setRecognitionLocale] = useState<string>("en-IN");

  // Error & Fallback
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [showTextFallback, setShowTextFallback] = useState<boolean>(false);
  const [fallbackTypedText, setFallbackTypedText] = useState<string>("");

  // Subtitles & Audio Reactive Level
  const [audioLevel, setAudioLevel] = useState<number>(0);
  const [interimSpeech, setInterimSpeech] = useState<string>("");
  const [humanSpeech, setHumanSpeech] = useState<string>("");
  const [assistantSpeech, setAssistantSpeech] = useState<string>("");

  // Multi-Turn Conversation History
  const [conversationHistory, setConversationHistory] = useState<ConversationTurn[]>([]);
  const [copiedTranscript, setCopiedTranscript] = useState<boolean>(false);
  const [pendingAction, setPendingAction] = useState<ProposedAction | null>(null);

  // Floating Trigger Position (when closed)
  const [position, setPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);

  // Internal Session & Audio Refs
  const sessionIdRef = useRef<string>(`session-${Date.now()}`);
  const isSubmittingRef = useRef<boolean>(false);
  const isMutedRef = useRef<boolean>(false);
  const selectedPersonaRef = useRef<VoicePersona>(VOICE_PERSONAS[0]);
  const pendingActionRef = useRef<ProposedAction | null>(null);

  // Speech Recognition & End-of-Turn Silence Debouncing Refs
  const recognitionRef = useRef<any>(null);
  const recognitionStartingRef = useRef<boolean>(false);
  const recognitionActiveRef = useRef<boolean>(false);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const accumulatedTranscriptRef = useRef<string>("");
  const interimTranscriptRef = useRef<string>("");
  const currentUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Web Audio Analyser Refs
  const audioStreamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);

  const transcriptEndRef = useRef<HTMLDivElement | null>(null);
  const dragStartRef = useRef<{ startX: number; startY: number; elemX: number; elemY: number; moved: boolean }>({
    startX: 0,
    startY: 0,
    elemX: 0,
    elemY: 0,
    moved: false,
  });

  // Sync refs with state
  useEffect(() => {
    isMutedRef.current = isMuted;
  }, [isMuted]);

  useEffect(() => {
    selectedPersonaRef.current = selectedPersona;
  }, [selectedPersona]);

  useEffect(() => {
    pendingActionRef.current = pendingAction;
  }, [pendingAction]);

  // Initialize Position & Event Listeners
  useEffect(() => {
    if (typeof window === "undefined") return;

    // Load initial position
    const pad = 24;
    const btnSize = 64;
    const defaultX = window.innerWidth - btnSize - pad;
    const defaultY = window.innerHeight - btnSize - pad;
    const storedPos = localStorage.getItem("clinova_assistant_pos");
    if (storedPos) {
      try {
        const parsed = JSON.parse(storedPos);
        setPosition({
          x: Math.max(16, Math.min(window.innerWidth - btnSize - 16, parsed.x)),
          y: Math.max(16, Math.min(window.innerHeight - btnSize - 16, parsed.y)),
        });
      } catch {
        setPosition({ x: defaultX, y: defaultY });
      }
    } else {
      setPosition({ x: defaultX, y: defaultY });
    }

    // Load saved persona
    const storedPersona = localStorage.getItem("clinova_voice_persona");
    if (storedPersona) {
      const p = VOICE_PERSONAS.find((x) => x.id === storedPersona);
      if (p) {
        setSelectedPersona(p);
        selectedPersonaRef.current = p;
      }
    }

    // Global event listener to open voice assistant from Dashboard or other entry points
    const handleOpenAssistant = () => {
      openVoiceSession();
    };
    window.addEventListener("clinova-open-voice-assistant", handleOpenAssistant);

    return () => {
      window.removeEventListener("clinova-open-voice-assistant", handleOpenAssistant);
    };
  }, []);

  // Keyboard Accessibility: Escape to close, Space to interrupt/mute
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      if (e.code === "Escape") {
        e.preventDefault();
        closeVoiceSession();
      } else if (e.code === "Space") {
        e.preventDefault();
        if (voiceStateRef.current === "ASSISTANT_SPEAKING") {
          interruptAssistant("keyboard");
        } else {
          toggleMute();
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  // Keep transcript view scrolled to bottom
  useEffect(() => {
    if (showTranscript && transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [conversationHistory, showTranscript]);

  // -------------------------------------------------------------
  // MICROPHONE & WEB AUDIO ANALYSER (Echo-Cancelled)
  // -------------------------------------------------------------
  const startAudioAnalyser = async (): Promise<boolean> => {
    try {
      if (typeof window === "undefined" || !navigator.mediaDevices?.getUserMedia) {
        setVoiceError("Microphone access is not supported in this browser environment.");
        return false;
      }

      setVoiceState("REQUESTING_MIC");

      // Request microphone with hardware acoustic echo cancellation and noise suppression
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      audioStreamRef.current = stream;

      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioCtx) {
        const ctx = new AudioCtx();
        if (ctx.state === "suspended") await ctx.resume();
        audioCtxRef.current = ctx;

        const analyser = ctx.createAnalyser();
        analyser.fftSize = 64;
        analyserRef.current = analyser;

        const source = ctx.createMediaStreamSource(stream);
        source.connect(analyser);

        const sampleAudio = () => {
          if (!analyserRef.current) return;
          const data = new Uint8Array(analyserRef.current.frequencyBinCount);
          analyserRef.current.getByteFrequencyData(data);

          let sum = 0;
          for (let i = 0; i < data.length; i++) sum += data[i];
          const avg = sum / data.length;
          const normalized = Math.min(1, avg / 120);
          setAudioLevel(normalized);

          animFrameRef.current = requestAnimationFrame(sampleAudio);
        };
        sampleAudio();
      }

      return true;
    } catch (err: any) {
      console.error("[VoiceAssistant] Microphone access error:", err);
      const isDenied = err.name === "NotAllowedError" || err.name === "PermissionDeniedError";
      setVoiceError(
        isDenied
          ? "Microphone access was denied. Please allow microphone permissions in your browser to converse."
          : "Could not access microphone hardware. Please verify your audio input settings."
      );
      setVoiceState("ERROR");
      setShowTextFallback(true);
      return false;
    }
  };

  const stopAudioAnalyser = () => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach((t) => t.stop());
      audioStreamRef.current = null;
    }
    if (audioCtxRef.current) {
      try {
        audioCtxRef.current.close();
      } catch {}
      audioCtxRef.current = null;
    }
    setAudioLevel(0);
  };

  // -------------------------------------------------------------
  // TEXT-TO-SPEECH SYNTHESIS & NATURAL TURN RE-ENTRY
  // -------------------------------------------------------------
  const speakVoice = useCallback(
    (text: string, onDone?: () => void) => {
      if (typeof window === "undefined" || !("speechSynthesis" in window)) {
        onDone?.();
        if (isOpen && !isMutedRef.current) {
          startListening();
        }
        return;
      }

      // Stop speech recognition while speaking to avoid capturing own TTS audio
      stopListening();

      window.speechSynthesis.cancel();
      setVoiceState("ASSISTANT_SPEAKING");
      setAssistantSpeech(text);

      const utterance = new SpeechSynthesisUtterance(text);
      currentUtteranceRef.current = utterance;
      utterance.rate = selectedPersonaRef.current.rate * speechRate;
      utterance.pitch = selectedPersonaRef.current.pitch;

      // Select regional voice matching current language
      const voices = window.speechSynthesis.getVoices();
      if (language === "hi") {
        utterance.lang = "hi-IN";
        const hiVoice = voices.find((v) => v.lang.startsWith("hi"));
        if (hiVoice) utterance.voice = hiVoice;
      } else if (language === "or") {
        utterance.lang = "or-IN";
        const orVoice = voices.find((v) => v.lang.startsWith("or") || v.lang.startsWith("hi"));
        if (orVoice) utterance.voice = orVoice;
      } else if (language === "bn") {
        utterance.lang = "bn-IN";
        const bnVoice = voices.find((v) => v.lang.startsWith("bn") || v.lang.startsWith("hi"));
        if (bnVoice) utterance.voice = bnVoice;
      } else if (language === "ta") {
        utterance.lang = "ta-IN";
        const taVoice = voices.find((v) => v.lang.startsWith("ta"));
        if (taVoice) utterance.voice = taVoice;
      } else if (language === "te") {
        utterance.lang = "te-IN";
        const teVoice = voices.find((v) => v.lang.startsWith("te"));
        if (teVoice) utterance.voice = teVoice;
      } else {
        utterance.lang = "en-IN";
        const enVoice = voices.find(
          (v) =>
            v.lang.startsWith("en-IN") ||
            v.lang.startsWith("en-GB") ||
            v.lang.startsWith("en-US")
        );
        if (enVoice) utterance.voice = enVoice;
      }

      utterance.onend = () => {
        currentUtteranceRef.current = null;
        onDone?.();
        // AUTOMATIC TURN-TAKING: Return directly to LISTENING without requiring a button press!
        if (isOpen && !isMutedRef.current && voiceStateRef.current !== "CLOSED") {
          startListening();
        } else {
          setVoiceState("IDLE");
        }
      };

      utterance.onerror = (e) => {
        console.warn("[TTS] Utterance error or cancelled:", e);
        currentUtteranceRef.current = null;
        onDone?.();
        if (isOpen && !isMutedRef.current && voiceStateRef.current !== "CLOSED") {
          startListening();
        } else {
          setVoiceState("IDLE");
        }
      };

      window.speechSynthesis.speak(utterance);
    },
    [isOpen, language, speechRate, setVoiceState]
  );

  // -------------------------------------------------------------
  // USER INTERRUPTION (BARGE-IN)
  // -------------------------------------------------------------
  const interruptAssistant = useCallback(
    (reason: string) => {
      if (voiceStateRef.current === "ASSISTANT_SPEAKING") {
        if (typeof window !== "undefined" && "speechSynthesis" in window) {
          window.speechSynthesis.cancel();
        }
        currentUtteranceRef.current = null;
        playChime("interrupt");
        setVoiceState("INTERRUPTED");
        setTimeout(() => {
          if (isOpen && !isMutedRef.current && voiceStateRef.current !== "CLOSED") {
            startListening();
          }
        }, 50);
      }
    },
    [isOpen, setVoiceState]
  );

  // -------------------------------------------------------------
  // AI CONVERSATION TURN PROCESSING (Idempotent & Context-Aware)
  // -------------------------------------------------------------
  const processSpokenInput = async (spokenText: string) => {
    const clean = spokenText.trim();
    if (!clean || isSubmittingRef.current || voiceStateRef.current === "CLOSED") return;

    isSubmittingRef.current = true;
    setVoiceError(null);
    setInterimSpeech("");
    setHumanSpeech(clean);
    setVoiceState("PROCESSING");

    const turnId = generateTurnId(sessionIdRef.current);
    const userTurn: ConversationTurn = {
      id: turnId,
      role: "user",
      text: clean,
      language,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setConversationHistory((prev) => [...prev, userTurn]);
    setVoiceState("ASSISTANT_THINKING");

    // Check voice confirmation of pending clinical action
    const lower = clean.toLowerCase();
    const currentAction = pendingActionRef.current;

    if (currentAction) {
      const isAffirmative =
        lower.includes("confirm") ||
        lower.includes("yes") ||
        lower.includes("proceed") ||
        lower.includes("approve") ||
        lower.includes("do it") ||
        lower.includes("हाँ") ||
        lower.includes("कर दो") ||
        lower.includes("ହଁ");

      const isNegative =
        lower.includes("cancel") ||
        lower.includes("no") ||
        lower.includes("stop") ||
        lower.includes("don't") ||
        lower.includes("नहीं") ||
        lower.includes("ନା");

      if (isAffirmative) {
        try {
          await assistantApi.executeTool({
            tool_name: currentAction.tool_name,
            parameters: currentAction.parameters,
            confirmed: true,
          });
          setPendingAction(null);
          const confirmReply = "Action confirmed and recorded successfully.";
          recordAssistantTurn(confirmReply, "Clinical Action Confirmed");
          speakVoice(confirmReply);
        } catch {
          setPendingAction(null);
          const failReply = "Could not execute action. Please try again.";
          recordAssistantTurn(failReply, "Error");
          speakVoice(failReply);
        } finally {
          isSubmittingRef.current = false;
        }
        return;
      } else if (isNegative) {
        setPendingAction(null);
        const cancelReply = "Action cancelled.";
        recordAssistantTurn(cancelReply, "Action Cancelled");
        speakVoice(cancelReply);
        isSubmittingRef.current = false;
        return;
      }
    }

    // Call Assistant Backend with multi-turn conversation memory
    try {
      const historyPayload = conversationHistory.slice(-8).map((t) => ({
        role: t.role,
        content: t.text,
      }));

      const res = await assistantApi.sendMessage({
        message: clean,
        language,
        voice_input: true,
        history: historyPayload,
        voice_persona: selectedPersonaRef.current.id,
      });

      if (res.data) {
        const replyText = res.data.text;
        const sourceLabel = res.data.source_label || "Clinova Voice AI";

        // Auto-switch language if detected
        if (!isManualLanguageOverride && res.data.detected_language && res.data.detected_language !== language) {
          setLanguage(res.data.detected_language);
          const names: Record<string, string> = {
            en: "English",
            hi: "Hindi",
            or: "Odia",
            bn: "Bengali",
            ta: "Tamil",
            te: "Telugu",
          };
          setDetectedLanguageLabel(`${names[res.data.detected_language] || res.data.detected_language.toUpperCase()} (Auto)`);
        }

        recordAssistantTurn(replyText, sourceLabel);

        if (res.data.requires_confirmation && res.data.proposed_action) {
          setPendingAction(res.data.proposed_action);
          const voicePrompt = `${replyText}. Please say "Confirm" to proceed, or "Cancel" to stop.`;
          speakVoice(voicePrompt);
        } else {
          speakVoice(replyText);
        }
      } else {
        const fallbackMsg = res.error || "I could not process that statement. Please say that again.";
        recordAssistantTurn(fallbackMsg, "Error");
        speakVoice(fallbackMsg);
        setVoiceError(fallbackMsg);
      }
    } catch (err) {
      console.error("[VoiceAssistant] SendMessage error:", err);
      const errMsg = "Connection problem. Please check your network and speak again.";
      recordAssistantTurn(errMsg, "Connection Notice");
      speakVoice(errMsg);
      setVoiceError(errMsg);
    } finally {
      isSubmittingRef.current = false;
    }
  };

  const recordAssistantTurn = (text: string, sourceLabel: string) => {
    const aiTurn: ConversationTurn = {
      id: generateTurnId(sessionIdRef.current),
      role: "assistant",
      text,
      language,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      sourceLabel,
      persona: selectedPersonaRef.current.name,
    };
    setConversationHistory((prev) => [...prev, aiTurn]);
  };

  // -------------------------------------------------------------
  // SPEECH RECOGNITION ENGINE (Race-Condition Free with End-of-Turn Pause Debouncing)
  // -------------------------------------------------------------
  const startListening = () => {
    if (
      typeof window === "undefined" ||
      isMutedRef.current ||
      isSubmittingRef.current ||
      voiceStateRef.current === "CLOSED" ||
      voiceStateRef.current === "ASSISTANT_SPEAKING" ||
      recognitionStartingRef.current ||
      recognitionActiveRef.current
    ) {
      return;
    }

    if (!isSpeechRecognitionSupported()) {
      setVoiceError("Speech recognition is not supported in this browser. Please use Chrome or Edge, or type your query.");
      setShowTextFallback(true);
      setVoiceState("IDLE");
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    try {
      recognitionStartingRef.current = true;

      // Abort any prior instance cleanly
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {}
      }

      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;

      // Determine Locale
      let currentLocale = recognitionLocale;
      if (!isManualLanguageOverride) {
        const map: Record<string, string> = {
          hi: "hi-IN",
          or: "or-IN",
          bn: "bn-IN",
          ta: "ta-IN",
          te: "te-IN",
          en: "en-IN",
        };
        currentLocale = map[language] || "en-IN";
      }
      recognition.lang = currentLocale;

      recognition.onstart = () => {
        recognitionStartingRef.current = false;
        recognitionActiveRef.current = true;
        setVoiceError(null);
        setVoiceState("LISTENING");
      };

      recognition.onresult = (event: any) => {
        // If assistant was speaking and user interrupts with speech
        if (voiceStateRef.current === "ASSISTANT_SPEAKING") {
          interruptAssistant("user_speech_barge_in");
        }

        let interim = "";
        let accumulatedFinal = "";

        for (let i = 0; i < event.results.length; ++i) {
          const item = event.results[i];
          if (item.isFinal) {
            accumulatedFinal += item[0].transcript + " ";
          } else {
            interim += item[0].transcript;
          }
        }
        accumulatedFinal = accumulatedFinal.trim();
        interim = interim.trim();

        accumulatedTranscriptRef.current = accumulatedFinal;
        interimTranscriptRef.current = interim;

        setHumanSpeech(accumulatedFinal);
        setInterimSpeech(interim);

        const currentStream = (accumulatedFinal + " " + interim).trim();

        if (currentStream) {
          // Transition to USER_SPEAKING
          if (voiceStateRef.current === "LISTENING") {
            setVoiceState("USER_SPEAKING");
          }

          // Real-time script detection if auto mode
          if (!isManualLanguageOverride) {
            const detected = detectScriptFromText(currentStream);
            if (detected.code !== "unknown" && detected.code !== language) {
              setLanguage(detected.code);
              setDetectedLanguageLabel(detected.label);
            }
          }

          // Natural Pause & End-of-Turn Debouncing
          if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

          const hasTerminalPunct = hasSentenceTerminalPunctuation(currentStream);
          const timeout = hasTerminalPunct
            ? DEFAULT_VOICE_CONFIG.punctuationSilenceTimeoutMs
            : DEFAULT_VOICE_CONFIG.silenceTimeoutMs;

          silenceTimerRef.current = setTimeout(() => {
            if (isSubmittingRef.current) return;
            const fullText = (accumulatedTranscriptRef.current || interimTranscriptRef.current).trim();
            if (fullText.length >= 2) {
              stopListening();
              processSpokenInput(fullText);
            }
          }, timeout);
        }
      };

      recognition.onerror = (e: any) => {
        recognitionStartingRef.current = false;
        if (e.error === "not-allowed" || e.error === "permission-denied") {
          setVoiceError("Microphone access was blocked. Please grant microphone permissions, or type below.");
          setShowTextFallback(true);
          recognitionActiveRef.current = false;
          setVoiceState("ERROR");
        } else if (e.error === "no-speech") {
          // Normal pause during listening; keep recognition open
        } else if (e.error === "network") {
          setVoiceError("Network issue during speech recognition.");
          recognitionActiveRef.current = false;
          setVoiceState("ERROR");
        } else if (e.error !== "aborted") {
          console.warn("[SpeechRecognition] error:", e.error);
        }
      };

      recognition.onend = () => {
        recognitionActiveRef.current = false;
        recognitionStartingRef.current = false;

        // If the user was speaking and Chrome prematurely fired onend due to silence:
        const pendingSpeech = (accumulatedTranscriptRef.current || interimTranscriptRef.current).trim();
        if (
          voiceStateRef.current === "USER_SPEAKING" &&
          pendingSpeech.length >= 2 &&
          !isSubmittingRef.current
        ) {
          // Commit turn on browser natural speech end
          if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
          processSpokenInput(pendingSpeech);
          return;
        }

        // Otherwise, if still in LISTENING state and modal is open, smoothly restart
        if (
          isOpen &&
          !isMutedRef.current &&
          voiceStateRef.current === "LISTENING" &&
          !isSubmittingRef.current
        ) {
          setTimeout(() => {
            if (isOpen && !isMutedRef.current && voiceStateRef.current === "LISTENING") {
              startListening();
            }
          }, 100);
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error("[SpeechRecognition] Start error:", err);
      recognitionStartingRef.current = false;
      recognitionActiveRef.current = false;
    }
  };

  const stopListening = () => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {}
      recognitionRef.current = null;
    }
    recognitionActiveRef.current = false;
    recognitionStartingRef.current = false;
  };

  // -------------------------------------------------------------
  // SESSION LIFECYCLE: Open, Close, Mute
  // -------------------------------------------------------------
  const openVoiceSession = async () => {
    setIsOpen(true);
    setIsMuted(false);
    isMutedRef.current = false;
    setVoiceError(null);
    setPendingAction(null);
    sessionIdRef.current = `session-${Date.now()}`;
    playChime("connect");

    const micGranted = await startAudioAnalyser();
    if (!micGranted) return;

    setVoiceState("CONNECTING");

    // Welcome Greeting
    const greetings: Record<string, string> = {
      en: `Hello, I'm ${selectedPersona.name}, your Clinova voice companion. How can I assist you with your health today?`,
      hi: `नमस्ते, मैं ${selectedPersona.name}, आपका क्लिनोवा वॉयस सहायक हूँ। आज मैं आपकी क्या सहायता कर सकता हूँ?`,
      or: `ନମସ୍କାର, ମୁଁ ${selectedPersona.name}, କ୍ଲିନୋଭା ର ଭଏସ୍ ସହାୟକ। ଆଜି ମୁଁ ଆପଣଙ୍କୁ କିପରି ସାହାଯ୍ୟ କରିପାରିବି?`,
    };
    const greeting = greetings[language] || greetings["en"];
    recordAssistantTurn(greeting, "Session Start");
    speakVoice(greeting);
  };

  const closeVoiceSession = () => {
    playChime("disconnect");
    stopAudioAnalyser();
    stopListening();

    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }

    currentUtteranceRef.current = null;
    isSubmittingRef.current = false;
    accumulatedTranscriptRef.current = "";
    interimTranscriptRef.current = "";

    setIsOpen(false);
    setVoiceState("CLOSED");
    setShowTranscript(false);
    setShowPersonaPicker(false);
    setShowLanguagePicker(false);
    setInterimSpeech("");
    setVoiceError(null);
  };

  const toggleMute = () => {
    if (isMuted) {
      setIsMuted(false);
      isMutedRef.current = false;
      startListening();
    } else {
      setIsMuted(true);
      isMutedRef.current = true;
      stopListening();
      if (voiceStateRef.current === "ASSISTANT_SPEAKING") {
        interruptAssistant("mute");
      }
      setVoiceState("IDLE");
    }
  };

  const selectLanguageMode = (code: string) => {
    setShowLanguagePicker(false);
    setSelectedLanguageCode(code);
    if (code === "auto") {
      setIsManualLanguageOverride(false);
      setLanguage("en");
      setRecognitionLocale("en-IN");
      setDetectedLanguageLabel("Auto-Detect (Active)");
    } else {
      const match = LANGUAGE_OPTIONS.find((l) => l.code === code);
      setIsManualLanguageOverride(true);
      setLanguage(code);
      const loc = match?.locale || `${code}-IN`;
      setRecognitionLocale(loc);
      setDetectedLanguageLabel(`${match?.name || code.toUpperCase()} (Manual)`);
    }

    if (recognitionActiveRef.current) {
      stopListening();
      setTimeout(() => {
        if (isOpen && !isMutedRef.current && voiceStateRef.current !== "ASSISTANT_SPEAKING") {
          startListening();
        }
      }, 150);
    }
  };

  const copyTranscript = () => {
    const text = conversationHistory
      .map((t) => `[${t.timestamp}] ${t.role === "user" ? "You" : t.persona || "Clinova"}: ${t.text}`)
      .join("\n\n");
    navigator.clipboard.writeText(text);
    setCopiedTranscript(true);
    setTimeout(() => setCopiedTranscript(false), 2000);
  };

  // Dragging for floating mini-orb when closed
  const handlePointerDown = (e: React.PointerEvent) => {
    if (e.button !== 0) return;
    dragStartRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      elemX: position.x,
      elemY: position.y,
      moved: false,
    };
    setIsDragging(true);
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isDragging) return;
    const dx = e.clientX - dragStartRef.current.startX;
    const dy = e.clientY - dragStartRef.current.startY;
    if (Math.hypot(dx, dy) > 6) dragStartRef.current.moved = true;
    const btnSize = 64;
    setPosition({
      x: Math.max(12, Math.min(window.innerWidth - btnSize - 12, dragStartRef.current.elemX + dx)),
      y: Math.max(12, Math.min(window.innerHeight - btnSize - 12, dragStartRef.current.elemY + dy)),
    });
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    if (!isDragging) return;
    setIsDragging(false);
    try {
      (e.target as HTMLElement).releasePointerCapture(e.pointerId);
    } catch {}
    if (typeof window !== "undefined") {
      localStorage.setItem("clinova_assistant_pos", JSON.stringify(position));
    }
    if (!dragStartRef.current.moved) {
      openVoiceSession();
    }
  };

  return (
    <>
      {/* ------------------------------------------------------------- */}
      {/* DEDICATED VOICE CONVERSATION OVERLAY                          */}
      {/* ------------------------------------------------------------- */}
      {isOpen && (
        <div
          className="fixed inset-0 z-[120] bg-slate-950/95 backdrop-blur-3xl text-white flex flex-col justify-between overflow-hidden animate-in fade-in duration-300 select-none"
          role="dialog"
          aria-modal="true"
          aria-label="Clinova Voice AI"
        >
          {/* Top Bar: Brand, State Status, Language, Persona, Close */}
          <div className="w-full max-w-4xl mx-auto px-6 py-5 flex items-center justify-between border-b border-slate-800/80">
            {/* Status & Brand */}
            <div className="flex items-center gap-3">
              <ClinovaLogo variant="full" size="sm" theme="dark" />
              <div className="hidden sm:block w-px h-5 bg-slate-800" />
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-teal-500/30">
                <span
                  className={`w-2.5 h-2.5 rounded-full ${
                    isMuted
                      ? "bg-slate-500"
                      : voiceState === "ASSISTANT_SPEAKING"
                      ? "bg-teal-400 animate-ping"
                      : voiceState === "PROCESSING" || voiceState === "ASSISTANT_THINKING"
                      ? "bg-amber-400 animate-pulse"
                      : voiceState === "USER_SPEAKING"
                      ? "bg-rose-400 animate-pulse"
                      : voiceState === "LISTENING"
                      ? "bg-emerald-400 animate-pulse"
                      : "bg-slate-400"
                  }`}
                />
                <span className="text-xs font-semibold tracking-wide text-teal-300">
                  {isMuted
                    ? "Microphone Muted"
                    : voiceState === "ASSISTANT_SPEAKING"
                    ? "Clinova Speaking..."
                    : voiceState === "PROCESSING" || voiceState === "ASSISTANT_THINKING"
                    ? "Thinking..."
                    : voiceState === "USER_SPEAKING"
                    ? "Hearing you..."
                    : voiceState === "LISTENING"
                    ? "Listening to you..."
                    : voiceState === "INTERRUPTED"
                    ? "Interrupted"
                    : "Ready"}
                </span>
              </div>

              {/* Language Selector */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowLanguagePicker(!showLanguagePicker)}
                  className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 border border-slate-700 hover:border-slate-600 text-xs font-mono text-slate-200 transition-all shadow-xs cursor-pointer"
                  title="Toggle Language Recognition Mode"
                >
                  <Globe className="w-3.5 h-3.5 text-teal-400" />
                  <span>{detectedLanguageLabel}</span>
                  <ChevronDown className="w-3 h-3 text-slate-400" />
                </button>

                {showLanguagePicker && (
                  <div className="absolute left-0 mt-2 w-64 bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95">
                    <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 px-3 py-1.5">
                      Language Mode & Recognition
                    </div>
                    {LANGUAGE_OPTIONS.map((opt) => (
                      <button
                        key={opt.code}
                        type="button"
                        onClick={() => selectLanguageMode(opt.code)}
                        className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-colors cursor-pointer ${
                          selectedLanguageCode === opt.code
                            ? "bg-teal-500/20 text-teal-200 border border-teal-500/30 font-semibold"
                            : "hover:bg-slate-800 text-slate-300"
                        }`}
                      >
                        <span>{opt.name}</span>
                        <span className="text-[10px] font-mono text-slate-500">{opt.locale}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Persona Selector Pill */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowPersonaPicker(!showPersonaPicker)}
                className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-slate-200 transition-all shadow-xs"
              >
                <Sparkles className="w-3.5 h-3.5 text-teal-400" />
                <span>{selectedPersona.name}</span>
                <ChevronDown className="w-3 h-3 text-slate-400" />
              </button>

              {showPersonaPicker && (
                <div className="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95">
                  <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 px-3 py-1.5">
                    Select Voice Persona
                  </div>
                  {VOICE_PERSONAS.map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => {
                        setSelectedPersona(p);
                        selectedPersonaRef.current = p;
                        localStorage.setItem("clinova_voice_persona", p.id);
                        setShowPersonaPicker(false);
                        speakVoice(`Voice changed to ${p.name}.`);
                      }}
                      className={`w-full text-left p-2.5 rounded-xl transition-all flex items-start gap-2.5 ${
                        selectedPersona.id === p.id
                          ? "bg-teal-500/20 text-teal-200 border border-teal-500/40"
                          : "hover:bg-slate-800 text-slate-300"
                      }`}
                    >
                      <div className="mt-0.5">
                        <Radio className="w-4 h-4 text-teal-400" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-white">{p.name}</div>
                        <div className="text-[11px] text-teal-400">{p.roleTitle}</div>
                        <div className="text-[10px] text-slate-400 line-clamp-1">{p.description}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Dedicated Close Control */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={closeVoiceSession}
                title="Close Voice Assistant (Esc)"
                aria-label="Close voice assistant"
                className="p-2 rounded-full hover:bg-rose-950/50 text-slate-400 hover:text-rose-400 transition-colors cursor-pointer"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Center: Reactive Fluid Orb & Subtitles */}
          <div className="flex-1 flex flex-col items-center justify-center px-6 relative max-w-xl mx-auto w-full">
            <div
              onClick={() => {
                if (voiceState === "ASSISTANT_SPEAKING") {
                  interruptAssistant("tap_orb");
                }
              }}
              className="relative cursor-pointer group flex flex-col items-center"
              title={voiceState === "ASSISTANT_SPEAKING" ? "Tap orb to interrupt assistant" : "Living Voice Orb"}
            >
              {/* Outer Ambient Glow */}
              <div
                style={{
                  transform: `scale(${
                    voiceState === "ASSISTANT_SPEAKING"
                      ? 1.25 + audioLevel * 0.4
                      : voiceState === "USER_SPEAKING"
                      ? 1.2 + audioLevel * 0.5
                      : voiceState === "LISTENING"
                      ? 1.08 + audioLevel * 0.3
                      : 1.0
                  })`,
                }}
                className={`absolute inset-0 rounded-full blur-3xl transition-transform duration-100 ${
                  isMuted
                    ? "bg-slate-700/20"
                    : voiceState === "ASSISTANT_SPEAKING"
                    ? "bg-gradient-to-tr from-teal-500/40 via-cyan-500/30 to-indigo-500/40"
                    : voiceState === "PROCESSING" || voiceState === "ASSISTANT_THINKING"
                    ? "bg-amber-500/30"
                    : voiceState === "USER_SPEAKING"
                    ? "bg-gradient-to-tr from-rose-500/40 via-pink-500/30 to-teal-500/40"
                    : "bg-gradient-to-tr from-teal-500/30 via-emerald-500/20 to-cyan-500/30"
                }`}
              />

              {/* Main Living Orb */}
              <div
                style={{
                  transform: `scale(${
                    voiceState === "ASSISTANT_SPEAKING"
                      ? 1 + audioLevel * 0.25
                      : voiceState === "USER_SPEAKING"
                      ? 1 + audioLevel * 0.35
                      : 1
                  })`,
                }}
                className={`relative w-48 h-48 sm:w-60 sm:h-60 rounded-full flex items-center justify-center transition-all duration-150 shadow-2xl ${
                  isMuted
                    ? "bg-slate-800 ring-4 ring-slate-700 shadow-slate-900"
                    : voiceState === "ASSISTANT_SPEAKING"
                    ? "bg-gradient-to-tr from-teal-500 via-cyan-400 to-indigo-600 ring-8 ring-teal-400/30 shadow-teal-500/50"
                    : voiceState === "PROCESSING" || voiceState === "ASSISTANT_THINKING"
                    ? "bg-gradient-to-tr from-amber-500 via-orange-400 to-yellow-600 ring-8 ring-amber-400/30 shadow-amber-500/50 animate-spin"
                    : voiceState === "USER_SPEAKING"
                    ? "bg-gradient-to-tr from-rose-600 via-pink-500 to-amber-500 ring-8 ring-rose-400/30 shadow-rose-500/50 animate-pulse"
                    : "bg-gradient-to-tr from-teal-600 via-cyan-500 to-emerald-500 ring-8 ring-teal-400/30 shadow-teal-600/50 animate-pulse"
                }`}
              >
                {/* Dynamic Waveform Bars Inside Orb */}
                <div className="absolute inset-4 rounded-full bg-slate-950/60 backdrop-blur-md flex items-center justify-center overflow-hidden">
                  <div className="flex items-center gap-1.5 h-16">
                    {[30, 60, 95, 45, 80, 50, 90, 40].map((h, i) => (
                      <span
                        key={i}
                        style={{
                          height:
                            voiceState === "ASSISTANT_SPEAKING"
                              ? `${Math.max(20, (h * Math.sin((i + 1) * 1.2)) % 100)}%`
                              : voiceState === "USER_SPEAKING" || voiceState === "LISTENING"
                              ? `${Math.max(15, h * (0.2 + audioLevel * 0.8))}%`
                              : "15%",
                        }}
                        className={`w-1.5 rounded-full transition-all duration-100 ${
                          voiceState === "ASSISTANT_SPEAKING"
                            ? "bg-teal-300 animate-pulse"
                            : voiceState === "USER_SPEAKING"
                            ? "bg-rose-400 animate-pulse"
                            : voiceState === "LISTENING"
                            ? "bg-emerald-400"
                            : "bg-slate-500"
                        }`}
                      />
                    ))}
                  </div>
                </div>

                {/* State Icon */}
                {isMuted ? (
                  <MicOff className="w-10 h-10 text-slate-400 relative z-10" />
                ) : voiceState === "ASSISTANT_SPEAKING" ? (
                  <Volume2 className="w-10 h-10 text-teal-100 relative z-10" />
                ) : voiceState === "PROCESSING" || voiceState === "ASSISTANT_THINKING" ? (
                  <Sparkles className="w-10 h-10 text-amber-200 relative z-10 animate-bounce" />
                ) : (
                  <Mic className="w-10 h-10 text-white relative z-10" />
                )}
              </div>

              {/* Tap to Interrupt Indicator */}
              {voiceState === "ASSISTANT_SPEAKING" && (
                <div className="mt-4 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-700 text-[11px] text-teal-300 tracking-wide font-medium flex items-center gap-1.5 animate-pulse">
                  <Pause className="w-3 h-3" />
                  Tap orb or start speaking to interrupt
                </div>
              )}
            </div>

            {/* Subtitles & Streaming Live Text */}
            <div className="mt-6 w-full max-w-lg min-h-[90px] max-h-[140px] overflow-y-auto text-center px-4">
              {/* Assistant Speech */}
              {voiceState === "ASSISTANT_SPEAKING" && assistantSpeech && (
                <p className="text-teal-200 text-sm sm:text-base leading-relaxed font-medium animate-in fade-in">
                  &ldquo;{assistantSpeech}&rdquo;
                </p>
              )}

              {/* Human Spoken Text */}
              {voiceState !== "ASSISTANT_SPEAKING" && (humanSpeech || interimSpeech) && (
                <div className="space-y-1 animate-in fade-in">
                  <span className="text-slate-400 text-[11px] block font-semibold uppercase tracking-wider">
                    {voiceState === "USER_SPEAKING" ? "Listening..." : "Recognized Speech:"}
                  </span>
                  <p className="text-slate-100 text-sm sm:text-base leading-relaxed">
                    <span>&ldquo;{humanSpeech}</span>
                    {interimSpeech && (
                      <span className="text-teal-300 italic font-normal">
                        {" "}{interimSpeech}
                        <span className="inline-block w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse ml-1 align-middle" />
                      </span>
                    )}
                    <span>&rdquo;</span>
                  </p>
                  <div className="text-[11px] text-teal-400 font-mono">
                    {detectedLanguageLabel} • Locale: {recognitionLocale}
                  </div>
                </div>
              )}

              {/* Prompt when Listening and idle */}
              {voiceState === "LISTENING" && !humanSpeech && !interimSpeech && (
                <div className="space-y-1">
                  <p className="text-slate-300 text-sm font-medium">
                    Listening... describe your symptoms or ask a clinical question
                  </p>
                  <p className="text-slate-500 text-xs font-mono">
                    Speak naturally in English, Hindi, Odia, Bengali, Tamil, or Telugu
                  </p>
                </div>
              )}

              {/* Thinking State */}
              {(voiceState === "PROCESSING" || voiceState === "ASSISTANT_THINKING") && (
                <div className="space-y-2 animate-pulse">
                  <p className="text-amber-300 text-sm font-medium">
                    Clinova AI is thinking... formulating response
                  </p>
                  {humanSpeech && (
                    <div className="text-[11px] text-slate-400 font-mono truncate">
                      Input: &ldquo;{humanSpeech}&rdquo;
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Error Notice & Retry */}
            {voiceError && (
              <div className="mt-4 p-3.5 bg-rose-950/80 border border-rose-500/50 rounded-2xl max-w-md text-center text-xs text-rose-200 space-y-2 animate-in fade-in">
                <div className="flex items-center justify-center gap-1.5 text-rose-300 font-bold uppercase tracking-wider text-[11px]">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>Microphone / Speech Notice</span>
                </div>
                <div>{voiceError}</div>
                <div className="flex items-center justify-center gap-2 pt-1">
                  <button
                    type="button"
                    onClick={() => {
                      setVoiceError(null);
                      startListening();
                    }}
                    className="px-3 py-1 bg-rose-800 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold cursor-pointer flex items-center gap-1"
                  >
                    <RefreshCw className="w-3 h-3" />
                    <span>Retry Microphone</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowTextFallback(true)}
                    className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold cursor-pointer"
                  >
                    Type Instead
                  </button>
                </div>
              </div>
            )}

            {/* Text Input Fallback */}
            {showTextFallback && (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (fallbackTypedText.trim() && !isSubmittingRef.current) {
                    processSpokenInput(fallbackTypedText.trim());
                    setFallbackTypedText("");
                  }
                }}
                className="mt-4 w-full max-w-md flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-2xl p-1.5"
              >
                <input
                  type="text"
                  value={fallbackTypedText}
                  onChange={(e) => setFallbackTypedText(e.target.value)}
                  placeholder="Type a clinical query..."
                  className="flex-1 bg-transparent px-3 py-1.5 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={!fallbackTypedText.trim() || isSubmittingRef.current}
                  className="px-4 py-1.5 bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl transition-colors cursor-pointer flex items-center gap-1"
                >
                  <Send className="w-3 h-3" />
                  <span>Send</span>
                </button>
              </form>
            )}

            {/* Pending Clinical Action Gate */}
            {pendingAction && (
              <div className="mt-4 p-3 bg-amber-950/80 border border-amber-500/50 rounded-2xl max-w-md text-center text-xs text-amber-200 space-y-1">
                <div className="font-bold text-amber-100 uppercase tracking-wider text-[11px]">
                  Requires Voice Confirmation
                </div>
                <div>{pendingAction.description}</div>
                <div className="font-semibold text-amber-300 text-[11px] pt-1">
                  Say &ldquo;Confirm&rdquo; to execute, or &ldquo;Cancel&rdquo; to discard.
                </div>
              </div>
            )}
          </div>

          {/* Bottom Dock Control Bar */}
          <div className="w-full max-w-xl mx-auto px-6 py-6 flex items-center justify-between border-t border-slate-800/80">
            {/* Transcript Drawer Toggle */}
            <button
              type="button"
              onClick={() => setShowTranscript(true)}
              aria-label="View conversation transcript"
              className="p-3.5 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white transition-all shadow-md relative cursor-pointer"
            >
              <FileText className="w-5 h-5" />
              {conversationHistory.length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-teal-500 text-[10px] font-bold text-white flex items-center justify-center">
                  {conversationHistory.length}
                </span>
              )}
            </button>

            {/* Voice Speed Toggle */}
            <button
              type="button"
              onClick={() => {
                const nextRate = speechRate === 1.0 ? 1.2 : speechRate === 1.2 ? 0.8 : 1.0;
                setSpeechRate(nextRate);
              }}
              title={`Speech Rate: ${speechRate}x`}
              className="px-3.5 py-2 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-mono font-bold text-slate-300 hover:text-white transition-all shadow-md cursor-pointer"
            >
              {speechRate}x
            </button>

            {/* Mute / Unmute Button */}
            <button
              type="button"
              onClick={toggleMute}
              aria-label={isMuted ? "Unmute microphone" : "Mute microphone"}
              className={`p-4 rounded-full transition-all shadow-xl cursor-pointer ${
                isMuted
                  ? "bg-rose-600 hover:bg-rose-500 text-white ring-4 ring-rose-400/40"
                  : "bg-slate-800 hover:bg-slate-700 text-white border border-slate-600"
              }`}
            >
              {isMuted ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
            </button>

            {/* Manual Interrupt Button */}
            <button
              type="button"
              onClick={() => interruptAssistant("bottom_dock")}
              title="Interrupt assistant speaking"
              disabled={voiceState !== "ASSISTANT_SPEAKING"}
              className={`p-3.5 rounded-full border transition-all shadow-md ${
                voiceState === "ASSISTANT_SPEAKING"
                  ? "bg-teal-600 hover:bg-teal-500 border-teal-400 text-white animate-pulse cursor-pointer"
                  : "bg-slate-900 border-slate-800 text-slate-600 cursor-not-allowed"
              }`}
            >
              <Pause className="w-5 h-5" />
            </button>

            {/* Dedicated End / Close Button */}
            <button
              type="button"
              onClick={closeVoiceSession}
              aria-label="Close voice assistant"
              title="Close Voice Assistant"
              className="p-3.5 rounded-full bg-rose-600 hover:bg-rose-500 text-white shadow-lg hover:shadow-rose-600/40 transition-all cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Transcript Slide-over Drawer */}
          {showTranscript && (
            <div
              className="absolute inset-y-0 right-0 w-full sm:w-[420px] bg-slate-900/98 border-l border-slate-700 shadow-2xl flex flex-col z-50 animate-in slide-in-from-right duration-200"
              role="dialog"
              aria-label="Conversation Transcript"
            >
              <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-teal-400" />
                  <span className="text-sm font-bold text-white">Conversation Transcript</span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={copyTranscript}
                    className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors cursor-pointer"
                    title="Copy full transcript"
                  >
                    {copiedTranscript ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowTranscript(false)}
                    className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors cursor-pointer"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {conversationHistory.length === 0 ? (
                  <div className="text-center text-slate-400 text-xs py-10 italic">
                    Spoken conversation transcript will appear here.
                  </div>
                ) : (
                  conversationHistory.map((t) => (
                    <div
                      key={t.id}
                      className={`flex flex-col gap-1 ${
                        t.role === "user" ? "items-end" : "items-start"
                      }`}
                    >
                      <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                        {t.role !== "user" && <ClinovaLogo variant="mark" size="xs" />}
                        <span className="font-semibold text-slate-300">
                          {t.role === "user" ? "You" : t.persona || "Clinova"}
                        </span>
                        <span>•</span>
                        <span>{t.timestamp}</span>
                        {t.sourceLabel && (
                          <span className="px-1.5 py-0.2 rounded bg-slate-800 text-teal-300 font-mono text-[9px]">
                            {t.sourceLabel}
                          </span>
                        )}
                      </div>
                      <div
                        className={`p-3 rounded-2xl text-xs leading-relaxed max-w-[85%] ${
                          t.role === "user"
                            ? "bg-teal-600 text-white rounded-br-none"
                            : "bg-slate-800/90 text-slate-200 border border-slate-700 rounded-bl-none"
                        }`}
                      >
                        {t.text}
                      </div>
                    </div>
                  ))
                )}
                <div ref={transcriptEndRef} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* FLOATING MINI-ORB BUTTON (When modal is closed)               */}
      {/* ------------------------------------------------------------- */}
      {!isOpen && (
        <div
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerCancel={() => setIsDragging(false)}
          style={{
            left: `${position.x}px`,
            top: `${position.y}px`,
            touchAction: "none",
          }}
          className={`fixed z-[95] select-none ${
            isDragging ? "cursor-grabbing opacity-90 scale-105" : "cursor-grab"
          } transition-transform duration-75`}
        >
          <button
            type="button"
            aria-label="Clinova Voice AI"
            title="Clinova Voice AI (Click to converse hands-free)"
            className="relative group flex items-center justify-center w-16 h-16 rounded-full bg-white text-slate-800 ring-2 ring-teal-500/30 hover:ring-teal-500 shadow-xl hover:shadow-teal-500/20 hover:scale-105 active:scale-95 transition-all cursor-pointer"
          >
            <div className="relative flex items-center justify-center p-1">
              <ClinovaLogo variant="mark" size="md" />
              <span className="absolute -bottom-1 -right-1 p-1 rounded-full bg-teal-600 text-white shadow-xs">
                <Mic className="w-2.5 h-2.5" />
              </span>
            </div>
          </button>
        </div>
      )}
    </>
  );
};
