<script lang="ts">
  import type { Node } from '$lib/api';
  
  export let node: Node;
  export let onEdit: (node: Node) => void;
  export let onDelete: (node: Node) => void;
  export let onTest: (node: Node) => void;
</script>

<div class="bg-white overflow-hidden shadow rounded-lg">
  <div class="px-4 py-5 sm:p-6">
    <h3 class="text-lg leading-6 font-medium text-gray-900">
      {node.name}
    </h3>
    <div class="mt-2 max-w-xl text-sm text-gray-500">
      <p>{node.description}</p>
    </div>
    
    <div class="mt-3">
      <h4 class="text-xs font-medium text-gray-500 uppercase tracking-wide">Inputs</h4>
      <div class="mt-1 flex flex-wrap gap-1">
        {#each node.input as input}
          <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
            {input.name}
            {#if input.required}
              <span class="ml-1 text-red-500">*</span>
            {/if}
          </span>
        {/each}
      </div>
    </div>
    
    <div class="mt-3">
      <h4 class="text-xs font-medium text-gray-500 uppercase tracking-wide">Outputs</h4>
      <div class="mt-1 flex flex-wrap gap-1">
        {#each node.output as output}
          <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
            {output.name}
          </span>
        {/each}
      </div>
    </div>
    
    <div class="mt-5 flex space-x-3">
      <button
        on:click={() => onTest(node)}
        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Test
      </button>
      <button
        on:click={() => onEdit(node)}
        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Edit
      </button>
      <button
        on:click={() => onDelete(node)}
        class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
      >
        Delete
      </button>
    </div>
  </div>
</div>
