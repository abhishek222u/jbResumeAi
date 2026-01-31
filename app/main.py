from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api import resume_extract, resume_parse, question_gnerator
from app.api import interview, tts_routes

app = FastAPI(title="Resume Parser & Interview Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev (or ["http://localhost:5173"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/storage", StaticFiles(directory="app/storage"), name="storage") # For Audio Playback

# Serve Index on Root
@app.get("/")
async def read_index():
    return FileResponse("app/static/index.html")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/avatar.png")

app.include_router(resume_extract.router)       
app.include_router(resume_parse.router)
app.include_router(question_gnerator.router)


app.include_router(interview.router)
app.include_router(tts_routes.router)
