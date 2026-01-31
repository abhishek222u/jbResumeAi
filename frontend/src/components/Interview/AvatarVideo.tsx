import React from 'react';

interface AvatarVideoProps {
    isSpeaking: boolean;
}

export const AvatarVideo: React.FC<AvatarVideoProps> = ({ isSpeaking }) => {
    // Paths to assets served by FastAPI static mount
    // We use the existing avatar.png since video loops are not yet uploaded.
    const avatarImage = "/static/avatar.png";

    return (
        <div className="relative w-full h-full bg-gray-900 rounded-xl overflow-hidden shadow-2xl border border-gray-700 flex items-center justify-center">

            {/* Avatar Image with Speaking Animation */}
            <img
                src={avatarImage}
                alt="AI Avatar"
                className={`
                    w-full h-full object-cover transition-transform duration-100 ease-in-out
                    ${isSpeaking ? 'scale-[1.02] brightness-110' : 'scale-100'}
                `}
                style={{
                    // Simple "talking" vibration effect when speaking
                    animation: isSpeaking ? 'pulse-talk 0.2s infinite alternate' : 'none'
                }}
            />

            {/* CSS for custom talk animation */}
            <style>{`
                @keyframes pulse-talk {
                    0% { transform: scale(1); }
                    100% { transform: scale(1.03); }
                }
            `}</style>

            <div className="absolute bottom-4 left-4 bg-black/50 px-3 py-1 rounded-full text-white text-sm flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${isSpeaking ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`} />
                <span>AI Interviewer</span>
            </div>
        </div>
    );
};
