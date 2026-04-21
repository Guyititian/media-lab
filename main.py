from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import os
import tempfile

# import tool
from tools.gif_motion import process as gif_process

app = FastAPI()


# ----------------------------
# TOOL REGISTRY (future-proofing layer)
# ----------------------------
TOOLS = {
    "gif_motion": gif_process
}


# ----------------------------
# ROOT
# ----------------------------
@app.get("/")
def root():
    return {
        "status": "media-lab tool engine v1",
        "tools": list(TOOLS.keys())
    }


# ----------------------------
# SUBMIT JOB (tool-based)
# ----------------------------
@app.post("/tools/{tool_name}/submit")
async def submit(tool_name: str, file: UploadFile = File(...)):
    
    if tool_name not in TOOLS:
        return {"error": "tool not found"}

    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input.mp4")
        output_path = os.path.join(tmp, "output.gif")

        contents = await file.read()

        with open(input_path, "wb") as f:
            f.write(contents)

        # run tool
        TOOLS[tool_name](input_path, output_path)

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return {"job_id": job_id, "error": "processing failed"}

        with open(output_path, "rb") as f:
            gif_data = f.read()

    # store job
    app.state.jobs = getattr(app.state, "jobs", {})

    app.state.jobs[job_id] = {
        "tool": tool_name,
        "status": "completed",
        "file": gif_data
    }

    return {
        "job_id": job_id,
        "status": "completed",
        "result_url": f"/jobs/{job_id}/result"
    }


# ----------------------------
# JOB STATUS
# ----------------------------
@app.get("/jobs/{job_id}")
def job_status(job_id: str):

    jobs = getattr(app.state, "jobs", {})

    if job_id not in jobs:
        return {"error": "job not found"}

    return {
        "job_id": job_id,
        "tool": jobs[job_id]["tool"],
        "status": jobs[job_id]["status"]
    }


# ----------------------------
# RESULT DOWNLOAD
# ----------------------------
@app.get("/jobs/{job_id}/result")
def job_result(job_id: str):

    jobs = getattr(app.state, "jobs", {})

    if job_id not in jobs:
        return {"error": "job not found"}

    path = f"/tmp/{job_id}.gif"

    with open(path, "wb") as f:
        f.write(jobs[job_id]["file"])

    return FileResponse(
        path,
        media_type="image/gif",
        filename="output.gif"
    )
