/*
    Copyright (c) 2021 Alethea Katherine Flowers.
    Published under the standard MIT License.
    Full text available at: https://opensource.org/licenses/MIT
*/

function deg2rad(deg) {
    return (deg * Math.PI) / 180;
}

class Font {
    constructor(font_data) {
        this.font_data = font_data;
        this.last_had_overbar = false;
    }

    calculate_font_point(linepoint, text, offsetx, offsety, tilt) {
        var point = [
            linepoint[0] * text.width + offsetx,
            linepoint[1] * text.height + offsety,
        ];
        // This approximates pcbnew behavior with how text tilts depending on horizontal justification
        point[0] -=
            (linepoint[1] + 0.5 * (1 + text.justify[0])) * text.height * tilt;
        return point;
    }

    draw_glyph(ctx, glyph, position_func) {
        for (var line of glyph.l) {
            ctx.beginPath();
            ctx.moveTo(...position_func(line[0]));
            for (var k = 1; k < line.length; k++) {
                ctx.lineTo(...position_func(line[k]));
            }
            ctx.stroke();
        }
    }

    draw_overbar(ctx, glyph, x, y, width, height, tilt) {
        var start = [x, -height * 1.4 + y];
        var end = [x + width * glyph.w, start[1]];

        if (!this.last_had_overbar) {
            start[0] += height * 1.4 * tilt;
            this.last_had_overbar = true;
        }

        ctx.beginPath();
        ctx.moveTo(...start);
        ctx.lineTo(...end);
        ctx.stroke();
    }

    draw(ctx, text, color) {
        ctx.save();
        ctx.fillStyle = color;
        ctx.strokeStyle = color;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.lineWidth = text.thickness;
        ctx.translate(...text.pos);
        ctx.translate(text.thickness * 0.5, 0);
        var angle = -text.angle;
        if (text.attr.includes("mirrored")) {
            ctx.scale(-1, 1);
            angle = -angle;
        }
        var tilt = 0;
        if (text.attr.includes("italic")) {
            tilt = 0.125;
        }
        var interline = text.height * 1.5 + text.thickness;
        var txt = text.text.split("\n");
        // KiCad ignores last empty line.
        if (txt[txt.length - 1] == "") txt.pop();
        ctx.rotate(deg2rad(angle));

        var offsety = ((1 - text.justify[1]) / 2) * text.height; // One line offset
        offsety -= (((txt.length - 1) * (text.justify[1] + 1)) / 2) * interline; // Multiline offset

        for (const i in txt) {
            let lineWidth = text.thickness + (interline / 2) * tilt;

            /* Calculate the overall width of the line first, needed for alignment. */
            for (let j = 0; j < txt[i].length; j++) {
                const txt_ij = txt[i][j];
                if (txt_ij == "\t") {
                    var fourSpaces = 4 * this.font_data[" "].w * text.width;
                    lineWidth += fourSpaces - (lineWidth % fourSpaces);
                    continue;
                } else if (txt_ij == "~") {
                    j++;
                    if (j == txt[i].length) {
                        break;
                    }
                }
                lineWidth += this.font_data[txt_ij].w * text.width;
            }

            var offsetx = (-lineWidth * (text.justify[0] + 1)) / 2;
            var in_overbar = false;
            for (var j = 0; j < txt[i].length; j++) {
                const txt_ij = txt[i][j];
                const glyph = this.font_data[txt_ij];

                if (txt_ij == "\t") {
                    var fourSpaces = 4 * this.font_data[" "].w * text.width;
                    offsetx += fourSpaces - (offsetx % fourSpaces);
                    continue;
                }

                if (txt_ij == "~") {
                    j++;
                    if (j == txt[i].length) break;
                    if (txt_ij != "~") {
                        in_overbar = !in_overbar;
                    }
                }

                if (in_overbar) {
                    this.draw_overbar(
                        ctx,
                        glyph,
                        offsetx,
                        offsety,
                        text.width,
                        text.height,
                        tilt
                    );
                } else {
                    this.last_had_overbar = false;
                }

                this.draw_glyph(ctx, glyph, (line) => {
                    return this.calculate_font_point(
                        line,
                        text,
                        offsetx,
                        offsety,
                        tilt
                    );
                });

                offsetx += glyph.w * text.width;
            }
            offsety += interline;
        }
        ctx.restore();
    }
}

