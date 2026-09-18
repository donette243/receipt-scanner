from pathlib import Path

import cv2
import numpy as np
import pytest

from app.services.image_processor import preprocess_image


def test_preprocess_image(tmp_path):
    input_path = tmp_path / "receipt.jpg"

    image = np.full(
        (100, 100, 3),
        255,
        dtype=np.uint8,
    )

    cv2.imwrite(
        str(input_path),
        image,
    )

    result = preprocess_image(
        str(input_path)
    )

    assert Path(result).exists()
    assert result.endswith("_processed.png")


def test_preprocess_image_invalid_file(tmp_path):
    input_path = tmp_path / "invalid.jpg"

    input_path.write_text(
        "not an image"
    )

    with pytest.raises(
        ValueError,
        match="Не удалось прочитать изображение",
    ):
        preprocess_image(
            str(input_path)
        )


def test_preprocess_image_save_error(
    tmp_path,
    monkeypatch,
):
    input_path = tmp_path / "receipt.jpg"

    image = np.full(
        (100, 100, 3),
        255,
        dtype=np.uint8,
    )

    cv2.imwrite(
        str(input_path),
        image,
    )

    monkeypatch.setattr(
        cv2,
        "imwrite",
        lambda *args, **kwargs: False,
    )

    with pytest.raises(
        ValueError,
        match="Не удалось сохранить",
    ):
        preprocess_image(
            str(input_path)
        )