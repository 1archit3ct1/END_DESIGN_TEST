/**
 * Default scopes per OAuth provider.
 */

export const PROVIDER_SCOPES = {
  google: {
    read: ['openid', 'email', 'profile'],
    write: ['https://www.googleapis.com/auth/userinfo.profile'],
    admin: ['https://www.googleapis.com/auth/admin.directory.user.readonly']
  },
  github: {
    read: ['user:email', 'read:user'],
    write: ['public_repo', 'repo'],
    admin: ['admin:org', 'admin:repo_hook']
  },
  twitter: {
    read: ['tweet.read', 'users.read'],
    write: ['tweet.write', 'like.write'],
    admin: ['follows.write', 'offline.access']
  },
  instagram: {
    read: ['instagram_basic', 'pages_read_engagement'],
    write: ['instagram_content_publish', 'pages_manage_posts'],
    admin: ['pages_manage_engagement', 'business_management']
  },
  discord: {
    read: ['identify', 'email'],
    write: ['guilds.join', 'messages.write'],
    admin: ['guilds', 'guilds.manage']
  },
  meta: {
    read: ['public_profile', 'email'],
    write: ['publish_to_groups', 'pages_read_engagement'],
    admin: ['pages_manage_posts', 'pages_manage_engagement']
  }
}

/**
 * Get default scopes for a provider.
 */
export function getDefaultScopes(providerId) {
  return PROVIDER_SCOPES[providerId] || {}
}

/**
 * Get all scope types (read, write, admin).
 */
export function getScopeTypes() {
  return ['read', 'write', 'admin']
}

/**
 * Get all provider IDs.
 */
export function getProviderIds() {
  return Object.keys(PROVIDER_SCOPES)
}
