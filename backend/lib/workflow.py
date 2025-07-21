import json
import asyncio
import time
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from backend.lib.db import Workflow, Job, Node
from backend.lib.node import execute_node

class WorkflowExecutor:
    def __init__(self, workflow: Workflow, job: Job):
        self.workflow = workflow
        self.job = job
        self.results = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def evaluate_expression(self, expr: str, context: Dict[str, Any]) -> Any:
        """Safely evaluate a JavaScript-like expression"""
        # Create a safe evaluation context
        safe_context = {
            'flow_input': context.get('flow_input', {}),
            'results': context.get('results', {}),
            'true': True,
            'false': False,
            'null': None
        }
        
        # Replace JavaScript operators with Python equivalents
        expr = expr.replace('===', '==').replace('!==', '!=')
        
        try:
            # Use eval with restricted globals
            return eval(expr, {"__builtins__": {}}, safe_context)
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression '{expr}': {str(e)}")
    
    def transform_input(self, transforms: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply input transformations"""
        result = {}
        
        for key, transform in transforms.items():
            if isinstance(transform, dict):
                transform_type = transform.get('type', 'static')
                
                if transform_type == 'static':
                    result[key] = transform.get('value')
                elif transform_type == 'javascript':
                    expr = transform.get('expr', '')
                    result[key] = self.evaluate_expression(expr, context)
                else:
                    result[key] = transform
            else:
                # Direct value
                result[key] = transform
        
        return result
    
    async def execute_module(self, module: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a single module"""
        module_id = module.get('id', 'unknown')
        module_value = module.get('value', {})
        module_type = module_value.get('type', 'script')
        
        try:
            if module_type == 'script':
                # Execute a node
                path = module_value.get('path', '')
                if path.startswith('node/'):
                    node_id = int(path.split('/')[-1].replace('_node_id', ''))
                    
                    # Transform inputs
                    input_transforms = module_value.get('input_transforms', {})
                    input_data = self.transform_input(input_transforms, context)
                    
                    # Execute node
                    result = await asyncio.get_event_loop().run_in_executor(
                        self.executor, execute_node, node_id, input_data
                    )
                    
                    # Store result
                    self.results[module_id] = result
                    context['results'][module_id] = result
                    
                    return result
                else:
                    raise ValueError(f"Invalid node path: {path}")
            
            elif module_type == 'branchone':
                # Conditional execution
                branches = module_value.get('branches', [])
                default_modules = module_value.get('default', [])
                
                for branch in branches:
                    expr = branch.get('expr', 'false')
                    if self.evaluate_expression(expr, context):
                        # Execute modules in this branch
                        results = []
                        for sub_module in branch.get('modules', []):
                            result = await self.execute_module(sub_module, context)
                            results.append(result)
                        return results
                
                # Execute default branch
                results = []
                for sub_module in default_modules:
                    result = await self.execute_module(sub_module, context)
                    results.append(result)
                return results
            
            elif module_type == 'branchall':
                # Parallel execution
                branches = module_value.get('branches', [])
                parallel = module_value.get('parallel', False)
                
                if parallel:
                    # Execute all branches in parallel
                    tasks = []
                    for branch in branches:
                        branch_modules = branch.get('modules', [])
                        for sub_module in branch_modules:
                            task = self.execute_module(sub_module, context)
                            tasks.append(task)
                    
                    results = await asyncio.gather(*tasks)
                    return results
                else:
                    # Execute branches sequentially
                    results = []
                    for branch in branches:
                        branch_modules = branch.get('modules', [])
                        for sub_module in branch_modules:
                            result = await self.execute_module(sub_module, context)
                            results.append(result)
                    return results
            
            else:
                raise ValueError(f"Unknown module type: {module_type}")
                
        except Exception as e:
            # Handle retry logic
            retry_config = module.get('retry', {})
            if retry_config:
                exponential = retry_config.get('exponential', {})
                attempts = exponential.get('attempts', 1)
                multiplier = exponential.get('multiplier', 2)
                seconds = exponential.get('seconds', 5)
                
                for attempt in range(attempts):
                    if attempt > 0:
                        wait_time = seconds * (multiplier ** (attempt - 1))
                        await asyncio.sleep(wait_time)
                    
                    try:
                        # Retry the execution
                        return await self.execute_module(module, context)
                    except Exception:
                        if attempt == attempts - 1:
                            raise
            else:
                raise
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow"""
        # Update job status
        self.job.status = 'running'
        self.job.input = input_data
        self.job.save()
        
        try:
            # Initialize context
            context = {
                'flow_input': input_data,
                'results': {}
            }
            
            # Get workflow modules
            workflow_nodes = self.workflow.nodes
            modules = workflow_nodes.get('value', {}).get('modules', [])
            
            # Execute modules sequentially
            final_result = None
            for module in modules:
                result = await self.execute_module(module, context)
                final_result = result
            
            # Update job with success
            self.job.status = 'completed'
            self.job.output = self.results
            self.job.save()
            
            return self.results
            
        except Exception as e:
            # Update job with failure
            self.job.status = 'failed'
            self.job.error = str(e)
            self.job.save()
            raise
        finally:
            self.executor.shutdown(wait=False)


async def execute_workflow(workflow_id: int, input_data: Dict[str, Any], job_name: Optional[str] = None) -> Job:
    """Execute a workflow by ID"""
    try:
        workflow = Workflow.get(Workflow.id == workflow_id)
        
        # Create job
        job = Job.create(
            name=job_name or f"Job for {workflow.name}",
            workflow=workflow,
            status='pending',
            input=input_data
        )
        
        # Execute workflow
        executor = WorkflowExecutor(workflow, job)
        await executor.execute(input_data)
        
        return job
        
    except Workflow.DoesNotExist:
        raise ValueError(f"Workflow with ID {workflow_id} not found")
