import json
from unittest.mock import patch, Mock
from io import BytesIO
from app.enums.job_status import JobStatus


# ---------------- UPLOAD ENDPOINT -------------------#


@patch("app.ppt_converter_routes.convert_to_pdf")
def test_upload_successful(mock_convert_to_pdf, client):
    client.application.redis.set = Mock()

    test_file = BytesIO(b"test ppt content")
    test_file.filename = "test.pptx"

    response = client.post("/convert/upload", data={"file": (test_file, "test.pptx")})
    assert response.status_code == 200
    assert "job_id" in response.json

    # Verify Redis
    job_id = response.json["job_id"]
    client.application.redis.set.assert_called_once()
    call_args = client.application.redis.set.call_args[0]
    assert call_args[0] == f"job:{job_id}"
    assert json.loads(call_args[1]) == {"status": JobStatus.PROCESSING.value}

    # Verify Celery task was called
    mock_convert_to_pdf.delay.assert_called_once()
    task_args = mock_convert_to_pdf.delay.call_args[0]
    assert task_args[0] == job_id
    assert task_args[1] == f"/tmp/{job_id}.pptx"


def test_upload_no_file(client):
    response = client.post("/convert/upload")
    assert response.status_code == 400
    assert b"No file in the request" in response.data


def test_upload_empty_filename(client):
    data = {"file": (BytesIO(b""), "")}
    response = client.post("/convert/upload", data=data)
    assert response.status_code == 400
    assert response.json == {"message": "No selected file"}


def test_upload_invalid_file_type(client):
    data = {"file": (BytesIO(b"test"), "test.txt")}
    response = client.post("/convert/upload", data=data)
    assert response.status_code == 400
    assert b"Invalid file type" in response.data


# ---------------- STATUS/<JOB_ID> ENDPOINT -------------------#


def test_status_completed_with_url(client):
    job_data = json.dumps(
        {
            "status": JobStatus.COMPLETED.value,
            "url": "https://example.com/download.pdf"
        }
    )
    client.application.redis.get.return_value = job_data

    response = client.get("/convert/status/completed-job")
    assert response.status_code == 200
    assert response.json == {
        "status": JobStatus.COMPLETED.value,
        "presignUrl": "https://example.com/download.pdf"
    }


def test_status_processing(client):
    job_data = json.dumps({"status": JobStatus.PROCESSING.value})
    client.application.redis.get.return_value = job_data
    response = client.get("/convert/status/processing-job")
    assert response.status_code == 200
    assert response.json == {"status": "processing"}


def test_status_invalid_job_id(client):
    client.application.redis.get.return_value = None
    response = client.get("/convert/status/non-existent-id")
    assert response.status_code == 404
    assert response.json == {"message": "Invalid Job Id"}


def test_status_failed(client):
    job_data = json.dumps({"status": JobStatus.FAILED.value})
    client.application.redis.get.return_value = job_data
    response = client.get("/convert/status/failed-job")
    assert response.status_code == 500
    assert response.json == {"message": "Job failed during processing"}


def test_status_completed_missing_url(client):
    job_data = json.dumps({"status": JobStatus.COMPLETED.value})
    client.application.redis.get.return_value = job_data
    response = client.get("/convert/status/completed-job-no-url")
    assert response.status_code == 500
    assert response.json == {"message": "Missing download URL"}
