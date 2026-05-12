"""
轻量级内容抓取模块

从网页链接提取正文内容。纯文本输入直接透传。
"""

import logging
import re

logger = logging.getLogger(__name__)


async def fetch_content(source: str, source_type: str = "text") -> str:
    """
    根据来源类型获取纯文本内容。

    - text: 直接返回原文
    - web_link: 抓取网页正文
    - 其他类型: 直接返回原文（后续可扩展）
    """
    if source_type == "text":
        return source

    if source_type == "web_link":
        return await _fetch_web(source)

    # image / douyin_video 暂不支持，返回原文让 LLM 根据 URL 尽力理解
    logger.warning("Source type '%s' not fully supported, passing through", source_type)
    return source


async def _fetch_web(url: str) -> str:
    """抓取网页正文"""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; DanshenBot/1.0)"},
            )
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        logger.warning("Failed to fetch URL: %s", e)
        return url  # 返回原始 URL，让 LLM 根据 URL 尽力理解

    # 尝试用 trafilatura 提取正文（如果可用）
    try:
        import trafilatura
        text = trafilatura.extract(html, include_links=False, include_images=False)
        if text and len(text.strip()) > 50:
            return text.strip()
    except ImportError:
        pass

    # 回退：简单 HTML 标签清理
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) < 50:
        return url
    return text[:5000]
