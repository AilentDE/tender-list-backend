from pydantic import BaseModel
from fastapi.responses import JSONResponse


class BaseResponse(BaseModel):
    success: bool = True
    message: str = "ok"
    data: dict | list[dict] | None = None
    detail: str | None = None

    def response(self, status_code: int = 200) -> JSONResponse:
        return JSONResponse(content=self.model_dump(), status_code=status_code)
