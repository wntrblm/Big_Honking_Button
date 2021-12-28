/*
    Copyright (c) 2021 Alethea Katherine Flowers.
    Published under the standard MIT License.
    Full text available at: https://opensource.org/licenses/MIT
*/

import { $s, $on, $make } from "./utils.js";
import { Renderer } from "./pcbrender.js";

async function fetch_pcb_data(path) {
    const request = new Request(path, {
        method: "GET",
    });

    const response = await fetch(request);

    return await response.json();
}

function extract_bom(pcb_data) {
    const items = [];
    const front_items = [];

    for (const group of pcb_data.bom.F) {
        for (const [ref, _] of group) {
            front_items.push(ref);
        }
    }

    for (const group of pcb_data.bom.both) {
        for (const [ref, index] of group) {
            const fields = pcb_data.bom.fields[index];
            items.push({
                ref: ref,
                value: fields[0],
                footprint: fields[1],
                show: fields[2] ? true : false,
                side: front_items.includes(ref) ? "Front" : "Back",
            });
        }
    }

    return items;
}

function filter_bom(bom) {
    return bom.filter((item) => item.show);
}

function filter_bom_pin_one_highlights(bom) {
    return bom.filter(
        (item) =>
            item.ref.startsWith("D") ||
            item.ref.startsWith("U") ||
            item.ref.startsWith("CP")
    );
}

function group_bom(bom) {
    const front_by_value = {};
    const back_by_value = {};
    for (const item of bom) {
        let dest = item.side === "Front" ? front_by_value : back_by_value;
        if (dest[item.value] === undefined) {
            dest[item.value] = [];
        }
        dest[item.value].push(item);
    }
    return {
        front: front_by_value,
        back: back_by_value,
    };
}

function grouped_bom_to_rows(bom) {
    const rows = [];
    for (const [value, items] of Object.entries(bom)) {
        rows.push({
            refs: items.map((x) => x.ref).join(", "),
            value: value,
        });
    }
    return rows;
}

class BOMTable {
    constructor(items, renderer) {
        this.items = items;
        this.renderer = renderer;
    }

    row_for_item(idx, bom_item) {
        const checkbox = $make("input", {
            type: "checkbox",
            class: "checkbox",
            "aria-label": `Mark row ${idx+1} complete`,
        });
        const cells = [bom_item.refs, bom_item.value];
        const cell_elems = [
            $make("td", {
                children: [checkbox],
            }),
        ];
        for (const cell of cells) {
            cell_elems.push($make("td", { innerText: cell }));
        }
        const tr = $make("tr", { children: cell_elems });
        tr.dataset.bomIdx = idx;

        $on(checkbox, "click", () => {
            if (checkbox.checked) {
                tr.classList.add("complete");
            } else {
                tr.classList.remove("complete");
            }
        });

        return tr;
    }

    make() {
        const header_elems = [];

        for (const [header, label] of [["", "Completed"], ["Reference", "Component references"], ["Value", "Component values"]]) {
            header_elems.push($make(header ? "th" : "td", { innerText: header , "aria-label": label}));
        }

        const row_elems = this.items.map((item, idx) =>
            this.row_for_item(idx, item)
        );

        const table = $make("table", {
            children: [
                $make("thead", { children: header_elems }),
                $make("tbody", { children: row_elems }),
            ],
            class: "bom-table",
            "aria-label": "Table of components",
        });

        $on(table, "click", (ev) => {
            const row = ev.target.closest("tr[data-bom-idx]");
            if (!row) {
                return;
            }
            this.highlight_row_items(row);
        });

        row_elems[0].click();

        return table;
    }

    highlight_row_items(row) {
        const item = this.items[row.dataset.bomIdx];
        this.renderer.highlight(item.refs.split(",").map((x) => x.trim()));

        for (const tr of $s(row.parentNode, "tr")) {
            tr.classList.remove("active");
        }
        row.classList.add("active");
    }
}

async function init(elem) {
    const pcb_data = await fetch_pcb_data(elem.dataset.pcbAssembly);
    const bom = filter_bom(extract_bom(pcb_data));
    const grouped_bom = group_bom(bom);
    const front_bom_rows = grouped_bom_to_rows(grouped_bom.front);
    const back_bom_rows = grouped_bom_to_rows(grouped_bom.back);

    const r = new Renderer(elem, pcb_data);
    r.highlight_pin_one(filter_bom_pin_one_highlights(bom).map((v) => v.ref));

    const front_table = new BOMTable(front_bom_rows, r);
    r.front.canvas.after(front_table.make());
    const back_table = new BOMTable(back_bom_rows, r);
    r.back.canvas.after(back_table.make());
}

for (const elem of $s("[data-pcb-assembly]")) {
    init(elem);
}
