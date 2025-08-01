<script lang="ts">
  import { onMount } from 'svelte';
  import { api, type Workflow } from '$lib/api';
  import Modal from '$lib/components/Modal.svelte';
  import WorkflowBuilder from '$lib/components/workflow/WorkflowBuilder.svelte';

  let workflows: Workflow[] = [];
  let loading = true;
  let error = '';
  let showModal = false;
  let showRunModal = false;
  let editingWorkflow: Partial<Workflow> | null = null;
  let runningWorkflow: Workflow | null = null;
  let runInput = '{}';
  let runResult: any = null;
  let runError = '';
  let workflowJson = '';
  let jsonError = '';

  // Helper functions for safety
  function getModuleCount(workflow: Workflow): number {
    return workflow.nodes?.value?.modules?.length || 0;
  }

  function isValidWorkflow(workflow: any): workflow is Workflow {
    return workflow && 
           workflow.nodes && 
           workflow.nodes.value && 
           Array.isArray(workflow.nodes.value.modules);
  }

  function createDefaultNodes() {
    return {
      summary: '',
      description: '',
      schema: {
        type: 'object',
        properties: {},
        required: []
      },
      value: {
        modules: []
      }
    };
  }

  onMount(() => {
    loadWorkflows();
  });

  async function loadWorkflows() {
    try {
      loading = true;
      const rawWorkflows = await api.getWorkflows();
      
      // Validate and sanitize workflows
      workflows = rawWorkflows.map(workflow => ({
        ...workflow,
        nodes: workflow.nodes || createDefaultNodes()
      }));
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load workflows';
    } finally {
      loading = false;
    }
  }

  function handleCreate() {
    editingWorkflow = {
      name: '',
      description: '',
      nodes: createDefaultNodes()
    };
    workflowJson = JSON.stringify(editingWorkflow.nodes, null, 2);
    showModal = true;
  }

  function handleEdit(workflow: Workflow) {
    // Ensure workflow has proper structure
    const safeWorkflow = {
      ...workflow,
      nodes: workflow.nodes || createDefaultNodes()
    };
    
    editingWorkflow = { ...safeWorkflow };
    workflowJson = JSON.stringify(safeWorkflow.nodes, null, 2);
    showModal = true;
  }

  async function handleSubmit() {
    try {
      jsonError = '';
      const nodes = JSON.parse(workflowJson);
      const data = {
        name: editingWorkflow!.name || '',
        description: editingWorkflow!.description || '',
        nodes
      };

      if (editingWorkflow?.id) {
        await api.updateWorkflow(editingWorkflow.id, data);
      } else {
        await api.createWorkflow(data);
      }

      showModal = false;
      editingWorkflow = null;
      await loadWorkflows();
    } catch (err) {
      if (err instanceof SyntaxError) {
        jsonError = 'Invalid JSON';
      } else {
        alert(err instanceof Error ? err.message : 'Failed to save workflow');
      }
    }
  }

  async function handleDelete(workflow: Workflow) {
    if (confirm(`Are you sure you want to delete "${workflow.name}"?`)) {
      try {
        await api.deleteWorkflow(workflow.id);
        await loadWorkflows();
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Failed to delete workflow');
      }
    }
  }

  function handleRun(workflow: Workflow) {
    if (!isValidWorkflow(workflow)) {
      alert('Invalid workflow structure');
      return;
    }
    
    runningWorkflow = workflow;
    const schema = workflow.nodes?.schema || { properties: {} };
    const defaultInput: Record<string, any> = {};

    if (schema.properties) {
      Object.entries(schema.properties).forEach(([key, prop]: [string, any]) => {
        defaultInput[key] = prop?.default || '';
      });
    }

    runInput = JSON.stringify(defaultInput, null, 2);
    runResult = null;
    runError = '';
    showRunModal = true;
  }

  async function runWorkflow() {
    if (!runningWorkflow) return;

    try {
      runError = '';
      const input = JSON.parse(runInput);
      const result = await api.runWorkflow(runningWorkflow.id, input);
      runResult = result;
    } catch (err) {
      runError = err instanceof Error ? err.message : 'Run failed';
    }
  }

  function handleCancel() {
    showModal = false;
    editingWorkflow = null;
    jsonError = '';
  }

  function handleRunCancel() {
    showRunModal = false;
    runningWorkflow = null;
    runResult = null;
    runError = '';
  }
