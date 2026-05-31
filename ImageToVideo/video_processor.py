import cv2
import numpy as np
from pathlib import Path
from typing import List


def _load_and_resize(image_path: Path, target_size: tuple[int, int]):
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Cannot load image: {image_path}")
    return cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)


def _get_target_size(image_paths: List[Path]) -> tuple[int, int]:
    sizes = []
    for p in image_paths:
        img = cv2.imread(str(p))
        if img is not None:
            sizes.append((img.shape[1], img.shape[0]))
    if not sizes:
        raise ValueError("No valid images found")
    w = max(s[0] for s in sizes)
    h = max(s[1] for s in sizes)
    if w % 2 != 0:
        w += 1
    if h % 2 != 0:
        h += 1
    return w, h


def _create_transition_frame(img1, img2, alpha):
    return cv2.addWeighted(img1, 1 - alpha, img2, alpha, 0)


def create_video_from_images(
    image_paths: List[Path],
    output_path: Path,
    fps: int = 1,
    duration_per_image: float = 2.0,
    transition: str = "none",
):
    target_size = _get_target_size(image_paths)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, target_size)

    frames_per_image = max(1, int(fps * duration_per_image))
    transition_frames = int(fps * 0.5) if transition != "none" else 0

    for i, img_path in enumerate(image_paths):
        img = _load_and_resize(img_path, target_size)

        for _ in range(frames_per_image):
            out.write(img)

        if transition != "none" and i < len(image_paths) - 1:
            next_img = _load_and_resize(image_paths[i + 1], target_size)
            for t in range(1, transition_frames + 1):
                alpha = t / transition_frames
                frame = _create_transition_frame(img, next_img, alpha)
                out.write(frame)

    out.release()
    cv2.destroyAllWindows()
