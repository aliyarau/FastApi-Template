from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import ORJSONResponse

from api.deps.auth import TokenUser, get_current_user

router = APIRouter()


@router.get('/example/of/protected/route')
def example(request: Request, user: Annotated[TokenUser, Depends(get_current_user)]) -> ORJSONResponse:
    """
    Проверка системы аутентификации из LDAP

    Этот запрос используется для проверки работы системы аутентификации через LDAP.
    Он возвращает эхо заголовков (Headers), которые были получены от клиента.

    **Как использовать:**
    1. Выполните регистрацию пользователя.
    2. Проверьте, что при отправке запроса с авторизацией через LDAP возвращается эхо заголовков.
    3. После выполнения регистрации проверьте, что при попытке доступа без авторизации будет возвращена ошибка авторизации.

    **Параметры:**
    - `request`: Объект запроса, содержащий заголовки, которые будут возвращены в ответе.
    - `user`: Информация о текущем авторизованном пользователе, полученная с помощью зависимостей, связанной с процессом аутентификации через LDAP.

    **Ответ:**
    - Код состояния: 200 OK
    - Тело ответа: JSON объект с ключом `X-HEADERS-ECHO`, содержащий эхо всех заголовков запроса.

    **Пример запроса:**
    ```
    GET /example/of/protected/route
    ```

    **Пример ответа:**
    ```json
    {
      "X-HEADERS-ECHO": {
        "User-Agent": "Mozilla/5.0",
        "Authorization": "Bearer <token>"
      }
    }
    ```

    **Ошибки:**
    - 401 Unauthorized: В случае, если пользователь не прошел аутентификацию через LDAP.
    """
    return ORJSONResponse(
        content={"X-HEADERS-ECHO": dict(request.headers), "X-User": dict(asdict(user))}, status_code=status.HTTP_200_OK
    )
