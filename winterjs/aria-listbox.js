import { $e, $on } from "./utils.js";

function random_id(length = 6) {
    return Math.random().toString(36).substr(2, length);
}

export class AriaListBox {
    constructor(list_elem) {
        this.list_elem = $e(list_elem);
        this.options = this.list_elem.querySelectorAll('[role="option"]');
        this.create_virtual_input();
        this.assign_ids();
        this.select_default();
        this.setup_events();
    }

    create_virtual_input() {
        const name = this.list_elem.dataset.name;
        if (!name) return;
        this.virtual_input = document.createElement("input");
        this.virtual_input.name = name;
        this.virtual_input.type = "hidden";
        this.list_elem.insertAdjacentElement("afterend", this.virtual_input);
    }

    set virtual_input_value(val) {
        if (!this.virtual_input) {
            return;
        }
        this.virtual_input.value = val;
    }

    assign_ids() {
        for (const elem of this.options) {
            if (!elem.id) {
                elem.id = random_id();
            }
        }
    }

    select_default() {
        if (this.active_item) return;
        const item = this.options[0];
        item.setAttribute("aria-selected", true);
        this.list_elem.setAttribute("aria-activedescendant", item.id);
        this.virtual_input_value = item.dataset.value;
    }

    get active_item() {
        return $e(this.list_elem.getAttribute("aria-activedescendant"));
    }

    set active_item(e) {
        if (!e) {
            return;
        }
        this.active_item.removeAttribute("aria-selected");
        e.setAttribute("aria-selected", true);
        this.list_elem.setAttribute("aria-activedescendant", $e(e).id);
        this.scroll_to_item(e);
        this.virtual_input_value = e.dataset.value;
    }

    scroll_to_item(e) {
        const e_top = e.offsetTop;
        const e_height = e.offsetHeight;
        const e_bottom = e_top + e_height;
        const view_height = this.list_elem.clientHeight;
        const scroll_top = this.list_elem.scrollTop;
        const scroll_bottom = scroll_top + view_height;
        if (e_bottom > scroll_bottom) {
            this.list_elem.scrollTo({ top: e_top - view_height + e_height });
            return;
        }
        if (e_top < scroll_top) {
            this.list_elem.scrollTo({ top: e_top });
            return;
        }
    }

    select_previous_item() {
        const prev = this.active_item.previousElementSibling;
        this.active_item = prev;
        return prev ? true : false;
    }

    select_next_item() {
        const next = this.active_item.nextElementSibling;
        this.active_item = next;
        return next ? true : false;
    }

    select_first_item() {
        const first = this.options[0];
        if (this.active_item == first) {
            return false;
        }
        this.active_item = first;
        return true;
    }

    select_last_item() {
        const last = this.options[this.options.length - 1];
        if (this.active_item == last) {
            return false;
        }
        this.active_item = last;
        return true;
    }

    setup_events() {
        $on(this.list_elem, "click", (e) => {
            this.on_click(e);
        });
        $on(this.list_elem, "keydown", (e) => {
            this.on_key_down(e);
        });
    }

    on_click(event) {
        const option = event.target.closest('[role="option"]');
        this.active_item = option;
    }

    on_key_down(event) {
        const key = event.key;

        switch (key) {
            case "ArrowUp":
                if (this.select_previous_item()) {
                    event.preventDefault();
                }
                break;
            case "ArrowDown":
                if (this.select_next_item()) {
                    event.preventDefault();
                }
                break;
            case "Home":
                if (this.select_first_item()) {
                    event.preventDefault();
                }
                break;
            case "End":
                if (this.select_last_item()) {
                    event.preventDefault();
                }
                break;

            default:
                break;
        }
    }
}

for (const el of document.querySelectorAll('[role="listbox"]')) {
    new AriaListBox(el);
}
