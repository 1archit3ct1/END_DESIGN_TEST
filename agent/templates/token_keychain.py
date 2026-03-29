#!/usr/bin/env python3
"""
Token Keychain Template — Secure token storage using OS keychain for Rust.

Generates code for: oauth_integration.token_keychain
"""

from typing import Dict, Any


def generate_token_keychain_template(task: Dict[str, Any]) -> str:
    """Generate token keychain storage implementation.

    Args:
        task: Task dictionary

    Returns:
        Rust code for token keychain storage
    """
    return '''// Auto-generated token keychain storage
// Task: oauth_integration.token_keychain

use keyring::Entry;
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

/// Token data structure for storage
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenData {
    pub access_token: String,
    pub refresh_token: Option<String>,
    pub expires_at: Option<u64>,
    pub token_type: String,
    pub scope: String,
}

impl TokenData {
    /// Create new token data
    pub fn new(
        access_token: String,
        token_type: String,
        scope: String,
        refresh_token: Option<String>,
        expires_in: Option<u64>,
    ) -> Self {
        let expires_at = expires_in.map(|expires_in| {
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs()
                + expires_in
        });

        Self {
            access_token,
            refresh_token,
            expires_at,
            token_type,
            scope,
        }
    }

    /// Check if token is expired
    pub fn is_expired(&self) -> bool {
        match self.expires_at {
            Some(expires_at) => {
                let now = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_secs();
                now >= expires_at
            }
            None => false, // No expiry = never expires
        }
    }

    /// Check if token should be refreshed (within 5 minutes of expiry)
    pub fn should_refresh(&self) -> bool {
        match self.expires_at {
            Some(expires_at) => {
                let now = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_secs();
                // Refresh if within 5 minutes of expiry
                expires_at.saturating_sub(now) < 300
            }
            None => false,
        }
    }
}

/// Secure token storage using OS keychain
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
    pub fn store_token(
        &self,
        provider: &str,
        token: &TokenData,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let entry = Entry::new(&self.service_name, provider)?;
        let json = serde_json::to_string(token)?;
        entry.set_password(&json)?;
        Ok(())
    }

    /// Retrieve token from OS keychain
    pub fn get_token(
        &self,
        provider: &str,
    ) -> Result<Option<TokenData>, Box<dyn std::error::Error>> {
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
            Some(token) => Ok(token.is_expired()),
            None => Ok(true), // No token = expired
        }
    }

    /// Get token if valid (not expired)
    pub fn get_valid_token(
        &self,
        provider: &str,
    ) -> Result<Option<TokenData>, Box<dyn std::error::Error>> {
        match self.get_token(provider)? {
            Some(token) if !token.is_expired() => Ok(Some(token)),
            _ => Ok(None),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_token_data_creation() {
        let token = TokenData::new(
            "access_token_123".to_string(),
            "Bearer".to_string(),
            "read write".to_string(),
            Some("refresh_token_456".to_string()),
            Some(3600),
        );

        assert_eq!(token.access_token, "access_token_123");
        assert_eq!(token.token_type, "Bearer");
        assert!(token.expires_at.is_some());
    }

    #[test]
    fn test_token_serialization() {
        let token = TokenData::new(
            "access_token_123".to_string(),
            "Bearer".to_string(),
            "read write".to_string(),
            None,
            None,
        );

        let json = serde_json::to_string(&token).unwrap();
        let deserialized: TokenData = serde_json::from_str(&json).unwrap();

        assert_eq!(token.access_token, deserialized.access_token);
        assert_eq!(token.token_type, deserialized.token_type);
    }
}
'''


def get_task_id() -> str:
    """Return the task ID this template handles."""
    return 'oauth_integration.token_keychain'


def get_language() -> str:
    """Return the programming language for this template."""
    return 'rust'


def get_output_path() -> str:
    """Return the output file path for generated code."""
    return 'src-tauri/src/auth/token_keychain.rs'