</script>

<div class="space-y-6">
  <div class="sm:flex sm:items-center sm:justify-between">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Workflows</h1>
      <p class="mt-1 text-sm text-gray-600">
        Design and manage automation workflows
      </p>
    </div>
    <div class="mt-4 sm:mt-0">
      <button
        on:click={handleCreate}
        class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
      >
        Create Workflow
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
  {:else if workflows.length === 0}
    <div class="text-center py-12">
      <p class="text-gray-500">No workflows found. Create your first workflow to get started.</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-4">
      {#each workflows as workflow}
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <div class="sm:flex sm:items-start sm:justify-between">
              <div>
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                  {workflow.name}
                </h3>
                <div class="mt-1 max-w-2xl text-sm text-gray-500">
                  <p>{workflow.description}</p>
                </div>
                <div class="mt-2 text-sm text-gray-500">
                  <p>{getModuleCount(workflow)} modules</p>
                </div>
              </div>
              <div class="mt-5 sm:mt-0 sm:ml-6 sm:flex-shrink-0 sm:flex sm:items-center space-x-3">
                <button
                  on:click={() => handleRun(workflow)}
                  class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Run
                </button>
                <button
                  on:click={() => handleEdit(workflow)}
                  class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Edit
                </button>
                <button
                  on:click={() => handleDelete(workflow)}
                  class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<Modal
  open={showModal}
  title={editingWorkflow?.id ? 'Edit Workflow' : 'Create Workflow'}
  onClose={handleCancel}
>
  {#if editingWorkflow}
    <div class="space-y-6">
      <WorkflowBuilder
        initialWorkflow={editingWorkflow.nodes || createDefaultNodes()}
        onworkflowchange={(workflow) => {
          if (editingWorkflow) {
            editingWorkflow.nodes = workflow || createDefaultNodes();
            workflowJson = JSON.stringify(editingWorkflow.nodes, null, 2);
          }
        }}
        on:workflowChange={(e: CustomEvent) => {
          if (editingWorkflow) {
            editingWorkflow.nodes = e.detail || createDefaultNodes();
            workflowJson = JSON.stringify(editingWorkflow.nodes, null, 2);
          }
        }}
      />
      <form on:submit|preventDefault={handleSubmit} class="space-y-6">
        <div>
          <label for="name" class="block text-sm font-medium text-gray-700">
            Name
          </label>
          <input
            type="text"
            id="name"
            bind:value={editingWorkflow.name}
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
            bind:value={editingWorkflow.description}
            required
            rows="3"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>

        <div>
          <label for="nodes" class="block text-sm font-medium text-gray-700">
            Workflow Definition (JSON)
          </label>
          <textarea
            id="nodes"
            bind:value={workflowJson}
            rows="12"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm font-mono text-xs"
          />
          {#if jsonError}
            <p class="mt-1 text-sm text-red-600">{jsonError}</p>
          {/if}
        </div>

        <div class="flex justify-end space-x-3">
          <button
            type="button"
            on:click={handleCancel}
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
    </div>
  {/if}
</Modal>

<Modal
  open={showRunModal}
  title={`Run Workflow: ${runningWorkflow?.name || ''}`}
  onClose={handleRunCancel}
>
  {#if runningWorkflow}
    <div class="space-y-4">
      <div>
        <label for="run-input" class="block text-sm font-medium text-gray-700">
          Input (JSON)
        </label>
        <textarea
          id="run-input"
          bind:value={runInput}
          rows="6"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm font-mono text-xs"
        />
      </div>
      <button
        on:click={runWorkflow}
        class="w-full inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
      >
        Run Workflow
      </button>
      {#if runError}
        <div class="rounded-md bg-red-50 p-4">
          <p class="text-sm text-red-800">{runError}</p>
        </div>
      {/if}
      {#if runResult}
        <div>
          <label class="block text-sm font-medium text-gray-700">
            Result
          </label>
          <pre class="mt-1 p-4 bg-gray-100 rounded-md text-xs overflow-auto">{JSON.stringify(runResult, null, 2)}</pre>
        </div>
      {/if}
    </div>
  {/if}
</Modal>
