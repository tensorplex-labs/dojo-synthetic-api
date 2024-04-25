import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Assuming code_gen is a FastAPI router imported from your project's module
from commons.routes.code_gen import code_gen_router

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the code_gen router
app.include_router(code_gen_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
