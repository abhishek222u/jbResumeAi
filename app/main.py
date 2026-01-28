from fastapi import FastAPI
from app.api import resume_extract, resume_parse, question_gnerator
app = FastAPI(title="Resume Parser & Interview Generator API")
app.include_router(resume_extract.router)       
app.include_router(resume_parse.router)
app.include_router(question_gnerator.router)