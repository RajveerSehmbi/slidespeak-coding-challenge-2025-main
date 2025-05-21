import os
import json
import requests
from celery import shared_task
from flask import current_app
from .enums.job_status import JobStatus



unoserver_url = os.getenv("UNOSERVER_URL")


@shared_task
def convert_to_pdf(job_id, ppt_path):
    r = current_app.redis
    lock_key = "unoserver_lock"
    lock = r.lock(lock_key, timeout=120, blocking_timeout=10)
    if not lock.acquire(blocking=True):
        convert_to_pdf.apply_async((job_id, ppt_path), countdown=10)
        return

    try:
        with open(ppt_path, "rb") as file:
            files = {"file": (ppt_path, file)}
            data = {"convert-to": "pdf"}

            response = requests.post(unoserver_url, files=files, data=data)

            if response.status_code == 200:
                output_file = f"/tmp/{job_id}.pdf"
                with open(output_file, "wb") as f:
                    f.write(response.content)
                current_app.logger.info(
                    f"Conversion successful. Saved to {output_file}"
                )
                upload_to_s3.delay(job_id, ppt_path, output_file)
            else:
                current_app.logger.error(
                    f"Failed to convert file. Status code: {response.status_code}"
                )
                r.set(f"job:{job_id}", json.dumps({"status": JobStatus.FAILED.value}))
    finally:
        lock.release()


@shared_task
def upload_to_s3(job_id, ppt_path, pdf_path):
    s3_service = current_app.s3_service
    r = current_app.redis
    ppt_key = job_id + ".pptx"
    with open(ppt_path, "rb") as f:
        if not s3_service.upload_file_to_s3(f, ppt_key):
            r.set(f"job:{job_id}", json.dumps({"status": JobStatus.FAILED.value}))

    pdf_key = job_id + ".pdf"
    with open(pdf_path, "rb") as f:
        if not s3_service.upload_file_to_s3(f, pdf_key):
            r.set(f"job:{job_id}", json.dumps({"status": JobStatus.FAILED.value}))

    presign_url = s3_service.generate_presigned_url(pdf_key)
    if presign_url is None:
        r.set(f"job:{job_id}", json.dumps({"status": JobStatus.FAILED.value}))
    else:
        r.set(
            f"job:{job_id}",
            json.dumps({"status": JobStatus.COMPLETED.value, "url": presign_url}),
        )

    delete_from_s3.apply_async((ppt_key,), countdown=1800)
    delete_from_s3.apply_async((pdf_key,), countdown=1800)

    if os.path.exists(ppt_path):
        os.remove(ppt_path)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)


@shared_task
def delete_from_s3(key):
    s3_service = current_app.s3_service
    s3_service.delete_file_from_s3(key)
