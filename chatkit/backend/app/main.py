"""FastAPI entrypoint for the ChatKit starter backend."""

from __future__ import annotations

from chatkit.server import StreamingResult
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

from .server import StarterChatServer

app = FastAPI(title="ChatKit Starter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatkit_server = StarterChatServer()


@app.post("/chatkit")
async def chatkit_endpoint(request: Request) -> Response:
    """Proxy the ChatKit web component payload to the server implementation."""
    payload = await request.body()
    result = await chatkit_server.process(payload, {"request": request})

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)
    @app.api_route(
    "/attachments/{attachment_id}/upload",
    methods=["POST", "PUT"],
    name="upload_attachment",
)
async def upload_attachment(
    attachment_id: str,
    request: Request,
):
    content_type = request.headers.get("content-type", "").lower()

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        file = form.get("file")

        if file is None or not hasattr(file, "read"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multipart uploads must include a 'file' field.",
            )

        data = await file.read()
    else:
        data = await request.body()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attachment payload is required.",
        )

    attachment = await chatkit_server.attachment_uploader.write_file(
        attachment_id,
        data,
        {"request": request},
    )

    return attachment.model_dump()
    @app.get(
    "/attachments/{attachment_id}/content",
    name="download_attachment",
)
async def download_attachment(
    attachment_id: str,
    request: Request,
) -> Response:
    attachment, data = await chatkit_server.attachment_uploader.read_file(
        attachment_id,
        {"request": request},
    )

    return Response(
        content=data,
        media_type=attachment.mime_type,
        headers={
            "Cache-Control": "private, max-age=600",
            "Content-Disposition": f'inline; filename="{attachment.name}"',
            "Access-Control-Allow-Origin": "*",
        },
    )
