#!/usr/bin/env python3
"""
Template Coder — Generate code from Python templates.

Includes import statement generation for different languages.
"""

from typing import Optional, Dict, Any, List

from .logger import setup_logger

logger = setup_logger(__name__)


# Import templates per language
IMPORT_TEMPLATES = {
    'rust': {
        'http': 'use reqwest::{Client, Response};',
        'json': 'use serde_json::{json, Value};',
        'serde': 'use serde::{Deserialize, Serialize};',
        'tokio': 'use tokio;\nuse tokio::runtime::Runtime;',
        'base64': 'use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine};',
        'sha2': 'use sha2::{Digest, Sha256};',
        'rand': 'use rand::RngCore;',
        'tiny_http': 'use tiny_http::{Server, Response, Header, StatusCode};',
        'keyring': 'use keyring::Entry;',
        'urlencoding': 'use urlencoding;',
        'std_collections': 'use std::collections::HashMap;',
        'std_sync': 'use std::sync::mpsc::channel;',
        'std_thread': 'use std::thread;',
        'std_time': 'use std::time::{SystemTime, UNIX_EPOCH};',
        'std_io': 'use std::io::{self, Read, Write};',
        'std_fs': 'use std::fs;',
        'std_path': 'use std::path::{Path, PathBuf};',
        'std_error': 'use std::error::Error;',
        'thiserror': 'use thiserror::Error;',
        'anyhow': 'use anyhow::{Result, Context};',
    },
    'typescript': {
        'http': "import http from 'http';",
        'https': "import https from 'https';",
        'url': "import url from 'url';",
        'fs': "import fs from 'fs/promises';",
        'path': "import path from 'path';",
        'crypto': "import crypto from 'crypto';",
        'events': "import { EventEmitter } from 'events';",
        'fetch': "import fetch from 'node-fetch';",
        'express': "import express, { Request, Response } from 'express';",
        'axios': "import axios from 'axios';",
        'react': "import React, { useState, useEffect } from 'react';",
        'react_dom': "import ReactDOM from 'react-dom';",
    },
    'python': {
        'http': 'import http.client',
        'requests': 'import requests',
        'json': 'import json',
        'os': 'import os',
        'sys': 'import sys',
        'pathlib': 'from pathlib import Path',
        'datetime': 'from datetime import datetime, timedelta',
        'typing': 'from typing import Dict, List, Optional, Any, Tuple',
        'hashlib': 'import hashlib',
        'base64': 'import base64',
        'secrets': 'import secrets',
        'urllib': 'from urllib.parse import urlencode, parse_qs',
        'logging': 'import logging',
        'asyncio': 'import asyncio',
        'flask': 'from flask import Flask, request, jsonify',
        'fastapi': 'from fastapi import FastAPI, Request, HTTPException',
    },
}


