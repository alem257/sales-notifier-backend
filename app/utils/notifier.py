import logging
import os

import httpx

logger = logging.getLogger(__name__)


def notify_n8n(payload: dict) -> None:
    url = os.getenv("N8N_WEBHOOK_URL")
    if not url:
        logger.warning("N8N_WEBHOOK_URL no configurada; se omite la notificación.")
        return
    try:
        response = httpx.post(url, json=payload, timeout=15.0)
        response.raise_for_status()
        logger.info("Webhook n8n OK (%s)", response.status_code)
    except httpx.HTTPStatusError as e:
        logger.warning(
            "n8n respondió error HTTP %s: %s",
            e.response.status_code,
            e.response.text[:500] if e.response.text else "",
        )
    except Exception as e:
        logger.warning("Error notificando a n8n: %s", e)
