# Image Processing Service

 A backend system for an image processing service similar to Cloudinary. 
 The service allows users to upload images, perform various transformations, and retrieve images in different formats. 
 The system features user authentication, image upload, transformation operations, and efficient retrieval mechanisms.

## Architecture

- **JWT Authentication** 
- **Redis** — Acts as the message broker: cache for ip-based rate limiter 
- **Celery** —  Job queue to process uploaded files in the background
- **S3** — Stores uploaded files 
- **Postgres** — Persists job metadata and results, user credentials
- **Pillow** - Image processing library
- **AWS Cloudfront** - Caching most frequestly accessed uploaded files

## How It Works

1. Client uploads an image via `POST`
2. API server saves the image to S3 
3. Client request the image from CDN to be transformed 
4. The API applies the image transformation methods via asynchronous task using Celery 

## Getting Started

### Prerequisites

- Python 3.10+
- Redis server running locally or via Docker
- Celery 

### Running Redis

```bash
docker run -d -p 6379:6379 redis
```

### Start the API Server

```bash
python main.py
```

### Start the Celery Worker

```bash
celery -A `celery instance path` worker 
```

## API Reference

**Request:** 

`POST /images/:id/transform`

```json
{
  "transformations": {
    "resize": {
      "width": "number",
      "height": "number"
    },
    "crop": {
      "width": "number",
      "height": "number",
      "x": "number",
      "y": "number"
    },
    "rotate": "number",
    "format": "string",
    "filters": {
      "grayscale": "boolean",
      "sepia": "boolean"
    }
  }
}
```
