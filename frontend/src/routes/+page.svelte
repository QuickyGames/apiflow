<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  
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
      <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
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
      </div>
    </div>
  {/if}
</div>
