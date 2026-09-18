import asyncio
import html
import re

import httpx

from app.core.config import settings


class TallyClient:

    # TallyPrime's built-in HTTP-XML server processes one request at a
    # time. Firing several report calls close together (e.g. the
    # dashboard loading alongside Ledger List / Balance Sheet /
    # Receivables) makes Tally queue them internally, and the later
    # ones blow past our client timeout even though Tally itself is
    # up and working. This lock serializes our own outgoing requests
    # so they queue politely on our side instead.
    _lock = asyncio.Lock()

    def __init__(self):
        self.base_url = settings.tally_url

    @staticmethod
    def _raise_for_tally_error(xml_response: str):
        status_match = re.search(
            r"<STATUS>\s*0\s*</STATUS>",
            xml_response,
            flags=re.IGNORECASE
        )

        if not status_match:
            return

        error_match = re.search(
            r"<LINEERROR>(.*?)</LINEERROR>",
            xml_response,
            flags=re.IGNORECASE | re.DOTALL
        )

        if error_match:
            message = html.unescape(
                error_match.group(1).strip()
            )
        else:
            message = "Tally returned an unsuccessful response"

        raise RuntimeError(message)

    async def check_connection(self):

        try:

            async with httpx.AsyncClient(
                timeout=8.0
            ) as client:

                response = await client.get(
                    self.base_url
                )

            return {
                "connected": True,
                "status_code": response.status_code,
                "url": self.base_url
            }

        except Exception as e:

            return {
                "connected": False,
                "url": self.base_url,
                "error": str(e)
            }

    async def send_xml(
        self,
        xml_payload: str,
        timeout: float = 45.0
    ):

        async with self._lock:

            async with httpx.AsyncClient(
                timeout=timeout
            ) as client:

                response = await client.post(
                    self.base_url,
                    content=xml_payload,
                    headers={
                        "Content-Type": "text/xml"
                    }
                )

                response.raise_for_status()

                xml_response = response.text

                self._raise_for_tally_error(
                    xml_response
                )

                return xml_response