/**
 * PKCE code challenge generator (RFC 7636).
 */

/**
 * Generate PKCE code verifier and challenge.
 */
export async function generatePKCE() {
  const codeVerifier = generateCodeVerifier()
  const codeChallenge = await generateCodeChallenge(codeVerifier)

  return {
    codeVerifier,
    codeChallenge
  }
}

/**
 * Generate random code verifier (43-128 characters).
 */
function generateCodeVerifier() {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return base64UrlEncode(array)
}

/**
 * Generate code challenge from verifier using SHA-256.
 */
async function generateCodeChallenge(verifier) {
  const encoder = new TextEncoder()
  const data = encoder.encode(verifier)
  const digest = await crypto.subtle.digest('SHA-256', data)
  return base64UrlEncode(new Uint8Array(digest))
}

/**
 * Base64URL encode without padding.
 */
function base64UrlEncode(buffer) {
  const base64 = btoa(String.fromCharCode(...buffer))
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}

/**
 * Verify PKCE code challenge.
 */
export async function verifyPKCE(codeVerifier, expectedChallenge) {
  const { codeChallenge } = await generatePKCEFromVerifier(codeVerifier)
  return codeChallenge === expectedChallenge
}

/**
 * Generate code challenge from existing verifier.
 */
export async function generatePKCEFromVerifier(codeVerifier) {
  const encoder = new TextEncoder()
  const data = encoder.encode(codeVerifier)
  const digest = await crypto.subtle.digest('SHA-256', data)
  const codeChallenge = base64UrlEncode(new Uint8Array(digest))

  return { codeVerifier, codeChallenge }
}
