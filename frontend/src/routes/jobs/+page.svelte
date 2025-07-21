<script lang="ts">
  import { onMount } from 'svelte';
  import { api, type Job } from '$lib/api';
  
  let jobs: Job[] = [];
  let loading = true;
  let error = '';
  let autoRefresh = true;
  let refreshInterval: number;
  
  onMount(() => {
    loadJobs();
    startAutoRefresh();
    
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  });
  
  async function loadJobs() {
    try {
      loading = true;
      jobs = await api.getJobs();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load jobs';
    } finally {
      loading = false;
    }
  }
  
  function startAutoRefresh() {
    if (autoRefresh) {
      refreshInterval = setInterval(() => {
        loadJobs();
      }, 5000); // Refresh every 5 seconds
    }
  }
  
  function toggleAutoRefresh() {
    autoRefresh = !autoRefresh;
    if (autoRefresh) {
      startAutoRefresh();
    } else if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  }
  
  async function handleCancel(job: Job) {
    if (confirm(`Are you sure you want to cancel job "${job.name}"?`)) {
      try {
        await api.cancelJob(job.id);
        await loadJobs();
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Failed to cancel job');
      }
    }
  }
  
  function getStatusColor(status: string) {
    switch (status) {
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'running':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
  
  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleString();
  }
</script>

<div class="space-y-6">
  <div class="sm:flex sm:items-center sm:justify-between">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Jobs</h1>
      <p class="mt-1 text-sm text-gray-600">
        Monitor workflow executions
      </p>
    </div>
    <div class="mt-4 sm:mt-0 flex items-center space-x-4">
      <label class="flex items-center">
        <input
          type="checkbox"
          bind:checked={autoRefresh}
          on:change={toggleAutoRefresh}
          class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
        <span class="ml-2 text-sm text-gray-600">Auto-refresh</span>
      </label>
      <button
        on:click={loadJobs}
        class="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
      >
        Refresh
      </button>
    </div>
  </div>

  {#if loading && jobs.length === 0}
    <div class="flex justify-center py-12">
      <div class="text-gray-500">Loading...</div>
    </div>
  {:else if error}
    <div class="rounded-md bg-red-50 p-4">
      <p class="text-sm text-red-800">{error}</p>
    </div>
  {:else if jobs.length === 0}
    <div class="text-center py-12">
      <p class="text-gray-500">No jobs found.</p>
    </div>
  {:else}
    <div class="overflow-hidden bg-white shadow sm:rounded-md">
      <ul class="divide-y divide-gray-200">
        {#each jobs as job}
          <li class="px-4 py-4 sm:px-6">
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center justify-between">
                  <p class="truncate text-sm font-medium text-indigo-600">
                    {job.name}
                  </p>
                  <div class="ml-2 flex flex-shrink-0">
                    <p class={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${getStatusColor(job.status)}`}>
                      {job.status}
                    </p>
                  </div>
                </div>
                <div class="mt-2 sm:flex sm:justify-between">
                  <div class="sm:flex">
                    <p class="flex items-center text-sm text-gray-500">
                      Workflow: {job.workflow_name}
                    </p>
                    {#if job.retry_count > 0}
                      <p class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                        Retries: {job.retry_count}
                      </p>
                    {/if}
                  </div>
                  <div class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                    <p>
                      Created: {formatDate(job.created_at)}
                    </p>
                  </div>
                </div>
                
                {#if job.error}
                  <div class="mt-2">
                    <p class="text-sm text-red-600">Error: {job.error}</p>
                  </div>
                {/if}
                
                <div class="mt-3">
                  <details class="group">
                    <summary class="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                      View Details
                    </summary>
                    <div class="mt-2 space-y-2">
                      {#if Object.keys(job.input).length > 0}
                        <div>
                          <h4 class="text-xs font-medium text-gray-500">Input:</h4>
                          <pre class="mt-1 p-2 bg-gray-100 rounded text-xs overflow-auto">{JSON.stringify(job.input, null, 2)}</pre>
                        </div>
                      {/if}
                      {#if Object.keys(job.output).length > 0}
                        <div>
                          <h4 class="text-xs font-medium text-gray-500">Output:</h4>
                          <pre class="mt-1 p-2 bg-gray-100 rounded text-xs overflow-auto">{JSON.stringify(job.output, null, 2)}</pre>
                        </div>
                      {/if}
                    </div>
                  </details>
                </div>
              </div>
              
              {#if job.status === 'pending' || job.status === 'running'}
                <div class="ml-4">
                  <button
                    on:click={() => handleCancel(job)}
                    class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    Cancel
                  </button>
                </div>
              {/if}
            </div>
          </li>
        {/each}
      </ul>
    </div>
  {/if}
</div>
