from fastapi import APIRouter, Depends, HTTPException, status
from src.convBI_engine.convBI import TextToSQLWorkflow
from src.schemas.chat_schemas import ChatRequest
from fastapi import status
from fastapi.responses import JSONResponse
conv_bi_router = APIRouter()


@conv_bi_router.post("/chat-question")
def chat_question(request:ChatRequest):
    question = request.question


    workflow = TextToSQLWorkflow()

    
    try:
        response = workflow.run_workflow(question)
        # print(f"Response: {response}")
        content = {
        "status_code": status.HTTP_200_OK,  # Now using integer status codes
        "message": "Success",
        "body": response
        }
    
        return JSONResponse(
            content=content,
            status_code=status.HTTP_200_OK  # This is the actual HTTP status code
        )
    
    except Exception as e:
            print(f"Error: {e}")
            content = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,  # Now using integer status codes
            "message": "Internal Server Error",
            "body": {"detail": str(e)}
            }
            return JSONResponse(
            content=content,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR  # This is the actual HTTP status code
        )

        


