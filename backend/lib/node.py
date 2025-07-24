import json
import requests
import re
import os
import logging
from typing import Any, Dict, List
from backend.lib.db import Node, Connector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeExecutor:
    def __init__(self, node: Node):
        self.node = node
        self.connector = node.connector
    
    def prepare_input(self, provided_input: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input by merging provided values with defaults"""
        prepared = {}
        
        for input_def in self.node.input:
            name = input_def['name']
            input_type = input_def.get('type', 'string')
            
            # Check if value is provided and not empty
            if name in provided_input and provided_input[name] != '':
                value = provided_input[name]
                
                # Type conversion for specific types
                if input_type == 'boolean':
                    if isinstance(value, str):
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        value = bool(value)
                elif input_type == 'integer':
                    if isinstance(value, str) and value.isdigit():
                        value = int(value)
                elif input_type == 'number':
                    if isinstance(value, str):
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                
                prepared[name] = value
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
        """Build the full request URL by combining connector base_url with node path"""
        base_url = self.connector.base_url.rstrip('/')
        node_path = self.node.path.strip()
        
        # Combine base URL with node path
        if node_path:
            if not node_path.startswith('/'):
                node_path = '/' + node_path
            full_url = base_url + node_path
        else:
            full_url = base_url
        
        logger.info(f"Building URL: base_url='{base_url}', node_path='{self.node.path}', full_url='{full_url}'")
        return full_url
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node with given input"""
        logger.info(f"Executing node '{self.node.name}' (ID: {self.node.id})")
        logger.info(f"Input data: {input_data}")
        
        # Prepare input
        prepared_input = self.prepare_input(input_data)
        logger.info(f"Prepared input: {prepared_input}")
        
        # Build request
        url = self.build_request_url(prepared_input)
        
        # Prepare headers with variable substitution
        headers = self.substitute_variables(self.connector.header, prepared_input)
        logger.info(f"Request headers: {headers}")
        
        # Prepare body
        body = None
        if self.connector.method in ['POST', 'PUT', 'PATCH']:
            if self.connector.body:
                body = self.substitute_variables(self.connector.body, prepared_input)
            else:
                # Use input data as body
                body = {"input": prepared_input}  # Wrap in input object for Replicate API
        
        logger.info(f"Request method: {self.connector.method}")
        logger.info(f"Request URL: {url}")
        logger.info(f"Request body: {body}")
        
        # Make request
        try:
            response = requests.request(
                method=self.connector.method,
                url=url,
                headers=headers,
                json=body if body else None,
                timeout=300  # 5 minutes timeout
            )
            
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.content:
                logger.info(f"Response content: {response.text[:1000]}...")  # Log first 1000 chars
            
            response.raise_for_status()
            
            # Parse response
            result = response.json() if response.content else {}
            logger.info(f"Parsed response: {result}")
            
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
                logger.info(f"Mapped output '{name}': {value}")
            
            logger.info(f"Final output: {output}")
            return output
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            logger.error(f"Response status: {getattr(e.response, 'status_code', 'N/A')}")
            logger.error(f"Response text: {getattr(e.response, 'text', 'N/A')}")
            raise Exception(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Node execution failed: {str(e)}")
            raise Exception(f"Node execution failed: {str(e)}")


def execute_node(node_id: int, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a node by ID"""
    try:
        node = Node.get(Node.id == node_id)
        executor = NodeExecutor(node)
        return executor.execute(input_data)
    except Node.DoesNotExist:
        raise ValueError(f"Node with ID {node_id} not found")
