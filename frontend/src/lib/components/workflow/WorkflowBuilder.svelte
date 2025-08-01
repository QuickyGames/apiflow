<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { api, type Node as ApiNode } from '$lib/api';
  
  // Props
  export let initialWorkflow: any = null;
  export let onworkflowchange: ((workflow: any) => void) | undefined = undefined;
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // State
  let availableNodes: ApiNode[] = [];
  let workflowNodes: WorkflowNode[] = [];
  let branches: Branch[] = [];
  let showNodeSelector = false;
  let showSidebar = false;
  let selectedNode: WorkflowNode | null = null;
  let searchTerm = '';
  let nextNodeId = 1;
  let nextBranchId = 1;
  let forceRerender = 0; // Force reactivity updates
  
  // Types
  interface WorkflowNode {
    id: string;
    nodeId: number;
    name: string;
    description: string;
    type: 'script' | 'branchone' | 'branchall';
    inputs: NodeInput[];
    outputs: NodeOutput[];
    inputTransforms: Record<string, any>;
    branchId?: string;
    position: number; // Position in the flow (0, 1, 2, etc.)
    branches?: BranchCondition[]; // For branch nodes
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
  
  interface Branch {
    id: string;
    name: string;
    condition?: string;
    nodes: WorkflowNode[];
    isDefault?: boolean;
  }
  
  interface BranchCondition {
    expr: string;
    summary: string;
    modules: any[];
  }
  
  // Load available nodes on mount
  onMount(async () => {
    try {
      availableNodes = await api.getNodes();
      
      // Load initial workflow if provided
      if (initialWorkflow) {
        loadWorkflow(initialWorkflow);
      } else {
        // Initialize with main branch
        branches = [{
          id: 'main',
          name: 'Main Flow',
          nodes: []
        }];
      }
    } catch (error) {
      console.error('Failed to load nodes:', error);
    }
  });
  
  // Load workflow from JSON
  function loadWorkflow(workflow: any) {
    if (!workflow.value?.modules) return;
    
    workflowNodes = [];
    branches = [{
      id: 'main',
      name: 'Main Flow',
      nodes: []
    }];
    nextNodeId = 1;
    
    workflow.value.modules.forEach((module: any, index: number) => {
      if (module.value.type === 'branchone' || module.value.type === 'branchall') {
        // Handle branch nodes
        const branchNode: WorkflowNode = {
          id: module.id || `branch_${nextNodeId++}`,
          nodeId: 0,
          name: module.summary || 'Branch',
          description: 'Conditional branch',
          type: module.value.type,
          inputs: [],
          outputs: [],
          inputTransforms: {},
          position: index,
          branches: module.value.branches || []
        };
        
        branches[0].nodes.push(branchNode);
        
        // Create sub-branches
        if (module.value.branches) {
          module.value.branches.forEach((branch: any, branchIndex: number) => {
            const branchId = `${branchNode.id}_branch_${branchIndex}`;
            const newBranch: Branch = {
              id: branchId,
              name: branch.summary || `Branch ${branchIndex + 1}`,
              condition: branch.expr,
              nodes: []
            };
            
            // Add nodes to this branch
            if (branch.modules) {
              branch.modules.forEach((branchModule: any, moduleIndex: number) => {
                const nodeId = branchModule.value.path?.split('/').pop();
                const apiNode = availableNodes.find(n => n.id.toString() === nodeId);
                
                if (apiNode) {
                  const workflowNode: WorkflowNode = {
                    id: branchModule.id || `node_${nextNodeId++}`,
                    nodeId: apiNode.id,
                    name: apiNode.name,
                    description: apiNode.description,
                    type: 'script',
                    inputs: apiNode.input || [],
                    outputs: apiNode.output || [],
                    inputTransforms: branchModule.value.input_transforms || {},
                    branchId: branchId,
                    position: moduleIndex
                  };
                  
                  newBranch.nodes.push(workflowNode);
                }
              });
            }
            
            branches.push(newBranch);
          });
        }
        
        // Handle default branch
        if (module.value.default) {
          const defaultBranchId = `${branchNode.id}_default`;
          const defaultBranch: Branch = {
            id: defaultBranchId,
            name: 'Default',
            nodes: [],
            isDefault: true
          };
          
          module.value.default.forEach((defaultModule: any, moduleIndex: number) => {
            const nodeId = defaultModule.value.path?.split('/').pop();
            const apiNode = availableNodes.find(n => n.id.toString() === nodeId);
            
            if (apiNode) {
              const workflowNode: WorkflowNode = {
                id: defaultModule.id || `node_${nextNodeId++}`,
                nodeId: apiNode.id,
                name: apiNode.name,
                description: apiNode.description,
                type: 'script',
                inputs: apiNode.input || [],
                outputs: apiNode.output || [],
                inputTransforms: defaultModule.value.input_transforms || {},
                branchId: defaultBranchId,
                position: moduleIndex
              };
              
              defaultBranch.nodes.push(workflowNode);
            }
          });
          
          branches.push(defaultBranch);
        }
      } else {
        // Handle regular script nodes
        const nodeId = module.value.path?.split('/').pop();
        const apiNode = availableNodes.find(n => n.id.toString() === nodeId);
        
        if (apiNode) {
          const workflowNode: WorkflowNode = {
            id: module.id || `node_${nextNodeId++}`,
            nodeId: apiNode.id,
            name: apiNode.name,
            description: apiNode.description,
            type: 'script',
            inputs: apiNode.input || [],
            outputs: apiNode.output || [],
            inputTransforms: module.value.input_transforms || {},
            position: index
          };
          
          branches[0].nodes.push(workflowNode);
        }
      }
    });
    
    workflowNodes = [...workflowNodes];
    branches = [...branches];
  }
  
  // Filter available nodes based on search
  $: filteredNodes = availableNodes.filter(node =>
    node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    node.description.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // Add node to specific branch
  function addNode(apiNode: ApiNode, branchId: string = 'main') {
    const branch = branches.find(b => b.id === branchId);
    if (!branch) return;
    
    // Generate unique ID across all branches
    const allNodes = getAllNodes();
    let uniqueId: string;
    do {
      uniqueId = `node_${nextNodeId++}`;
    } while (allNodes.some(n => n.id === uniqueId));
    
    const workflowNode: WorkflowNode = {
      id: uniqueId,
      nodeId: apiNode.id,
      name: apiNode.name,
      description: apiNode.description,
      type: 'script',
      inputs: apiNode.input || [],
      outputs: apiNode.output || [],
      inputTransforms: {},
      branchId: branchId,
      position: branch.nodes.length
    };
    
    branch.nodes.push(workflowNode);
    branches = [...branches];
    showNodeSelector = false;
    exportWorkflow();
  }
  
  // Add branch node
  function addBranchNode(type: 'branchone' | 'branchall') {
    const mainBranch = branches.find(b => b.id === 'main');
    if (!mainBranch) return;
    
    const branchNode: WorkflowNode = {
      id: `branch_${nextBranchId++}`,
      nodeId: 0,
      name: type === 'branchone' ? 'Conditional Branch' : 'Parallel Branch',
      description: type === 'branchone' ? 'Execute one branch based on condition' : 'Execute all branches in parallel',
      type: type,
      inputs: [],
      outputs: [],
      inputTransforms: {},
      position: mainBranch.nodes.length,
      branches: []
    };
    
    mainBranch.nodes.push(branchNode);
    
    // Create initial branches
    const branch1: Branch = {
      id: `${branchNode.id}_branch_1`,
      name: 'Branch 1',
      condition: type === 'branchone' ? 'flow_input.condition === "option1"' : '',
      nodes: []
    };
    
    const branch2: Branch = {
      id: `${branchNode.id}_branch_2`,
      name: 'Branch 2',
      condition: type === 'branchone' ? 'flow_input.condition === "option2"' : '',
      nodes: []
    };
    
    branches.push(branch1, branch2);
    
    if (type === 'branchone') {
      // Add default branch for branchone
      const defaultBranch: Branch = {
        id: `${branchNode.id}_default`,
        name: 'Default',
        nodes: [],
        isDefault: true
      };
      branches.push(defaultBranch);
    }
    
    branches = [...branches];
    showNodeSelector = false;
    exportWorkflow();
  }
  
  // Remove node
  function removeNode(nodeId: string, branchId?: string) {
    if (branchId) {
      const branch = branches.find(b => b.id === branchId);
      if (branch) {
        branch.nodes = branch.nodes.filter(n => n.id !== nodeId);
      }
    } else {
      // Remove from all branches
      branches.forEach(branch => {
        branch.nodes = branch.nodes.filter(n => n.id !== nodeId);
      });
    }
    
    // If it's a branch node, remove associated branches
    const node = getAllNodes().find(n => n.id === nodeId);
    if (node && (node.type === 'branchone' || node.type === 'branchall')) {
      branches = branches.filter(b => !b.id.startsWith(nodeId));
    }
    
    branches = [...branches];
    exportWorkflow();
  }
  
  // Get all nodes from all branches
  function getAllNodes(): WorkflowNode[] {
    return branches.flatMap(branch => branch.nodes);
  }
  
  // Handle node click to open sidebar
  function handleNodeClick(node: WorkflowNode) {
    selectedNode = node;
    showSidebar = true;
  }
  
  // Update input transform value
  function updateInputTransform(nodeId: string, inputName: string, value: any, transformType: 'static' | 'javascript' = 'static') {
    const allNodes = getAllNodes();
    const node = allNodes.find(n => n.id === nodeId);
    if (node) {
      // Always create the transform object for both static and javascript types
      if (transformType === 'static') {
        if (value === '' || value === null || value === undefined) {
          // Delete empty static values
          delete node.inputTransforms[inputName];
        } else {
          node.inputTransforms[inputName] = {
            type: 'static',
            value: value
          };
        }
      } else if (transformType === 'javascript') {
        // Always create javascript transform, even if expr is empty
        node.inputTransforms[inputName] = {
          type: 'javascript',
          expr: value || ''
        };
      }
      
      // Force reactivity updates
      branches = [...branches];
      forceRerender++; // Force reactivity update
      
      // Always export workflow after any change
      exportWorkflow();
    }
  }
  
  // Update branch condition
  function updateBranchCondition(branchId: string, condition: string) {
    const branch = branches.find(b => b.id === branchId);
    if (branch) {
      branch.condition = condition;
      branches = [...branches];
      exportWorkflow();
    }
  }
  
  // Export workflow as JSON
  function exportWorkflow() {
    const mainBranch = branches.find(b => b.id === 'main');
    if (!mainBranch) return;
    
    const modules = mainBranch.nodes.map(node => {
      if (node.type === 'branchone' || node.type === 'branchall') {
        // Handle branch nodes
        const branchModules = branches
          .filter(b => b.id.startsWith(node.id) && !b.isDefault)
          .map(branch => ({
            expr: branch.condition || 'true',
            summary: branch.name,
            modules: branch.nodes.map(branchNode => ({
              id: branchNode.id,
              summary: branchNode.name,
              value: {
                type: 'script',
                path: `node/${branchNode.nodeId}`,
                input_transforms: branchNode.inputTransforms
              }
            }))
          }));
        
        const defaultBranch = branches.find(b => b.id.startsWith(node.id) && b.isDefault);
        const defaultModules = defaultBranch ? defaultBranch.nodes.map(branchNode => ({
          id: branchNode.id,
          summary: branchNode.name,
          value: {
            type: 'script',
            path: `node/${branchNode.nodeId}`,
            input_transforms: branchNode.inputTransforms
          }
        })) : [];
        
        return {
          id: node.id,
          summary: node.name,
          value: {
            type: node.type,
            branches: branchModules,
            ...(defaultModules.length > 0 && { default: defaultModules }),
            ...(node.type === 'branchall' && { parallel: true })
          }
        };
      } else {
        // Handle regular script nodes
        return {
          id: node.id,
          summary: node.name,
          value: {
            type: 'script',
            path: `node/${node.nodeId}`,
            input_transforms: node.inputTransforms
          }
        };
      }
    });
    
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
    
    // Call the callback prop if provided
    onworkflowchange?.(workflow);
    
    // Also dispatch the event for Svelte event handling
    dispatch('workflowChange', workflow);
    
    console.log('Workflow exported:', workflow);
  }
  
  // Get available outputs for mapping
  function getAvailableOutputs(currentNodeId: string, currentBranchId?: string): Array<{id: string, name: string, outputs: NodeOutput[], category: string}> {
    const allNodes = getAllNodes();
    const currentNode = allNodes.find(n => n.id === currentNodeId);
    if (!currentNode) return [];
    
    // Get nodes that come before this node in the execution flow
    const availableNodes: Array<{id: string, name: string, outputs: NodeOutput[], category: string}> = [];
    
    // Add flow_input as a special case
    availableNodes.push({
      id: 'flow_input',
      name: 'Workflow Input',
      category: 'Input',
      outputs: [
        { name: 'input_image', type: 'string', default: '', mapping: '', description: 'Input image URL' },
        { name: 'prompt', type: 'string', default: '', mapping: '', description: 'Input prompt' },
        { name: 'condition', type: 'string', default: '', mapping: '', description: 'Condition value' },
        { name: 'processing_type', type: 'string', default: '', mapping: '', description: 'Processing type selection' }
      ]
    });
    
    // Helper function to determine if a node comes before another in execution order
    function nodeComesBeforeInFlow(sourceNodeId: string, targetNodeId: string, targetBranchId?: string): boolean {
      const mainBranch = branches.find(b => b.id === 'main');
      if (!mainBranch) return false;
      
      // If target is in main branch
      if (!targetBranchId || targetBranchId === 'main') {
        const targetIndex = mainBranch.nodes.findIndex(n => n.id === targetNodeId);
        const sourceIndex = mainBranch.nodes.findIndex(n => n.id === sourceNodeId);
        
        // Source must come before target in main branch
        return sourceIndex >= 0 && sourceIndex < targetIndex;
      }
      
      // If target is in a sub-branch, find the parent branch node
      const parentBranchNodeId = targetBranchId.split('_branch_')[0].replace('_default', '');
      const parentBranchNode = mainBranch.nodes.find(n => n.id === parentBranchNodeId);
      
      if (!parentBranchNode) return false;
      
      const parentIndex = mainBranch.nodes.findIndex(n => n.id === parentBranchNodeId);
      const sourceIndex = mainBranch.nodes.findIndex(n => n.id === sourceNodeId);
      
      // Source in main branch must come before the parent branch node
      if (sourceIndex >= 0 && sourceIndex < parentIndex) {
        return true;
      }
      
      // If source is in the same branch, check position within branch
      const targetBranch = branches.find(b => b.id === targetBranchId);
      if (targetBranch) {
        const sourceBranchNode = targetBranch.nodes.find(n => n.id === sourceNodeId);
        const targetBranchNode = targetBranch.nodes.find(n => n.id === targetNodeId);
        
        if (sourceBranchNode && targetBranchNode) {
          const sourceBranchIndex = targetBranch.nodes.findIndex(n => n.id === sourceNodeId);
          const targetBranchIndex = targetBranch.nodes.findIndex(n => n.id === targetNodeId);
          return sourceBranchIndex < targetBranchIndex;
        }
      }
      
      return false;
    }
    
    // Add all nodes that come before the current node in execution order
    allNodes.forEach(node => {
      if (node.id === currentNodeId) return; // Skip self
      if (node.outputs.length === 0) return; // Skip nodes without outputs
      
      if (nodeComesBeforeInFlow(node.id, currentNodeId, currentBranchId)) {
        let category = 'Main Flow';
        
        // Determine category based on node location
        if (node.branchId && node.branchId !== 'main') {
          const branch = branches.find(b => b.id === node.branchId);
          if (branch) {
            if (branch.isDefault) {
              category = `${branch.name} (Default)`;
            } else {
              category = branch.name;
            }
          }
        }
        
        availableNodes.push({
          id: node.id,
          name: node.name,
          category: category,
          outputs: node.outputs
        });
      }
    });
    
    // Sort by category and then by name for better organization
    availableNodes.sort((a, b) => {
      if (a.category !== b.category) {
        // Input always first, then Main Flow, then branches
        if (a.category === 'Input') return -1;
        if (b.category === 'Input') return 1;
        if (a.category === 'Main Flow') return -1;
        if (b.category === 'Main Flow') return 1;
        return a.category.localeCompare(b.category);
      }
      return a.name.localeCompare(b.name);
    });
    
    return availableNodes;
  }
</script>

<div class="workflow-builder">
  <!-- Main Flow Canvas -->
  <div class="flow-container">
    <div class="flow-header">
      <h3>Workflow Flow</h3>
      <div class="flow-controls">
        <button class="btn-add" on:click={() => { showNodeSelector = true; searchTerm = ''; }}>
          + Add Node
        </button>
        <button class="btn-add" on:click={() => addBranchNode('branchone')}>
          + Conditional Branch
        </button>
        <button class="btn-add" on:click={() => addBranchNode('branchall')}>
          + Parallel Branch
        </button>
      </div>
    </div>

    <!-- Horizontal Flow Display -->
    <div class="flow-content">
      {#each branches as branch (branch.id)}
        <div class="branch-container" class:main-branch={branch.id === 'main'}>
          {#if branch.id !== 'main'}
            <div class="branch-header">
              <h4 class="branch-title">{branch.name}</h4>
              {#if branch.condition}
                <div class="branch-condition">
                  <input
                    type="text"
                    class="condition-input"
                    bind:value={branch.condition}
                    on:input={() => updateBranchCondition(branch.id, branch.condition || '')}
                    placeholder="Enter condition..."
                  />
                </div>
              {/if}
            </div>
          {/if}
          
          <div class="nodes-flow">
            {#each branch.nodes as node, index (node.id)}
              <div class="node-wrapper">
                <!-- Connection line -->
                {#if index > 0}
                  <div class="connection-line"></div>
                {/if}
                
                <!-- Node -->
                <div 
                  class="flow-node"
                  class:branch-node={node.type === 'branchone' || node.type === 'branchall'}
                  on:click={() => handleNodeClick(node)}
                >
                  <div class="node-header">
                    <h4 class="node-title">{node.name}</h4>
                    <button 
                      class="remove-btn"
                      on:click|stopPropagation={() => removeNode(node.id, branch.id)}
                      title="Remove node"
                    >
                      ×
                    </button>
                  </div>
                  
                  <div class="node-type-badge">
                    {#if node.type === 'branchone'}
                      Conditional
                    {:else if node.type === 'branchall'}
                      Parallel
                    {:else}
                      Script
                    {/if}
                  </div>
                  
                  <div class="node-meta">
                    <span class="input-count">{node.inputs.length} inputs</span>
                    <span class="output-count">{node.outputs.length} outputs</span>
                  </div>
                </div>
              </div>
            {/each}
            
            <!-- Add node to branch button -->
            {#if branch.id !== 'main' || branch.nodes.length === 0}
              <div class="add-to-branch">
                <button 
                  class="btn-add-to-branch"
                  on:click={() => { showNodeSelector = true; searchTerm = ''; }}
                  title="Add node to this branch"
                >
                  +
                </button>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Sidebar for node configuration -->
  {#if showSidebar && selectedNode}
    <div class="sidebar-overlay" on:click={() => showSidebar = false}>
      <div class="sidebar" on:click|stopPropagation>
        <div class="sidebar-header">
          <h3>{selectedNode.name}</h3>
          <button class="close-btn" on:click={() => showSidebar = false}>×</button>
        </div>
        
        <div class="sidebar-content">
          <div class="node-description">
            <p>{selectedNode.description}</p>
          </div>
          
          <!-- Input Configuration -->
          {#if selectedNode.inputs.length > 0}
            <div class="config-section">
              <h4>Input Configuration</h4>
              {#each selectedNode.inputs as input (input.name)}
                <div class="input-config">
                  <label class="input-label">
                    {input.name}
                    {#if input.required}<span class="required">*</span>{/if}
                  </label>
                  <p class="input-description">{input.description}</p>
                  
                  <div class="input-mapping">
                    <div class="mapping-tabs">
                      <button 
                        class="tab-btn"
                        class:active={!selectedNode?.inputTransforms[input.name] || selectedNode?.inputTransforms[input.name]?.type === 'static'}
                        on:click={() => {
                          if (!selectedNode) return;
                          // Switch to static mode
                          const currentValue = selectedNode.inputTransforms[input.name]?.value || '';
                          updateInputTransform(selectedNode.id, input.name, currentValue, 'static');
                        }}
                      >
                        Static Value
                      </button>
                      <button 
                        class="tab-btn"
                        class:active={selectedNode?.inputTransforms[input.name]?.type === 'javascript'}
                        on:click={() => {
                          if (!selectedNode) return;
                          // Switch to dynamic mode - ensure we create the transform object
                          const currentExpr = selectedNode.inputTransforms[input.name]?.expr || '';
                          // Force create the transform object even if expr is empty
                          console.log('Switching to dynamic mapping for', input.name, 'with current expr:', currentExpr); 
                          updateInputTransform(selectedNode.id, input.name, currentExpr || '', 'javascript');
                        }}
                      >
                        Dynamic Mapping
                      </button>
                    </div>
                    
                    {#if forceRerender >= 0 && (!selectedNode?.inputTransforms[input.name] || selectedNode?.inputTransforms[input.name]?.type === 'static')}
                      <input
                        type="text"
                        class="input-field"
                        placeholder={input.default?.toString() || ''}
                        value={selectedNode?.inputTransforms[input.name]?.value || ''}
                        on:input={(e) => selectedNode && updateInputTransform(selectedNode.id, input.name, (e.target as HTMLInputElement).value, 'static')}
                      />
                    {:else}
                      <div class="mapping-section">
                        <div class="mapping-builder">
                          <div class="source-selection">
                            <label class="mapping-label">Select Output Source:</label>
                            <select 
                              class="mapping-select"
                              on:change={(e) => {
                                if (!selectedNode) return;
                                const target = e.target as HTMLSelectElement;
                                const [sourceId, outputName] = target.value.split('.');
                                if (sourceId && outputName) {
                                  const baseExpression = sourceId === 'flow_input' ? 'flow_input' : 'results.' + sourceId;
                                  updateInputTransform(selectedNode.id, input.name, `${baseExpression}.${outputName}`, 'javascript');
                                }
                              }}
                            >
                              <option value="">Select source...</option>
                              {#each getAvailableOutputs(selectedNode?.id || '', selectedNode?.branchId) as source}
                                <optgroup label="{source.category}: {source.name}">
                                  {#each source.outputs as output}
                                    <option value="{source.id}.{output.name}">
                                      {output.name} ({output.type}) - {output.description}
                                    </option>
                                  {/each}
                                </optgroup>
                              {/each}
                            </select>
                          </div>
                          
                          <!-- Object Key Selection for complex outputs -->
                          {#if selectedNode?.inputTransforms[input.name]?.expr}
                            {@const currentExpr = selectedNode.inputTransforms[input.name].expr}
                            {@const isObjectOutput = currentExpr && (currentExpr.includes('results.') || currentExpr.includes('flow_input.'))}
                            {#if isObjectOutput}
                              <div class="object-key-selection">
                                <label class="mapping-label">Access Object Property:</label>
                                <div class="key-input-group">
                                  <input
                                    type="text"
                                    class="key-input"
                                    placeholder="Enter property key (e.g., image_url, metadata.width)"
                                    on:input={(e) => {
                                      if (!selectedNode) return;
                                      const keyPath = (e.target as HTMLInputElement).value.trim();
                                      if (keyPath) {
                                        const baseExpr = currentExpr.split('.').slice(0, -1).join('.');
                                        const newExpr = `${baseExpr}.${keyPath}`;
                                        updateInputTransform(selectedNode.id, input.name, newExpr, 'javascript');
                                      }
                                    }}
                                  />
                                  <button 
                                    class="key-help-btn"
                                    type="button"
                                    title="Common object keys: image_url, output, result, data, metadata, url, content"
                                  >
                                    ?
                                  </button>
                                </div>
                                <div class="key-suggestions">
                                  <span class="suggestion-label">Common keys:</span>
                                  {#each ['image_url', 'output', 'result', 'data', 'url', 'content', 'metadata'] as suggestedKey}
                                    <button 
                                      class="key-suggestion"
                                      type="button"
                                      on:click={() => {
                                        if (!selectedNode) return;
                                        const baseExpr = currentExpr.split('.').slice(0, -1).join('.');
                                        const newExpr = `${baseExpr}.${suggestedKey}`;
                                        updateInputTransform(selectedNode.id, input.name, newExpr, 'javascript');
                                      }}
                                    >
                                      {suggestedKey}
                                    </button>
                                  {/each}
                                </div>
                              </div>
                            {/if}
                          {/if}
                          
                          <div class="custom-expression">
                            <label class="mapping-label">Custom Expression:</label>
                            <input
                              type="text"
                              class="input-field expression-field"
                              placeholder="Or enter custom expression (e.g., results.node_1.output.image_url)"
                              value={selectedNode?.inputTransforms[input.name]?.expr || ''}
                              on:input={(e) => selectedNode && updateInputTransform(selectedNode.id, input.name, (e.target as HTMLInputElement).value, 'javascript')}
                            />
                          </div>
                          
                          <!-- Expression Preview -->
                          {#if selectedNode?.inputTransforms[input.name]?.expr}
                            <div class="expression-preview">
                              <span class="preview-label">Expression:</span>
                              <code class="expression-code">{selectedNode.inputTransforms[input.name].expr}</code>
                            </div>
                          {/if}
                        </div>
                      </div>
                    {/if}
                  </div>
                </div>
              {/each}
            </div>
          {/if}
          
          <!-- Output Information -->
          {#if selectedNode.outputs.length > 0}
            <div class="config-section">
              <h4>Outputs</h4>
              {#each selectedNode.outputs as output (output.name)}
                <div class="output-info">
                  <div class="output-name">{output.name}</div>
                  <div class="output-type">{output.type}</div>
                  <div class="output-description">{output.description}</div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    </div>
  {/if}

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
</div>

<style>
  .workflow-builder {
    position: relative;
    width: 100%;
    height: 600px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
    display: flex;
  }
  
  .flow-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .flow-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #e2e8f0;
    background: #f8fafc;
  }
  
  .flow-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
  }
  
  .flow-controls {
    display: flex;
    gap: 8px;
  }
  
  .btn-add {
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .btn-add:hover {
    background: #2563eb;
  }
  
  .flow-content {
    flex: 1;
    overflow: auto;
    padding: 16px;
  }
  
  .branch-container {
    margin-bottom: 24px;
  }
  
  .main-branch {
    border: 2px solid #3b82f6;
    border-radius: 8px;
    padding: 16px;
    background: #f8fafc;
  }
  
  .branch-header {
    margin-bottom: 12px;
    padding: 8px 12px;
    background: #e2e8f0;
    border-radius: 6px;
  }
  
  .branch-title {
    margin: 0 0 8px 0;
    font-size: 14px;
    font-weight: 600;
    color: #374151;
  }
  
  .condition-input {
    width: 100%;
    padding: 6px 8px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 12px;
    font-family: monospace;
  }
  
  .condition-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 1px #3b82f6;
  }
  
  .nodes-flow {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    overflow-y: auto;
    padding: 8px 0;
  }
  
  .node-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }
  
  .connection-line {
    width: 2px;
    height: 32px;
    background: #9ca3af;
    position: relative;
  }
  
  .connection-line::after {
    content: '';
    position: absolute;
    bottom: -4px;
    left: -2px;
    width: 0;
    height: 0;
    border-top: 6px solid #9ca3af;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
  }
  
  .flow-node {
    min-width: 180px;
    padding: 12px;
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .flow-node:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  
  .flow-node.branch-node {
    border-color: #f59e0b;
    background: #fffbeb;
  }
  
  .flow-node.branch-node:hover {
    border-color: #d97706;
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
  
  .node-type-badge {
    display: inline-block;
    padding: 2px 6px;
    background: #e2e8f0;
    color: #374151;
    font-size: 10px;
    font-weight: 500;
    border-radius: 4px;
    margin-bottom: 8px;
    text-transform: uppercase;
  }
  
  .node-meta {
    display: flex;
    gap: 8px;
    font-size: 11px;
    color: #6b7280;
  }
  
  .add-to-branch {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .btn-add-to-branch {
    width: 40px;
    height: 40px;
    border: 2px dashed #d1d5db;
    background: transparent;
    border-radius: 50%;
    cursor: pointer;
    font-size: 18px;
    color: #6b7280;
    transition: all 0.2s;
  }
  
  .btn-add-to-branch:hover {
    border-color: #3b82f6;
    color: #3b82f6;
    background: #f8fafc;
  }
  
  /* Sidebar Styles */
  .sidebar-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: stretch;
    justify-content: flex-end;
    z-index: 1000;
  }
  
  .sidebar {
    width: 400px;
    background: white;
    display: flex;
    flex-direction: column;
    box-shadow: -4px 0 8px rgba(0, 0, 0, 0.1);
  }
  
  .sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #e2e8f0;
    background: #f8fafc;
  }
  
  .sidebar-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
  }
  
  .sidebar-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }
  
  .node-description {
    margin-bottom: 24px;
    padding: 12px;
    background: #f8fafc;
    border-radius: 6px;
  }
  
  .node-description p {
    margin: 0;
    font-size: 14px;
    color: #64748b;
    line-height: 1.5;
  }
  
  .config-section {
    margin-bottom: 24px;
  }
  
  .config-section h4 {
    margin: 0 0 16px 0;
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
  }
  
  .input-config {
    margin-bottom: 20px;
    padding: 16px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
  }
  
  .input-label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: #374151;
    margin-bottom: 4px;
  }
  
  .required {
    color: #ef4444;
  }
  
  .input-description {
    margin: 0 0 12px 0;
    font-size: 12px;
    color: #6b7280;
    line-height: 1.4;
  }
  
  .mapping-tabs {
    display: flex;
    margin-bottom: 12px;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .tab-btn {
    background: none;
    border: none;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 500;
    color: #6b7280;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
  }
  
  .tab-btn.active {
    color: #3b82f6;
    border-bottom-color: #3b82f6;
  }
  
  .tab-btn:hover {
    color: #374151;
  }
  
  .input-field {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
  }
  
  .input-field:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 1px #3b82f6;
  }
  
  .mapping-section {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .mapping-builder {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 12px;
    background: #f8fafc;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
  }
  
  .source-selection {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  
  .mapping-label {
    font-size: 12px;
    font-weight: 500;
    color: #374151;
    margin-bottom: 4px;
  }
  
  .mapping-select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
    background: white;
  }
  
  .mapping-select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 1px #3b82f6;
  }
  
  .object-key-selection {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .key-input-group {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  
  .key-input {
    flex: 1;
    padding: 6px 8px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 12px;
    font-family: monospace;
  }
  
  .key-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 1px #3b82f6;
  }
  
  .key-help-btn {
    background: #6b7280;
    color: white;
    border: none;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    cursor: pointer;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  
  .key-help-btn:hover {
    background: #374151;
  }
  
  .key-suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    align-items: center;
  }
  
  .suggestion-label {
    font-size: 11px;
    color: #6b7280;
    margin-right: 4px;
  }
  
  .key-suggestion {
    background: #e5e7eb;
    color: #374151;
    border: none;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .key-suggestion:hover {
    background: #3b82f6;
    color: white;
  }
  
  .custom-expression {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  
  .expression-field {
    font-family: monospace;
    font-size: 12px;
  }
  
  .expression-preview {
    padding: 8px;
    background: #f3f4f6;
    border-radius: 4px;
    border-left: 3px solid #3b82f6;
  }
  
  .preview-label {
    font-size: 11px;
    font-weight: 500;
    color: #6b7280;
    margin-right: 8px;
  }
  
  .expression-code {
    font-family: monospace;
    font-size: 11px;
    color: #1f2937;
    background: #e5e7eb;
    padding: 2px 4px;
    border-radius: 3px;
  }
  
  .output-info {
    margin-bottom: 12px;
    padding: 12px;
    background: #f8fafc;
    border-radius: 6px;
  }
  
  .output-name {
    font-size: 14px;
    font-weight: 500;
    color: #374151;
    margin-bottom: 4px;
  }
  
  .output-type {
    font-size: 12px;
    color: #6b7280;
    margin-bottom: 4px;
  }
  
  .output-description {
    font-size: 12px;
    color: #64748b;
    line-height: 1.4;
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
  
  /* Modal Styles */
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
</style>
