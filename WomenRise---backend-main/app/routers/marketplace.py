"""Marketplace router — products + orders. TO BE IMPLEMENTED.

Endpoints (prefix /api):
  GET   /api/products?category=       -> List[ProductOut]
  GET   /api/products/{id}            -> ProductOut
  POST  /api/products (auth)  body=ProductCreate -> ProductOut  (seller = current user)
  GET   /api/products/mine (auth)     -> List[ProductOut]       (current user's listings)
  POST  /api/orders (auth)    body=OrderCreate   -> OrderOut    (decrement stock)
  GET   /api/orders (auth)            -> List[OrderOut]         (current user's)
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/api", tags=["marketplace"])


# NOTE: /products/mine must be declared BEFORE /products/{id} so FastAPI
# doesn't treat "mine" as an integer id.
@router.get("/products/mine", response_model=List[schemas.ProductOut])
def my_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Product).filter(models.Product.seller_id == current_user.id).all()


@router.get("/products", response_model=List[schemas.ProductOut])
def list_products(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Product)
    if category:
        query = query.filter(models.Product.category == category)
    return query.all()


@router.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/products", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    body: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    product = models.Product(
        seller_id=current_user.id,
        title=body.title,
        description=body.description,
        category=body.category,
        price=body.price,
        image_url=body.image_url,
        stock=body.stock,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.post("/orders", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    body: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not body.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must have at least one item")

    # Validate all products exist and have sufficient stock before any mutation
    resolved = []
    for item_in in body.items:
        product = db.query(models.Product).filter(models.Product.id == item_in.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item_in.product_id} not found",
            )
        if product.stock < item_in.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product '{product.title}'",
            )
        resolved.append((product, item_in.quantity))

    total = sum(p.price * qty for p, qty in resolved)

    order = models.Order(buyer_id=current_user.id, total=total)
    db.add(order)
    db.flush()  # get order.id without full commit

    for product, qty in resolved:
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            unit_price=product.price,
            title=product.title,
        )
        db.add(order_item)
        product.stock -= qty

    db.commit()
    db.refresh(order)
    return order


@router.get("/orders", response_model=List[schemas.OrderOut])
def my_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Order).filter(models.Order.buyer_id == current_user.id).all()
