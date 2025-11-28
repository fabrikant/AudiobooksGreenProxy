from math import e
import aiohttp
import tempfile
from fastapi.responses import FileResponse
from fastapi import HTTPException
from pydantic import BaseModel


class AudiobookshelfProgressItem(BaseModel):
    libraryItemId: str
    currentTime: float
    progress: float


class AudiobookshelfProgress(BaseModel):
    server: str
    token: str
    items: list[AudiobookshelfProgressItem]


def sanitze_server_name(server):
    result = server
    if not result.startswith("https://"):
        result = "https://" + result
    if "/" in result[-1]:
        result = result[:-1]
    return result


def get_book_info(resp_book):
    res = {
        "id": resp_book["id"],
        "author": "",
        "title": resp_book["media"]["metadata"]["title"],
        # "cover": resp_book["media"]["coverPath"],
    }
    if len(resp_book["media"]["metadata"]["authors"]) > 0:
        res["author"] = resp_book["media"]["metadata"]["authors"][0]["name"]
    return res


async def get_playlists(server, token):
    result = []
    url = f"{sanitze_server_name(server)}/api/playlists"
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.ok:
                    resp_json = await resp.json()
                    for resp_playlist in resp_json["playlists"]:
                        result.append(
                            {
                                "id": resp_playlist["id"],
                                "libraryId": resp_playlist["libraryId"],
                                "name": resp_playlist["name"],
                            }
                        )
                else:
                    resp_content_b = await resp.content.read()
                    raise HTTPException(
                        status_code=resp.status,
                        detail=resp_content_b.decode("utf-8"),
                    )
        except aiohttp.ClientConnectorError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Network connection error to Audiobookshelf server: {e}",
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while fetching playlists: {e}",
            )

    return result


async def get_playlist(server, playlist_id, token):
    result = []
    url = f"{sanitze_server_name(server)}/api/playlists/{playlist_id}"
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.ok:
                    resp_json = await resp.json()
                    for resp_book in resp_json["items"]:
                        result.append(get_book_info(resp_book["libraryItem"]))
                else:
                    resp_content_b = await resp.content.read()
                    raise HTTPException(
                        status_code=resp.status,
                        detail=resp_content_b.decode("utf-8"),
                    )
        except aiohttp.ClientConnectorError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Network connection error to Audiobookshelf server: {e}",
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while fetching playlist: {e}",
            )

    return result


async def get_book(server, book_id, token, skip=0, limit=0):
    result = {}
    url = f"{sanitze_server_name(server)}/api/items/{book_id}"
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.ok:
                    resp_book = await resp.json()
                    result = get_book_info(resp_book)

                    files_list_on_server = resp_book["media"]["audioFiles"]
                    result["total"] = len(files_list_on_server)
                    result["skip"] = skip
                    result["limit"] = limit
                    files = []
                    counter = 0
                    added = 0
                    for file in files_list_on_server:
                        if counter >= skip and (
                            limit == 0 or (limit > 0 and added < limit)
                        ):
                            added += 1
                            files.append(
                                {
                                    "filename": file["metadata"]["filename"],
                                    "duration": file["duration"],
                                    "id": file["ino"],
                                }
                            )
                        counter += 1
                    result["files"] = files
                else:
                    resp_content_b = await resp.content.read()
                    raise HTTPException(
                        status_code=resp.status,
                        detail=resp_content_b.decode("utf-8"),
                    )
        except aiohttp.ClientConnectorError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Network connection error to Audiobookshelf server: {e}",
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while fetching book details: {e}",
            )

    return result


async def get_token(server, login, password):
    result = {}
    url = f"{sanitze_server_name(server)}/login"
    json_data = {"username": login, "password": password}
    headers = {"Content-Type": "application/json", "x-return-tokens": "true"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=json_data) as resp:
                if resp.ok:
                    resp_json = await resp.json()
                    keys_list = ["token", "refreshToken", "accessToken"]
                    for key_name in keys_list:
                        if key_name in resp_json["user"].keys():
                            result[key_name] = resp_json["user"][key_name]
                else:
                    resp_content_b = await resp.content.read()
                    raise HTTPException(
                        status_code=resp.status,
                        detail=resp_content_b.decode("utf-8"),
                    )
        except aiohttp.ClientConnectorError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Network connection error to Audiobookshelf server: {e}",
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while getting token: {e}",
            )

    return result


async def get_cover(url):
    if "api/items" in url and "cover" in url:
        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False)
        cover_filename = tmp_file.name
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.ok:
                        data = await resp.read()
                        try:
                            with open(cover_filename, "wb") as f:
                                f.write(data)
                            return FileResponse(cover_filename)
                        except IOError as e:
                            raise HTTPException(
                                status_code=500,
                                detail=f"Failed to write cover image to temporary file: {e}",
                            )
                    else:
                        resp_content_b = await resp.content.read()
                        raise HTTPException(
                            status_code=resp.status,
                            detail=f"Failed to fetch cover image: {resp_content_b.decode('utf-8')}",
                        )
            except aiohttp.ClientConnectorError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Network connection error while fetching cover: {e}",
                )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"An unexpected error occurred while fetching cover: {e}",
                )

    return None


async def set_progress(data):
    url = sanitze_server_name(data.server)
    url += "/api/me/progress/batch/update"
    headers = {
        "Authorization": f"Bearer {data.token}",
        "Content-Type": "application/json",
    }
    req_data = []
    for item in data.items:
        req_data.append(
            {
                "libraryItemId": item.libraryItemId,
                "currentTime": item.currentTime,
                "progress": item.progress,
            }
        )
    async with aiohttp.ClientSession() as session:
        try:
            async with session.patch(url, headers=headers, json=req_data) as resp:
                if resp.ok:
                    return await resp.text()
                else:
                    resp_content_b = await resp.content.read()
                    raise HTTPException(
                        status_code=resp.status,
                        detail=resp_content_b.decode("utf-8"),
                    )
        except aiohttp.ClientConnectorError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Network connection error to Audiobookshelf server: {e}",
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while setting progress: {e}",
            )
