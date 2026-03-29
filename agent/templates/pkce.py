#!/usr/bin/env python3
"""
PKCE Template — RFC 7636 compliant PKCE implementation for Rust.

Generates code for: rust_backend.pkce_rfc7636
"""

from typing import Dict, Any


def generate_pkce_template(task: Dict[str, Any]) -> str:
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


def get_task_id() -> str:
    """Return the task ID this template handles."""
    return 'rust_backend.pkce_rfc7636'


def get_language() -> str:
    """Return the programming language for this template."""
    return 'rust'


def get_output_path() -> str:
    """Return the output file path for generated code."""
    return 'src-tauri/src/auth/pkce.rs'
