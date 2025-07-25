<script lang="ts">
  import { Node, Svelvet, Minimap, Controls, Anchor } from 'svelvet';
  import { onMount, createEventDispatcher } from 'svelte';
  import { api, type Node as ApiNode } from '$lib/api';
  
  const dispatch = createEventDispatcher();
  
  // Props
  export let initialWorkflow: any = null;
  
  // State
  let availableNodes: ApiNode[] = [];
  let workflowNodes: WorkflowNode[] = [];
  let connections: Connection[] = [];
  let showNodeSelector = false;
  let searchTerm = '';
  let canvasElement: HTMLElement;
  let nextNodeId = 1;
  
  // Types
  interface WorkflowNode {
    id: string;
    nodeId: number;
    name: string;
    description: string;
    position: { x: number; y: number };
    inputs: NodeInput[];
    outputs: NodeOutput[];
    inputTransforms: Record<string, any>;
  }
  
  interface NodeInput {
    name: string;
    type: string;
    required: boolean;
    default: any;
    description: string;
  }
  
  interface NodeOutput {
    name: string;
    type: string;
    default: any;
    mapping: string;
    description: string;
  }
  
  interface Connection {
    id: string;
    sourceNodeId: string;
    sourceOutput: string;
    targetNodeId: string;
    targetInput: string;
  }
  
  // Load available nodes on mount
  onMount(async () => {
    try {
      availableNodes = await api.getNodes();
      
      // Load initial workflow if provided
      if (initialWorkflow) {
        loadWorkflow(initialWorkflow);
      }
    } catch (error) {
      console.error('Failed to load nodes:', error);
    }
  });
  
  // Load workflow from JSON
  function loadWorkflow(workflow: any) {
    if (!workflow.value?.modules) return;
    
    workflowNodes = [];
    connections = [];
    nextNodeId = 1;
    
    workflow.value.modules.forEach((module: any, index: number) => {
      const nodeId = module.value.path.split('/').pop();
      const apiNode = availableNodes.find(n => n.id.toString() === nodeId);
      
      if (apiNode) {
        const workflowNode: WorkflowNode = {
          id: module.id || `node_${nextNodeId++}`,
          nodeId: apiNode.id,
          name: apiNode.name,
          description: apiNode.description,
          position: { x: index * 300 + 100, y: 100 },
          inputs: apiNode.input || [],
          outputs: apiNode.output || [],
          inputTransforms: module.value.input_transforms || {}
        };
        
        workflowNodes.push(workflowNode);
        
        // Parse connections from input_transforms
        Object.entries(workflowNode.inputTransforms).forEach(([inputName, transform]: [string, any]) => {
          if (transform.type === 'javascript' && transform.expr?.startsWith('results.')) {
            const match = transform.expr.match(/results\.([^.]+)\.(.+)/);
            if (match) {
              const sourceNodeId = match[1];
              const sourceOutput = match[2];
              
              connections.push({
                id: `${sourceNodeId}_${sourceOutput}_${workflowNode.id}_${inputName}`,
                sourceNodeId,
                sourceOutput,
                targetNodeId: workflowNode.id,
                targetInput: inputName
              });
            }
          }
        });
      }
    });
    
    workflowNodes = [...workflowNodes];
    connections = [...connections];
  }
  
  // Filter available nodes based on search
  $: filteredNodes = availableNodes.filter(node =>
    node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    node.description.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // Handle canvas double-click to show node selector
  function handleCanvasDoubleClick(event: MouseEvent) {
    // Check if the click is on the canvas background (not on a node)
    const target = event.target as HTMLElement;
    if (target && (target.classList.contains('svelvet-canvas') || target.tagName === 'svg' || target === canvasElement)) {
      showNodeSelector = true;
      searchTerm = '';
    }
  }
  
  // Add node to canvas
  function addNode(apiNode: ApiNode) {
    const workflowNode: WorkflowNode = {
      id: `node_${nextNodeId++}`,
      nodeId: apiNode.id,
      name: apiNode.name,
      description: apiNode.description,
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      inputs: apiNode.input || [],
      outputs: apiNode.output || [],
      inputTransforms: {}
    };
    
    workflowNodes = [...workflowNodes, workflowNode];
    showNodeSelector = false;
    exportWorkflow();
  }
  
  // Remove node from canvas
  function removeNode(nodeId: string) {
    workflowNodes = workflowNodes.filter(n => n.id !== nodeId);
    connections = connections.filter(c => c.sourceNodeId !== nodeId && c.targetNodeId !== nodeId);
    exportWorkflow();
  }
  
  // Handle connection creation
  function handleConnection(sourceNodeId: string, sourceOutput: string, targetNodeId: string, targetInput: string) {
    const connectionId = `${sourceNodeId}_${sourceOutput}_${targetNodeId}_${targetInput}`;
    
    // Remove existing connection to the same input
    connections = connections.filter(c => !(c.targetNodeId === targetNodeId && c.targetInput === targetInput));
    
    // Add new connection
    const newConnection: Connection = {
      id: connectionId,
      sourceNodeId,
      sourceOutput,
      targetNodeId,
      targetInput
    };
    
    connections = [...connections, newConnection];
    
    // Update input transforms
    const targetNode = workflowNodes.find(n => n.id === targetNodeId);
    if (targetNode) {
      targetNode.inputTransforms[targetInput] = {
        type: 'javascript',
        expr: `results.${sourceNodeId}.${sourceOutput}`
      };
      workflowNodes = [...workflowNodes];
    }
    
    exportWorkflow();
  }
  
  // Handle connection removal
  function handleDisconnection(connectionId: string) {
    const connection = connections.find(c => c.id === connectionId);
    if (connection) {
      connections = connections.filter(c => c.id !== connectionId);
      
      // Remove input transform
      const targetNode = workflowNodes.find(n => n.id === connection.targetNodeId);
      if (targetNode) {
        delete targetNode.inputTransforms[connection.targetInput];
        workflowNodes = [...workflowNodes];
      }
      
      exportWorkflow();
    }
  }
  
  // Update input transform value
  function updateInputTransform(nodeId: string, inputName: string, value: any) {
    const node = workflowNodes.find(n => n.id === nodeId);
    if (node) {
      if (value === '' || value === null || value === undefined) {
        delete node.inputTransforms[inputName];
      } else {
        node.inputTransforms[inputName] = {
          type: 'static',
          value: value
        };
      }
      workflowNodes = [...workflowNodes];
      exportWorkflow();
    }
  }
  
  // Export workflow as JSON
  function exportWorkflow() {
    const modules = workflowNodes.map(node => ({
      id: node.id,
      summary: node.name,
      value: {
        type: 'script',
        path: `node/${node.nodeId}`,
        input_transforms: node.inputTransforms
      }
    }));
    
    const workflow = {
      summary: 'Generated Workflow',
      description: 'Workflow created with visual builder',
      schema: {
        type: 'object',
        properties: {},
        required: []
      },
      value: {
        modules
      }
    };
    
    dispatch('workflowChange', workflow);
  }
  
  // Check if input is connected
  function isInputConnected(nodeId: string, inputName: string): boolean {
    return connections.some(c => c.targetNodeId === nodeId && c.targetInput === inputName);
  }
  
  // Get connection for input
  function getInputConnection(nodeId: string, inputName: string): Connection | undefined {
    return connections.find(c => c.targetNodeId === nodeId && c.targetInput === inputName);
  }
</script>

<div class="workflow-builder">
  <!-- Canvas -->
  <div 
    class="canvas-container"
    bind:this={canvasElement}
    on:dblclick={handleCanvasDoubleClick}
  >
    <Svelvet 
      id="workflow-canvas" 
      width={800} 
      height={600} 
      minimap 
      controls 
      theme="light"
      fitView
    >
      <!-- Workflow Nodes -->
      {#each workflowNodes as workflowNode (workflowNode.id)}
        <Node 
          id={workflowNode.id}
          position={workflowNode.position}
          useDefaults
          bgColor="#f8fafc"
          borderColor="#e2e8f0"
          textColor="#1e293b"
          selectionColor="#3b82f6"
          locked={false}
        >
          <div class="workflow-node">
            <!-- Node Header -->
            <div class="node-header">
              <h3 class="node-title">{workflowNode.name}</h3>
              <button 
                class="remove-btn"
                on:click={() => removeNode(workflowNode.id)}
                title="Remove node"
              >
                ×
              </button>
            </div>
            
            <!-- Node Description -->
            <p class="node-description">{workflowNode.description}</p>
            
            <!-- Inputs -->
            <div class="node-section">
              <h4 class="section-title">Inputs</h4>
              {#each workflowNode.inputs as input (input.name)}
                <div class="input-row">
                  <Anchor 
                    id={`${workflowNode.id}_input_${input.name}`}
                    input
                    multiple={false}
                    bgColor="#ef4444"
                    direction="west"
                  />
                  <div class="input-content">
                    <label class="input-label">
                      {input.name}
                      {#if input.required}<span class="required">*</span>{/if}
                    </label>
                    
                    {#if !isInputConnected(workflowNode.id, input.name)}
                      <input
                        type="text"
                        class="input-field"
                        placeholder={input.default?.toString() || ''}
                        value={workflowNode.inputTransforms[input.name]?.value || ''}
                        on:input={(e) => updateInputTransform(workflowNode.id, input.name, (e.target as HTMLInputElement)?.value)}
                      />
                    {:else}
                      {@const connection = getInputConnection(workflowNode.id, input.name)}
                      <div class="connected-input">
                        Connected to: {connection?.sourceNodeId}.{connection?.sourceOutput}
                      </div>
                    {/if}
                  </div>
                </div>
              {/each}
            </div>
            
            <!-- Outputs -->
            <div class="node-section">
              <h4 class="section-title">Outputs</h4>
              {#each workflowNode.outputs as output (output.name)}
                <div class="output-row">
                  <div class="output-content">
                    <label class="output-label">{output.name}</label>
                    <span class="output-type">{output.type}</span>
                  </div>
                  <Anchor 
                    id={`${workflowNode.id}_output_${output.name}`}
                    output
                    bgColor="#22c55e"
                    direction="east"
                  />
                </div>
              {/each}
            </div>
          </div>
        </Node>
      {/each}
    </Svelvet>
  </div>
  
  <!-- Node Selector Modal -->
  {#if showNodeSelector}
    <div class="modal-overlay" on:click={() => showNodeSelector = false}>
      <div class="modal-content" on:click|stopPropagation>
        <div class="modal-header">
          <h3>Add Node</h3>
          <button class="close-btn" on:click={() => showNodeSelector = false}>×</button>
        </div>
        
        <div class="search-container">
          <input
            type="text"
            placeholder="Search nodes..."
            bind:value={searchTerm}
            class="search-input"
          />
        </div>
        
        <div class="nodes-list">
          {#each filteredNodes as node (node.id)}
            <div class="node-item" on:click={() => addNode(node)}>
              <h4 class="node-item-title">{node.name}</h4>
              <p class="node-item-description">{node.description}</p>
              <div class="node-item-meta">
                <span class="input-count">{node.input?.length || 0} inputs</span>
                <span class="output-count">{node.output?.length || 0} outputs</span>
              </div>
            </div>
          {/each}
          
          {#if filteredNodes.length === 0}
            <div class="no-nodes">No nodes found</div>
          {/if}
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Add Node Button -->
  <div class="add-node-btn">
    <button 
      class="btn-add-node"
      on:click={() => { showNodeSelector = true; searchTerm = ''; }}
      title="Add Node"
    >
      + Add Node
    </button>
  </div>
  
</div>

<style>
  .workflow-builder {
    position: relative;
    width: 100%;
    height: 600px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .canvas-container {
    width: 100%;
    height: 100%;
  }
  
  .workflow-node {
    width: 280px;
    min-height: 200px;
    padding: 16px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .node-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  
  .node-title {
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }
  
  .remove-btn {
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 4px;
    width: 20px;
    height: 20px;
    cursor: pointer;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .remove-btn:hover {
    background: #dc2626;
  }
  
  .node-description {
    font-size: 12px;
    color: #64748b;
    margin: 0 0 16px 0;
    line-height: 1.4;
  }
  
  .node-section {
    margin-bottom: 16px;
  }
  
  .section-title {
    font-size: 12px;
    font-weight: 600;
    color: #374151;
    margin: 0 0 8px 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .input-row, .output-row {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    position: relative;
  }
  
  .input-content, .output-content {
    flex: 1;
    margin: 0 8px;
  }
  
  .input-label, .output-label {
    display: block;
    font-size: 11px;
    font-weight: 500;
    color: #374151;
    margin-bottom: 2px;
  }
  
  .required {
    color: #ef4444;
  }
  
  .input-field {
    width: 100%;
    padding: 4px 6px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 11px;
  }
  
  .input-field:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 1px #3b82f6;
  }
  
  .connected-input {
    font-size: 10px;
    color: #059669;
    font-weight: 500;
    padding: 4px 6px;
    background: #ecfdf5;
    border-radius: 4px;
  }
  
  .output-type {
    font-size: 10px;
    color: #6b7280;
  }
  
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    border-radius: 8px;
    width: 500px;
    max-height: 600px;
    display: flex;
    flex-direction: column;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .modal-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #6b7280;
  }
  
  .close-btn:hover {
    color: #374151;
  }
  
  .search-container {
    padding: 16px;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .search-input {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
  }
  
  .search-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 1px #3b82f6;
  }
  
  .nodes-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }
  
  .node-item {
    padding: 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .node-item:hover {
    border-color: #3b82f6;
    background: #f8fafc;
  }
  
  .node-item-title {
    margin: 0 0 4px 0;
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
  }
  
  .node-item-description {
    margin: 0 0 8px 0;
    font-size: 12px;
    color: #64748b;
    line-height: 1.4;
  }
  
  .node-item-meta {
    display: flex;
    gap: 12px;
    font-size: 11px;
    color: #6b7280;
  }
  
  .no-nodes {
    text-align: center;
    padding: 32px;
    color: #6b7280;
  }
  
  .add-node-btn {
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 100;
  }
  
  .btn-add-node {
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.2s;
  }
  
  .btn-add-node:hover {
    background: #2563eb;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
</style>
