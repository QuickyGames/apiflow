<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { page } from '$app/stores';
  
  const navigation = [
    { name: 'Dashboard', href: '/' },
    { name: 'Connectors', href: '/connectors' },
    { name: 'Nodes', href: '/nodes' },
    { name: 'Workflows', href: '/workflows' },
    { name: 'Jobs', href: '/jobs' },
    { name: 'Users', href: '/users' },
  ];
  
  let isAuthenticated = false;
  
  onMount(async () => {
    // Check if user has a token
    const token = localStorage.getItem('api_token');
    if (!token) {
      goto('/login');
      return;
    }
    
    // Verify token is valid
    try {
      await api.getUser(1);
      isAuthenticated = true;
    } catch {
      api.clearToken();
      goto('/login');
    }
  });
  
  function handleLogout() {
    api.clearToken();
    goto('/login');
  }
</script>

{#if isAuthenticated}
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex h-16 justify-between">
          <div class="flex">
            <div class="flex flex-shrink-0 items-center">
              <h1 class="text-xl font-bold text-gray-900">APIFlow</h1>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              {#each navigation as item}
                <a
                  href={item.href}
                  class="inline-flex items-center border-b-2 px-1 pt-1 text-sm font-medium {$page.url.pathname === item.href
                    ? 'border-indigo-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}"
                >
                  {item.name}
                </a>
              {/each}
            </div>
          </div>
          <div class="flex items-center">
            <button
              on:click={handleLogout}
              class="text-sm text-gray-500 hover:text-gray-700"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <slot />
    </main>
  </div>
{:else}
  <div class="flex justify-center items-center min-h-screen">
    <div class="text-gray-500">Loading...</div>
  </div>
{/if}
