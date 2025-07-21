<script lang="ts">
  import type { Connector } from '$lib/api';
  
  export let connector: Partial<Connector> = {
    name: '',
    base_url: '',
    method: 'GET',
    header: {},
    body: {}
  };
  export let onSubmit: (data: Partial<Connector>) => void;
  export let onCancel: () => void;
  
  let headerJson = JSON.stringify(connector.header || {}, null, 2);
  let bodyJson = JSON.stringify(connector.body || {}, null, 2);
  let headerError = '';
  let bodyError = '';
  
  function handleSubmit() {
    headerError = '';
    bodyError = '';
    
    try {
      connector.header = JSON.parse(headerJson);
    } catch (e) {
      headerError = 'Invalid JSON';
      return;
    }
    
    try {
      connector.body = JSON.parse(bodyJson);
    } catch (e) {
      bodyError = 'Invalid JSON';
      return;
    }
    
    onSubmit(connector);
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-6">
  <div>
    <label for="name" class="block text-sm font-medium text-gray-700">
      Name
    </label>
    <input
      type="text"
      id="name"
      bind:value={connector.name}
      required
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
    />
  </div>

  <div>
    <label for="base_url" class="block text-sm font-medium text-gray-700">
      Base URL
    </label>
    <input
      type="url"
      id="base_url"
      bind:value={connector.base_url}
      required
      placeholder="https://api.example.com/v1"
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
    />
  </div>

  <div>
    <label for="method" class="block text-sm font-medium text-gray-700">
      Method
    </label>
    <select
      id="method"
      bind:value={connector.method}
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
    >
      <option value="GET">GET</option>
      <option value="POST">POST</option>
      <option value="PUT">PUT</option>
      <option value="PATCH">PATCH</option>
      <option value="DELETE">DELETE</option>
    </select>
  </div>

  <div>
    <label for="header" class="block text-sm font-medium text-gray-700">
      Headers (JSON)
    </label>
    <textarea
      id="header"
      bind:value={headerJson}
      rows="4"
      placeholder={'{"Authorization": "Bearer $API_TOKEN"}'}
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm font-mono text-xs"
    />
    {#if headerError}
      <p class="mt-1 text-sm text-red-600">{headerError}</p>
    {/if}
  </div>

  <div>
    <label for="body" class="block text-sm font-medium text-gray-700">
      Body Template (JSON)
    </label>
    <textarea
      id="body"
      bind:value={bodyJson}
      rows="4"
      placeholder={'{}'}
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm font-mono text-xs"
    />
    {#if bodyError}
      <p class="mt-1 text-sm text-red-600">{bodyError}</p>
    {/if}
  </div>

  <div class="flex justify-end space-x-3">
    <button
      type="button"
      on:click={onCancel}
      class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
    >
      Cancel
    </button>
    <button
      type="submit"
      class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
    >
      Save
    </button>
  </div>
</form>
