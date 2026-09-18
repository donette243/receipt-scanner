from pathlib import Path

import cv2


def preprocess_image(input_path: str) -> str:
    image = cv2.imread(input_path)

    if image is None:
        raise ValueError(
            "Не удалось прочитать изображение."
        )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    height, width = gray.shape[:2]

    if width < 2000:
        scale = min(
            2.0,
            2000 / max(width, 1),
        )

        gray = cv2.resize(
            gray,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )

    denoised = cv2.medianBlur(
        gray,
        3,
    )

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    enhanced = clahe.apply(
        denoised
    )

    processed = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    output_path = Path(input_path).with_name(
        f"{Path(input_path).stem}_processed.png"
    )

    success = cv2.imwrite(
        str(output_path),
        processed,
    )

    if not success:
        raise ValueError(
            "Не удалось сохранить обработанное изображение."
        )

    return str(output_path)