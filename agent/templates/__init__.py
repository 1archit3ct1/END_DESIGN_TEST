#!/usr/bin/env python3
"""
Template Library — Code templates for Phase 9.

This package contains templates for:
- PKCE (RFC 7636) implementation
- OAuth callback server
- Provider catalog
- Token keychain storage
"""

from .pkce import generate_pkce_template, get_task_id as pkce_task_id
from .oauth_callback import generate_oauth_callback_template, get_task_id as oauth_callback_task_id
from .provider_catalog import generate_provider_catalog_template, get_task_id as provider_catalog_task_id
from .token_keychain import generate_token_keychain_template, get_task_id as token_keychain_task_id

__all__ = [
    'generate_pkce_template',
    'generate_oauth_callback_template',
    'generate_provider_catalog_template',
    'generate_token_keychain_template',
    'pkce_task_id',
    'oauth_callback_task_id',
    'provider_catalog_task_id',
    'token_keychain_task_id',
]
