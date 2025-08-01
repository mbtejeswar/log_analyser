from fastapi import FastAPI
from pydantic import BaseModel
from rca_service import perform_root_cause_analysis

app = FastAPI()

class RCARequest(BaseModel):
    error_log: str

@app.post("/analyze")
def analyze_error(request: RCARequest):
    """API endpoint to trigger a root cause analysis."""
    result = perform_root_cause_analysis(request.error_log)
    return result

# To run this server: uvicorn main_rca_agent:app --reload
