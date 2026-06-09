import os
import tempfile

import cv2
from django.conf import settings
from PIL import Image

from apps.ai_engine.image_analyzer import extract_text_from_image
from apps.ai_engine.multimodal_rules import (
    build_analysis_summary,
    clean_ocr_text,
    detect_issue_type,
)


def extract_key_frames(video_path: str, max_frames: int = 5) -> list[str]:
    frame_paths = []

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        return frame_paths

    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        capture.release()
        return frame_paths

    max_frames = min(max_frames, total_frames)

    if max_frames <= 1:
        frame_indices = [0]
    else:
        step = max(total_frames // max_frames, 1)
        frame_indices = [i * step for i in range(max_frames)]

    temp_dir = tempfile.mkdtemp(prefix="smartdesk_video_frames_")

    for index, frame_number in enumerate(frame_indices):
        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        success, frame = capture.read()

        if not success:
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)

        frame_path = os.path.join(temp_dir, f"frame_{index + 1}.jpg")
        image.save(frame_path, "JPEG", quality=90)

        frame_paths.append(frame_path)

    capture.release()

    return frame_paths


def analyze_video_attachment(video_path: str) -> dict:
    if not settings.VIDEO_ANALYSIS_ENABLED:
        return {
            "success": False,
            "issue_type": "Video Analysis Disabled",
            "extracted_text": "",
            "summary": "Video analysis is disabled in settings.",
            "frames_analyzed": 0,
        }

    frame_paths = extract_key_frames(
        video_path=video_path,
        max_frames=settings.VIDEO_MAX_FRAMES,
    )

    extracted_text_parts = []

    for frame_path in frame_paths:
        text = extract_text_from_image(frame_path)

        if text:
            extracted_text_parts.append(text)

    combined_text = clean_ocr_text(" ".join(extracted_text_parts))

    issue_type = detect_issue_type(
        combined_text,
        file_type="VIDEO",
    )

    summary = build_analysis_summary(
        file_type="VIDEO",
        issue_type=issue_type,
        extracted_text=combined_text,
        frame_count=len(frame_paths),
    )

    if not frame_paths:
        summary += (
            "\nNote: Video frames could not be extracted. "
            "The file may be unsupported or corrupted."
        )

    elif not combined_text:
        summary += (
            "\nNote: OCR could not detect readable text from the selected video frames. "
            "Agent should manually review the video."
        )

    return {
        "success": True,
        "issue_type": issue_type,
        "extracted_text": combined_text,
        "summary": summary,
        "frames_analyzed": len(frame_paths),
    }