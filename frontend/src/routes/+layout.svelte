<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';
  
  const navigation = [
    { name: 'Dashboard', href: '/' },
    { name: 'Connectors', href: '/connectors' },
    { name: 'Nodes', href: '/nodes' },
    { name: 'Workflows', href: '/workflows' },
    { name: 'Jobs', href: '/jobs' },
    { name: 'Users', href: '/users' },
  ];
</script>

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
      </div>
    </div>
  </nav>

  <main class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
    <slot />
  </main>
</div>
