# Workflow setup

## Curl command:
```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Prefer: wait" \
  -d $'{
    "input": {
      "steps": 25,
      "width": 1024,
      "height": 1024,
      "prompt": "The world\'s largest black forest cake, the size of a building, surrounded by trees of the black forest",
      "guidance": 3,
      "interval": 2,
      "aspect_ratio": "1:1",
      "output_format": "webp",
      "output_quality": 80,
      "safety_tolerance": 2,
      "prompt_upsampling": false
    }
  }' \
  https://api.replicate.com/v1/models/black-forest-labs/flux-pro/predictions
```
**Output:**
```json
{
  "completed_at": "2025-07-24T12:20:47.653643Z",
  "created_at": "2025-07-24T12:20:40.332000Z",
  "data_removed": false,
  "error": null,
  "id": "bjesnqf71hrma0cr7hgacg0ypm",
  "input": {
    "steps": 25,
    "width": 1024,
    "height": 1024,
    "prompt": "The world's largest black forest cake, the size of a building, surrounded by trees of the black forest",
    "guidance": 3,
    "interval": 2,
    "aspect_ratio": "1:1",
    "output_format": "webp",
    "output_quality": 80,
    "safety_tolerance": 2,
    "prompt_upsampling": false
  },
  "logs": "Running prediction...\nUsing seed: 43242\nGenerating image...\nGenerated image in 6.9sec\nDownloaded image in 0.41sec",
  "metrics": {
    "image_count": 1,
    "predict_time": 7.313384184,
    "total_time": 7.321643
  },
  "output": "https://replicate.delivery/xezq/SfOZHbMoTp2jCCipxrcISvBzotE8fPeF2wZY40j1UyIex1PUB/tmp1p43r0ma.webp",
  "started_at": "2025-07-24T12:20:40.340259Z",
  "status": "succeeded",
  "urls": {
    "stream": "https://stream.replicate.com/v1/files/bcwr-fltb4vg7zsxh2zxmjcxggnga5njaexnulx3qwnaqyzzorlcd267a",
    "get": "https://api.replicate.com/v1/predictions/bjesnqf71hrma0cr7hgacg0ypm",
    "cancel": "https://api.replicate.com/v1/predictions/bjesnqf71hrma0cr7hgacg0ypm/cancel",
    "web": "https://replicate.com/p/bjesnqf71hrma0cr7hgacg0ypm"
  },
  "version": "hidden"
}
```

## Create a connector

Name: Replicate
Base URL: https://api.replicate.com/v1
Method: POST
Headers:
```json
{
  "Authorization": "Bearer token",
"Content-Type": "application/json",
"Prefer": "wait"
}
```

## Create a node
Name: Flux Pro 
Description: Flux Pro text to image generation.
Connector: Replicate
Path: /models/black-forest-labs/flux-pro/predictions
Body Template:
```json
{
  "input": {
    "steps": "$steps",
    "width": "$width",
    "height": "$height",
    "prompt": "$prompt",
    "guidance": "$guidance",
    "interval": "$interval",
    "aspect_ratio": "$aspect_ratio",
    "output_format": "$output_format",
    "output_quality": "$output_quality",
    "safety_tolerance": "$safety_tolerance",
    "prompt_upsampling": "$prompt_upsampling"
  }
}
```
Input Schema:
```json
[
    {
        "name": "steps",
        "type": "integer",
        "description": "Number of steps for the image generation",
        "default": 25
    },
    {
        "name": "width",
        "type": "integer",
        "description": "Width of the generated image",
        "default": 1024
    },
    {
        "name": "height",
        "type": "integer",
        "description": "Height of the generated image",
        "default": 1024
    },
    {
        "name": "prompt",
        "type": "string",
        "description": "Text prompt for image generation",
        "default": "The world's largest black forest cake, the size of a building, surrounded by trees of the black forest"
    },
    {
        "name": "guidance",
        "type": "number",
        "description": "Guidance scale for image generation",
        "default": 3.0
    },
    {
        "name": "interval",
        "type": "integer",
        "description": "Interval for image generation steps",
        "default": 2
    },
    {
        "name": "aspect_ratio",
        "type": "string",
        "description": "Aspect ratio of the generated image (e.g., '1:1')",
        "default": "1:1"
    },
    {
        "name": "output_format",
        "type": "string",
        "description": "Output format of the generated image (e.g., 'webp')",
        "default": "webp"
    },
    {
        "name": "output_quality",
        "type": "integer",
        "description": "Quality of the output image (0-100)",
        "default": 80
    },
    {
        "name": "safety_tolerance",
        "type": "integer",
        "description": "Safety tolerance level for content filtering (0-5)",
        "default": 2
    },
    {
        "name": "prompt_upsampling",
        "type": "boolean",
        "description": "Whether to apply upsampling to the prompt",
        "default": false
    }
]
```

Output Schema:
```json
[
    {
        "name": "output",
        "type": "string",
        "description": "URL of the generated image"
    },
    {
        "name": "status",
        "type": "string",
        "description": "Status of the prediction (e.g., 'succeeded', 'failed')"
    },
    {
        "name": "logs",
        "type": "string",
        "description": "Logs from the prediction process"
    },
    {
        "name": "metrics",
        "type": "object",
        "description": "Metrics related to the prediction, such as time taken"
    }
]
```
