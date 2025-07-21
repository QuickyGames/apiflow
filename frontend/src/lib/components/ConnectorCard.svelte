<script lang="ts">
  import type { Connector } from '$lib/api';
  
  export let connector: Connector;
  export let onEdit: (connector: Connector) => void;
  export let onDelete: (connector: Connector) => void;
</script>

<div class="bg-white overflow-hidden shadow rounded-lg">
  <div class="px-4 py-5 sm:p-6">
    <h3 class="text-lg leading-6 font-medium text-gray-900">
      {connector.name}
    </h3>
    <div class="mt-2 max-w-xl text-sm text-gray-500">
      <p class="font-mono text-xs">{connector.method} {connector.base_url}</p>
    </div>
    <div class="mt-3">
      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        {connector.method}
      </span>
    </div>
    <div class="mt-5 flex space-x-3">
      <button
        on:click={() => onEdit(connector)}
        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Edit
      </button>
      <button
        on:click={() => onDelete(connector)}
        class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
      >
        Delete
      </button>
    </div>
  </div>
</div>
