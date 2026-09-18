const form = document.getElementById("receiptForm");
const fileInput = document.getElementById("file");
const scanButton = document.getElementById("scanButton");
const statusElement = document.getElementById("status");

const resultSection = document.getElementById("resultSection");
const receiptResult = document.getElementById("receiptResult");

const historyElement = document.getElementById("history");
const statisticsElement = document.getElementById("statistics");
const refreshButton = document.getElementById("refreshButton");

const preview = document.getElementById("preview");
const previewContainer = document.getElementById("previewContainer");

const dropZone = document.getElementById("dropZone");
const removePreviewButton = document.getElementById(
    "removePreviewButton"
);

let previewUrl = null;

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function formatMoney(value) {
    if (value === null || value === undefined) {
        return "—";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return (
        number.toLocaleString(
            "ru-RU",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }
        )
        + " ₽"
    );
}


function formatQuantity(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return number.toLocaleString(
        "ru-RU",
        {
            maximumFractionDigits: 3
        }
    );
}


function categoryLabel(category) {
    const labels = {
        food: "Продукты питания",
        beverages: "Напитки",
        hygiene: "Гигиена",
        clothing: "Одежда",
        electronics: "Электроника",
        transport: "Транспорт",
        medicine: "Лекарства",
        restaurant: "Ресторан",
        other: "Другое"
    };

    return labels[category] || category || "Другое";
}


function categoryClass(category) {
    const allowed = new Set([
        "food",
        "beverages",
        "hygiene",
        "clothing",
        "electronics",
        "transport",
        "medicine",
        "restaurant",
        "other"
    ]);

    if (allowed.has(category)) {
        return `badge-${category}`;
    }

    return "badge-other";
}


function showStatus(message, type = "") {
    statusElement.textContent = message;
    statusElement.className = `status ${type}`;
}

function clearPreview() {
    if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
        previewUrl = null;
    }

    preview.removeAttribute("src");
    previewContainer.hidden = true;

    fileInput.value = "";

    showStatus("");
}


function showPreview(file) {
    if (!file) {
        clearPreview();
        return;
    }

    if (!file.type.startsWith("image/")) {
        clearPreview();

        showStatus(
            "Выберите файл изображения.",
            "error"
        );

        return;
    }

    if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
    }

    previewUrl = URL.createObjectURL(file);

    preview.src = previewUrl;
    previewContainer.hidden = false;

    showStatus("");
}

function renderReceipt(receipt) {
    const items = receipt.items || [];

    let html = `
        <div class="receipt-info">

            <div>
                <strong>Магазин</strong>

                <span>
                    ${escapeHtml(
                        receipt.store || "Не определён"
                    )}
                </span>
            </div>


            <div>
                <strong>Дата</strong>

                <span>
                    ${escapeHtml(
                        receipt.receipt_date || "Не определена"
                    )}
                </span>
            </div>


            <div>
                <strong>Сумма</strong>

                <span>
                    ${formatMoney(receipt.total)}
                </span>
            </div>

        </div>


        <h3>
            Распознанные товары
        </h3>
    `;


    if (!items.length) {
        html += `
            <p class="empty">
                Не удалось автоматически распознать товары.
            </p>
        `;
    } else {
        html += `
            <div class="table-wrapper">

                <table>

                    <thead>
                        <tr>
                            <th>Товар</th>
                            <th>Количество</th>
                            <th>Цена</th>
                            <th>Категория</th>
                        </tr>
                    </thead>

                    <tbody>
        `;


        for (const item of items) {
            const category =
                item.category || "other";

            html += `
                <tr>

                    <td>
                        ${escapeHtml(item.name)}
                    </td>

                    <td>
                        ${formatQuantity(item.quantity)}
                    </td>

                    <td>
                        ${formatMoney(item.price)}
                    </td>

                    <td>
                        <span
                            class="
                                badge
                                ${categoryClass(category)}
                            "
                        >
                            ${escapeHtml(
                                categoryLabel(category)
                            )}
                        </span>
                    </td>

                </tr>
            `;
        }


        html += `
                    </tbody>

                </table>

            </div>
        `;
    }


    html += `
        <details>

            <summary>
                Показать распознанный текст OCR
            </summary>

            <pre>${escapeHtml(
                receipt.raw_text || ""
            )}</pre>

        </details>
    `;


    receiptResult.innerHTML = html;
    resultSection.hidden = false;
}

