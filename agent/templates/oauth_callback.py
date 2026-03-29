#!/usr/bin/env python3
"""
OAuth Callback Template — OAuth callback server implementation for Python.

Generates code for: oauth_integration.callback_server
"""

from typing import Dict, Any


def generate_oauth_callback_template(task: Dict[str, Any]) -> str:
    """Generate OAuth callback server implementation.

    Args:
        task: Task dictionary

    Returns:
        Python code for OAuth callback server
    """
    return '''"""
Auto-generated OAuth callback server
Task: oauth_integration.callback_server
"""

import http.server
import socketserver
import urllib.parse
import json
from typing import Optional, Dict, Any


class CallbackResponse:
    """Response from OAuth callback."""

    def __init__(self, code: Optional[str] = None,
                 state: Optional[str] = None,
                 error: Optional[str] = None):
        self.code = code
        self.state = state
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'state': self.state,
            'error': self.error
        }


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""

    callback_response: Optional[CallbackResponse] = None

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urllib.parse.urlparse(self.path)

        if parsed_path.path == '/callback':
            query_params = urllib.parse.parse_qs(parsed_path.query)

            self.callback_response = CallbackResponse(
                code=query_params.get('code', [None])[0],
                state=query_params.get('state', [None])[0],
                error=query_params.get('error', [None])[0]
            )

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = self.get_success_html()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def get_success_html(self) -> str:
        """Get success HTML response."""
        return """<!DOCTYPE html>
<html>
<head><title>OAuth Callback Successful</title></head>
<body>
<h1>Authentication Successful!</h1>
<p>You can close this window and return to the application.</p>
<script>window.close();</script>
</body>
</html>"""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class OAuthCallbackServer:
    """OAuth callback server."""

    def __init__(self, port: int = 7823):
        self.port = port
        self.server: Optional[socketserver.TCPServer] = None

    def wait_for_callback(self) -> CallbackResponse:
        """Start server and wait for OAuth callback.

        Returns:
            CallbackResponse with authorization code and state
        """
        with socketserver.TCPServer(("127.0.0.1", self.port),
                                    OAuthCallbackHandler) as httpd:
            print(f"OAuth callback server listening on port {self.port}")
            httpd.handle_request()

            if OAuthCallbackHandler.callback_response:
                return OAuthCallbackHandler.callback_response
            else:
                raise Exception("No callback received")


if __name__ == "__main__":
    server = OAuthCallbackServer()
    response = server.wait_for_callback()
    print(f"Received callback: {response.to_dict()}")
'''


def get_task_id() -> str:
    """Return the task ID this template handles."""
    return 'oauth_integration.callback_server'


def get_language() -> str:
    """Return the programming language for this template."""
    return 'python'


def get_output_path() -> str:
    """Return the output file path for generated code."""
    return 'src/oauth/callback_server.py'
