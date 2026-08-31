from fastapi import APIRouter

from src.api.v1.endpoints import (
    analytics,
    categories,
    customers,
    database,
    ml,
    order_items,
    orders,
    products,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(categories.router)
api_router.include_router(customers.router)
api_router.include_router(products.router)
api_router.include_router(orders.router)
api_router.include_router(order_items.router)
api_router.include_router(analytics.router)
api_router.include_router(database.router)
api_router.include_router(ml.router)
