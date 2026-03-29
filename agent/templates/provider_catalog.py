#!/usr/bin/env python3
"""
Provider Catalog Template — OAuth provider catalog in JSON format.

Generates code for: oauth_integration.provider_catalog
"""

from typing import Dict, Any
import json


def generate_provider_catalog_template(task: Dict[str, Any]) -> str:
    """Generate OAuth provider catalog.

    Args:
        task: Task dictionary

    Returns:
        JSON configuration for OAuth providers
    """
    catalog = {
        "name": "OAuth Provider Catalog",
        "version": "1.0.0",
        "description": "Configuration for supported OAuth/OIDC providers",
        "providers": [
            {
                "id": "google",
                "name": "Google",
                "type": "oidc",
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scopes": ["openid", "email", "profile"],
                "default_scope": "openid email profile",
                "pkce_required": True
            },
            {
                "id": "github",
                "name": "GitHub",
                "type": "oauth2",
                "auth_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
                "scopes": ["user:email", "read:user"],
                "default_scope": "user:email read:user",
                "pkce_required": True
            },
            {
                "id": "microsoft",
                "name": "Microsoft",
                "type": "oidc",
                "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "userinfo_url": "https://graph.microsoft.com/v1.0/me",
                "scopes": ["openid", "email", "profile", "User.Read"],
                "default_scope": "openid email profile User.Read",
                "pkce_required": True
            },
            {
                "id": "spotify",
                "name": "Spotify",
                "type": "oauth2",
                "auth_url": "https://accounts.spotify.com/authorize",
                "token_url": "https://accounts.spotify.com/api/token",
                "userinfo_url": "https://api.spotify.com/v1/me",
                "scopes": ["user-read-private", "user-read-email"],
                "default_scope": "user-read-private user-read-email",
                "pkce_required": True
            },
            {
                "id": "discord",
                "name": "Discord",
                "type": "oauth2",
                "auth_url": "https://discord.com/api/oauth2/authorize",
                "token_url": "https://discord.com/api/oauth2/token",
                "userinfo_url": "https://discord.com/api/users/@me",
                "scopes": ["identify", "email"],
                "default_scope": "identify email",
                "pkce_required": True
            }
        ],
        "callback": {
            "default_port": 7823,
            "path": "/callback",
            "protocol": "http"
        },
        "security": {
            "state_parameter_required": True,
            "pkce_required": True,
            "token_validation": "jwt"
        }
    }

    return json.dumps(catalog, indent=2)


def get_task_id() -> str:
    """Return the task ID this template handles."""
    return 'oauth_integration.provider_catalog'


def get_language() -> str:
    """Return the programming language for this template."""
    return 'json'


def get_output_path() -> str:
    """Return the output file path for generated code."""
    return 'data/provider_catalog.json'
