from unittest.mock import Mock, patch, mock_open, ANY
import json
import pytest
from app.tasks import convert_to_pdf, upload_to_s3, delete_from_s3
from app.enums.job_status import JobStatus


@pytest.fixture
def mock_redis(client):
    with client.application.app_context():
        with patch("app.tasks.current_app.redis") as mock:
            mock.lock.return_value.__enter__.return_value = True
            mock.lock.return_value.__exit__.return_value = None
            yield mock


@pytest.fixture
def mock_s3_service(client):
    with client.application.app_context():
        with patch("app.tasks.current_app.s3_service") as mock:
            mock.upload_file_to_s3.return_value = True
            mock.generate_presigned_url.return_value = (
                "https://example.com/download.pdf"
            )
            mock.delete_file_from_s3.return_value = True
            yield mock


@pytest.fixture
def mock_requests():
    with patch("app.tasks.requests") as mock:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"pdf content"
        mock.post.return_value = mock_response
        yield mock


@pytest.fixture
def mock_upload_to_s3():
    with patch("app.tasks.upload_to_s3") as mock:
        yield mock


@pytest.fixture
def mock_convert_to_pdf():
    with patch("app.tasks.convert_to_pdf") as mock:
        yield mock


@pytest.fixture()
def mock_delete_from_s3():
    with patch("app.tasks.delete_from_s3") as mock:
        yield mock


# ---------------- CONVERT_TO_PDF TASK -------------------#
def test_convert_to_pdf_success(mock_redis, mock_requests, mock_upload_to_s3):
    job_id = "test-job"
    ppt_path = f"/tmp/{job_id}.pptx"
    pdf_path = f"/tmp/{job_id}.pdf"

    with patch("app.tasks.open", mock_open(read_data=b"ppt content")):
        convert_to_pdf(job_id, ppt_path)

    mock_redis.lock.assert_called_once_with(
        "unoserver_lock", timeout=120, blocking_timeout=10
    )

    # Verify unoserver request
    mock_requests.post.assert_called_once()
    call_args = mock_requests.post.call_args
    assert call_args[1]["data"] == {"convert-to": "pdf"}

    mock_upload_to_s3.delay.assert_called_once_with(job_id, ppt_path, pdf_path)


def test_convert_to_pdf_request_failure(mock_redis, mock_requests):
    job_id = "test-job"
    ppt_path = f"/tmp/{job_id}.pptx"

    mock_requests.post.return_value.status_code = 500

    with patch("app.tasks.open", mock_open(read_data=b"ppt content")):
        convert_to_pdf(job_id, ppt_path)

    mock_redis.lock.assert_called_once_with(
        "unoserver_lock", timeout=120, blocking_timeout=10
    )

    mock_redis.set.assert_called_once_with(
        f"job:{job_id}", json.dumps({"status": JobStatus.FAILED.value})
    )


def test_convert_to_pdf_lock_failure(mock_redis, mock_convert_to_pdf):
    job_id = "test-job"
    ppt_path = f"/tmp/{job_id}.pptx"

    mock_redis.lock.return_value.acquire.return_value = False

    with patch("app.tasks.open", mock_open(read_data=b"ppt content")):
        convert_to_pdf(job_id, ppt_path)

    mock_redis.lock.assert_called_once_with(
        "unoserver_lock", timeout=120, blocking_timeout=10
    )

    mock_convert_to_pdf.apply_async.assert_called_once_with(
        (job_id, ppt_path), countdown=10
    )


# ---------------- UPLOAD_TO_S3 TASK -------------------#
def test_upload_to_s3_success(mock_redis, mock_s3_service, mock_delete_from_s3):
    job_id = "test-job"
    ppt_path = f"/tmp/{job_id}.pptx"
    pdf_path = f"/tmp/{job_id}.pdf"

    with patch("app.tasks.open", mock_open(read_data=b"file content")):
        upload_to_s3(job_id, ppt_path, pdf_path)

    mock_s3_service.upload_file_to_s3.assert_any_call(ANY, f"{job_id}-PPT")
    mock_s3_service.upload_file_to_s3.assert_any_call(ANY, f"{job_id}-PDF")
    mock_s3_service.generate_presigned_url.assert_called_once_with(f"{job_id}-PDF")

    mock_redis.set.assert_called_once_with(
        f"job:{job_id}",
        json.dumps(
            {
                "status": JobStatus.COMPLETED.value,
                "url": "https://example.com/download.pdf",
            }
        ),
    )

    mock_delete_from_s3.apply_async.assert_any_call((f"{job_id}-PPT",), countdown=1800)
    mock_delete_from_s3.apply_async.assert_any_call((f"{job_id}-PDF",), countdown=1800)


def test_upload_to_s3_ppt_upload_failure(
    mock_redis, mock_s3_service, mock_delete_from_s3
):
    job_id = "test-job"
    ppt_path = f"/tmp/{job_id}.pptx"
    pdf_path = f"/tmp/{job_id}.pdf"

    mock_s3_service.upload_file_to_s3.side_effect = [False, True]

    with patch("app.tasks.open", mock_open(read_data=b"file content")):
        upload_to_s3(job_id, ppt_path, pdf_path)

    mock_redis.set.assert_any_call(
        f"job:{job_id}", json.dumps({"status": JobStatus.FAILED.value})
    )


def test_upload_to_s3_pdf_upload_failure(
    mock_redis, mock_s3_service, mock_delete_from_s3
):
    job_id = "test-job"
    ppt_path = f"/tmp/{job_id}.pptx"
    pdf_path = f"/tmp/{job_id}.pdf"

    mock_s3_service.upload_file_to_s3.side_effect = [True, False]

    with patch("app.tasks.open", mock_open(read_data=b"file content")):
        upload_to_s3(job_id, ppt_path, pdf_path)

    mock_redis.set.assert_any_call(
        f"job:{job_id}", json.dumps({"status": JobStatus.FAILED.value})
    )


def test_upload_to_s3_presigned_url_failure(
    mock_redis, mock_s3_service, mock_delete_from_s3
):
    job_id = "test-job"
    ppt_path = f"/tmp/{job_id}.pptx"
    pdf_path = f"/tmp/{job_id}.pdf"

    mock_s3_service.generate_presigned_url.return_value = None

    with patch("app.tasks.open", mock_open(read_data=b"file content")):
        upload_to_s3(job_id, ppt_path, pdf_path)

    mock_redis.set.assert_called_once_with(
        f"job:{job_id}", json.dumps({"status": JobStatus.FAILED.value})
    )


def test_upload_to_s3_cleanup(mock_redis, mock_s3_service, mock_delete_from_s3):
    job_id = "test-job"
    ppt_path = f"/tmp/{job_id}.pptx"
    pdf_path = f"/tmp/{job_id}.pdf"

    with patch("app.tasks.os.path.exists") as mock_exists, patch(
        "app.tasks.os.remove"
    ) as mock_remove:
        mock_exists.side_effect = [True, True]

        with patch("app.tasks.open", mock_open(read_data=b"file content")):
            upload_to_s3(job_id, ppt_path, pdf_path)

        assert mock_remove.call_count == 2
        mock_remove.assert_any_call(ppt_path)
        mock_remove.assert_any_call(pdf_path)


# ---------------- DELETE_TO_S3 TASK -------------------#
def test_delete_from_s3(mock_s3_service):
    key = "test-key"

    delete_from_s3(key)

    mock_s3_service.delete_file_from_s3.assert_called_once_with(key)