async function scanReceipt(event) {
    event.preventDefault();


    if (!fileInput.files.length) {
        showStatus(
            "Сначала выберите изображение чека.",
            "error"
        );

        return;
    }


    const file = fileInput.files[0];


    if (!file.type.startsWith("image/")) {
        showStatus(
            "Выберите файл изображения.",
            "error"
        );

        return;
    }


    const formData = new FormData();

    formData.append(
        "file",
        file
    );


    scanButton.disabled = true;

    scanButton.innerHTML = `
        <span class="scan-button-icon">
            ◌
        </span>

        <span>
            Распознавание...
        </span>
    `;


    showStatus(
        "Чек обрабатывается. Распознаём данные...",
        "loading"
    );


    try {
        const response = await fetch(
            "/receipts/scan",
            {
                method: "POST",
                body: formData
            }
        );


        let data;


        try {
            data = await response.json();
        } catch {
            throw new Error(
                "Сервер вернул некорректный ответ."
            );
        }


        if (!response.ok) {
            let message =
                "Ошибка при обработке чека.";

            if (
                data
                && typeof data.detail === "string"
            ) {
                message = data.detail;
            }

            throw new Error(message);
        }


        showStatus(
            "Чек успешно обработан и сохранён.",
            "success"
        );


        renderReceipt(data);


        await Promise.all([
            loadHistory(),
            loadStatistics()
        ]);


        resultSection.scrollIntoView(
            {
                behavior: "smooth",
                block: "start"
            }
        );

    } catch (error) {
        showStatus(
            `Ошибка: ${
                error.message
                || "Не удалось обработать чек."
            }`,
            "error"
        );

    } finally {
        scanButton.disabled = false;

        scanButton.innerHTML = `
            <span class="scan-button-icon">
                ✦
            </span>

            <span>
                Сканировать чек
            </span>
        `;
    }
}

async function loadHistory() {
    try {
        const response = await fetch(
            "/receipts"
        );


        if (!response.ok) {
            throw new Error(
                "Не удалось загрузить историю чеков."
            );
        }


        const receipts =
            await response.json();


        if (!Array.isArray(receipts)) {
            throw new Error(
                "Сервер вернул некорректные данные."
            );
        }


        if (!receipts.length) {
            historyElement.innerHTML = `
                <p class="empty">
                    Сохранённых чеков пока нет.
                </p>
            `;

            return;
        }


        let html = "";


        for (const receipt of receipts) {
            html += `
                <div class="history-item">

                    <div>

                        <strong>
                            ${escapeHtml(
                                receipt.store
                                || "Магазин не определён"
                            )}
                        </strong>

                        <small>
                            ${escapeHtml(
                                receipt.receipt_date
                                || "Дата не определена"
                            )}
                        </small>

                        <strong>
                            ${formatMoney(
                                receipt.total
                            )}
                        </strong>

                    </div>


                    <div class="history-actions">

                        <button
                            type="button"
                            onclick="showReceipt(${receipt.id})"
                        >
                            Открыть
                        </button>

                        <button
                            type="button"
                            class="secondary"
                            onclick="deleteReceipt(${receipt.id})"
                        >
                            Удалить
                        </button>

                    </div>

                </div>
            `;
        }


        historyElement.innerHTML = html;

    } catch (error) {
        historyElement.innerHTML = `
            <p class="error">
                ${escapeHtml(error.message)}
            </p>
        `;
    }
}

async function showReceipt(id) {
    try {
        const response = await fetch(
            `/receipts/${id}`
        );


        let receipt;


        try {
            receipt =
                await response.json();
        } catch {
            throw new Error(
                "Сервер вернул некорректный ответ."
            );
        }


        if (!response.ok) {
            throw new Error(
                receipt.detail
                || "Чек не найден."
            );
        }


        renderReceipt(receipt);


        resultSection.scrollIntoView(
            {
                behavior: "smooth",
                block: "start"
            }
        );

    } catch (error) {
        alert(
            error.message
            || "Не удалось открыть чек."
        );
    }
}

