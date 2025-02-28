from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OrderData(BaseModel):
    productUrl: str
    quantity: int

@app.post("/trigger-script")
def trigger_script(data: OrderData):
    # Adjust the path separator to be safe:
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "ali-order.py")
    try:
        subprocess.run(["python3", script_path, data.productUrl, str(data.quantity)], check=True)
        return {"message": "Script executed successfully"}
    except subprocess.CalledProcessError as e:
        return {"error": f"Script execution failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)