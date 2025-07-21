<script lang="ts">
  import { onMount } from 'svelte';
  import { api, type Node } from '$lib/api';
  import NodeCard from '$lib/components/NodeCard.svelte';
  import NodeForm from '$lib/components/NodeForm.svelte';
  import Modal from '$lib/components/Modal.svelte';
  
  let nodes: Node[] = [];
  let loading = true;
  let error = '';
  
  let showModal = false;
  let showTestModal = false;
  let editingNode: Partial<Node> | null = null;
  let testingNode: Node | null = null;
  let testInput = '{}';
  let testResult: any = null;
  let testError = '';
  
  onMount(() => {
    loadNodes();
  });
  
  async function loadNodes() {
    try {
      loading = true;
      nodes = await api.getNodes();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load nodes';
    } finally {
      loading = false;
    }
  }
  
  function handleCreate() {
    editingNode = {
      name: '',
      description: '',
      connector_id: 0,
      input: [],
      output: [],
      data: {}
    };
    showModal = true;
  }
  
  function handleEdit(node: Node) {
    editingNode = { ...node };
    showModal = true;
  }
  
  async function handleSubmit(data: Partial<Node>) {
    try {
      if (editingNode?.id) {
        await api.updateNode(editingNode.id, data);
      } else {
        await api.createNode(data as Omit<Node, 'id' | 'created_at' | 'updated_at'>);
      }
      showModal = false;
      editingNode = null;
      await loadNodes();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save node');
    }
  }
  
  async function handleDelete(node: Node) {
    if (confirm(`Are you sure you want to delete "${node.name}"?`)) {
      try {
        await api.deleteNode(node.id);
        await loadNodes();
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Failed to delete node');
      }
    }
  }
  
  function handleTest(node: Node) {
    testingNode = node;
    testInput = JSON.stringify(
      node.input.reduce((acc, input) => {
        acc[input.name] = input.default || '';
        return acc;
      }, {} as Record<string, any>),
      null,
      2
    );
    testResult = null;
    testError = '';
    showTestModal = true;
  }
  
  async function runTest() {
    if (!testingNode) return;
    
    try {
      testError = '';
      const input = JSON.parse(testInput);
      const result = await api.runNode(testingNode.id, input);
      testResult = result;
    } catch (err) {
      testError = err instanceof Error ? err.message : 'Test failed';
    }
  }
  
  function handleCancel() {
    showModal = false;
    editingNode = null;
  }
  
  function handleTestCancel() {
    showTestModal = false;
    testingNode = null;
    testResult = null;
    testError = '';
  }
</script>

<div class="space-y-6">
  <div class="sm:flex sm:items-center sm:justify-between">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Nodes</h1>
      <p class="mt-1 text-sm text-gray-600">
        Build workflow components from connectors
      </p>
    </div>
    <div class="mt-4 sm:mt-0">
      <button
        on:click={handleCreate}
        class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
      >
        Create Node
      </button>
    </div>
  </div>

  {#if loading}
    <div class="flex justify-center py-12">
      <div class="text-gray-500">Loading...</div>
    </div>
  {:else if error}
    <div class="rounded-md bg-red-50 p-4">
      <p class="text-sm text-red-800">{error}</p>
    </div>
  {:else if nodes.length === 0}
    <div class="text-center py-12">
      <p class="text-gray-500">No nodes found. Create your first node to get started.</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {#each nodes as node}
        <NodeCard
          {node}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onTest={handleTest}
        />
      {/each}
    </div>
  {/if}
</div>

<Modal
  open={showModal}
  title={editingNode?.id ? 'Edit Node' : 'Create Node'}
  onClose={handleCancel}
>
  {#if editingNode}
    <NodeForm
      node={editingNode}
      onSubmit={handleSubmit}
      onCancel={handleCancel}
    />
  {/if}
</Modal>

<Modal
  open={showTestModal}
  title={`Test Node: ${testingNode?.name || ''}`}
  onClose={handleTestCancel}
>
  {#if testingNode}
    <div class="space-y-4">
      <div>
        <label for="test-input" class="block text-sm font-medium text-gray-700">
          Input (JSON)
        </label>
        <textarea
          id="test-input"
          bind:value={testInput}
          rows="6"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm font-mono text-xs"
        />
      </div>
      
      <button
        on:click={runTest}
        class="w-full inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
      >
        Run Test
      </button>
      
      {#if testError}
        <div class="rounded-md bg-red-50 p-4">
          <p class="text-sm text-red-800">{testError}</p>
        </div>
      {/if}
      
      {#if testResult}
        <div>
          <label class="block text-sm font-medium text-gray-700">
            Result
          </label>
          <pre class="mt-1 p-4 bg-gray-100 rounded-md text-xs overflow-auto">{JSON.stringify(testResult, null, 2)}</pre>
        </div>
      {/if}
    </div>
  {/if}
</Modal>
