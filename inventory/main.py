from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from dotenv import load_dotenv
import os

load_dotenv()

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

redis = get_redis_connection(
    host=host, port=port, password=password, decode_responses=True
)


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get("/")
def health():
    return {"message": "Server running successfully"}


@app.get("/products")
def get_all():
    return [Product.get(pk) for pk in Product.all_pks()]


@app.post("/products")
def create_products(product: Product):
    return product.save()


@app.get("/products/{pk}")
def get_single(pk:str):
    return Product.get(pk)


@app.delete("/products/{pk}")
def delete_products(pk: str):
    return  Product.delete(pk)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", reload=True, port=8000)
