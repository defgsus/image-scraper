document.addEventListener("DOMContentLoaded", () => {

    const
        csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value,
        search_url = document.querySelector(".search").getAttribute("data-url"),
        image_pk_url = document.querySelector(".search").getAttribute("data-image-pk-url");

    let search_state = [
        {"type": "text", "value": "a beautiful sunset", "amount": 5},
        {"type": "text", "value": "trees", "amount": 0},
    ];

    function on_level_click(e) {
        const
            row_idx = parseInt(e.target.parentElement.parentElement.getAttribute("data-idx")),
            level = parseInt(e.target.getAttribute("data-level"));

        if (search_state[row_idx].amount !== level) {
            search_state[row_idx].amount = level;
            render_search();
            get_images();
        }
    }

    function on_input_change(e) {
        const
            row_idx = parseInt(e.target.parentElement.parentElement.getAttribute("data-idx")),
            value = e.target.value;
        if (search_state[row_idx].value !== value) {
            search_state[row_idx].value = value;
            render_search();
            get_images();
        }
    }

    function on_delete_click(e) {
        const row_idx = parseInt(e.target.parentElement.getAttribute("data-idx"));
        search_state.splice(row_idx, 1);
        render_search();
        get_images();
    }

    function on_add_click(e) {
        search_state.push({
            "type": "text", "value": "", "amount": 5,
        });
        render_search();
        const row_idx = search_state.length - 1;
        document.querySelector(`.search .row[data-idx="${row_idx}"] .input input`).focus();
    }

    function on_similar_click(e) {
        const
            image_pk = e.target.parentElement.parentElement.getAttribute("data-pk");
        search_state.push({
            "type": "image", "value": image_pk, "amount": 5,
        });
        render_search();
        get_images();
    }

    function render_search() {
        let html = ``;

        for (let row_idx=0; row_idx<search_state.length; ++row_idx) {
            const row = search_state[row_idx];

            html += `<div class="row" data-idx="${row_idx}">`;
            html += `<div class="icon delete">X</div>`;

            html += `<div class="levels">`;
            for (let i = -5; i <= 5; ++i) {
                const
                    selected = i === row.amount ? "selected" : "",
                    highlight = i % 5 === 0 ? "highlight" : "";
                html += `<div class="level ${selected} ${highlight}" data-level="${i}">${i}</div>`;
            }
            html += `</div>`;

            html += `<div class="input">`;
            if (row.type === "text") {
                html += `<input type="text" value="${row.value}">`;
            } else if (row.type === "image") {
                const url = image_pk_url.replace("0", `${row.value}`);
                html += `<img src="${url}">`;
            }
            html += `</div>`;

            html += `</div>`;
        }

        html += `<div class="row">`;
        html += `<div class="icon add">+</div>`;
        html += `</div>`;

        document.querySelector(".search").innerHTML = html;

        for (const elem of document.querySelectorAll(".search .levels .level")) {
            elem.onclick = on_level_click;
        }
        for (const elem of document.querySelectorAll(".search .input input")) {
            elem.onchange = on_input_change;
        }
        for (const elem of document.querySelectorAll(".search .icon.add")) {
            elem.onclick = on_add_click;
        }
        for (const elem of document.querySelectorAll(".search .icon.delete")) {
            elem.onclick = on_delete_click;
        }
    }

    function render_images(images) {
        let html = ``;
        for (const image of images) {
            html += `<div class="image" data-pk="${image.pk}">`;
            html += `<img src="${image.url}" title="${image.caption}">`;

            html += `<div><b>${Math.round(image.score * 100) / 100}</b> `;
            html += `<div class="similar-click">similar</div>`;
            html += `</div>`;

            html += `</div>`;
        }
        document.querySelector(".images").innerHTML = html;
        for (const elem of document.querySelectorAll(".images .image .similar-click")) {
            elem.onclick = on_similar_click;
        }
    }

    function get_images() {
        //console.log(search_state);
        window
            .fetch(
                search_url,
                {
                    method: "post",
                    headers: {'X-CSRFToken': csrftoken},
                    body: JSON.stringify({
                        search_rows: search_state,
                    }),
                }
            )
            .then(response => response.json())
            .then(data => {
                render_images(data.images);
            });
    }

    render_search();


});