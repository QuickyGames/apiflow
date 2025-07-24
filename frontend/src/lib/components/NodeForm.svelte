<script lang="ts">
  import type { Node, Connector } from '$lib/api';
  import { api } from '$lib/api';
  import { onMount } from 'svelte';
  
  export let node: Partial<Node> = {
    name: '',
    description: '',
    connector_id: 0,
    path: '',
    input: [],
    output: [],
    data: {}
  };
  export let onSubmit: (data: Partial<Node>) => void;
  export let onCancel: () => void;
  
  let connectors: Connector[] = [];
  let inputJson = JSON.stringify(node.input || [], null, 2);
  let outputJson = JSON.stringify(node.output || [], null, 2);
  let dataJson = JSON.stringify(node.data || {}, null, 2);
  let inputError = '';
  let outputError = '';
  let dataError = '';
  
  onMount(async () => {
    try {
      connectors = await api.getConnectors();
      if (!node.connector_id && connectors.length > 0) {
        node.connector_id = connectors[0].id;
      }
    } catch (err) {
      console.error('Failed to load connectors:', err);
    }
  });
  
  function handleSubmit() {
    inputError = '';
    outputError = '';
    dataError = '';
    
    try {
      node.input = JSON.parse(inputJson);
    } catch (e) {
      inputError = 'Invalid JSON';
      return;
    }
    
    try {
      node.output = JSON.parse(outputJson);
    } catch (e) {
      outputError = 'Invalid JSON';
      return;
    }
    
    try {
      node.data = JSON.parse(dataJson);
    } catch (e) {
      dataError = 'Invalid JSON';
      return;
    }
    
    onSubmit(node);
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
      bind:value={node.name}
      required
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
    />
  </div>

  <div>
    <label for="description" class="block text-sm font-medium text-gray-700">
      Description
    </label>
    <textarea
      id="description"
      bind:value={node.description}
      required
      rows="3"
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
    />
  </div>

  <div>
    <label for="connector" class="block text-sm font-medium text-gray-700">
      Connector
    </label>
    <select
      id="connector"
      bind:value={node.connector_id}
      required
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
    >
      {#each connectors as connector}
        <option value={connector.id}>
          {connector.name} ({connector.method} {connector.base_url})
        </option>
      {/each}
    </select>
  </div>

  <div>
    <label for="path" class="block text-sm font-medium text-gray-700">
      Path
    </label>
    <input
      type="text"
      id="path"
      bind:value={node.path}
      placeholder="/models/black-forest-labs/flux-pro/predictions"
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
    />
    <p class="mt-1 text-sm text-gray-500">
      Path to append to the connector's base URL. Leave empty to use base URL only.
    </p>
  </div>

  <div>
    <label for="input" class="block text-sm font-medium text-gray-700">
      Input Schema (JSON)
    </label>
    <textarea
      id="input"
      bind:value={inputJson}
      rows="6"
      placeholder={'[{"name": "prompt", "type": "string", "required": true, "default": "", "description": "The prompt"}]'}
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm font-mono text-xs"
    />
    {#if inputError}
      <p class="mt-1 text-sm text-red-600">{inputError}</p>
    {/if}
  </div>

  <div>
    <label for="output" class="block text-sm font-medium text-gray-700">
      Output Schema (JSON)
    </label>
    <textarea
      id="output"
      bind:value={outputJson}
      rows="6"
      placeholder={'[{"name": "result", "type": "string", "default": "", "mapping": "output", "description": "The result"}]'}
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm font-mono text-xs"
    />
    {#if outputError}
      <p class="mt-1 text-sm text-red-600">{outputError}</p>
    {/if}
  </div>

  <div>
    <label for="data" class="block text-sm font-medium text-gray-700">
      Additional Data (JSON)
    </label>
    <textarea
      id="data"
      bind:value={dataJson}
      rows="4"
      placeholder={'{}'}
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm font-mono text-xs"
    />
    {#if dataError}
      <p class="mt-1 text-sm text-red-600">{dataError}</p>
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
