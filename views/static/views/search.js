document.addEventListener("DOMContentLoaded", () => {

    const
        csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value,
        search_url = document.querySelector(".search").getAttribute("data-url"),
        image_pk_url = document.querySelector(".search").getAttribute("data-image-pk-url"),
        image_rate_url = document.querySelector(".search").getAttribute("data-image-rate-url");

    let search_state = [
        {"type": "text", "value": "a beautiful sunset", "amount": 5},
        {"type": "text", "value": "trees", "amount": 0},
        {"type": "text", "value": "a vast landscape", "amount": 0},
    ];
    let
        image_count = 20,
        extra_image_count = 0;

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

    function on_count_change(e) {
        image_count = parseInt(document.querySelector('input[name="count"]').value) || 20;
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
            image_pk = e.target.parentElement.getAttribute("data-pk");
        search_state.push({
            "type": "image", "value": image_pk, "amount": 5,
        });
        render_search();
        get_images();
    }

    function on_rating_click(e) {
        const
            pk = e.target.getAttribute("data-pk"),
            rate = e.target.getAttribute("data-rate"),
            user = document.querySelector('input[name="rating-user"]').value,
            remove_rating = e.target.classList.contains("active");

        window
            .fetch(
                image_rate_url,
                {
                    method: "post",
                    headers: {'X-CSRFToken': csrftoken},
                    body: JSON.stringify({pk, rate, user, remove: remove_rating}),
                }
            )
            .then(response => {
                if (response.status === 201) {
                    render_rating_buttons(pk, remove_rating ? 0 : rate);
                }
            });
    }

    function on_more_images_click(e) {
        e.stopPropagation();
        extra_image_count += image_count;
        get_images(true);
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
        html += `<div class="icon add">+</div> <input name="count" type="number" min="1" value="${image_count}">`;
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
        document.querySelector('.search input[name="count"]').onchange = on_count_change;
    }

    const rate_content_mapping = {
        "-1": "👎",
        "1": "👍",
    };

    function rating_buttons_html(image_pk, active_rating) {
        let html = "";
        const image_rating = `${active_rating}`;
        for (const rate of Object.keys(rate_content_mapping)) {
            const className = `rating-button${image_rating === rate ? " active" : ""} rate-${rate}`;
            let title = image_rating === rate ? `remove rating ${rate}` : `set rating to ${rate}`;
            html += `<button class="${className}" data-rate="${rate}" data-pk="${image_pk}"
                            title="${title}"
                            >${rate_content_mapping[rate]}</button>`;
        }
        return html
    }

    function render_images(images) {
        let html = ``;
        for (const image of images) {
            html += `<div class="image" data-pk="${image.pk}">`;
            html += `<img loading="lazy" src="${image.url}" title="${image.caption}">`;

            html += `<div>`;
            html += `<div class="rating-buttons">${rating_buttons_html(image.pk, image.rating)}</div>`;

            html += `<b>${Math.round(image.score * 100) / 100}</b> `;
            html += `<a class="source" href="${image.original_url}" target="_blank">source</a>`;

            html += `</div>`;

            html += `</div>`;
        }
        html += `<button class="more-images">+</button>`;
        document.querySelector(".images").innerHTML = html;
        for (const elem of document.querySelectorAll(".images .image img")) {
            elem.onclick = on_similar_click;
        }
        for (const elem of document.querySelectorAll(".images .rating-button")) {
            elem.onclick = on_rating_click;
        }
        document.querySelector("button.more-images").onclick = on_more_images_click;
    }

    function render_rating_buttons(image_pk, active_rating) {
        const elem = document.querySelector(`.image[data-pk="${image_pk}"]`).querySelector(".rating-buttons");
        elem.innerHTML = rating_buttons_html(image_pk, active_rating);
        for (const e of elem.querySelectorAll(".rating-button")) {
            e.onclick = on_rating_click;
        }
    }

    function get_images(keep_extra_image_count=false) {
        //console.log(search_state);
        if (!keep_extra_image_count)
            extra_image_count = 0;

        const
            scraper = document.querySelector('select[name="scraper"]').value,
            user = document.querySelector('input[name="rating-user"]').value;

        window
            .fetch(
                search_url,
                {
                    method: "post",
                    headers: {'X-CSRFToken': csrftoken},
                    body: JSON.stringify({
                        search_rows: search_state,
                        count: image_count + extra_image_count,
                        scraper: scraper,
                        user: user,
                    }),
                }
            )
            .then(response => response.json())
            .then(data => {
                render_images(data.images);
            });
    }

    render_search();

    document.querySelector('input[name="rating-user"]').onchange = e => {
        get_images();
    };
});