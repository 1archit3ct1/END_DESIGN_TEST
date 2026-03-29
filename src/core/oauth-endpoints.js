/**
 * OAuth endpoints configuration for all 6 providers.
 */

export const OAUTH_ENDPOINTS = {
  google: {
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    revokeUrl: 'https://oauth2.googleapis.com/revoke',
    userInfoUrl: 'https://www.googleapis.com/oauth2/v2/userinfo',
    scopes: {
      read: ['openid', 'email', 'profile'],
      write: ['https://www.googleapis.com/auth/userinfo.profile'],
      admin: ['https://www.googleapis.com/auth/admin.directory.user.readonly']
    }
  },
  github: {
    authUrl: 'https://github.com/login/oauth/authorize',
    tokenUrl: 'https://github.com/login/oauth/access_token',
    revokeUrl: null,
    userInfoUrl: 'https://api.github.com/user',
    scopes: {
      read: ['user:email', 'read:user'],
      write: ['public_repo', 'repo'],
      admin: ['admin:org', 'admin:repo_hook']
    }
  },
  twitter: {
    authUrl: 'https://twitter.com/i/oauth2/authorize',
    tokenUrl: 'https://api.twitter.com/2/oauth2/token',
    revokeUrl: null,
    userInfoUrl: 'https://api.twitter.com/2/users/me',
    scopes: {
      read: ['tweet.read', 'users.read'],
      write: ['tweet.write', 'like.write'],
      admin: ['follows.write', 'offline.access']
    }
  },
  instagram: {
    authUrl: 'https://www.instagram.com/oauth/authorize',
    tokenUrl: 'https://api.instagram.com/oauth/access_token',
    revokeUrl: null,
    userInfoUrl: 'https://graph.instagram.com/me',
    scopes: {
      read: ['instagram_basic', 'pages_read_engagement'],
      write: ['instagram_content_publish', 'pages_manage_posts'],
      admin: ['pages_manage_engagement', 'business_management']
    }
  },
  discord: {
    authUrl: 'https://discord.com/api/oauth2/authorize',
    tokenUrl: 'https://discord.com/api/oauth2/token',
    revokeUrl: null,
    userInfoUrl: 'https://discord.com/api/users/@me',
    scopes: {
      read: ['identify', 'email'],
      write: ['guilds.join', 'messages.write'],
      admin: ['guilds', 'guilds.manage']
    }
  },
  meta: {
    authUrl: 'https://www.facebook.com/v18.0/dialog/oauth',
    tokenUrl: 'https://graph.facebook.com/v18.0/oauth/access_token',
    revokeUrl: 'https://graph.facebook.com/v18.0/permissions',
    userInfoUrl: 'https://graph.facebook.com/me',
    scopes: {
      read: ['public_profile', 'email'],
      write: ['publish_to_groups', 'pages_read_engagement'],
      admin: ['pages_manage_posts', 'pages_manage_engagement']
    }
  }
}

/**
 * Get endpoint for provider.
 */
export function getEndpoint(providerId, type = 'auth') {
  const provider = OAUTH_ENDPOINTS[providerId]
  if (!provider) return null

  switch (type) {
    case 'auth': return provider.authUrl
    case 'token': return provider.tokenUrl
    case 'revoke': return provider.revokeUrl
    case 'userinfo': return provider.userInfoUrl
    default: return provider.authUrl
  }
}

/**
 * Get scopes for provider.
 */
export function getScopesForProvider(providerId, scopeType = 'read') {
  const provider = OAUTH_ENDPOINTS[providerId]
  if (!provider) return []

  return provider.scopes[scopeType] || []
}

/**
 * Get all provider IDs.
 */
export function getAllProviderIds() {
  return Object.keys(OAUTH_ENDPOINTS)
}

/**
 * Check if provider supports revocation.
 */
export function supportsRevocation(providerId) {
  return OAUTH_ENDPOINTS[providerId]?.revokeUrl !== null
}
