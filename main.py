import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Order, ContactMessage

app = FastAPI(title="KFC Website API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic root and health
@app.get("/")
def read_root():
    return {"message": "KFC API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Menu endpoints (static list for demo; could be stored in DB later)
class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    image: Optional[str] = None


MENU: List[MenuItem] = [
    MenuItem(id="zinger-burger", name="Zinger Burger", description="Crispy chicken fillet with fresh lettuce and mayo.", price=5.99, category="Burgers", image="/images/zinger.jpg"),
    MenuItem(id="bucket-8", name="8pc Chicken Bucket", description="Eight pieces of our world-famous fried chicken.", price=14.99, category="Buckets", image="/images/bucket.jpg"),
    MenuItem(id="twister", name="Twister Wrap", description="Grilled tortilla with crispy chicken and tangy sauce.", price=4.99, category="Wraps", image="/images/twister.jpg"),
    MenuItem(id="fries", name="Large Fries", description="Golden fries with signature seasoning.", price=2.49, category="Sides", image="/images/fries.jpg"),
]

@app.get("/api/menu", response_model=List[MenuItem])
def get_menu():
    return MENU

# Orders
@app.post("/api/orders")
def create_order(order: Order):
    try:
        order_id = create_document("order", order)  # collection is lowercase class name
        return {"success": True, "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Contact messages
@app.post("/api/contact")
def submit_contact(message: ContactMessage):
    try:
        msg_id = create_document("contactmessage", message)
        return {"success": True, "message_id": msg_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
