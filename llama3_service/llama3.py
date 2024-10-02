from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# FastAPI app instance with debugging enabled
app = FastAPI(debug=True)

# Load the summarization pipeline from Hugging Face's transformers library
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Pydantic model for input
class SummaryRequest(BaseModel):
    content: str

# Endpoint to generate a summary
@app.post("/generate-summary/")
async def generate_summary(request: SummaryRequest):
    try:
        # Use the summarizer model to generate a summary
        summary = summarizer(
            request.content,
            max_length=450,
            min_length=40,
            do_sample=False,
            clean_up_tokenization_spaces=False  # Avoid future warnings
        )
        return {"summary": summary[0]['summary_text']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
