from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from dotenv import load_dotenv
import os
import httpx

load_dotenv()
PRODUCT_SERVICE_URL = "http://localhost:8000/products"

host = os.getenv("HOST")
port = int(os.getenv("PORT"))
password = os.getenv("PASSWORD")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# this can be any other db but here for ease I am using same
redis = get_redis_connection(
    host=host, port=port, password=password, decode_responses=True
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis

def order_complelte(order: Order):
    order.status = "completed"
    return order.save()

@app.get("/")
def health():
    return {"message": "Server running successfully"}


@app.post("/orders")
async def create(request: Request):
    body = await request.json()
    print("body", body)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PRODUCT_SERVICE_URL}/{body['id']}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Product not found")

    product = response.json()
    
    # Now create the order
    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=product['price'] * 0.2,
        total=product['price'] * 1.2,
        quantity=body['quantity'],
        status="pending"
    )
    order.save()
    # order_complelte(order)
    return order


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", reload=True, port=8001)
