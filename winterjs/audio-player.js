/*
    Copyright (c) 2021 Alethea Katherine Flowers.
    Published under the standard MIT License.
    Full text available at: https://opensource.org/licenses/MIT
*/

const fft_size = 1024;
const stroke_width = 4;
const player_height = 100;

/* Safari's web audio implementation is absolutely broken trash. */
const is_safari = /apple/i.test(navigator.vendor);
// eslint-disable-next-line compat/compat
const has_audio_context = is_safari ? false : window.AudioContext !== undefined;

/*
    Manages the single audio context shared across all instances of the
    oscilloscope.
*/
class AudioContextManager {
    constructor() {
        if (has_audio_context) {
            this.create_context();
        }
    }

    create_context() {
        // eslint-disable-next-line compat/compat
        this.context = new window.AudioContext();

        this.analyser = this.context.createAnalyser();
        this.analyser.fftSize = fft_size;
        this.analyser.connect(this.context.destination);
        this.data_array = new Uint8Array(fft_size);

        this.current_source = null;
    }

    create_source(audio) {
        if (!has_audio_context) return null;
        return this.context.createMediaElementSource(audio);
    }

    connect_source(src) {
        if (!has_audio_context) return;

        if (this.current_source !== null) {
            this.current_source.disconnect();
        }

        this.current_source = src;

        src.connect(this.analyser);

        this.context.resume();
    }

    get_analyzer_data() {
        this.analyser.getByteTimeDomainData(this.data_array);
        return this.data_array;
    }
}

const manager = new AudioContextManager();

class AudioPlayer {
    constructor(container) {
        this.container = container;
        this.audio = container.querySelector("audio");
        this.audio.addEventListener("play", () => this.on_play());

        this.media_source = manager.create_source(this.audio);

        this.create_ui();
    }

    create_ui() {
        const container_styles = window.getComputedStyle(this.container);
        this.bg_color = container_styles.backgroundColor;
        this.stroke_color = container_styles.color;
        this.container.classList.add("is-loaded");

        this.canvas = document.createElement("canvas", { alpha: false });
        this.canvas.width = Math.max(500, this.container.clientWidth);
        this.canvas.height = player_height;
        this.container.insertBefore(this.canvas, this.audio);
        this.canvas_ctx = this.canvas.getContext("2d");
        this.canvas.addEventListener("click", () => this.on_click());
        this.sine_offset = 0;
        this.draw_sine(true);

        const title = document.createElement("p");
        title.innerText = this.audio.title;
        this.container.appendChild(title);
    }

    on_click() {
        if (this.audio.paused) {
            this.audio.play();
        } else {
            this.audio.pause();
        }
    }

    on_play() {
        /* pause all other elements. */
        for (const player of audio_players) {
            if (player === this) {
                continue;
            }
            player.audio.pause();
        }

        manager.connect_source(this.media_source);

        this.draw();
    }

    draw() {
        if (has_audio_context) {
            this.draw_analyzer();
        } else {
            this.draw_sine();
        }
    }

    clear() {
        this.canvas_ctx.beginPath();
        this.canvas_ctx.fillStyle = this.bg_color;
        this.canvas_ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    draw_analyzer() {
        const data = manager.get_analyzer_data();
        const buffer_length = data.length;

        this.clear();
        this.canvas_ctx.lineWidth = stroke_width;
        this.canvas_ctx.strokeStyle = this.stroke_color;
        this.canvas_ctx.beginPath();

        var slice_width = (this.canvas.width * 1.0) / buffer_length;
        var x = 0;

        for (var i = 0; i < buffer_length; i++) {
            var v = data[i] / 128.0;
            var y = (v * this.canvas.height) / 2;

            if (i === 0) {
                this.canvas_ctx.moveTo(x, y);
            } else {
                this.canvas_ctx.lineTo(x, y);
            }

            x += slice_width;
        }

        this.canvas_ctx.lineTo(this.canvas.width, this.canvas.height / 2);
        this.canvas_ctx.stroke();

        if (!this.audio.paused && !this.audio.ended) {
            window.requestAnimationFrame(() => this.draw());
        }
    }

    draw_sine(once) {
        this.clear();
        this.canvas_ctx.lineWidth = stroke_width;
        this.canvas_ctx.strokeStyle = this.stroke_color;
        this.canvas_ctx.beginPath();

        const divider = 4;
        const width = parseFloat(this.canvas.width) / divider;

        for (var i = 0; i < width + 1; i++) {
            var v = Math.sin(8 * Math.PI * (i / width) + this.sine_offset / 8);
            var y = this.canvas.height / 2 + ((v * this.canvas.height) / 2) * 0.9;
            if (i === 0) {
                this.canvas_ctx.moveTo(i * divider, y);
            } else {
                this.canvas_ctx.lineTo(i * divider, y);
            }
        }

        this.canvas_ctx.stroke();

        this.sine_offset++;

        if (!once && !this.audio.paused && !this.audio.ended) {
            window.requestAnimationFrame(() => this.draw());
        }
    }
}

const audio_players = [];

for (const el of document.querySelectorAll(".winter-audio-player")) {
    audio_players.push(new AudioPlayer(el));
}
