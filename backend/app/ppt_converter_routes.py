import uuid
import os
import json
from flask import Blueprint, request, jsonify, current_app
from .tasks import convert_to_pdf
from .enums.job_status import JobStatus

ppt_converter = Blueprint("ppt_converter", __name__, url_prefix="/convert")


# Request body: {'file': fileObj}
@ppt_converter.route("/upload", methods=["POST"])
def upload():
    r = current_app.redis
    if "file" not in request.files:
        return jsonify({"message": "No file in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    allowed_extensions = {"ppt", "pptx"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext.replace(".", "") not in allowed_extensions:
        return (
            jsonify({"message": "Invalid file type. Only .ppt and .pptx allowed."}),
            400,
        )

    job_id = str(uuid.uuid4())

    # store file in tmp and add job to redis
    ppt_path = f"/tmp/{job_id}.pptx"
    file.save(ppt_path)
    r.set(f"job:{job_id}", json.dumps({"status": JobStatus.PROCESSING.value}))

    # start worker process
    convert_to_pdf.delay(job_id, ppt_path)

    return jsonify({"job_id": job_id})


@ppt_converter.route("/status/<job_id>", methods=["GET"])
def check_status(job_id):
    r = current_app.redis
    job_data = r.get(f"job:{job_id}")

    if not job_data:
        return jsonify({"message": "Invalid Job Id"}), 404

    try:
        job = json.loads(job_data)
    except json.JSONDecodeError:
        return jsonify({"error": "Corrupted job data"}), 500

    status = job.get("status")

    if status == JobStatus.PROCESSING.value:
        return jsonify({"status": "processing"}), 200
    elif status == JobStatus.FAILED.value:
        return jsonify({"message": "Job failed during processing"}), 500
    elif status == JobStatus.COMPLETED.value:
        presign_url = job.get("url")
        if not presign_url:
            return jsonify({"message": "Missing download URL"}), 500
        return (
            jsonify({"status": JobStatus.COMPLETED.value, "presignUrl": presign_url}),
            200,
        )
    else:
        return jsonify({"message": "Unknown error"}), 500
