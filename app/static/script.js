const BASE_URL = window.location.origin; // e.g. http://127.0.0.1:8000

// Elements
const uploadStage = document.getElementById('upload-stage');
const interviewStage = document.getElementById('interview-stage');
const resultStage = document.getElementById('result-stage');

const selectFileBtn = document.getElementById('select-file-btn');
const fileInput = document.getElementById('resume-upload');
const startBtn = document.getElementById('start-btn');
const fileNameDisplay = document.getElementById('file-name');

const speakingIndicator = document.getElementById('speaking-indicator');
const aiQuestion = document.getElementById('ai-question');
const recordBtn = document.getElementById('record-btn');
const micStatus = document.getElementById('mic-status');

// State
let sessionId = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let selectedFile = null;

// --- Event Listeners ---
selectFileBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        fileNameDisplay.innerText = "Selected: " + selectedFile.name;
        startBtn.disabled = false;
    }
});

startBtn.addEventListener('click', startInterview);
recordBtn.addEventListener('click', toggleRecording);

// --- Functions ---

async function startInterview() {
    if (!selectedFile) return;

    // Show Loader
    document.getElementById('upload-loader').classList.remove('hidden');
    startBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch(`${BASE_URL}/interview/start`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error("Upload Failed");

        const data = await response.json();
        sessionId = data.session_id;

        // Transition to Interview
        uploadStage.classList.add('hidden');
        interviewStage.classList.remove('hidden');

        // Play First Question
        // questionText.innerText = "Interviewer is speaking..."; // Removed to keep specific question visible
        aiQuestion.innerText = `Question 1: ${data.current_question}`;
        await playAudio(data.audio_path);

        setupRecorder();

    } catch (err) {
        alert("Error starting interview: " + err.message);
        location.reload();
    }
}

async function playAudio(relativePath) {
    return new Promise((resolve) => {
        // Construct full URL. remove leading slash if needed
        const audioUrl = `${BASE_URL}${relativePath}`;
        const audio = new Audio(audioUrl);

        speakingIndicator.classList.remove('hidden');

        audio.onended = () => {
            speakingIndicator.classList.add('hidden');
            resolve();
        };

        audio.play().catch(e => console.error("Audio play error", e));
    });
}

// --- Recorder Logic ---
async function setupRecorder() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = sendAnswer;

    } catch (err) {
        alert("Microphone access denied. Please enable it.");
    }
}

function toggleRecording() {
    if (!mediaRecorder) return;

    if (!isRecording) {
        // Start
        audioChunks = [];
        mediaRecorder.start();
        isRecording = true;
        recordBtn.classList.add('recording');
        micStatus.innerText = "Recording... Tap to Stop";
    } else {
        // Stop
        mediaRecorder.stop();
        isRecording = false;
        recordBtn.classList.remove('recording');
        micStatus.innerText = "Processing Answer... Thinking...";
        // questionText.innerText = "Thinking..."; // Don't hide the question
    }
}

async function sendAnswer() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/mpeg' }); // or audio/wav
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('file', audioBlob, "answer.mp3");

    try {
        const response = await fetch(`${BASE_URL}/interview/next`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.is_finished) {
            showResults();
        } else {
            // Play Next Question
            aiQuestion.innerText = `Question ${data.progress}: ${data.next_question}`;
            micStatus.innerText = "Listen Carefully...";
            await playAudio(data.audio_path);
            micStatus.innerText = "Tap to Answer";
        }

    } catch (err) {
        console.error(err);
        alert("Error sending answer");
    }
}

async function showResults() {
    interviewStage.classList.add('hidden');
    resultStage.classList.remove('hidden');

    const res = await fetch(`${BASE_URL}/interview/feedback?session_id=${sessionId}`);
    const data = await res.json();

    const container = document.getElementById('feedback-container');
    container.innerHTML = ''; // clear

    data.feedbacks.forEach((fb, index) => {
        const div = document.createElement('div');
        div.className = 'feedback-item';
        div.innerHTML = `
            <strong>Q${index + 1}</strong>: ${fb.is_satisfactory ? "✅" : "❌"} (${fb.rating})<br>
            <small>${fb.feedback}</small>
        `;
        container.appendChild(div);
    });
}
