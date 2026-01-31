import React from 'react';
import { Mic, Square } from 'lucide-react';

interface ControlsProps {
    isRecording: boolean;
    onToggle: () => void;
    disabled: boolean;
    statusText: string;
}

export const Controls: React.FC<ControlsProps> = ({ isRecording, onToggle, disabled, statusText }) => {
    return (
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex flex-col items-center gap-4 z-50">
            <div className="bg-black/60 backdrop-blur-md px-6 py-2 rounded-full text-white font-medium shadow-lg border border-white/10">
                {statusText}
            </div>

            <button
                onClick={onToggle}
                disabled={disabled}
                className={`
                    w-16 h-16 rounded-full flex items-center justify-center shadow-2xl transition-all transform hover:scale-105 active:scale-95
                    ${disabled ? 'bg-gray-600 cursor-not-allowed opacity-50' :
                        isRecording ? 'bg-red-500 hover:bg-red-600 ring-4 ring-red-500/30' : 'bg-blue-500 hover:bg-blue-600'}
                `}
            >
                {isRecording ? (
                    <Square className="w-6 h-6 text-white fill-current" />
                ) : (
                    <Mic className="w-8 h-8 text-white" />
                )}
            </button>
        </div>
    );
};
