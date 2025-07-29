# Claude to flux

Workflow json delcartion for 
claude prompt : `you ar a image generation prompt generator, you will be given a text description and you will generate a prompt for the image generation model.`
user: `A duck on a lake`

use the claude response for the flux promp generation

```json
{
    "name": "Claude to Flux Pro Workflow",
    "description": "Uses Claude to generate optimized prompts for Flux Pro image generation",
    "nodes": {
        "summary": "Claude to Flux Pro Image Generation",
        "description": "A workflow that uses Claude to generate an optimized image generation prompt from user input, then uses Flux Pro to generate the image",
        "schema": {
            "type": "object",
            "properties": {
                "user_description": {
                    "type": "string",
                    "description": "The user's text description of what they want to generate"
                },
                "image_width": {
                    "type": "integer",
                    "description": "Width of the generated image",
                    "default": 1024
                },
                "image_height": {
                    "type": "integer",
                    "description": "Height of the generated image", 
                    "default": 1024
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": "Aspect ratio of the generated image",
                    "default": "1:1"
                }
            },
            "required": ["user_description"]
        },
        "value": {
            "modules": [
                {
                    "id": "claude_prompt_generator",
                    "summary": "Generate optimized image prompt with Claude",
                    "value": {
                        "type": "script",
                        "path": "node/anthropic_chat_node_id",
                        "input_transforms": {
                            "model": {
                                "type": "static",
                                "value": "claude-opus-4-20250514"
                            },
                            "max_tokens": {
                                "type": "static",
                                "value": 1024
                            },
                            "messages": {
                                "type": "static",
                                "value": [
                                    {
                                        "role": "user",
                                        "content": "You are an image generation prompt generator. You will be given a text description and you will generate a detailed, optimized prompt for an image generation model. Make the prompt vivid, descriptive, and include artistic style elements that will produce high-quality results.\n\nUser description: ${flow_input.user_description}\n\nGenerate an optimized image generation prompt:"
                                    }
                                ]
                            }
                        }
                    }
                },
                {
                    "id": "flux_image_generation",
                    "summary": "Generate image with Flux Pro",
                    "value": {
                        "type": "script",
                        "path": "node/flux_pro_node_id",
                        "input_transforms": {
                            "prompt": {
                                "type": "javascript",
                                "expr": "results.claude_prompt_generator.content[0].text"
                            },
                            "width": {
                                "type": "javascript",
                                "expr": "flow_input.image_width || 1024"
                            },
                            "height": {
                                "type": "javascript",
                                "expr": "flow_input.image_height || 1024"
                            },
                            "aspect_ratio": {
                                "type": "javascript",
                                "expr": "flow_input.aspect_ratio || '1:1'"
                            },
                            "steps": {
                                "type": "static",
                                "value": 25
                            },
                            "guidance": {
                                "type": "static",
                                "value": 3.0
                            },
                            "interval": {
                                "type": "static",
                                "value": 2
                            },
                            "output_format": {
                                "type": "static",
                                "value": "webp"
                            },
                            "output_quality": {
                                "type": "static",
                                "value": 80
                            },
                            "safety_tolerance": {
                                "type": "static",
                                "value": 2
                            },
                            "prompt_upsampling": {
                                "type": "static",
                                "value": false
                            }
                        }
                    }
                }
            ]
        }
    }
}
```