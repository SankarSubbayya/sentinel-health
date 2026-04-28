from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from app.api import routes

app = FastAPI(
    title="Sentinel Health",
    description="Clinical decision support system for resource-limited settings",
    version="0.1.0",
)

app.include_router(routes.router)


@app.get("/demo")
async def demo():
    """Serve demo HTML page."""
    demo_path = Path(__file__).parent / "demo" / "index.html"
    if demo_path.exists():
        return FileResponse(demo_path, media_type="text/html")
    else:
        return {"error": "Demo page not found"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
