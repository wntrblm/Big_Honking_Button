/*
    Simple helper for Bulma-style modals.
*/

import { $e, $on, DOMHelpers } from "./utils.js";

export class Modal {
    constructor(elem) {
        elem = $e(elem);
        if (!elem) {
            elem = this._make_modal();
        }

        this.elem = elem;
        this.content_elem = this.elem.querySelector(".modal-content");
        this.close_elem = this.elem.querySelector(".modal-close");

        if (this.close_elem) {
            $on(this.close_elem, "click", () => {
                this.hide();
            });
        }
    }

    _make_modal() {
        let elem = document.createElement("div");
        elem.classList.add("modal");

        let bg = document.createElement("div");
        bg.classList.add("modal-background");
        elem.appendChild(bg);

        let content = document.createElement("div");
        content.classList.add("modal-content");
        elem.appendChild(content);

        let close = document.createElement("div");
        close.classList.add("modal-close");
        elem.appendChild(close);

        document.querySelector("body").appendChild(elem);

        return elem;
    }

    show(content) {
        this.elem.classList.add("is-active");
        document.documentElement.classList.add("is-clipped");

        if (content !== undefined) {
            if (content instanceof HTMLElement) {
                DOMHelpers.remove_all_children(this.content_elem);
                this.content_elem.appendChild(content);
            } else {
                this.content_elem.innerHTML = content;
            }
        }
    }

    hide() {
        this.elem.classList.remove("is-active");
        document.documentElement.classList.remove("is-clipped");
    }
}

export class ImageModal extends Modal {
    show(image) {
        let new_content = image.cloneNode(true);
        super.show(new_content);
    }
}
