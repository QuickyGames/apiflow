import json
import requests
import re
import os
from typing import Any, Dict, List
from backend.lib.db import Node, Connector

class NodeExecutor:
    def __init__(self, node: Node):
        self.node = node
        self.connector = node.connector
    
    def prepare_input(self, provided_input: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input by merging provided values with defaults"""
        prepared = {}
        
        for input_def in self.node.input:
            name = input_def['name']
            
            if name in provided_input:
                prepared[name] = provided_input[name]
            elif input_def.get('required', False):
                if 'default' in input_def:
                    prepared[name] = input_def['default']
                else:
                    raise ValueError(f"Required input '{name}' not provided and no default value")
            elif 'default' in input_def:
                prepared[name] = input_def['default']
        
        return prepared
    
    def substitute_variables(self, template: Any, context: Dict[str, Any]) -> Any:
        """Recursively substitute variables in templates"""
        if isinstance(template, str):
            # Replace $VARIABLE_NAME with actual values
            def replace_var(match):
                var_name = match.group(1)
                if var_name in context:
                    return str(context[var_name])
                # Check environment variables
                env_value = os.getenv(var_name)
                if env_value:
                    return env_value
                return match.group(0)  # Return original if not found
            
            return re.sub(r'\$([A-Z_][A-Z0-9_]*)', replace_var, template)
        
        elif isinstance(template, dict):
            return {k: self.substitute_variables(v, context) for k, v in template.items()}
        
        elif isinstance(template, list):
            return [self.substitute_variables(item, context) for item in template]
        
        return template
    
    def build_request_url(self, input_data: Dict[str, Any]) -> str:
        """Build the full request URL"""
        base_url = self.connector.base_url
        
        # Handle path parameters if needed
        if 'path' in input_data:
            if not base_url.endswith('/'):
                base_url += '/'
            base_url += input_data['path']
        
        return base_url
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node with given input"""
        # Prepare input
        prepared_input = self.prepare_input(input_data)
        
        # Build request
        url = self.build_request_url(prepared_input)
        
        # Prepare headers with variable substitution
        headers = self.substitute_variables(self.connector.header, prepared_input)
        
        # Prepare body
        body = None
        if self.connector.method in ['POST', 'PUT', 'PATCH']:
            if self.connector.body:
                body = self.substitute_variables(self.connector.body, prepared_input)
            else:
                # Use input data as body
                body = prepared_input
        
        # Make request
        try:
            response = requests.request(
                method=self.connector.method,
                url=url,
                headers=headers,
                json=body if body else None,
                timeout=300  # 5 minutes timeout
            )
            
            response.raise_for_status()
            
            # Parse response
            result = response.json() if response.content else {}
            
            # Map outputs
            output = {}
            for output_def in self.node.output:
                name = output_def['name']
                mapping = output_def.get('mapping', name)
                
                # Navigate through nested response
                value = result
                for key in mapping.split('.'):
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        value = output_def.get('default', None)
                        break
                
                output[name] = value
            
            return output
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Node execution failed: {str(e)}")


def execute_node(node_id: int, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a node by ID"""
    try:
        node = Node.get(Node.id == node_id)
        executor = NodeExecutor(node)
        return executor.execute(input_data)
    except Node.DoesNotExist:
        raise ValueError(f"Node with ID {node_id} not found")