class TemplateCoder:
    """Generate code from templates for known patterns."""

    def __init__(self):
        """Initialize template coder."""
        self.templates = self._load_templates()

    def generate_imports(self, language: str, modules: List[str]) -> str:
        """Generate import statements for given modules.

        Args:
            language: Programming language (rust, typescript, python)
            modules: List of module names to import

        Returns:
            Import statements string
        """
        lang_templates = IMPORT_TEMPLATES.get(language.lower(), {})
        imports = []

        for module in modules:
            if module in lang_templates:
                imports.append(lang_templates[module])
            else:
                # Generate generic import for unknown modules
                if language.lower() == 'rust':
                    imports.append(f'use {module};')
                elif language.lower() in ['typescript', 'javascript']:
                    imports.append(f"import {{ }} from '{module}';")
                elif language.lower() == 'python':
                    imports.append(f'import {module}')

        return '\n'.join(imports)

    def get_import_for_module(self, language: str, module: str) -> Optional[str]:
        """Get import statement for a specific module.

        Args:
            language: Programming language
            module: Module name

        Returns:
            Import statement or None
        """
        lang_templates = IMPORT_TEMPLATES.get(language.lower(), {})
        return lang_templates.get(module)

    def generate_code(self, task: Dict[str, Any]) -> Optional[str]:
        """Generate code from template.

        Args:
            task: Task dictionary with id, name, desc

        Returns:
            Generated code string or None
        """
        task_id = task.get('id', '')

        if task_id in self.templates:
            logger.info(f"Using template for task: {task_id}")
            return self.templates[task_id](task)
        else:
            logger.warning(f"No template found for task: {task_id}")
            return None

    def generate_fallback_code(self, task: Dict[str, Any],
                               language: Optional[str] = None) -> str:
        """Generate fallback code when LLM fails.

        Creates a minimal but valid code structure based on task type.

        Args:
            task: Task dictionary with id, name, desc
            language: Optional language override (auto-detected if not provided)

        Returns:
            Fallback code string
        """
        if language is None:
            language = self._detect_language(task)

        task_id = task.get('id', 'unknown')
        task_name = task.get('name', 'Unknown Task')
        task_desc = task.get('desc', 'No description')

        logger.warning(f"Generating fallback code for task: {task_id}")

        if language == 'rust':
            return self._generate_rust_fallback(task_id, task_name, task_desc)
        elif language == 'typescript':
            return self._generate_typescript_fallback(task_id, task_name, task_desc)
        elif language == 'python':
            return self._generate_python_fallback(task_id, task_name, task_desc)
        else:
            return self._generate_typescript_fallback(task_id, task_name, task_desc)

    def _detect_language(self, task: Dict[str, Any]) -> str:
        """Detect programming language from task.

        Args:
            task: Task dictionary

        Returns:
            Language name
        """
        task_id = task.get('id', '').lower()

        if 'rust' in task_id or 'backend' in task_id:
            return 'rust'
        elif 'python' in task_id or 'agent' in task_id:
            return 'python'
        else:
            return 'typescript'

    def _generate_rust_fallback(self, task_id: str, task_name: str,
                                 task_desc: str) -> str:
        """Generate minimal Rust fallback code.

        Args:
            task_id: Task identifier
            task_name: Task name
            task_desc: Task description

        Returns:
            Rust code string
        """
        return f'''// Auto-generated fallback code - LLM generation failed
// Task: {task_id}
// Name: {task_name}
// Description: {task_desc}
// Note: This is a placeholder. Please implement the actual functionality.

/// {task_name}
/// TODO: Implement {task_name} functionality
pub struct {self._to_pascal_case(task_name)} {{
    // TODO: Add fields
}}

impl {self._to_pascal_case(task_name)} {{
    /// Create new instance
    pub fn new() -> Self {{
        Self {{
            // TODO: Initialize fields
        }}
    }}

    /// Execute {task_name}
    /// TODO: Implement the main functionality
    pub fn execute(&self) -> Result<(), Box<dyn std::error::Error>> {{
        // TODO: Implement functionality
        Ok(())
    }}
}}

impl Default for {self._to_pascal_case(task_name)} {{
    fn default() -> Self {{
        Self::new()
    }}
}}

#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn test_{self._to_snake_case(task_name)}_creation() {{
        let instance = {self._to_pascal_case(task_name)}::new();
        // TODO: Add assertions
    }}
}}
'''

    def _generate_typescript_fallback(self, task_id: str, task_name: str,
                                       task_desc: str) -> str:
        """Generate minimal TypeScript fallback code.

        Args:
            task_id: Task identifier
            task_name: Task name
            task_desc: Task description

        Returns:
            TypeScript code string
        """
        return f'''// Auto-generated fallback code - LLM generation failed
// Task: {task_id}
// Name: {task_name}
// Description: {task_desc}
// Note: This is a placeholder. Please implement the actual functionality.

/**
 * {task_name}
 * TODO: Implement {task_name} functionality
 */
export class {self._to_pascal_case(task_name)} {{
  // TODO: Add properties

  /**
   * Create new instance
   */
  constructor() {{
    // TODO: Initialize properties
  }}

  /**
   * Execute {task_name}
   * TODO: Implement the main functionality
   */
  public async execute(): Promise<void> {{
    // TODO: Implement functionality
    throw new Error('Not implemented');
  }}
}}

// TODO: Add interfaces and types as needed
export interface {self._to_pascal_case(task_name)}Config {{
  // TODO: Add configuration options
}}

// TODO: Add helper functions as needed
'''

    def _generate_python_fallback(self, task_id: str, task_name: str,
                                   task_desc: str) -> str:
        """Generate minimal Python fallback code.

        Args:
            task_id: Task identifier
            task_name: Task name
            task_desc: Task description

        Returns:
            Python code string
        """
        return f'''"""
Auto-generated fallback code - LLM generation failed
Task: {task_id}
Name: {task_name}
Description: {task_desc}
Note: This is a placeholder. Please implement the actual functionality.
"""

from typing import Any, Dict, Optional


class {self._to_pascal_case(task_name)}:
    """
    {task_name}
    
    TODO: Implement {task_name} functionality
    """

    def __init__(self):
        """Initialize {task_name}."""
        # TODO: Initialize attributes
        pass

    def execute(self) -> None:
        """
        Execute {task_name}.
        
        TODO: Implement the main functionality
        """
        # TODO: Implement functionality
        raise NotImplementedError("Not implemented")


# TODO: Add helper functions as needed
def {self._to_snake_case(task_name)}_helper() -> None:
    """
    Helper function for {task_name}.
    
    TODO: Implement helper functionality
    """
    pass
'''

    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase.

        Args:
            text: Input text

        Returns:
            PascalCase string
        """
        # Remove special characters and split
        words = ''.join(c if c.isalnum() else ' ' for c in text).split()
        return ''.join(word.capitalize() for word in words)

    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case.

        Args:
            text: Input text

        Returns:
            snake_case string
        """
        # Remove special characters
        text = ''.join(c if c.isalnum() else '_' for c in text.lower())
        # Remove consecutive underscores
        while '__' in text:
            text = text.replace('__', '_')
        return text.strip('_')

    def _load_templates(self) -> dict:
        """Load template functions.
        
        Returns:
            Dictionary mapping task IDs to template functions
        """
        return {
            'rust_backend.pkce_rfc7636': self._template_pkce,
            'rust_backend.callback_server': self._template_callback_server,
            'oauth_integration.callback_server': self._template_oauth_callback,
            'oauth_integration.token_keychain': self._template_token_keychain,
        }

    def _template_pkce(self, task: Dict[str, Any]) -> str:
        """Generate PKCE implementation (RFC 7636).
        
        Args:
            task: Task dictionary
            
        Returns:
            Rust code for PKCE
        """
        return '''// Auto-generated PKCE implementation - RFC 7636 compliant
// Task: rust_backend.pkce_rfc7636

use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine};
use sha2::{Digest, Sha256};
use rand::RngCore;

/// Generate a cryptographically secure code verifier (43-128 characters)
pub fn generate_code_verifier() -> String {
    let mut bytes = [0u8; 32];
    rand::thread_rng().fill_bytes(&mut bytes);
    URL_SAFE_NO_PAD.encode(&bytes)
}

/// Generate code challenge from verifier using SHA256
pub fn generate_code_challenge(verifier: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(verifier.as_bytes());
    let result = hasher.finalize();
    URL_SAFE_NO_PAD.encode(&result)
}

/// Verify PKCE code challenge
pub fn verify_pkce(code_verifier: &str, code_challenge: &str) -> bool {
    let generated_challenge = generate_code_challenge(code_verifier);
    generated_challenge == code_challenge
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_code_verifier_length() {
        let verifier = generate_code_verifier();
        assert!(verifier.len() >= 43);
        assert!(verifier.len() <= 128);
    }

    #[test]
    fn test_pkce_verification() {
        let verifier = generate_code_verifier();
        let challenge = generate_code_challenge(&verifier);
        assert!(verify_pkce(&verifier, &challenge));
    }
}
'''

    def _template_callback_server(self, task: Dict[str, Any]) -> str:
        """Generate OAuth callback server.
        
        Args:
            task: Task dictionary
            
        Returns:
            Rust code for callback server
        """
        return '''// Auto-generated OAuth callback server
// Task: rust_backend.callback_server

use tiny_http::{Server, Response, Header, StatusCode};
use std::sync::mpsc::channel;
use std::thread;

pub struct CallbackServer {
    server: Server,
    port: u16,
}

impl CallbackServer {
    /// Create new callback server on specified port
    pub fn new(port: u16) -> Result<Self, Box<dyn std::error::Error>> {
        let server = Server::http(format!("127.0.0.1:{}", port))?;
        Ok(Self { server, port })
    }

    /// Start server and wait for callback
    pub fn wait_for_callback(&self) -> Result<CallbackResponse, Box<dyn std::error::Error>> {
        for request in self.server.incoming_requests() {
            let url = request.url().to_string();
            
            // Parse query parameters
            let params = self.parse_query_string(&url);
            
            let code = params.get("code").cloned();
            let state = params.get("state").cloned();
            
            // Send success response
            let response = self.create_success_response();
            request.respond(response)?;
            
            return Ok(CallbackResponse { code, state });
        }
        
        Err("No callback received".into())
    }

    fn parse_query_string(&self, url: &str) -> std::collections::HashMap<String, String> {
        let mut params = std::collections::HashMap::new();
        
        if let Some(query_start) = url.find('?') {
            let query = &url[query_start + 1..];
            for pair in query.split('&') {
                if let Some(eq_pos) = pair.find('=') {
                    let key = &pair[..eq_pos];
                    let value = &pair[eq_pos + 1..];
                    params.insert(
                        urlencoding::decode(key).unwrap_or(key.into()).to_string(),
                        urlencoding::decode(value).unwrap_or(value.into()).to_string()
                    );
                }
            }
        }
        
        params
    }

    fn create_success_response(&self) -> Response<std::io::Cursor<Vec<u8>>> {
        let html = r#"<!DOCTYPE html>
<html>
<head><title>OAuth Callback Successful</title></head>
<body>
<h1>Authentication Successful!</h1>
<p>You can close this window and return to the application.</p>
<script>window.close();</script>
</body>
</html>"#;

        let mut response = Response::from_string(html);
        response = response.with_status_code(StatusCode(200));
        response = response.with_header(Header::from_bytes(&b"Content-Type"[..], &b"text/html"[..]).unwrap());
        response
    }
}

pub struct CallbackResponse {
    pub code: Option<String>,
    pub state: Option<String>,
}
'''

    def _template_oauth_callback(self, task: Dict[str, Any]) -> str:
        """Generate OAuth callback handler (TypeScript).
        
        Args:
            task: Task dictionary
            
        Returns:
            TypeScript code for OAuth callback
        """
        return '''// Auto-generated OAuth callback handler
// Task: oauth_integration.callback_server

import http from 'http';
import url from 'url';
import { EventEmitter } from 'events';

export interface CallbackResponse {
  code?: string;
  state?: string;
  error?: string;
}

export class OAuthCallbackServer extends EventEmitter {
  private server: http.Server;
  private port: number;

  constructor(port: number = 7823) {
    super();
    this.port = port;
    this.server = http.createServer(this.handleRequest.bind(this));
  }

  /**
   * Start server and wait for OAuth callback
   */
  public async waitForCallback(): Promise<CallbackResponse> {
    return new Promise((resolve, reject) => {
      this.server.listen(this.port, '127.0.0.1', () => {
        console.log(`OAuth callback server listening on port ${this.port}`);
      });

      this.once('callback', (response: CallbackResponse) => {
        this.server.close();
        resolve(response);
      });

      this.once('error', (error: Error) => {
        this.server.close();
        reject(error);
      });
    });
  }

  private handleRequest(req: http.IncomingMessage, res: http.ServerResponse) {
    const parsedUrl = url.parse(req.url || '', true);
    
    if (parsedUrl.pathname === '/callback') {
      const query = parsedUrl.query;
      
      const response: CallbackResponse = {
        code: query.code as string | undefined,
        state: query.state as string | undefined,
        error: query.error as string | undefined
      };

      // Send success response
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(this.getSuccessHtml());

      // Emit callback event
      this.emit('callback', response);
    } else {
      res.writeHead(404);
      res.end('Not found');
    }
  }

  private getSuccessHtml(): string {
    return `<!DOCTYPE html>
<html>
<head><title>OAuth Callback Successful</title></head>
<body>
<h1>Authentication Successful!</h1>
<p>You can close this window and return to the application.</p>
<script>window.close();</script>
</body>
</html>`;
  }
}
'''

    def _template_token_keychain(self, task: Dict[str, Any]) -> str:
        """Generate token keychain storage (Rust).
        
        Args:
            task: Task dictionary
            
        Returns:
            Rust code for token keychain
        """
        return '''// Auto-generated token keychain storage
// Task: oauth_integration.token_keychain

use keyring::Entry;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct TokenData {
    pub access_token: String,
    pub refresh_token: Option<String>,
    pub expires_at: Option<u64>,
    pub token_type: String,
    pub scope: String,
}

pub struct TokenKeychain {
    service_name: String,
}

impl TokenKeychain {
    /// Create new token keychain
    pub fn new(service_name: &str) -> Self {
        Self {
            service_name: service_name.to_string(),
        }
    }

    /// Store token in OS keychain
    pub fn store_token(&self, provider: &str, token: &TokenData) -> Result<(), Box<dyn std::error::Error>> {
        let entry = Entry::new(&self.service_name, provider)?;
        let json = serde_json::to_string(token)?;
        entry.set_password(&json)?;
        Ok(())
    }

    /// Retrieve token from OS keychain
    pub fn get_token(&self, provider: &str) -> Result<Option<TokenData>, Box<dyn std::error::Error>> {
        let entry = Entry::new(&self.service_name, provider)?;
        
        match entry.get_password() {
            Ok(json) => {
                let token: TokenData = serde_json::from_str(&json)?;
                Ok(Some(token))
            }
            Err(keyring::Error::NoEntry) => Ok(None),
            Err(e) => Err(Box::new(e)),
        }
    }

    /// Delete token from OS keychain
    pub fn delete_token(&self, provider: &str) -> Result<(), Box<dyn std::error::Error>> {
        let entry = Entry::new(&self.service_name, provider)?;
        entry.delete_password()?;
        Ok(())
    }

    /// Check if token is expired
    pub fn is_token_expired(&self, provider: &str) -> Result<bool, Box<dyn std::error::Error>> {
        match self.get_token(provider)? {
            Some(token) => {
                if let Some(expires_at) = token.expires_at {
                    let now = std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)?
                        .as_secs();
                    Ok(now >= expires_at)
                } else {
                    Ok(false) // No expiry = never expires
                }
            }
            None => Ok(true), // No token = expired
        }
    }
}
'''
