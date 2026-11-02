from http.server import BaseHTTPRequestHandler
from base64 import b64encode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import os

FIELD_MAP = {
    "Asset Storage: DAM Folder Structure ★★": "customfield_13240",
    "Image Optimization & Weight ★★": "customfield_13241",
    "Stibo DAM: Image & Metadata Integrity ★★": "customfield_13242",
    "Accessibility: Text-in-Image Restriction ★★★": "customfield_13243",
    "Template & Layout Consistency ★★★": "customfield_13244",
    "Multilingual Content: Page Localization ★★★★": "customfield_13245",
    "AEM Blocks: Visual Integrity ★★★★": "customfield_13246",
    "Image Quality & Readability ★★★": "customfield_13247",
    "Breadcrumb ★★★": "customfield_13248",
    "404 Error Handler: Localized Content & Setup ★★★": "customfield_13249",
    "Corporate Ecosystem: Brand Logo ★★": "customfield_13250",
    "Social Media: Official Channels ★★": "customfield_13251",
    "Product Renders: Packshot Accuracy ★★": "customfield_13252",
    "*404 UX Strategy & Navigation ★★★": "customfield_13253",
    "Hamburger Menu ★★★": "customfield_13254",
    "Global Nav & Footer: Link Localization ★★★": "customfield_13255",
    "Internal Search & Indexing ★★★": "customfield_13256",
    "Internal Links ★★★★": "customfield_13257",
    "Anchor Links & URL Parameters ★★★★": "customfield_13258",
    "Breadcrumb: Hierarchy & Link Integrity ★★★": "customfield_13259",
    "Buy Now button ★★★★★": "customfield_13260",
    "Responsive Design: Viewport Adaptability ★★★★": "customfield_13261",
    "WCAG: Color Contrast Ratio ★★★★★": "customfield_13262",
    "Keyboard Navigation: Tab & Focus ★★★★★": "customfield_13263",
    "Semantic HTML: Header Hierarchy ★★★★★": "customfield_13265",
    "Descriptive Alt Attributes ★★★★★": "customfield_13266",
    "Search Metadata: AEM & Pistol Tags ★★★": "customfield_13270",
    "Lead Gen & Forms: Functional Validation ★★★★★": "customfield_13273",
    "Hreflang Tag ★★★★★": "customfield_13274",
    "GTM ★★★★★": "customfield_13276",
    "Titles & Descriptions ★★★★": "customfield_13278",
    "Broken Links (404s) ★★★★★": "customfield_13280",
    "Redirection: 301 ★★★": "customfield_13279",
    "Sitemap.xml Validation ★★★": "customfield_13277",
    "Robots.txt Reference ★★★": "customfield_13275",
    "URL Slug Standardization ★★★": "customfield_13272",
    "Cookie TrustArc ★★★★": "customfield_13271",
    "Cookie Banner Functionality ★★★★": "customfield_13269",
    "Restricted Third-Party Assets ★★★★": "customfield_13268",
    "SSL: Certificate Validity ★★": "customfield_13267",
    "BEX Ticket Mandatory Fields ★★": "customfield_13264",
}


def _revert_field(issue_key, customfield, original_value, email, token, base_url):
    url = f"{base_url.rstrip('/')}/rest/api/3/issue/{issue_key}"
    payload = json.dumps({
        "fields": {
            customfield: {"value": original_value},
        }
    }).encode("utf-8")
    credentials = b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
    request = Request(
        url,
        data=payload,
        method="PUT",
        headers={
            "Authorization": f"Basic {credentials}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with urlopen(request, timeout=30) as response:
        return response.getcode()


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_response(400, {"error": "El cuerpo de la petición está vacío"})
                return

            body = json.loads(self.rfile.read(content_length).decode("utf-8"))

            issue_key = body.get("issueKey")
            field_name = body.get("fieldName")
            original_value = body.get("originalValue")
            email = body.get("email")
            token = body.get("token")

            missing = [
                name
                for name, value in (
                    ("issueKey", issue_key),
                    ("fieldName", field_name),
                    ("originalValue", original_value),
                    ("email", email),
                    ("token", token),
                )
                if not value
            ]
            if missing:
                self._send_response(400, {"error": f"Faltan campos requeridos: {', '.join(missing)}"})
                return

            customfield = FIELD_MAP.get(field_name)
            if not customfield:
                self._send_response(400, {"error": f"Campo desconocido: {field_name}"})
                return

            base_url = os.environ.get("JIRA_BASE_URL")
            if not base_url:
                self._send_response(500, {"error": "Falta la variable de entorno JIRA_BASE_URL"})
                return

            try:
                _revert_field(issue_key, customfield, original_value, email, token, base_url)
            except HTTPError as e:
                detail = e.read().decode("utf-8", errors="replace")
                self._send_response(502, {"error": "Error al actualizar Jira", "status": e.code, "detail": detail})
                return
            except URLError as e:
                self._send_response(502, {"error": f"No se pudo conectar con Jira: {e.reason}"})
                return

            self._send_response(200, {
                "ok": True,
                "issueKey": issue_key,
                "customfield": customfield,
            })

        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_response(self, code, payload):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())
