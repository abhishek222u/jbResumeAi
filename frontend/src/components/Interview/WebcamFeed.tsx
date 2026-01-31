import React, { useEffect, useRef, useState } from 'react';
import { Camera, CameraOff } from 'lucide-react';

interface WebcamFeedProps {
    onPermissionChange?: (hasPermission: boolean) => void;
}

export const WebcamFeed: React.FC<WebcamFeedProps> = ({ onPermissionChange }) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [hasPermission, setHasPermission] = useState<boolean | null>(null);

    useEffect(() => {
        let stream: MediaStream | null = null;

        const enableVideo = async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    setHasPermission(true);
                    onPermissionChange?.(true);
                }
            } catch (err) {
                console.error("Camera denied:", err);
                setHasPermission(false);
                onPermissionChange?.(false);
            }
        };

        enableVideo();

        return () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    return (
        <div className="relative w-full h-full bg-black rounded-xl overflow-hidden shadow-2xl border border-gray-700">
            {/* Camera View */}
            <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                className={`w-full h-full object-cover transform scale-x-[-1] ${hasPermission === false ? 'hidden' : ''}`}
            />

            {/* Fallback / Status */}
            {hasPermission === false && (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
                    <CameraOff className="w-16 h-16 mb-4" />
                    <p>Camera access denied</p>
                </div>
            )}

            {/* Overlay Label */}
            <div className="absolute bottom-4 left-4 bg-black/50 px-3 py-1 rounded-full text-white text-sm flex items-center gap-2">
                <Camera className="w-4 h-4" />
                <span>You</span>
            </div>
        </div>
    );
};
