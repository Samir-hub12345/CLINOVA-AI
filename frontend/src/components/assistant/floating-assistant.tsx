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
} from "lucide-react";
import { assistantApi } from "@/lib/api";
import { ProposedAction } from "@/types";
import { useAuth } from "@/lib/auth";
import { ClinovaLogo } from "@/components/common/clinova-logo";

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

// -------------------------------------------------------------
// HELPER: Detect Script Ranges for Real-Time Multilingual Speech
// -------------------------------------------------------------
function anyCharInRange(str: string, minCode: number, maxCode: number): boolean {
  for (let i = 0; i < str.length; i++) {
    const code = str.charCodeAt(i);
    if (code >= minCode && code <= maxCode) return true;
  }
  return false;
}

// -------------------------------------------------------------
// DATA TYPES
// -------------------------------------------------------------
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

// -------------------------------------------------------------
// WEB AUDIO HARMONIC CHIMES (Synthesized in-browser, 0 external mp3)
// -------------------------------------------------------------
function playChime(type: "connect" | "disconnect" | "interrupt") {
  try {
    const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    if (ctx.state === "suspended") ctx.resume();

    if (type === "connect") {
      // Ascending C5 -> G5 warm harmonic chime (Iconic connected sound)
      const osc1 = ctx.createOscillator();
      const gain = ctx.createGain();
      osc1.type = "sine";
      osc1.frequency.setValueAtTime(523.25, ctx.currentTime);
      osc1.frequency.exponentialRampToValueAtTime(783.99, ctx.currentTime + 0.16);
      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.38);
      osc1.connect(gain);
      gain.connect(ctx.destination);
      osc1.start();
      osc1.stop(ctx.currentTime + 0.4);
    } else if (type === "disconnect") {
      // Descending G5 -> C5 gentle chime
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(783.99, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(523.25, ctx.currentTime + 0.18);
      gain.gain.setValueAtTime(0.09, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } else if (type === "interrupt") {
      // Soft tactile blip on interruption
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(480, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(320, ctx.currentTime + 0.1);
      gain.gain.setValueAtTime(0.07, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.12);
    }
  } catch {}
}

// -------------------------------------------------------------
// MAIN COMPONENT: ChatGPT-style Voice Assistant
// -------------------------------------------------------------
export const FloatingAssistant: React.FC = () => {
  const { user } = useAuth();

  // Assistant enabled state & voice session active state
  const [enabled, setEnabled] = useState<boolean>(true);
  const [voiceActive, setVoiceActive] = useState<boolean>(false);
  const [voiceState, setVoiceState] = useState<"idle" | "listening" | "thinking" | "speaking">("idle");
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [showTranscript, setShowTranscript] = useState<boolean>(false);
  const [showPersonaPicker, setShowPersonaPicker] = useState<boolean>(false);

  // Persona & Speech Settings
  const [selectedPersona, setSelectedPersona] = useState<VoicePersona>(VOICE_PERSONAS[0]);
  const [speechRate, setSpeechRate] = useState<number>(1.0);
  const [language, setLanguage] = useState<string>("en");

  // Language & Metadata State (Workstream B / Section 7.5, 8.2, 8.4)
  const [selectedLanguageCode, setSelectedLanguageCode] = useState<string>("auto");
  const [isManualLanguageOverride, setIsManualLanguageOverride] = useState<boolean>(false);
  const [detectedLanguageLabel, setDetectedLanguageLabel] = useState<string>("Auto-Detect (Active)");
  const [recognitionLocale, setRecognitionLocale] = useState<string>("en-IN");
  const [showLanguagePicker, setShowLanguagePicker] = useState<boolean>(false);

  // Turn Submission Idempotency & Error Handling
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [showTextFallback, setShowTextFallback] = useState<boolean>(false);
  const [fallbackTypedText, setFallbackTypedText] = useState<string>("");
  const isSubmittingTurnRef = useRef<boolean>(false);

  // Real-time Audio Reactive Energy (0.0 to 1.0)
  const [audioLevel, setAudioLevel] = useState<number>(0);

  // Live streaming subtitles for spoken conversation
  const [interimSpeech, setInterimSpeech] = useState<string>("");
  const [humanSpeech, setHumanSpeech] = useState<string>("");
  const [assistantSpeech, setAssistantSpeech] = useState<string>("");

  // Multi-Turn Conversation History (Exact ChatGPT-style turns)
  const [conversationHistory, setConversationHistory] = useState<ConversationTurn[]>([]);
  const [copiedTranscript, setCopiedTranscript] = useState<boolean>(false);

  // Pending action awaiting voice confirmation
  const [pendingAction, setPendingAction] = useState<ProposedAction | null>(null);

  // Dragging & Dismiss State (Floating Orb mode)
  const [position, setPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isOverDismiss, setIsOverDismiss] = useState<boolean>(false);

  const dragStartRef = useRef<{
    startX: number;
    startY: number;
    elemX: number;
    elemY: number;
    moved: boolean;
  }>({ startX: 0, startY: 0, elemX: 0, elemY: 0, moved: false });

  const buttonRef = useRef<HTMLDivElement | null>(null);
  const dismissZoneRef = useRef<HTMLDivElement | null>(null);
  const transcriptEndRef = useRef<HTMLDivElement | null>(null);

  // Audio / Speech Recognition Refs
  const recognitionRef = useRef<any>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isSpeakingRef = useRef<boolean>(false);
  const isListeningRef = useRef<boolean>(false);
  const voiceActiveRef = useRef<boolean>(false);
  const isMutedRef = useRef<boolean>(false);
  const pendingActionRef = useRef<ProposedAction | null>(null);
  const selectedPersonaRef = useRef<VoicePersona>(VOICE_PERSONAS[0]);

  // Web Audio Analyser Refs
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const animFrameRef = useRef<number | null>(null);

  // Keep refs in sync
  useEffect(() => {
    voiceActiveRef.current = voiceActive;
  }, [voiceActive]);

  useEffect(() => {
    isMutedRef.current = isMuted;
  }, [isMuted]);

  useEffect(() => {
    pendingActionRef.current = pendingAction;
  }, [pendingAction]);

  useEffect(() => {
    selectedPersonaRef.current = selectedPersona;
  }, [selectedPersona]);

  // Load preferences and position on mount
  useEffect(() => {
    if (typeof window === "undefined") return;

    const storedEnabled = localStorage.getItem("clinova_assistant_enabled");
    setEnabled(storedEnabled !== "false");

    const storedLang = localStorage.getItem("clinova_assistant_language");
    if (storedLang) setLanguage(storedLang);

    const storedPersona = localStorage.getItem("clinova_voice_persona");
    if (storedPersona) {
      const p = VOICE_PERSONAS.find((x) => x.id === storedPersona);
      if (p) setSelectedPersona(p);
    }

    // Initial bounded position for mini-orb
    const pad = 24;
    const btnSize = 64;
    const defaultX = window.innerWidth - btnSize - pad;
    const defaultY = window.innerHeight - btnSize - pad;

    const storedPos = localStorage.getItem("clinova_assistant_pos");
    if (storedPos) {
      try {
        const parsed = JSON.parse(storedPos);
        const clampedX = Math.max(16, Math.min(window.innerWidth - btnSize - 16, parsed.x));
        const clampedY = Math.max(16, Math.min(window.innerHeight - btnSize - 16, parsed.y));
        setPosition({ x: clampedX, y: clampedY });
      } catch {
        setPosition({ x: defaultX, y: defaultY });
      }
    } else {
      setPosition({ x: defaultX, y: defaultY });
    }

    // Listen to custom toggle events from Header
    const handleToggle = (e: CustomEvent<{ enabled: boolean }>) => {
      if (typeof e.detail?.enabled === "boolean") {
        setEnabled(e.detail.enabled);
        if (!e.detail.enabled) {
          stopVoiceSession();
        }
      }
    };

    window.addEventListener("clinova-assistant-toggle", handleToggle as EventListener);
    return () => {
      window.removeEventListener("clinova-assistant-toggle", handleToggle as EventListener);
    };
  }, []);

  // Keyboard shortcuts (Space = Mute/Interrupt, Escape = Minimize/Close)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!voiceActive) return;
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      if (e.code === "Space") {
        e.preventDefault();
        if (isSpeakingRef.current) {
          interruptAssistant("keyboard");
        } else {
          toggleMute();
        }
      } else if (e.code === "Escape") {
        if (isExpanded) {
          setIsExpanded(false);
        } else {
          stopVoiceSession();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [voiceActive, isExpanded]);

  // Window resize bounds clamping
  useEffect(() => {
    const handleResize = () => {
      const btnSize = 64;
      setPosition((prev) => ({
        x: Math.max(16, Math.min(window.innerWidth - btnSize - 16, prev.x)),
        y: Math.max(16, Math.min(window.innerHeight - btnSize - 16, prev.y)),
      }));
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Auto-scroll transcript drawer to bottom
  useEffect(() => {
    if (showTranscript && transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [conversationHistory, showTranscript]);

  const selectLanguageMode = (code: string) => {
    setShowLanguagePicker(false);
    setSelectedLanguageCode(code);
    if (code === "auto") {
      setIsManualLanguageOverride(false);
      setLanguage("en");
      setRecognitionLocale("en-IN");
      setDetectedLanguageLabel("Auto-Detect (Active)");
      if (typeof window !== "undefined") {
        localStorage.setItem("clinova_assistant_lang_mode", "auto");
      }
    } else {
      const match = LANGUAGE_OPTIONS.find((l) => l.code === code);
      setIsManualLanguageOverride(true);
      setLanguage(code);
      const loc = match?.locale || `${code}-IN`;
      setRecognitionLocale(loc);
      setDetectedLanguageLabel(`${match?.name || code.toUpperCase()} (Manual Override)`);
      if (typeof window !== "undefined") {
        localStorage.setItem("clinova_assistant_lang_mode", code);
      }
    }

    if (recognitionRef.current && isListeningRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {}
      isListeningRef.current = false;
      setTimeout(() => {
        if (voiceActiveRef.current && !isSpeakingRef.current && !isMutedRef.current) {
          startListening();
        }
      }, 150);
    }
  };

  // -------------------------------------------------------------
  // REAL-TIME AUDIO ANALYSER (Reactive living fluid orb)
  // -------------------------------------------------------------
  const startAudioAnalyser = async () => {
    try {
      if (typeof window === "undefined" || !navigator.mediaDevices?.getUserMedia) return;
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStreamRef.current = stream;

      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
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
        for (let i = 0; i < data.length; i++) {
          sum += data[i];
        }
        const avg = sum / data.length;
        const normalized = Math.min(1, avg / 120);
        setAudioLevel(normalized);

        // Real-Time Barge-In / Interruption:
        // When AI is speaking, if the user starts talking loudly into the mic, immediately interrupt!
        if (isSpeakingRef.current && normalized > 0.35) {
          interruptAssistant("voice_barge_in");
        }

        animFrameRef.current = requestAnimationFrame(sampleAudio);
      };
      sampleAudio();
    } catch (e) {
      console.warn("Audio analyser initialization notice:", e);
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
  // SPEECH SYNTHESIS (Natural voice with persona pitch & rate)
  // -------------------------------------------------------------
  const speakVoice = useCallback(
    (text: string, onDone?: () => void) => {
      if (typeof window === "undefined" || !("speechSynthesis" in window)) {
        onDone?.();
        return;
      }

      window.speechSynthesis.cancel();
      isSpeakingRef.current = true;
      setVoiceState("speaking");
      setAssistantSpeech(text);

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = selectedPersonaRef.current.rate * speechRate;
      utterance.pitch = selectedPersonaRef.current.pitch;

      // Select regional voice matching current language and persona
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
        isSpeakingRef.current = false;
        if (voiceActiveRef.current && !isMutedRef.current) {
          // Immediately resume listening for natural hands-free continuous conversation
          startListening();
        } else {
          setVoiceState("idle");
        }
        onDone?.();
      };

      utterance.onerror = () => {
        isSpeakingRef.current = false;
        if (voiceActiveRef.current && !isMutedRef.current) {
          startListening();
        } else {
          setVoiceState("idle");
        }
        onDone?.();
      };

      window.speechSynthesis.speak(utterance);
    },
    [language, speechRate]
  );

  // -------------------------------------------------------------
  // INSTANT HUMAN INTERRUPTION / BARGE-IN HANDLER
  // -------------------------------------------------------------
  const interruptAssistant = useCallback(
    (reason?: string) => {
      if (isSpeakingRef.current) {
        if (typeof window !== "undefined" && "speechSynthesis" in window) {
          window.speechSynthesis.cancel();
        }
        isSpeakingRef.current = false;
        playChime("interrupt");
        setVoiceState("listening");
        if (voiceActiveRef.current && !isMutedRef.current) {
          startListening();
        }
      }
    },
    []
  );

  // -------------------------------------------------------------
  // PROCESS HUMAN SPOKEN UTTERANCE & MULTI-TURN AI CHAT
  // -------------------------------------------------------------
  const processSpokenInput = async (spokenText: string) => {
    const clean = spokenText.trim();
    if (!clean || isSubmittingTurnRef.current) return;

    isSubmittingTurnRef.current = true;
    setVoiceError(null);
    setInterimSpeech("");
    setHumanSpeech(clean);
    setVoiceState("thinking");

    // Add User turn to Conversation History
    const userTurn: ConversationTurn = {
      id: `turn-u-${Date.now()}`,
      role: "user",
      text: clean,
      language,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setConversationHistory((prev) => [...prev, userTurn]);

    // Check if user is confirming or cancelling a pending action verbally
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
          const confirmReply = "Action confirmed and executed successfully.";
          recordAssistantTurn(confirmReply, "Clinical Action Confirmed");
          speakVoice(confirmReply);
          return;
        } catch {
          setPendingAction(null);
          const failReply = "Could not execute action. Please try again.";
          recordAssistantTurn(failReply, "Error");
          speakVoice(failReply);
          return;
        } finally {
          isSubmittingTurnRef.current = false;
        }
      } else if (isNegative) {
        setPendingAction(null);
        const cancelReply = "Action cancelled.";
        recordAssistantTurn(cancelReply, "Action Cancelled");
        speakVoice(cancelReply);
        isSubmittingTurnRef.current = false;
        return;
      }
    }

    // Send query to assistant intelligence with Multi-turn history
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

        // Check if consequential action requires voice confirmation
        if (res.data.requires_confirmation && res.data.proposed_action) {
          setPendingAction(res.data.proposed_action);
          const voicePrompt = `${replyText}. Please say "Confirm" to proceed, or say "Cancel" to stop.`;
          speakVoice(voicePrompt);
        } else {
          speakVoice(replyText);
        }
      } else {
        const fallbackMsg = res.error || "I could not process that. Please say that again.";
        recordAssistantTurn(fallbackMsg, "Error");
        speakVoice(fallbackMsg);
        setVoiceError(fallbackMsg);
      }
    } catch {
      const errMsg = "Connection issue. Please check your network and speak again.";
      recordAssistantTurn(errMsg, "Connection Notice");
      speakVoice(errMsg);
      setVoiceError(errMsg);
    } finally {
      isSubmittingTurnRef.current = false;
      if (!isSpeakingRef.current && voiceActiveRef.current && !isMutedRef.current) {
        setVoiceState("idle");
      }
    }
  };

  const recordAssistantTurn = (text: string, sourceLabel: string) => {
    const aiTurn: ConversationTurn = {
      id: `turn-a-${Date.now()}`,
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
  // SPEECH RECOGNITION LISTENER (Streaming real-time STT)
  // -------------------------------------------------------------
  const startListening = () => {
    if (
      typeof window === "undefined" ||
      isSpeakingRef.current ||
      isMutedRef.current ||
      isSubmittingTurnRef.current
    )
      return;

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setVoiceError(
        "Voice recognition is not supported in this browser. Please use Chrome or Edge, or type your query below."
      );
      setShowTextFallback(true);
      setVoiceState("idle");
      return;
    }

    try {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {}
      }

      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;

      const currentLocale =
        isManualLanguageOverride
          ? language === "hi"
            ? "hi-IN"
            : language === "or"
            ? "or-IN"
            : language === "bn"
            ? "bn-IN"
            : language === "ta"
            ? "ta-IN"
            : language === "te"
            ? "te-IN"
            : "en-IN"
          : "en-IN";

      recognition.lang = currentLocale;
      setRecognitionLocale(currentLocale);

      recognition.onstart = () => {
        isListeningRef.current = true;
        setVoiceError(null);
        setVoiceState("listening");
      };

      recognition.onresult = (event: any) => {
        if (isSpeakingRef.current) {
          interruptAssistant("speech_detected");
        }

        let interim = "";
        let accumulatedFinal = "";

        // Standard Web Speech API: accumulate all finalized items and capture current interim
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

        setHumanSpeech(accumulatedFinal);
        setInterimSpeech(interim);

        const currentStream = (accumulatedFinal + " " + interim).trim();
        if (currentStream) {
          // Real-time language script identification if in auto mode
          if (!isManualLanguageOverride) {
            if (anyCharInRange(currentStream, 0x0900, 0x097F)) {
              setLanguage("hi");
              setDetectedLanguageLabel("Hindi (Auto)");
            } else if (anyCharInRange(currentStream, 0x0B00, 0x0B7F)) {
              setLanguage("or");
              setDetectedLanguageLabel("Odia (Auto)");
            } else if (anyCharInRange(currentStream, 0x0980, 0x09FF)) {
              setLanguage("bn");
              setDetectedLanguageLabel("Bengali (Auto)");
            } else if (anyCharInRange(currentStream, 0x0B80, 0x0BFF)) {
              setLanguage("ta");
              setDetectedLanguageLabel("Tamil (Auto)");
            } else if (anyCharInRange(currentStream, 0x0C00, 0x0C7F)) {
              setLanguage("te");
              setDetectedLanguageLabel("Telugu (Auto)");
            } else {
              const hasLetters = /[a-zA-Z]/.test(currentStream);
              if (hasLetters) {
                setLanguage("en");
                setDetectedLanguageLabel("English (Auto)");
              } else {
                setDetectedLanguageLabel("Detection uncertain (en-IN default)");
              }
            }
          }
        }

        // Silence / pause debounce: When user stops speaking, finalize and trigger AI turn
        if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
        const textToProcess = (accumulatedFinal || interim).trim();

        if (textToProcess && !isSubmittingTurnRef.current) {
          silenceTimerRef.current = setTimeout(() => {
            if (isSubmittingTurnRef.current) return;
            if (recognitionRef.current) {
              try {
                recognitionRef.current.stop();
              } catch {}
              isListeningRef.current = false;
            }
            processSpokenInput(textToProcess);
          }, accumulatedFinal ? 750 : 1200);
        }
      };

      recognition.onerror = (e: any) => {
        if (e.error === "not-allowed" || e.error === "permission-denied") {
          setVoiceError(
            "Microphone access is blocked or denied. Please grant microphone permissions in your browser, or type your query below."
          );
          setShowTextFallback(true);
          setVoiceState("idle");
          isListeningRef.current = false;
        } else if (e.error === "no-speech") {
          // Normal pause during listening; don't fabricate turn or show error
          if (
            voiceActiveRef.current &&
            !isSpeakingRef.current &&
            !isMutedRef.current &&
            !isSubmittingTurnRef.current
          ) {
            try {
              recognition.start();
            } catch {}
          }
        } else if (e.error === "network") {
          setVoiceError("Network issue encountered during speech recognition.");
          setShowTextFallback(true);
          setVoiceState("idle");
          isListeningRef.current = false;
        } else if (e.error !== "aborted") {
          setVoiceError(`Speech recognition notice: ${e.error}`);
          isListeningRef.current = false;
        }
      };

      recognition.onend = () => {
        isListeningRef.current = false;
        if (
          voiceActiveRef.current &&
          !isSpeakingRef.current &&
          !isMutedRef.current &&
          !isSubmittingTurnRef.current
        ) {
          try {
            recognition.start();
          } catch {}
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch {
      isListeningRef.current = false;
    }
  };

  // -------------------------------------------------------------
  // SESSION CONTROLS: Start, Stop, Mute, Dismiss
  // -------------------------------------------------------------
  const startVoiceSession = () => {
    setVoiceActive(true);
    voiceActiveRef.current = true;
    setIsExpanded(true); // Open in full ChatGPT-style canvas
    setIsMuted(false);
    isMutedRef.current = false;
    setPendingAction(null);
    setVoiceError(null);

    playChime("connect");
    startAudioAnalyser();

    const greetings: Record<string, string> = {
      en: `Hello, I'm ${selectedPersona.name}, your Clinova voice companion. How can I assist you today?`,
      hi: `नमस्ते, मैं ${selectedPersona.name}, आपका क्लिनोवा वॉयस सहायक हूँ। आज मैं आपकी क्या सहायता कर सकता हूँ?`,
      or: `ନମସ୍କାର, ମୁଁ ${selectedPersona.name}, କ୍ଲିନୋଭା ର ଭଏସ୍ ସହାୟକ। ଆଜି ମୁଁ ଆପଣଙ୍କୁ କିପରି ସାହାଯ୍ୟ କରିପାରିବି?`,
    };

    const greeting = greetings[language] || greetings["en"];
    recordAssistantTurn(greeting, "Session Start");
    speakVoice(greeting);
  };

  const stopVoiceSession = () => {
    playChime("disconnect");
    stopAudioAnalyser();

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

    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }

    isSpeakingRef.current = false;
    isListeningRef.current = false;
    voiceActiveRef.current = false;
    isSubmittingTurnRef.current = false;

    setVoiceActive(false);
    setVoiceState("idle");
    setIsExpanded(false);
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
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {}
      }
      isListeningRef.current = false;
      if (isSpeakingRef.current) {
        interruptAssistant("mute");
      }
      setVoiceState("idle");
    }
  };

  const dismissAssistant = useCallback(() => {
    stopVoiceSession();
    setEnabled(false);
    if (typeof window !== "undefined") {
      localStorage.setItem("clinova_assistant_enabled", "false");
      window.dispatchEvent(
        new CustomEvent("clinova-assistant-toggle", { detail: { enabled: false } })
      );
    }
    assistantApi
      .updatePreferences({
        assistant_enabled: false,
        language,
        voice_enabled: true,
        voice_response_enabled: true,
      })
      .catch(() => {});
  }, [language]);

  // Copy transcript to clipboard
  const copyTranscript = () => {
    const text = conversationHistory
      .map(
        (t) =>
          `[${t.timestamp}] ${t.role === "user" ? "You" : t.persona || "Clinova"}: ${t.text}`
      )
      .join("\n\n");
    navigator.clipboard.writeText(text);
    setCopiedTranscript(true);
    setTimeout(() => setCopiedTranscript(false), 2000);
  };

  // Pointer Drag Handlers (Draggable with drag-to-dismiss for mini orb)
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

    if (Math.hypot(dx, dy) > 6) {
      dragStartRef.current.moved = true;
    }

    const btnSize = 64;
    const nextX = Math.max(12, Math.min(window.innerWidth - btnSize - 12, dragStartRef.current.elemX + dx));
    const nextY = Math.max(12, Math.min(window.innerHeight - btnSize - 12, dragStartRef.current.elemY + dy));

    setPosition({ x: nextX, y: nextY });

    if (dismissZoneRef.current) {
      const rect = dismissZoneRef.current.getBoundingClientRect();
      const btnCenterX = nextX + btnSize / 2;
      const btnCenterY = nextY + btnSize / 2;

      const isOver =
        btnCenterX >= rect.left - 24 &&
        btnCenterX <= rect.right + 24 &&
        btnCenterY >= rect.top - 24 &&
        btnCenterY <= rect.bottom + 24;

      setIsOverDismiss(isOver);
    }
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    if (!isDragging) return;
    setIsDragging(false);
    try {
      (e.target as HTMLElement).releasePointerCapture(e.pointerId);
    } catch {}

    if (isOverDismiss) {
      dismissAssistant();
      setIsOverDismiss(false);
      return;
    }

    if (typeof window !== "undefined") {
      localStorage.setItem("clinova_assistant_pos", JSON.stringify(position));
    }

    if (!dragStartRef.current.moved) {
      if (!voiceActive) {
        startVoiceSession();
      } else {
        setIsExpanded(true);
      }
    }
  };

  if (!enabled) return null;

  return (
    <>
      {/* ------------------------------------------------------------- */}
      {/* DRAG-TO-DISMISS BOTTOM DROP ZONE                              */}
      {/* ------------------------------------------------------------- */}
      {isDragging && !isExpanded && (
        <div
          ref={dismissZoneRef}
          aria-live="polite"
          className={`fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] transition-all duration-200 pointer-events-none flex items-center gap-2.5 px-6 py-3 rounded-full border-2 shadow-2xl backdrop-blur-md ${
            isOverDismiss
              ? "bg-rose-600 border-rose-300 text-white scale-110 shadow-rose-900/50 ring-4 ring-rose-400/40"
              : "bg-slate-900/90 border-dashed border-slate-400 text-white shadow-black/40 scale-100"
          }`}
        >
          <div
            className={`p-1 rounded-full ${
              isOverDismiss ? "bg-white text-rose-600" : "bg-slate-800 text-slate-300"
            }`}
          >
            <X className="w-4 h-4" />
          </div>
          <span className="text-xs font-semibold tracking-wide">
            {isOverDismiss ? "Release to remove assistant" : "Drop here to dismiss assistant"}
          </span>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* FULL-SCREEN IMMERSIVE CHATGPT VOICE MODE CANVAS               */}
      {/* ------------------------------------------------------------- */}
      {voiceActive && isExpanded && (
        <div
          className="fixed inset-0 z-[120] bg-slate-950/95 backdrop-blur-3xl text-white flex flex-col justify-between overflow-hidden animate-in fade-in duration-300 select-none"
          role="dialog"
          aria-modal="true"
          aria-label="Clinova Voice AI"
        >
          {/* Top Bar: Navigation, Persona, Language, Controls */}
          <div className="w-full max-w-4xl mx-auto px-6 py-5 flex items-center justify-between border-b border-slate-800/80">
            {/* Mode & Live Status Badge */}
            <div className="flex items-center gap-3">
              <ClinovaLogo variant="full" size="sm" theme="dark" />
              <div className="hidden sm:block w-px h-5 bg-slate-800" />
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-teal-500/30">
                <span
                  className={`w-2.5 h-2.5 rounded-full ${
                    isMuted
                      ? "bg-slate-500"
                      : voiceState === "speaking"
                      ? "bg-teal-400 animate-ping"
                      : voiceState === "thinking"
                      ? "bg-amber-400 animate-pulse"
                      : "bg-rose-500 animate-pulse"
                  }`}
                />
                <span className="text-xs font-semibold tracking-wide text-teal-300">
                  {isMuted
                    ? "Microphone Muted"
                    : voiceState === "speaking"
                    ? "Clinova Speaking..."
                    : voiceState === "thinking"
                    ? "Formulating Response..."
                    : "Listening to you..."}
                </span>
              </div>

              {/* Interactive Language Selector & Metadata Badge */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowLanguagePicker(!showLanguagePicker)}
                  className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 border border-slate-700 hover:border-slate-600 text-xs font-mono text-slate-200 transition-all shadow-xs cursor-pointer"
                  title="Toggle Language Recognition Mode (Auto vs Manual Override)"
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
                className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-slate-200 transition-all shadow-sm"
              >
                <Sparkles className="w-3.5 h-3.5 text-teal-400" />
                <span>{selectedPersona.name}</span>
                <ChevronDown className="w-3 h-3 text-slate-400" />
              </button>

              {/* Persona Dropdown Menu */}
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

            {/* Minimize & Close Actions */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setIsExpanded(false)}
                title="Minimize to floating bubble"
                aria-label="Minimize voice mode"
                className="p-2 rounded-full hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
              >
                <Minimize2 className="w-5 h-5" />
              </button>
              <button
                type="button"
                onClick={stopVoiceSession}
                title="End Voice Session"
                aria-label="Close voice mode"
                className="p-2 rounded-full hover:bg-rose-950/50 text-slate-400 hover:text-rose-400 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Central Living Audio Orb & Subtitle Display */}
          <div className="flex-1 flex flex-col items-center justify-center px-6 relative max-w-xl mx-auto w-full">
            {/* Tap to Interrupt Touch Surface on Orb */}
            <div
              onClick={() => interruptAssistant("tap_orb")}
              className="relative cursor-pointer group flex flex-col items-center"
              title={isSpeakingRef.current ? "Tap to interrupt assistant" : "Listening..."}
            >
              {/* Outer Ambient Glow Wave */}
              <div
                style={{
                  transform: `scale(${
                    voiceState === "speaking"
                      ? 1.25 + audioLevel * 0.4
                      : voiceState === "listening"
                      ? 1.1 + audioLevel * 0.6
                      : 1.05
                  })`,
                }}
                className={`absolute inset-0 rounded-full blur-3xl transition-transform duration-100 ${
                  isMuted
                    ? "bg-slate-700/20"
                    : voiceState === "speaking"
                    ? "bg-gradient-to-tr from-teal-500/40 via-cyan-500/30 to-indigo-500/40"
                    : voiceState === "thinking"
                    ? "bg-amber-500/30"
                    : "bg-gradient-to-tr from-rose-500/30 via-teal-500/30 to-emerald-500/30"
                }`}
              />

              {/* The Iconic ChatGPT-Style Living Fluid Orb */}
              <div
                style={{
                  transform: `scale(${
                    voiceState === "speaking"
                      ? 1 + audioLevel * 0.25
                      : voiceState === "listening"
                      ? 1 + audioLevel * 0.4
                      : 1
                  })`,
                }}
                className={`relative w-48 h-48 sm:w-60 sm:h-60 rounded-full flex items-center justify-center transition-all duration-150 shadow-2xl ${
                  isMuted
                    ? "bg-slate-800 ring-4 ring-slate-700 shadow-slate-900"
                    : voiceState === "speaking"
                    ? "bg-gradient-to-tr from-teal-500 via-cyan-400 to-indigo-600 ring-8 ring-teal-400/30 shadow-teal-500/50"
                    : voiceState === "thinking"
                    ? "bg-gradient-to-tr from-amber-500 via-orange-400 to-yellow-600 ring-8 ring-amber-400/30 shadow-amber-500/50 animate-spin"
                    : "bg-gradient-to-tr from-teal-600 via-cyan-500 to-emerald-500 ring-8 ring-teal-400/30 shadow-teal-600/50 animate-pulse"
                }`}
              >
                {/* Organic fluid core particle wave */}
                <div className="absolute inset-4 rounded-full bg-slate-950/60 backdrop-blur-md flex items-center justify-center overflow-hidden">
                  {/* Dynamic waveform bars inside the orb */}
                  <div className="flex items-center gap-1.5 h-16">
                    {[30, 60, 95, 45, 80, 50, 90, 40].map((h, i) => (
                      <span
                        key={i}
                        style={{
                          height:
                            voiceState === "speaking"
                              ? `${Math.max(20, (h * Math.sin((i + 1) * 1.2)) % 100)}%`
                              : voiceState === "listening"
                              ? `${Math.max(15, h * (0.3 + audioLevel * 0.7))}%`
                              : "15%",
                        }}
                        className={`w-1.5 rounded-full transition-all duration-100 ${
                          voiceState === "speaking"
                            ? "bg-teal-300 animate-pulse"
                            : voiceState === "listening"
                            ? "bg-rose-400 animate-pulse"
                            : "bg-slate-500"
                        }`}
                      />
                    ))}
                  </div>
                </div>

                {/* Central State Icon */}
                {isMuted ? (
                  <MicOff className="w-10 h-10 text-slate-400 relative z-10" />
                ) : voiceState === "speaking" ? (
                  <Volume2 className="w-10 h-10 text-teal-100 relative z-10" />
                ) : voiceState === "thinking" ? (
                  <Sparkles className="w-10 h-10 text-amber-200 relative z-10 animate-bounce" />
                ) : (
                  <Mic className="w-10 h-10 text-white relative z-10" />
                )}
              </div>

              {/* Tap to Interrupt hint */}
              {voiceState === "speaking" && (
                <div className="mt-4 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-700 text-[11px] text-teal-300 tracking-wide font-medium flex items-center gap-1.5 animate-pulse">
                  <Pause className="w-3 h-3" />
                  Tap orb or start speaking to interrupt
                </div>
              )}
            </div>

            {/* Live Streaming Subtitles & Transcript */}
            <div className="mt-6 w-full max-w-lg min-h-[90px] max-h-[140px] overflow-y-auto text-center px-4">
              {/* While AI is speaking */}
              {voiceState === "speaking" && assistantSpeech && (
                <p className="text-teal-200 text-sm sm:text-base leading-relaxed font-medium animate-in fade-in">
                  &ldquo;{assistantSpeech}&rdquo;
                </p>
              )}

              {/* While User is speaking or just finished */}
              {voiceState !== "speaking" && (humanSpeech || interimSpeech) && (
                <div className="space-y-1 animate-in fade-in">
                  <span className="text-slate-400 text-[11px] block font-semibold uppercase tracking-wider">
                    Recognized Speech:
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

              {/* Idle State Prompt */}
              {voiceState === "listening" && !humanSpeech && !interimSpeech && (
                <div className="space-y-1">
                  <p className="text-slate-300 text-sm font-medium">
                    Listening... speak naturally in English, Hindi, or Odia
                  </p>
                  <p className="text-slate-500 text-xs font-mono">
                    Active: {detectedLanguageLabel}
                  </p>
                </div>
              )}

              {/* Thinking State */}
              {voiceState === "thinking" && (
                <div className="space-y-2 animate-pulse">
                  <p className="text-amber-300 text-sm font-medium">
                    Clinova AI is formulating clinical response...
                  </p>
                  <div className="text-[11px] text-slate-400 font-mono">
                    Input: &ldquo;{humanSpeech}&rdquo;
                  </div>
                </div>
              )}
            </div>

            {/* Voice Error Banner & Text Fallback Prompt */}
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
                    className="px-3 py-1 bg-rose-800 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold cursor-pointer"
                  >
                    Retry Voice
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

            {/* Text Input Fallback Bar (When mic is blocked/denied or user wants to type) */}
            {showTextFallback && (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (fallbackTypedText.trim() && !isSubmittingTurnRef.current) {
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
                  placeholder="Type a clinical query or question..."
                  className="flex-1 bg-transparent px-3 py-1.5 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={!fallbackTypedText.trim() || voiceState === "thinking"}
                  className="px-4 py-1.5 bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl transition-colors cursor-pointer flex items-center gap-1"
                >
                  <Send className="w-3 h-3" />
                  <span>Send</span>
                </button>
              </form>
            )}

            {/* Spoken Action Confirmation Gate */}
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

          {/* Bottom Dock Control Bar (Mute, Interrupt, Speed, Transcript, End) */}
          <div className="w-full max-w-xl mx-auto px-6 py-6 flex items-center justify-between border-t border-slate-800/80">
            {/* Transcript Drawer Toggle */}
            <button
              type="button"
              onClick={() => setShowTranscript(true)}
              aria-label="View conversation transcript"
              className="p-3.5 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white transition-all shadow-md relative"
            >
              <FileText className="w-5 h-5" />
              {conversationHistory.length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-teal-500 text-[10px] font-bold text-white flex items-center justify-center">
                  {conversationHistory.length}
                </span>
              )}
            </button>

            {/* Voice Speed Toggle (0.8x, 1.0x, 1.2x) */}
            <button
              type="button"
              onClick={() => {
                const nextRate = speechRate === 1.0 ? 1.2 : speechRate === 1.2 ? 0.8 : 1.0;
                setSpeechRate(nextRate);
              }}
              title={`Speech Rate: ${speechRate}x`}
              className="px-3.5 py-2 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-mono font-bold text-slate-300 hover:text-white transition-all shadow-md"
            >
              {speechRate}x
            </button>

            {/* Primary Mute / Unmute Button */}
            <button
              type="button"
              onClick={toggleMute}
              aria-label={isMuted ? "Unmute microphone" : "Mute microphone"}
              className={`p-4 rounded-full transition-all shadow-xl ${
                isMuted
                  ? "bg-rose-600 hover:bg-rose-500 text-white ring-4 ring-rose-400/40"
                  : "bg-slate-800 hover:bg-slate-700 text-white border border-slate-600"
              }`}
            >
              {isMuted ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
            </button>

            {/* Tap to Interrupt Button */}
            <button
              type="button"
              onClick={() => interruptAssistant("bottom_button")}
              title="Interrupt assistant speaking"
              disabled={!isSpeakingRef.current}
              className={`p-3.5 rounded-full border transition-all shadow-md ${
                isSpeakingRef.current
                  ? "bg-teal-600 hover:bg-teal-500 border-teal-400 text-white animate-pulse"
                  : "bg-slate-900 border-slate-800 text-slate-600 cursor-not-allowed"
              }`}
            >
              <Pause className="w-5 h-5" />
            </button>

            {/* End Session Button */}
            <button
              type="button"
              onClick={stopVoiceSession}
              aria-label="End conversation session"
              className="p-3.5 rounded-full bg-rose-600 hover:bg-rose-500 text-white shadow-lg hover:shadow-rose-600/40 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* ----------------------------------------------------------- */}
          {/* SLIDE-OVER TRANSCRIPT HISTORY DRAWER (ChatGPT-style)         */}
          {/* ----------------------------------------------------------- */}
          {showTranscript && (
            <div
              className="absolute inset-y-0 right-0 w-full sm:w-[420px] bg-slate-900/98 border-l border-slate-700 shadow-2xl flex flex-col z-50 animate-in slide-in-from-right duration-200"
              role="dialog"
              aria-label="Conversation Transcript"
            >
              {/* Drawer Header */}
              <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-teal-400" />
                  <span className="text-sm font-bold text-white">Conversation Transcript</span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={copyTranscript}
                    className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                    title="Copy full transcript"
                  >
                    {copiedTranscript ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowTranscript(false)}
                    className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Drawer Messages List */}
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
      {/* FLOATING MINI-ORB BUTTON (When minimized or inactive)         */}
      {/* ------------------------------------------------------------- */}
      {(!voiceActive || !isExpanded) && (
        <div
          ref={buttonRef}
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
            title={
              voiceActive
                ? "Clinova Voice Active (Tap to expand, drag to dismiss)"
                : "Clinova Voice AI (Tap to talk, drag to dismiss)"
            }
            className={`relative group flex items-center justify-center w-16 h-16 rounded-full shadow-2xl transition-all ${
              voiceActive
                ? isMuted
                  ? "bg-slate-800 text-white ring-4 ring-slate-600"
                  : voiceState === "speaking"
                  ? "bg-gradient-to-tr from-teal-500 to-cyan-500 text-white ring-4 ring-teal-300 shadow-teal-500/50 scale-110"
                  : "bg-gradient-to-tr from-rose-600 to-pink-600 text-white ring-4 ring-rose-300 shadow-rose-600/50 scale-110"
                : "bg-white text-slate-800 ring-2 ring-teal-500/30 hover:ring-teal-500 shadow-xl hover:shadow-teal-500/20 hover:scale-105 active:scale-95"
            }`}
          >
            {/* Ripples when active */}
            {voiceActive && !isMuted && (
              <>
                <span className="absolute -inset-2 rounded-full border-2 border-teal-400 animate-ping opacity-60 pointer-events-none" />
                <span className="absolute -inset-1 rounded-full border border-teal-300 animate-pulse opacity-80 pointer-events-none" />
              </>
            )}

            {voiceActive ? (
              isMuted ? (
                <MicOff className="w-7 h-7 text-slate-300" />
              ) : voiceState === "speaking" ? (
                <Volume2 className="w-7 h-7 animate-bounce" />
              ) : (
                <Mic className="w-7 h-7 animate-pulse" />
              )
            ) : (
              <div className="relative flex items-center justify-center p-1">
                <ClinovaLogo variant="mark" size="md" />
                <span className="absolute -bottom-1 -right-1 p-1 rounded-full bg-teal-600 text-white shadow-xs">
                  <Mic className="w-2.5 h-2.5" />
                </span>
              </div>
            )}
          </button>
        </div>
      )}
    </>
  );
};