class Draw {
    constructor(canvas, font, colors) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");
        this.font = font;
        this.colors = colors;
    }

    clear() {
        this.ctx.save();
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        this.ctx.fillStyle = this.colors.board;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.restore();
    }

    /* Drawing commands. */

    edge(edge, color) {
        const ctx = this.ctx;

        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.lineWidth = edge.width;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";

        ctx.beginPath();
        if (edge.type == "segment") {
            ctx.moveTo(...edge.start);
            ctx.lineTo(...edge.end);
        }
        if (edge.type == "rect") {
            ctx.moveTo(...edge.start);
            ctx.lineTo(edge.start[0], edge.end[1]);
            ctx.lineTo(...edge.end);
            ctx.lineTo(edge.end[0], edge.start[1]);
            ctx.lineTo(...edge.start);
        }
        if (edge.type == "arc") {
            ctx.arc(
                ...edge.start,
                edge.radius,
                deg2rad(edge.startangle),
                deg2rad(edge.endangle)
            );
        }
        if (edge.type == "circle") {
            ctx.arc(...edge.start, edge.radius, 0, 2 * Math.PI);
            ctx.closePath();
        }
        if (edge.type == "curve") {
            ctx.moveTo(...edge.start);
            ctx.bezierCurveTo(...edge.cpa, ...edge.cpb, ...edge.end);
        }
        if ("filled" in edge && edge.filled) {
            ctx.fill();
        } else {
            ctx.stroke();
        }
    }

    polygon(shape, color) {
        const ctx = this.ctx;
        ctx.save();
        ctx.translate(...shape.pos);
        ctx.rotate(deg2rad(-shape.angle));

        if ("filled" in shape && !shape.filled) {
            ctx.strokeStyle = color;
            ctx.lineWidth = shape.width;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";
            ctx.stroke(this.make_polygon_path(shape));
        } else {
            ctx.fillStyle = color;
            ctx.fill(this.make_polygon_path(shape));
        }
        ctx.restore();
    }

    item(item, color) {
        if (item.text) {
            this.font.draw(this.ctx, item, color);
        } else if (item.type == "polygon") {
            this.polygon(item, color);
        } else if (item.type !== undefined) {
            this.edge(item, color);
        } else {
            console.error("Unknown drawing item", item);
        }
    }

    items(items, color) {
        for (const item of items) {
            this.item(item, color);
        }
    }

    draw_pad(pad, color, outline) {
        const ctx = this.ctx;

        ctx.save();
        ctx.translate(...pad.pos);
        ctx.rotate(deg2rad(pad.angle));
        if (pad.offset) {
            ctx.translate(...pad.offset);
        }
        ctx.fillStyle = color;
        ctx.strokeStyle = color;
        var path = this.make_pad_path(pad);
        if (outline) {
            ctx.stroke(path);
        } else {
            ctx.fill(path);
        }
        ctx.restore();
    }

    draw_pad_hole(pad, color) {
        const ctx = this.ctx;

        if (pad.type != "th") return;
        ctx.save();
        ctx.translate(...pad.pos);
        ctx.rotate(deg2rad(pad.angle));
        ctx.fillStyle = color;
        if (pad.drillshape == "oblong") {
            ctx.fill(this.make_oblong_path(pad.drillsize));
        } else {
            ctx.fill(this.make_circle_path(pad.drillsize[0] / 2));
        }
        ctx.restore();
    }

    footprint(layer, footprint, highlight, pin_one_highlighted) {
        const ctx = this.ctx;

        for (var item of footprint.drawings) {
            if (item.layer == layer) {
                this.item(item, this.colors.pad);
            }
        }

        for (var pad of footprint.pads) {
            if (pad.layers.includes(layer)) {
                this.draw_pad(pad, this.colors.pad, false);
                if (pad.pin1 && pin_one_highlighted) {
                    this.draw_pad(pad, this.colors.pin1, true);
                }
            }
        }

        for (var pad of footprint.pads) {
            this.draw_pad_hole(pad, this.colors.hole);
        }

        if (highlight) {
            // draw bounding box
            if (footprint.layer == layer) {
                ctx.save();
                ctx.translate(...footprint.bbox.pos);
                ctx.rotate(deg2rad(-footprint.bbox.angle));
                ctx.translate(...footprint.bbox.relpos);
                ctx.fillStyle = this.colors.highlight_fill;
                ctx.fillRect(0, 0, ...footprint.bbox.size);
                ctx.strokeStyle = this.colors.highlight_stroke;
                ctx.strokeRect(0, 0, ...footprint.bbox.size);
                ctx.restore();
            }
        }
    }

    footprints(
        footprints,
        layer,
        highlighted_footprints = {},
        pin_one_highlighted_footprints = {}
    ) {
        const ctx = this.ctx;
        ctx.lineWidth = 1 / 4;

        for (var i = 0; i < footprints.length; i++) {
            var mod = footprints[i];
            var highlighted = highlighted_footprints[mod.ref] ? true : false;
            var pin_one_highlighted = pin_one_highlighted_footprints[mod.ref]
                ? true
                : false;
            this.footprint(layer, mod, highlighted, pin_one_highlighted);
        }
    }

    /* Path generation commands */

    make_chamfered_rect_path(size, radius, chamfpos, chamfratio) {
        // chamfpos is a bitmask, left = 1, right = 2, bottom left = 4, bottom right = 8
        var path = new Path2D();
        var width = size[0];
        var height = size[1];
        var x = width * -0.5;
        var y = height * -0.5;
        var chamfOffset = Math.min(width, height) * chamfratio;
        path.moveTo(x, 0);
        if (chamfpos & 4) {
            path.lineTo(x, y + height - chamfOffset);
            path.lineTo(x + chamfOffset, y + height);
            path.lineTo(0, y + height);
        } else {
            path.arcTo(x, y + height, x + width, y + height, radius);
        }
        if (chamfpos & 8) {
            path.lineTo(x + width - chamfOffset, y + height);
            path.lineTo(x + width, y + height - chamfOffset);
            path.lineTo(x + width, 0);
        } else {
            path.arcTo(x + width, y + height, x + width, y, radius);
        }
        if (chamfpos & 2) {
            path.lineTo(x + width, y + chamfOffset);
            path.lineTo(x + width - chamfOffset, y);
            path.lineTo(0, y);
        } else {
            path.arcTo(x + width, y, x, y, radius);
        }
        if (chamfpos & 1) {
            path.lineTo(x + chamfOffset, y);
            path.lineTo(x, y + chamfOffset);
            path.lineTo(x, 0);
        } else {
            path.arcTo(x, y, x, y + height, radius);
        }
        path.closePath();
        return path;
    }

    make_oblong_path(size) {
        return this.make_chamfered_rect_path(
            size,
            Math.min(size[0], size[1]) / 2,
            0,
            0
        );
    }

    make_polygon_path(shape) {
        if (shape.path2d) {
            return shape.path2d;
        }

        const path = new Path2D();
        for (const polygon of shape.polygons) {
            path.moveTo(...polygon[0]);
            for (let i = 1; i < polygon.length; i++) {
                path.lineTo(...polygon[i]);
            }
            path.closePath();
        }

        shape.path2d = path;

        return shape.path2d;
    }

    make_circle_path(radius) {
        var path = new Path2D();
        path.arc(0, 0, radius, 0, 2 * Math.PI);
        path.closePath();
        return path;
    }

    make_pad_path(pad) {
        if (pad.path2d) {
            return pad.path2d;
        }

        if (pad.shape == "rect") {
            pad.path2d = new Path2D();
            pad.path2d.rect(...pad.size.map((c) => -c * 0.5), ...pad.size);
        } else if (pad.shape == "oval") {
            pad.path2d = this.make_oblong_path(pad.size);
        } else if (pad.shape == "circle") {
            pad.path2d = this.make_circle_path(pad.size[0] / 2);
        } else if (pad.shape == "roundrect") {
            pad.path2d = this.make_chamfered_rect_path(
                pad.size,
                pad.radius,
                0,
                0
            );
        } else if (pad.shape == "chamfrect") {
            pad.path2d = this.make_chamfered_rect_path(
                pad.size,
                pad.radius,
                pad.chamfpos,
                pad.chamfratio
            );
        } else if (pad.shape == "custom") {
            pad.path2d = this.make_polygon_path(pad);
        }

        return pad.path2d;
    }
}

