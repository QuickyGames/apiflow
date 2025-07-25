<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { browser } from '$app/environment';

  export let open = false;
  export let title = '';
  export let onClose: () => void;

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape' && open) {
      onClose();
    }
  }

  onMount(() => {
    if (browser) {
      window.addEventListener('keydown', handleKeydown);
    }
  });

  onDestroy(() => {
    if (browser) {
      window.removeEventListener('keydown', handleKeydown);
    }
  });
</script>

{#if open}
  <!-- Background overlay -->
  <div
    class="fixed inset-0 z-40 bg-gray-500 bg-opacity-75 transition-opacity ease-in-out duration-300"
    on:click={onClose}
    transition:fade={{ duration: 300 }}
    role="button"
    tabindex="-1"
    on:keydown={handleKeydown}
  ></div>

  <!-- Modal container -->
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex min-h-screen items-center justify-center p-4 text-center sm:block sm:p-0">
      <!-- This element is to trick the browser into centering the modal contents. -->
      <span class="hidden sm:inline-block sm:h-screen sm:align-middle" aria-hidden="true">&#8203;</span>

      <!-- Modal panel -->
      <div
        class="relative inline-block w-full transform overflow-hidden rounded-lg bg-white text-left align-bottom shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:align-middle"
        transition:scale={{ duration: 300, start: 0.95 }}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div class="absolute top-0 right-0 pt-4 pr-4">
          <button
            type="button"
            on:click={onClose}
            class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            <span class="sr-only">Close</span>
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
              <h3 id="modal-title" class="text-lg font-medium leading-6 text-gray-900">
                {title}
              </h3>
              <div class="mt-4">
                <slot />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}