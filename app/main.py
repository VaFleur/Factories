from fastapi import FastAPI
from app.routers.factory_router import factory_router
from app.routers.department_router import department_router
from app.routers.equipment_router import equipment_router

app = FastAPI()

for router in [factory_router, department_router, equipment_router]:
    app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