class Colors {
    constructor(elem) {
        const color_names = [
            "edge-cuts",
            "board",
            "pad",
            "hole",
            "pin1",
            "silk",
            "highlight-stroke",
            "highlight-fill",
        ];

        const style = window.getComputedStyle(elem);

        for (const name of color_names) {
            const property_name = name.replace("-", "_");
            const css_name = `--${name}`;
            this[property_name] = (
                style.getPropertyValue(css_name) || "red"
            ).trim();
        }
    }
}

export class Renderer {
    constructor(elem, pcb_data) {
        this.elem = elem;
        this.pcb_data = pcb_data;
        this.font = new Font(pcb_data.font_data);
        this.colors = new Colors(elem);
        this.rotate = elem.dataset.pcbRotate !== undefined;
        this._angle = 0;

        this.width =
            this.pcb_data.edges_bbox.maxx - this.pcb_data.edges_bbox.minx;
        this.height =
            this.pcb_data.edges_bbox.maxy - this.pcb_data.edges_bbox.miny;

        if (this.rotate) {
            const height = this.height;
            this.height = this.width;
            this.width = height;
        }

        this.highlighted = {};
        this.pin_one_highlighted = {};

        this.make_canvases();
        this.draw();
    }

    highlight(refs) {
        this.highlighted = {};
        for (const ref of refs) {
            this.highlighted[ref] = true;
        }
        this.draw();
    }

