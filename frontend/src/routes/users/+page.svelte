<script lang="ts">
  import { onMount } from 'svelte';
  import { api, type User } from '$lib/api';
  import { PUBLIC_API_URL } from '$env/static/public';
  
  let currentUser: User | null = null;
  let loading = true;
  let error = '';
  
  // For now, we'll just show the current user's info
  // In a real app, you'd have admin functionality to manage multiple users
  
  onMount(() => {
    loadCurrentUser();
  });
  
  async function loadCurrentUser() {
    try {
      loading = true;
      // For demo purposes, we'll assume user ID 1
      // In a real app, you'd get this from authentication context
      currentUser = await api.getUser(1);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load user info';
    } finally {
      loading = false;
    }
  }
  
  async function handleResetToken() {
    if (!currentUser) return;
    
    if (confirm('Are you sure you want to reset your API token? Your current token will be invalidated.')) {
      try {
        const result = await api.resetUserToken(currentUser.id);
        alert(`Your new API token is: ${result.new_token}\n\nPlease save this token securely.`);
        await loadCurrentUser();
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Failed to reset token');
      }
    }
  }
  
  function copyToken() {
    if (!currentUser) return;
    
    navigator.clipboard.writeText(currentUser.api_token).then(() => {
      alert('API token copied to clipboard');
    }).catch(() => {
      alert('Failed to copy token');
    });
  }
</script>

<div class="space-y-6">
  <div>
    <h1 class="text-2xl font-bold text-gray-900">User Management</h1>
    <p class="mt-1 text-sm text-gray-600">
      Manage your account and API access
    </p>
  </div>

  {#if loading}
    <div class="flex justify-center py-12">
      <div class="text-gray-500">Loading...</div>
    </div>
  {:else if error}
    <div class="rounded-md bg-red-50 p-4">
      <p class="text-sm text-red-800">{error}</p>
    </div>
  {:else if currentUser}
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">
          User Information
        </h3>
        <p class="mt-1 max-w-2xl text-sm text-gray-500">
          Your account details and API credentials
        </p>
      </div>
      <div class="border-t border-gray-200">
        <dl>
          <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">Username</dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {currentUser.username}
            </dd>
          </div>
          <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">Email</dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {currentUser.email}
            </dd>
          </div>
          <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">Role</dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {currentUser.is_admin ? 'Administrator' : 'User'}
            </dd>
          </div>
          <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">API Token</dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              <div class="flex items-center space-x-2">
                <code class="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
                  {currentUser.api_token.substring(0, 8)}...{currentUser.api_token.substring(currentUser.api_token.length - 8)}
                </code>
                <button
                  on:click={copyToken}
                  class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Copy Full Token
                </button>
              </div>
            </dd>
          </div>
          <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">Created</dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {new Date(currentUser.created_at).toLocaleString()}
            </dd>
          </div>
        </dl>
      </div>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">
          Reset API Token
        </h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>Generate a new API token. This will invalidate your current token.</p>
        </div>
        <div class="mt-5">
          <button
            on:click={handleResetToken}
            class="inline-flex items-center justify-center px-4 py-2 border border-transparent font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:text-sm"
          >
            Reset Token
          </button>
        </div>
      </div>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">
          API Usage
        </h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>Use your API token to authenticate requests to the APIFlow API.</p>
        </div>
        <div class="mt-3">
          <pre class="bg-gray-100 p-3 rounded text-xs overflow-auto">
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  {PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/connectors</pre>
        </div>
      </div>
    </div>
  {/if}
</div>
