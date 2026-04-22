# Media-Lab

Media-Lab is a lightweight media processing service designed to transform video inputs into optimized motion GIF outputs using configurable presets. It is built to pair directly with the Media-Tiles frontend as a rendering tool layer inside a broader media curation system.

At its core, Media-Lab takes uploaded video files, applies motion and visual enhancement presets, and returns a downloadable optimized GIF.

---

## 🌐 Live System

- Frontend: Media-Tiles UI (GitHub Pages)
- Backend: Render-hosted API service
- Output: Optimized GIF files served via static endpoint

---

## 🧰 Core Features

### GIF Motion Processing
Convert MP4 (or compatible video formats) into high-quality GIF outputs with motion-aware processing.

### Preset-Based Rendering
Each preset controls motion interpolation, visual fidelity, and output compression behavior.

Available presets:

- **Balanced (balanced_v1)**
  - Stable output baseline
  - Clean motion
  - Minimal artifacts
  - Optimized file size

- **Fluid Motion (fluid_motion_v1)**
  - Higher interpolation strength
  - Smoother motion rendering
  - Enhanced perceived frame continuity

- **Cinematic (cinematic_v1)**
  - Builds on Fluid Motion base
  - Increased visual intensity
  - Higher contrast and perceptual sharpness
  - Film-like motion smoothing
  - Variable output size depending on source complexity

---

## 🧱 System Architecture

Media-Lab is split into two connected layers:

### 1. Frontend (Media-Tiles UI)
- Static HTML/JS interface
- Hosted via GitHub Pages
- Handles:
  - File upload
  - Preset selection
  - API requests
  - Download handling

### 2. Backend (Media-Lab API)
- Python FastAPI service (Uvicorn)
- Hosted on Render
- Handles:
  - Video ingestion
  - FFmpeg processing pipeline
  - Preset configuration mapping
  - Output generation and storage

---

## 🔗 Media-Tiles Integration

Media-Lab is designed as a tool module within the Media-Tiles ecosystem.

Media-Tiles acts as the UI and catalog layer, while Media-Lab functions as the processing engine.

Future planned integrations:
- Additional media transformation tools
- Catalog-driven preset selection
- Multi-tool routing system (GIF, upscale, interpolation, etc.)
- Shared output library across tiles

---

## ⚙️ API Overview

### POST `/upload`

Uploads a file and processes it using the selected preset.

**Form Data:**
- `file`: video file
- `tool`: processing tool (currently `gif_motion`)
- `preset`: rendering preset

**Response:**
```json
{
  "output_url": "/outputs/filename.gif"
}
