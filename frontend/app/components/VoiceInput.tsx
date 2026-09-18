"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2 } from 'lucide-react';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  onError?: (error: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  maxAlternatives: number;
  start(): void;
  stop(): void;
  abort(): void;
  onaudiostart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onaudioend: ((this: SpeechRecognition, ev: Event) => any) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
}

interface SpeechRecognitionStatic {
  new(): SpeechRecognition;
}

declare global {
  interface Window {
    SpeechRecognition: SpeechRecognitionStatic;
    webkitSpeechRecognition: SpeechRecognitionStatic;
  }
}

/**
 * Voice Input Component using Web Speech API
 * 
 * Enables hands-free voice input for Amica interface.
 * Supports Chrome/Edge (full), Safari (partial), Firefox (limited).
 */
export default function VoiceInput({
  onTranscript,
  onError,
  placeholder = "Click mic to speak...",
  disabled = false,
  className = ""
}: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [isSupported, setIsSupported] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Check for Web Speech API support
    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognitionAPI) {
      setIsSupported(true);
      
      const recognition = new SpeechRecognitionAPI();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsListening(true);
        // Auto-stop after 10 seconds
        timeoutRef.current = setTimeout(() => {
          recognition.stop();
        }, 10000);
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) {
            finalTranscript += result[0].transcript;
          } else {
            interimTranscript += result[0].transcript;
          }
        }

        const currentTranscript = finalTranscript || interimTranscript;
        setTranscript(currentTranscript);

        if (finalTranscript) {
          onTranscript(finalTranscript.trim());
          setTranscript("");
        }
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        setIsListening(false);
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
        
        let errorMessage = 'Speech recognition error';
        switch (event.error) {
          case 'no-speech':
            errorMessage = 'No speech detected. Please try again.';
            break;
          case 'audio-capture':
            errorMessage = 'Microphone access denied or unavailable.';
            break;
          case 'not-allowed':
            errorMessage = 'Microphone permission denied.';
            break;
          case 'network':
            errorMessage = 'Network error occurred.';
            break;
          default:
            errorMessage = `Speech recognition error: ${event.error}`;
        }
        
        if (onError) {
          onError(errorMessage);
        }
      };

      recognition.onend = () => {
        setIsListening(false);
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
      };

      // Simulate audio level animation
      recognition.onaudiostart = () => {
        const animateAudio = () => {
          if (isListening) {
            setAudioLevel(Math.random() * 100);
            setTimeout(animateAudio, 100);
          }
        };
        animateAudio();
      };

      recognition.onaudioend = () => {
        setAudioLevel(0);
      };

      recognitionRef.current = recognition;
    } else {
      setIsSupported(false);
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [onTranscript, onError, isListening]);

  const startListening = () => {
    if (recognitionRef.current && !isListening && !disabled) {
      setTranscript("");
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  if (!isSupported) {
    return (
      <div className={`voice-input-unsupported ${className}`}>
        <button
          type="button"
          disabled
          className="p-2 rounded-lg bg-gray-100 text-gray-400 cursor-not-allowed"
          title="Voice input not supported in this browser"
        >
          <MicOff className="w-4 h-4" />
        </button>
        <span className="text-xs text-gray-400 ml-2">
          Voice input requires Chrome/Edge
        </span>
      </div>
    );
  }

  return (
    <div className={`voice-input-container ${className}`}>
      <div className="relative flex items-center">
        {/* Voice Input Button */}
        <button
          type="button"
          onClick={toggleListening}
          disabled={disabled}
          className={`
            relative p-3 rounded-xl border-2 transition-all duration-200 
            ${isListening 
              ? 'bg-[#df7d4c] border-[#df7d4c] text-white shadow-lg' 
              : 'bg-white border-gray-300 text-gray-600 hover:border-[#df7d4c] hover:text-[#df7d4c]'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
          title={isListening ? "Stop listening" : "Start voice input"}
        >
          {isListening ? (
            <div className="relative">
              <Mic className="w-5 h-5" />
              {/* Audio Level Animation */}
              <div 
                className="absolute inset-0 rounded-full bg-white/30 animate-ping"
                style={{
                  transform: `scale(${1 + (audioLevel / 100) * 0.5})`,
                  opacity: audioLevel / 100
                }}
              />
            </div>
          ) : (
            <Mic className="w-5 h-5" />
          )}
        </button>

        {/* Listening Status */}
        {isListening && (
          <div className="ml-3 flex items-center gap-2">
            <div className="flex items-center gap-1">
              <div className="w-1 h-3 bg-[#df7d4c] rounded-full animate-pulse" />
              <div className="w-1 h-4 bg-[#df7d4c] rounded-full animate-pulse animation-delay-100" />
              <div className="w-1 h-2 bg-[#df7d4c] rounded-full animate-pulse animation-delay-200" />
            </div>
            <span className="text-sm text-gray-600 font-medium">
              Listening...
            </span>
          </div>
        )}

        {/* Transcript Preview */}
        {transcript && (
          <div className="ml-3 px-3 py-2 bg-gray-100 rounded-lg border">
            <span className="text-sm text-gray-800">{transcript}</span>
          </div>
        )}
      </div>

      {/* Instructions */}
      {!isListening && !transcript && (
        <p className="text-xs text-gray-500 mt-2">
          {placeholder}
        </p>
      )}

      {/* Browser Compatibility Notice */}
      <div className="text-xs text-gray-400 mt-1">
        <Volume2 className="w-3 h-3 inline mr-1" />
        Best in Chrome/Edge • Limited Safari support
      </div>
    </div>
  );
}