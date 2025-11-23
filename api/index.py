from fastapi import FastAPI, Query, Path, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import httpx
import uvicorn

app = FastAPI(title="音乐资源代理服务器", description="使用FastAPI实现的音乐资源代理转发服务")

# 基础URL
BASE_URL = "https://www.lihouse.xyz/coco_widget/music_resource"


# 自定义参数验证：确保limit是5的倍数
def validate_limit(limit: int) -> int:
    if limit % 5 != 0:
        raise ValueError("limit必须是5的倍数")
    return limit


# 全局异常处理器
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": False, "msg": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"status": False, "msg": f"请求参数错误: {exc.errors()}"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": False, "msg": f"服务器内部错误: {str(exc)}"}
    )


@app.get("/")
def read_root():
    return {"message": "音乐资源代理服务器正在运行"}


@app.get("/api/music/search", tags=["音乐搜索"])
async def search_music(
        key: str = Query(..., description="歌曲昵称"),
        page: int = Query(1, ge=1, description="页码"),
        limit: int = Query(10, ge=1, le=15, description="每页数量，必须是5的倍数")
):
    print(key, page, limit)
    # 使用自定义验证函数验证limit参数必须是5的倍数
    try:
        validate_limit(limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 构建目标URL
    target_url = f"{BASE_URL}/info?key={key}&page={page}&limit={limit}"

    # 使用httpx发送异步请求，设置超时时间为10秒
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(target_url)
        # 检查响应状态码
        response.raise_for_status()
        # 返回原始响应的JSON数据
        return response.json()


@app.get("/api/music/detail/{music_id}", tags=["音乐详情"])
async def get_music_detail(
        music_id: int = Path(..., ge=1, description="音乐ID")
):
    # 构建目标URL
    target_url = f"{BASE_URL}/id/{music_id}"

    # 使用httpx发送异步请求，设置超时时间为10秒
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(target_url)
        # 检查响应状态码
        response.raise_for_status()
        # 返回原始响应的JSON数据
        return response.json()

