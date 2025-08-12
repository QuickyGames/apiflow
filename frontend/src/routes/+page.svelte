<script lang="ts">
  import { onMount } from 'svelte';
  import { api, type Node, type Workflow } from '$lib/api';
  
  let stats = {
    connectors: 0,
    nodes: 0,
    workflows: 0,
    jobs: 0,
    runningJobs: 0,
    completedJobs: 0,
    failedJobs: 0
  };
  
  let loading = true;
  let error = '';
  let exportLoading = false;
  let importLoading = false;
  let importMessage = '';
  let fileInput: HTMLInputElement;
  
  onMount(async () => {
    try {
      const [connectors, nodes, workflows, jobs] = await Promise.all([
        api.getConnectors(),
        api.getNodes(),
        api.getWorkflows(),
        api.getJobs()
      ]);
      
      stats = {
        connectors: connectors.length,
        nodes: nodes.length,
        workflows: workflows.length,
        jobs: jobs.length,
        runningJobs: jobs.filter(j => j.status === 'running').length,
        completedJobs: jobs.filter(j => j.status === 'completed').length,
        failedJobs: jobs.filter(j => j.status === 'failed').length
      };
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load stats';
    } finally {
      loading = false;
    }
  });

  async function exportWorkspace() {
    exportLoading = true;
    try {
      const [connectors, nodes, workflows] = await Promise.all([
        api.getConnectors(),
        api.getNodes(),
        api.getWorkflows()
      ]);

      const exportData = {
        version: '1.0',
        timestamp: new Date().toISOString(),
        connectors: connectors.map(connector => ({
          id: connector.id,
          name: connector.name,
          base_url: connector.base_url,
          method: connector.method,
          header: connector.header,
          body: connector.body
        })),
        nodes: nodes.map(node => ({
          name: node.name,
          description: node.description,
          connector_id: node.connector_id,
          path: node.path,
          input: node.input,
          output: node.output,
          data: node.data,
          body_template: node.body_template
        })),
        workflows: workflows.map(workflow => ({
          name: workflow.name,
          description: workflow.description,
          nodes: workflow.nodes
        }))
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `apiflow-workspace-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to export workspace';
    } finally {
      exportLoading = false;
    }
  }

  function triggerImport() {
    fileInput.click();
  }

  async function handleImport(event: Event) {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    
    if (!file) return;

    importLoading = true;
    importMessage = '';
    
    try {
      const text = await file.text();
      const importData = JSON.parse(text);
      
      if (!importData.connectors && !importData.nodes && !importData.workflows) {
        throw new Error('Invalid workspace file format');
      }

      // Get existing data to check for name conflicts
      const [existingConnectors, existingNodes, existingWorkflows] = await Promise.all([
        api.getConnectors(),
        api.getNodes(),
        api.getWorkflows()
      ]);

      const existingConnectorNames = new Set(existingConnectors.map(c => c.name));
      const existingNodeNames = new Set(existingNodes.map(n => n.name));
      const existingWorkflowNames = new Set(existingWorkflows.map(w => w.name));

      let importedConnectors = 0;
      let importedNodes = 0;
      let importedWorkflows = 0;
      
      // Map old connector IDs to new connector IDs
      const connectorIdMap = new Map<number, number>();

      // Import connectors first
      if (importData.connectors) {
        for (const connectorData of importData.connectors) {
          let connectorName = connectorData.name;
          
          // Handle name conflicts by adding -copy suffix
          if (existingConnectorNames.has(connectorName)) {
            connectorName = `${connectorData.name}-copy`;
            let counter = 1;
            while (existingConnectorNames.has(connectorName)) {
              connectorName = `${connectorData.name}-copy-${counter}`;
              counter++;
            }
          }

          try {
            const newConnector = await api.createConnector({
              ...connectorData,
              name: connectorName
            });
            existingConnectorNames.add(connectorName);
            // Map old ID to new ID for nodes that reference this connector
            if (connectorData.id) {
              connectorIdMap.set(connectorData.id, newConnector.id);
            }
            importedConnectors++;
          } catch (err) {
            console.error(`Failed to import connector ${connectorData.name}:`, err);
          }
        }
      }

      // Import nodes
      if (importData.nodes) {
        for (const nodeData of importData.nodes) {
          let nodeName = nodeData.name;
          
          // Handle name conflicts by adding -copy suffix
          if (existingNodeNames.has(nodeName)) {
            nodeName = `${nodeData.name}-copy`;
            let counter = 1;
            while (existingNodeNames.has(nodeName)) {
              nodeName = `${nodeData.name}-copy-${counter}`;
              counter++;
            }
          }

          try {
            // Update connector_id if we have a mapping
            let connectorId = nodeData.connector_id;
            if (connectorIdMap.has(nodeData.connector_id)) {
              connectorId = connectorIdMap.get(nodeData.connector_id);
            }

            await api.createNode({
              ...nodeData,
              name: nodeName,
              connector_id: connectorId
            });
            existingNodeNames.add(nodeName);
            importedNodes++;
          } catch (err) {
            console.error(`Failed to import node ${nodeData.name}:`, err);
          }
        }
      }

      // Import workflows
      if (importData.workflows) {
        for (const workflowData of importData.workflows) {
          let workflowName = workflowData.name;
          
          // Handle name conflicts by adding -copy suffix
          if (existingWorkflowNames.has(workflowName)) {
            workflowName = `${workflowData.name}-copy`;
            let counter = 1;
            while (existingWorkflowNames.has(workflowName)) {
              workflowName = `${workflowData.name}-copy-${counter}`;
              counter++;
            }
          }

          try {
            await api.createWorkflow({
              ...workflowData,
              name: workflowName
            });
            existingWorkflowNames.add(workflowName);
            importedWorkflows++;
          } catch (err) {
            console.error(`Failed to import workflow ${workflowData.name}:`, err);
          }
        }
      }

      const parts = [];
      if (importedConnectors > 0) parts.push(`${importedConnectors} connectors`);
      if (importedNodes > 0) parts.push(`${importedNodes} nodes`);
      if (importedWorkflows > 0) parts.push(`${importedWorkflows} workflows`);
      
      importMessage = `Successfully imported ${parts.join(', ')}`;
      
      // Refresh stats
      const [connectors, nodes, workflows, jobs] = await Promise.all([
        api.getConnectors(),
        api.getNodes(),
        api.getWorkflows(),
        api.getJobs()
      ]);
      
      stats = {
        connectors: connectors.length,
        nodes: nodes.length,
        workflows: workflows.length,
        jobs: jobs.length,
        runningJobs: jobs.filter(j => j.status === 'running').length,
        completedJobs: jobs.filter(j => j.status === 'completed').length,
        failedJobs: jobs.filter(j => j.status === 'failed').length
      };

    } catch (err) {
      importMessage = err instanceof Error ? err.message : 'Failed to import workspace';
    } finally {
      importLoading = false;
      target.value = '';
    }
  }
</script>

<div class="space-y-6">
  <div>
    <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
    <p class="mt-1 text-sm text-gray-600">
      Overview of your API workflow system
    </p>
  </div>

  {#if loading}
    <div class="flex justify-center py-12">
      <div class="text-gray-500">Loading...</div>
    </div>
  {:else if error}
    <div class="rounded-md bg-red-50 p-4">
      <p class="text-sm text-red-800">{error}</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <!-- Connectors -->
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Total Connectors</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
          {stats.connectors}
        </dd>
      </div>

      <!-- Nodes -->
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Total Nodes</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
          {stats.nodes}
        </dd>
      </div>

      <!-- Workflows -->
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Total Workflows</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
          {stats.workflows}
        </dd>
      </div>

      <!-- Jobs -->
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Total Jobs</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
          {stats.jobs}
        </dd>
      </div>
    </div>

    <!-- Job Status Breakdown -->
    <div class="mt-8">
      <h2 class="text-lg font-medium text-gray-900">Job Status</h2>
      <div class="mt-4 grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt class="truncate text-sm font-medium text-gray-500">Running</dt>
          <dd class="mt-1 text-3xl font-semibold tracking-tight text-yellow-600">
            {stats.runningJobs}
          </dd>
        </div>

        <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt class="truncate text-sm font-medium text-gray-500">Completed</dt>
          <dd class="mt-1 text-3xl font-semibold tracking-tight text-green-600">
            {stats.completedJobs}
          </dd>
        </div>

        <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt class="truncate text-sm font-medium text-gray-500">Failed</dt>
          <dd class="mt-1 text-3xl font-semibold tracking-tight text-red-600">
            {stats.failedJobs}
          </dd>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="mt-8">
      <h2 class="text-lg font-medium text-gray-900">Quick Actions</h2>
      <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <a
          href="/connectors"
          class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
        >
          <div class="flex-1 min-w-0">
            <span class="absolute inset-0" aria-hidden="true"></span>
            <p class="text-sm font-medium text-gray-900">Create Connector</p>
            <p class="text-sm text-gray-500">Define API endpoints</p>
          </div>
        </a>

        <a
          href="/nodes"
          class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
        >
          <div class="flex-1 min-w-0">
            <span class="absolute inset-0" aria-hidden="true"></span>
            <p class="text-sm font-medium text-gray-900">Create Node</p>
            <p class="text-sm text-gray-500">Build workflow components</p>
          </div>
        </a>

        <a
          href="/workflows"
          class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
        >
          <div class="flex-1 min-w-0">
            <span class="absolute inset-0" aria-hidden="true"></span>
            <p class="text-sm font-medium text-gray-900">Create Workflow</p>
            <p class="text-sm text-gray-500">Design automation flows</p>
          </div>
        </a>

        <a
          href="/jobs"
          class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
        >
          <div class="flex-1 min-w-0">
            <span class="absolute inset-0" aria-hidden="true"></span>
            <p class="text-sm font-medium text-gray-900">View Jobs</p>
            <p class="text-sm text-gray-500">Monitor executions</p>
          </div>
        </a>

        <!-- Export Workspace Button -->
        <button
          on:click={exportWorkspace}
          disabled={exportLoading}
          class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900">
              {exportLoading ? 'Exporting...' : 'Export Workspace'}
            </p>
            <p class="text-sm text-gray-500">Download nodes & workflows</p>
          </div>
        </button>

        <!-- Import Workspace Button -->
        <button
          on:click={triggerImport}
          disabled={importLoading}
          class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900">
              {importLoading ? 'Importing...' : 'Import Workspace'}
            </p>
            <p class="text-sm text-gray-500">Upload nodes & workflows</p>
          </div>
        </button>
      </div>
    </div>

    <!-- Import Message -->
    {#if importMessage}
      <div class="mt-4 rounded-md bg-green-50 p-4">
        <p class="text-sm text-green-800">{importMessage}</p>
      </div>
    {/if}

    <!-- Hidden file input -->
    <input
      bind:this={fileInput}
      type="file"
      accept=".json"
      on:change={handleImport}
      class="hidden"
    />
  {/if}
</div>
