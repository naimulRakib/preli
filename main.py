from fastapi import FastAPI, HTTPException
from models import TicketRequest, TicketResponse, HealthResponse
from classifier import classify_ticket

app = FastAPI(title="Ticket Sorter", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    print("Ticket Sorter service started")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", service="ticket-sorter")

@app.post("/sort-ticket", response_model=TicketResponse)
async def sort_ticket(request: TicketRequest):
    try:
        result = classify_ticket(
            ticket_id=request.ticket_id,
            message=request.message,
            channel=request.channel or "",
            locale=request.locale or ""
        )
        return TicketResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
