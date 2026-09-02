import html
import re

import httpx

from app.core.config import settings


class TallyClient:
    _shared_client: httpx.AsyncClient | None = None

    def __init__(self):
        self.base_url = settings.tally_url

    @classmethod
    async def start_shared_client(cls) -> None:
        """
        Create the HTTP client used by the running API.

        The shared client allows HTTP connections to be
        reused instead of creating a new connection for
        every Tally request.
        """
        if cls._shared_client is not None:
            return

        cls._shared_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(
                max_connections=20,
                max_keepalive_connections=10,
            ),
        )

    @classmethod
    async def close_shared_client(cls) -> None:
        """
        Close the shared HTTP client during application
        shutdown.
        """
        if cls._shared_client is None:
            return

        await cls._shared_client.aclose()

        cls._shared_client = None

    @staticmethod
    def _raise_for_tally_error(
        xml_response: str,
    ) -> None:
        status_match = re.search(
            r"<STATUS>\s*0\s*</STATUS>",
            xml_response,
            flags=re.IGNORECASE,
        )

        if not status_match:
            return

        error_match = re.search(
            r"<LINEERROR>(.*?)</LINEERROR>",
            xml_response,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if error_match:
            message = html.unescape(
                error_match.group(1).strip()
            )
        else:
            message = (
                "Tally returned an unsuccessful response"
            )

        raise RuntimeError(message)

    async def check_connection(self) -> dict:
        try:
            if self._shared_client is not None:
                response = await self._shared_client.get(
                    self.base_url,
                    timeout=8.0,
                )

            else:
                # Fallback keeps direct unit tests and
                # standalone usage working even when the
                # FastAPI lifespan has not started.
                async with httpx.AsyncClient(
                    timeout=8.0
                ) as client:
                    response = await client.get(
                        self.base_url
                    )

            return {
                "connected": True,
                "status_code": response.status_code,
                "url": self.base_url,
            }

        except Exception as exc:
            return {
                "connected": False,
                "url": self.base_url,
                "error": str(exc),
            }

    async def send_xml(
        self,
        xml_payload: str,
        timeout: float = 30.0,
    ) -> str:
        if self._shared_client is not None:
            response = await self._shared_client.post(
                self.base_url,
                content=xml_payload,
                headers={
                    "Content-Type": "text/xml",
                },
                timeout=timeout,
            )

        else:
            # Fallback for tests or standalone calls where
            # the FastAPI application lifespan is not active.
            async with httpx.AsyncClient(
                timeout=timeout
            ) as client:
                response = await client.post(
                    self.base_url,
                    content=xml_payload,
                    headers={
                        "Content-Type": "text/xml",
                    },
                )

        response.raise_for_status()

        xml_response = response.text

        self._raise_for_tally_error(
            xml_response
        )

        return xml_response