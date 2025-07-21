<script lang="ts">
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  
  let apiToken = '';
  let error = '';
  let loading = false;
  
  async function handleLogin() {
    if (!apiToken.trim()) {
      error = 'Please enter an API token';
      return;
    }
    
    loading = true;
    error = '';
    
    try {
      // Set the token
      api.setToken(apiToken);
      
      // Try to fetch user info to validate the token
      await api.getUser(1);
      
      // If successful, redirect to home
      goto('/');
    } catch (err) {
      error = 'Invalid API token. Please check your token and try again.';
      api.clearToken();
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        Sign in to APIFlow
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Enter your API token to access the system
      </p>
    </div>
    <form class="mt-8 space-y-6" on:submit|preventDefault={handleLogin}>
      <div class="rounded-md shadow-sm -space-y-px">
        <div>
          <label for="api-token" class="sr-only">API Token</label>
          <input
            id="api-token"
            name="api-token"
            type="password"
            autocomplete="off"
            required
            bind:value={apiToken}
            class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
            placeholder="Enter your API token"
          />
        </div>
      </div>

      {#if error}
        <div class="rounded-md bg-red-50 p-4">
          <p class="text-sm text-red-800">{error}</p>
        </div>
      {/if}

      <div>
        <button
          type="submit"
          disabled={loading}
          class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </div>

      <div class="text-sm text-center">
        <p class="text-gray-600">
          Don't have an API token? Check the API logs when starting the application:
        </p>
        <code class="mt-2 block bg-gray-100 p-2 rounded text-xs">
          docker-compose logs api | grep "Admin API token"
        </code>
        <p class="mt-2 text-gray-500 text-xs">
          Default admin credentials are set in your .env file
        </p>
      </div>
    </form>
  </div>
</div>
