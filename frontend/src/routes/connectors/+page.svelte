<script lang="ts">
  import { onMount } from 'svelte';
  import { api, type Connector } from '$lib/api';
  import ConnectorCard from '$lib/components/ConnectorCard.svelte';
  import ConnectorForm from '$lib/components/ConnectorForm.svelte';
  import Modal from '$lib/components/Modal.svelte';
  
  let connectors: Connector[] = [];
  let loading = true;
  let error = '';
  
  let showModal = false;
  let editingConnector: Partial<Connector> | null = null;
  
  onMount(() => {
    loadConnectors();
  });
  
  async function loadConnectors() {
    try {
      loading = true;
      connectors = await api.getConnectors();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load connectors';
    } finally {
      loading = false;
    }
  }
  
  function handleCreate() {
    editingConnector = {
      name: '',
      base_url: '',
      method: 'GET',
      header: {},
      body: {}
    };
    showModal = true;
  }
  
  function handleEdit(connector: Connector) {
    editingConnector = { ...connector };
    showModal = true;
  }
  
  async function handleSubmit(data: Partial<Connector>) {
    try {
      if (editingConnector?.id) {
        await api.updateConnector(editingConnector.id, data);
      } else {
        await api.createConnector(data as Omit<Connector, 'id' | 'created_at' | 'updated_at'>);
      }
      showModal = false;
      editingConnector = null;
      await loadConnectors();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save connector');
    }
  }
  
  async function handleDelete(connector: Connector) {
    if (confirm(`Are you sure you want to delete "${connector.name}"?`)) {
      try {
        await api.deleteConnector(connector.id);
        await loadConnectors();
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Failed to delete connector');
      }
    }
  }
  
  function handleCancel() {
    showModal = false;
    editingConnector = null;
  }
</script>

<div class="space-y-6">
  <div class="sm:flex sm:items-center sm:justify-between">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Connectors</h1>
      <p class="mt-1 text-sm text-gray-600">
        Manage API endpoints and authentication
      </p>
    </div>
    <div class="mt-4 sm:mt-0">
      <button
        on:click={handleCreate}
        class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
      >
        Create Connector
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
  {:else if connectors.length === 0}
    <div class="text-center py-12">
      <p class="text-gray-500">No connectors found. Create your first connector to get started.</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {#each connectors as connector}
        <ConnectorCard
          {connector}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      {/each}
    </div>
  {/if}
</div>

<Modal
  open={showModal}
  title={editingConnector?.id ? 'Edit Connector' : 'Create Connector'}
  onClose={handleCancel}
>
  {#if editingConnector}
    <ConnectorForm
      connector={editingConnector}
      onSubmit={handleSubmit}
      onCancel={handleCancel}
    />
  {/if}
</Modal>
