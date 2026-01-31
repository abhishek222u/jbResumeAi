import { useState } from 'react';
import { ResumeUpload } from './components/ResumeUpload';
import { InterviewSession } from './components/Interview/InterviewSession';

function App() {
  const [sessionData, setSessionData] = useState<any>(null);
  const [isFinished, setIsFinished] = useState(false);
  const [feedback, setFeedback] = useState<any[]>([]);

  const handleStart = (data: any) => {
    setSessionData(data);
  };

  const handleFinish = async (sessionId: string) => {
    setIsFinished(true);
    // Fetch feedback
    try {
      const res = await fetch(`/interview/feedback?session_id=${sessionId}`);
      const data = await res.json();
      setFeedback(data.feedbacks || []);
    } catch (e) {
      console.error("Error fetching feedback", e);
    }
  };

  if (isFinished) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8 flex flex-col items-center">
        <h1 className="text-4xl font-bold mb-8 text-blue-400">Interview Complete</h1>
        <div className="w-full max-w-2xl space-y-4">
          {feedback.map((item, idx) => (
            <div key={idx} className="bg-gray-800 p-6 rounded-xl border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xl font-semibold">Question {idx + 1}</h3>
                <span className={`px-3 py-1 rounded-full text-sm ${item.is_satisfactory ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
                  {item.is_satisfactory ? "Satisfactory" : "Needs Improvement"}
                </span>
              </div>
              <p className="text-gray-300">{item.feedback}</p>
              <p className="text-sm text-gray-500 mt-2">Rating: {item.rating}/10</p>
            </div>
          ))}
        </div>

        <button
          onClick={() => window.location.reload()}
          className="mt-8 bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-xl font-bold transition-colors"
        >
          Start New Interview
        </button>
      </div>
    );
  }

  if (sessionData) {
    return (
      <InterviewSession
        sessionId={sessionData.session_id}
        initialQuestion={sessionData.current_question}
        initialAudio={sessionData.audio_path}
        onFinish={handleFinish}
      />
    );
  }

  return <ResumeUpload onStart={handleStart} />;
}

export default App;