async function deleteReceipt(id) {
    const confirmed = confirm(
        "Вы действительно хотите удалить этот чек?"
    );


    if (!confirmed) {
        return;
    }


    try {
        const response = await fetch(
            `/receipts/${id}`,
            {
                method: "DELETE"
            }
        );


        if (!response.ok) {
            let message =
                "Не удалось удалить чек.";


            try {
                const data =
                    await response.json();

                if (
                    data
                    && typeof data.detail === "string"
                ) {
                    message = data.detail;
                }

            } catch {
                
            }


            throw new Error(message);
        }


        if (
            resultSection.hidden === false
        ) {
            resultSection.hidden = true;
            receiptResult.innerHTML = "";
        }


        showStatus(
            "Чек успешно удалён.",
            "success"
        );


        await Promise.all([
            loadHistory(),
            loadStatistics()
        ]);

    } catch (error) {
        alert(
            error.message
            || "Не удалось удалить чек."
        );
    }
}

async function loadStatistics() {
    try {
        const response = await fetch(
            "/statistics"
        );


        if (!response.ok) {
            throw new Error(
                "Не удалось загрузить статистику."
            );
        }


        const data =
            await response.json();


        const categories =
            Array.isArray(data.categories)
                ? data.categories
                : [];


        let html = `
            <div class="stats">

                <div class="stat">

                    <span>
                        Общая сумма расходов
                    </span>

                    <strong>
                        ${formatMoney(
                            data.total_spent
                        )}
                    </strong>

                </div>


                <div class="stat">

                    <span>
                        Количество чеков
                    </span>

                    <strong>
                        ${escapeHtml(
                            data.receipts_count ?? 0
                        )}
                    </strong>

                </div>

            </div>


            <div class="categories">

                <h3>
                    Расходы по категориям
                </h3>
        `;


        if (!categories.length) {
            html += `
                <p class="empty">
                    Данных пока нет.
                </p>
            `;
        } else {
            for (const category of categories) {
                html += `
                    <div class="category-row">

                        <span>
                            ${escapeHtml(
                                categoryLabel(
                                    category.category
                                )
                            )}
                        </span>

                        <strong>
                            ${formatMoney(
                                category.total
                            )}
                        </strong>

                    </div>
                `;
            }
        }


        html += `
            </div>
        `;


        statisticsElement.innerHTML = html;

    } catch (error) {
        statisticsElement.innerHTML = `
            <p class="error">
                ${escapeHtml(error.message)}
            </p>
        `;
    }
}

fileInput.addEventListener(
    "change",
    () => {
        const file =
            fileInput.files[0];

        showPreview(file);
    }
);


if (removePreviewButton) {
    removePreviewButton.addEventListener(
        "click",
        (event) => {
            event.preventDefault();
            event.stopPropagation();

            clearPreview();
        }
    );
}

if (dropZone) {
    [
        "dragenter",
        "dragover"
    ].forEach((eventName) => {
        dropZone.addEventListener(
            eventName,
            (event) => {
                event.preventDefault();
                event.stopPropagation();

                dropZone.classList.add(
                    "drag-over"
                );
            }
        );
    });


    [
        "dragleave",
        "drop"
    ].forEach((eventName) => {
        dropZone.addEventListener(
            eventName,
            (event) => {
                event.preventDefault();
                event.stopPropagation();

                dropZone.classList.remove(
                    "drag-over"
                );
            }
        );
    });


    dropZone.addEventListener(
        "drop",
        (event) => {
            const files =
                event.dataTransfer.files;


            if (!files.length) {
                return;
            }


            const file = files[0];


            if (!file.type.startsWith("image/")) {
                showStatus(
                    "Можно загрузить только изображение чека.",
                    "error"
                );

                return;
            }


            const transfer =
                new DataTransfer();

            transfer.items.add(file);

            fileInput.files =
                transfer.files;


            showPreview(file);
        }
    );
}

form.addEventListener(
    "submit",
    scanReceipt
);


refreshButton.addEventListener(
    "click",
    async () => {
        refreshButton.disabled = true;

        const originalContent =
            refreshButton.innerHTML;


        refreshButton.innerHTML = `
            <span>↻</span>
            Обновление...
        `;


        try {
            await Promise.all([
                loadHistory(),
                loadStatistics()
            ]);

        } finally {
            refreshButton.disabled = false;

            refreshButton.innerHTML =
                originalContent;
        }
    }
);

loadHistory();
loadStatistics();