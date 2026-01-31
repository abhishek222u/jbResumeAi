import React, { useState, useEffect, useRef } from 'react';
import { WebcamFeed } from './WebcamFeed';
import { AvatarVideo } from './AvatarVideo';
import { Controls } from './Controls';
import { useAudioRecorder } from '../../hooks/useAudioRecorder';

interface InterviewSessionProps {
    sessionId: string;
    initialQuestion: string;
    initialAudio: string;
    onFinish: (session_id: string) => void;
}

export const InterviewSession: React.FC<InterviewSessionProps> = ({
    sessionId, initialQuestion, initialAudio, onFinish
}) => {
    const [question, setQuestion] = useState(initialQuestion);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [cameraAllowed, setCameraAllowed] = useState(false);

    // Audio Player
    const audioRef = useRef<HTMLAudioElement | null>(null);

    // Recorder
    const { isRecording, startRecording, stopRecording } = useAudioRecorder();

    // Play Audio Helper
    const playAudio = (path: string) => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
        }

        // Path comes as "app/storage/..." or similar relative path from backend
        // We need to ensure it has leading slash for proxy: "/app/storage..."
        // Or if backend returns relative "static/...", we prepend /
        const formattedPath = path.startsWith('/') ? path : `/${path}`;

        const audio = new Audio(formattedPath);
        audioRef.current = audio;

        setIsSpeaking(true);
        audio.play().catch(e => console.error("Audio play error", e));

        audio.onended = () => {
            setIsSpeaking(false);
        };
    };

    // Initial Play
    useEffect(() => {
        // Only play if camera is potentially ready? 
        // For now, let's play, but block answering if no camera.
        playAudio(initialAudio);
        return () => {
            if (audioRef.current) audioRef.current.pause();
        };
    }, []);

    const handleToggleRecording = async () => {
        if (!cameraAllowed) {
            alert("Camera is mandatory. Please enable it to continue.");
            return;
        }

        if (isRecording) {
            // STOP
            const audioBlob = await stopRecording();
            submitAnswer(audioBlob);
        } else {
            // START
            // Stop acting if speaking (interrupt?)
            if (isSpeaking && audioRef.current) {
                audioRef.current.pause();
                setIsSpeaking(false);
            }
            startRecording();
        }
    };

    const submitAnswer = async (blob: Blob) => {
        setIsProcessing(true);
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('file', blob, "answer.mp3");

        try {
            const res = await fetch('/interview/next', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.is_finished) {
                onFinish(sessionId);
            } else {
                setQuestion(data.next_question);
                playAudio(data.audio_path);
            }

        } catch (err) {
            console.error(err);
            alert("Error submitting answer");
        } finally {
            setIsProcessing(false);
        }
    };

    const getStatusText = () => {
        if (!cameraAllowed) return "⚠️ Camera Required";
        if (isProcessing) return "Thinking...";
        if (isSpeaking) return "Interviewer is speaking...";
        if (isRecording) return "Recording... (Tap to Stop)";
        return "Tap Mic to Answer";
    };

    return (
        <div className="flex flex-col h-screen bg-black p-4 gap-4">
            {/* Split Screen */}
            <div className="flex-1 flex gap-4 min-h-0">
                {/* Left: AI Avatar */}
                <div className="flex-1 relative">
                    <AvatarVideo isSpeaking={isSpeaking} />

                    {/* Captions / Question Text Overlay */}
                    <div className="absolute top-4 left-4 right-4 bg-black/60 backdrop-blur text-white p-4 rounded-xl border border-white/10 shadow-lg">
                        <p className="text-lg font-medium leading-relaxed">
                            {question}
                        </p>
                    </div>
                </div>

                {/* Right: User Webcam */}
                <div className="flex-1 relative">
                    <WebcamFeed onPermissionChange={setCameraAllowed} />
                    {!cameraAllowed && (
                        <div className="absolute inset-0 bg-black/80 flex items-center justify-center z-10">
                            <div className="text-center p-6">
                                <h3 className="text-red-500 text-xl font-bold mb-2">Camera Mandatory</h3>
                                <p className="text-gray-300">You must enable your camera to proceed.</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Bottom Controls */}
            <div className="h-24 relative">
                <Controls
                    isRecording={isRecording}
                    onToggle={handleToggleRecording}
                    disabled={isProcessing || !cameraAllowed}
                    statusText={getStatusText()}
                />
            </div>
        </div>
    );
};