    highlight_pin_one(refs) {
        this.pin_one_highlighted = {};
        for (const ref of refs) {
            this.pin_one_highlighted[ref] = true;
        }
        this.draw();
    }

    /* Content building */

    make_canvases() {
        this.front = new Draw(
            this.make_canvas(this.elem, this.width, this.height,"front"),
            this.font,
            this.colors
        );
        this.back = new Draw(
            this.make_canvas(this.elem, this.width, this.height, "back"),
            this.font,
            this.colors
        );
    }

    make_canvas(parent, width, height, class_, scale = 10) {
        const canvas = document.createElement("canvas");
        canvas.classList.add(class_);
        canvas.width = width * window.devicePixelRatio * scale;
        canvas.height = height * window.devicePixelRatio * scale;
        canvas.dataset.scale = scale;
        parent.appendChild(canvas);
        return canvas;
    }

    /* Drawing */

    draw() {
        this.set_canvas_transform(this.front.canvas);
        this.front.clear();
        this.front.items(this.pcb_data.drawings.silkscreen.F, this.colors.silk);
        this.front.footprints(
            this.pcb_data.footprints,
            "F",
            this.highlighted,
            this.pin_one_highlighted
        );
        this.front.items(this.pcb_data.edges, this.colors.edge_cuts);

        this.set_canvas_transform(this.back.canvas, true);
        this.back.clear();
        this.back.items(this.pcb_data.drawings.silkscreen.B, this.colors.silk);
        this.back.footprints(
            this.pcb_data.footprints,
            "B",
            this.highlighted,
            this.pin_one_highlighted
        );
        this.back.items(this.pcb_data.edges, this.colors.edge_cuts);

        setTimeout(() => this.draw(), 200);
    }

    set_canvas_transform(canvas, mirror) {
        var ctx = canvas.getContext("2d");
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.scale(
            canvas.dataset.scale * window.devicePixelRatio,
            canvas.dataset.scale * window.devicePixelRatio
        );
        if (this.rotate) {
            const x = this.width / 2;
            const y = this.height / 2;
            ctx.translate(x, y);
            ctx.rotate(deg2rad(90));
            ctx.translate(-y, -x);
        }
        ctx.translate(
            -this.pcb_data.edges_bbox.minx,
            -this.pcb_data.edges_bbox.miny
        );
    }
}
