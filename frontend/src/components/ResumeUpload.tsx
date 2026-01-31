import React, { useState } from 'react';
import { Upload, Loader2, FileText } from 'lucide-react';

interface ResumeUploadProps {
    onStart: (data: any) => void;
}

export const ResumeUpload: React.FC<ResumeUploadProps> = ({ onStart }) => {
    const [file, setFile] = useState<File | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleStart = async () => {
        if (!file) return;

        setIsLoading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Using /interview path which is proxied to backend
            const response = await fetch('/interview/start', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error("Failed to start interview");
            }

            const data = await response.json();
            onStart(data);
        } catch (error) {
            console.error(error);
            alert("Error starting interview. Please check console.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-6">
            <div className="max-w-md w-full bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-700 text-center">
                <div className="bg-blue-600/20 p-4 rounded-full inline-block mb-6">
                    <Upload className="w-10 h-10 text-blue-400" />
                </div>

                <h1 className="text-3xl font-bold mb-2">Resume AI</h1>
                <p className="text-gray-400 mb-8">Upload your resume to start a realistic AI video interview.</p>

                <label className="block w-full cursor-pointer group mb-6">
                    <input type="file" hidden accept=".pdf,.docx" onChange={handleFileChange} />
                    <div className="border-2 border-dashed border-gray-600 rounded-xl p-8 transition-colors group-hover:border-blue-500 group-hover:bg-gray-700/50">
                        {file ? (
                            <div className="flex flex-col items-center text-blue-400">
                                <FileText className="w-8 h-8 mb-2" />
                                <span className="font-medium truncate max-w-full">{file.name}</span>
                            </div>
                        ) : (
                            <div className="text-gray-500 group-hover:text-gray-300">
                                <p className="font-medium">Click to upload resume</p>
                                <p className="text-sm mt-1">PDF or DOCX</p>
                            </div>
                        )}
                    </div>
                </label>

                <button
                    onClick={handleStart}
                    disabled={!file || isLoading}
                    className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-all flex items-center justify-center gap-2"
                >
                    {isLoading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Analyzing Resume...
                        </>
                    ) : (
                        "Start Interview"
                    )}
                </button>
            </div>
        </div>
    );
};
