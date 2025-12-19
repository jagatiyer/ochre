from django import template
from bs4 import BeautifulSoup

register = template.Library()

@register.simple_tag
def first_image_src(html_content):
    """Return the src of the first <img> found in html_content or empty string."""
    if not html_content:
        return ""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            return img.get("src")
    except Exception:
        return ""
    return ""
