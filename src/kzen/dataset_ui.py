"""
UI tạo dataset: 10 câu tiếng Anh, mỗi câu ghi âm → WAV + manifest.json.
Chạy: python -m kzen.dataset_ui (từ thư mục repo, sau `pip install -e .`)
"""
from __future__ import annotations

import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np

from .configs import repo_root
from .utils import (
    CHANNELS,
    SD_DTYPE,
    SAMPLE_RATE,
    open_mic_input_stream,
    save_mic_frames_to_wav,
)

NUM_ITEMS = 10

DEFAULT_SENTENCES = [
    "Hello, how are you today?",
    "The quick brown fox jumps over the lazy dog.",
    "Please open the window.",
    "I would like a cup of coffee.",
    "What time is the meeting?",
    "She sells seashells by the seashore.",
    "The weather is nice this afternoon.",
    "Could you repeat that more slowly?",
    "Thank you for your help.",
    "See you tomorrow.",
]


class DatasetBuilderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KzEn — Tạo dataset (text + WAV)")
        self.minsize(720, 520)
        self._out_dir = os.path.join(repo_root(), "kz_dataset")
        self._recording_index: int | None = None
        self._record_frames: list[np.ndarray] = []
        self._stream = None

        pad = {"padx": 10, "pady": 4}
        top = ttk.Frame(self)
        top.pack(fill=tk.X, **pad)
        ttk.Label(top, text="Thư mục lưu WAV + manifest:").pack(side=tk.LEFT)
        self.dir_label = ttk.Label(top, text=self._short_path(self._out_dir), foreground="blue")
        self.dir_label.pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="Chọn thư mục…", command=self._pick_dir).pack(side=tk.LEFT)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        hint = ttk.Label(
            self,
            text=(
                "Mỗi dòng: đọc đúng câu trong ô → bấm «Ghi âm» → nói → bấm «Dừng» để lưu WAV "
                f"({NUM_ITEMS} file: 000.wav … {NUM_ITEMS - 1:03d}.wav)."
            ),
            wraplength=680,
            justify=tk.LEFT,
        )
        hint.pack(anchor="w", padx=10, pady=(0, 4))

        canvas = tk.Canvas(self, highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        inner_win = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _sync_inner_width(event: tk.Event) -> None:
            # Canvas chỉ cuộn dọc: nếu không ép width, hàng Entry+ nút rộng hơn viewport
            # → nút «Ghi âm» bị cắt ngoài màn hình.
            w = event.width
            if w > 1:
                canvas.itemconfigure(inner_win, width=w)

        canvas.bind("<Configure>", _sync_inner_width)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, **pad)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        inner.grid_columnconfigure(1, weight=1)

        self._entries: list[ttk.Entry] = []
        self._btns_rec: list[ttk.Button] = []
        self._labels_status: list[ttk.Label] = []

        ttk.Label(inner, text="#").grid(row=0, column=0, sticky="w", padx=(0, 4), pady=(0, 6))
        ttk.Label(inner, text="Câu tiếng Anh (sửa được)").grid(
            row=0, column=1, sticky="w", pady=(0, 6)
        )
        ttk.Label(inner, text="Ghi âm").grid(row=0, column=2, padx=6, pady=(0, 6))
        ttk.Label(inner, text="Trạng thái").grid(row=0, column=3, sticky="w", pady=(0, 6))

        for i in range(NUM_ITEMS):
            r = i + 1
            ttk.Label(inner, text=f"{i + 1}.").grid(row=r, column=0, sticky="nw", padx=(0, 4), pady=2)
            ent = ttk.Entry(inner)
            ent.insert(0, DEFAULT_SENTENCES[i] if i < len(DEFAULT_SENTENCES) else "")
            ent.grid(row=r, column=1, sticky="ew", padx=(0, 4), pady=2)
            ent.bind("<KeyRelease>", lambda _e, idx=i: self._on_text_change(idx))
            self._entries.append(ent)

            btn = ttk.Button(inner, text="Ghi âm", command=lambda idx=i: self._toggle_rec(idx))
            btn.grid(row=r, column=2, padx=6, pady=2, sticky="ew")
            self._btns_rec.append(btn)

            st = ttk.Label(inner, text="—", foreground="gray")
            st.grid(row=r, column=3, sticky="w", pady=2)
            self._labels_status.append(st)

        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, **pad)
        ttk.Button(bottom, text="Lưu manifest.json (chỉ metadata, không ghi WAV)", command=self._save_manifest_only).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(bottom, text="Mở thư mục dataset", command=self._open_out_dir).pack(side=tk.LEFT)

        self._refresh_all_status()

    @staticmethod
    def _short_path(p: str, max_len: int = 48) -> str:
        if len(p) <= max_len:
            return p
        return "…" + p[-(max_len - 1) :]

    def _pick_dir(self):
        d = filedialog.askdirectory(initialdir=self._out_dir)
        if d:
            self._out_dir = d
            self.dir_label.config(text=self._short_path(self._out_dir))
            self._refresh_all_status()

    def _wav_path(self, index: int) -> str:
        os.makedirs(self._out_dir, exist_ok=True)
        return os.path.join(self._out_dir, f"{index:03d}.wav")

    def _on_text_change(self, index: int):
        self._update_row_status(index)

    def _refresh_all_status(self):
        for i in range(NUM_ITEMS):
            self._update_row_status(i)

    def _update_row_status(self, index: int):
        p = self._wav_path(index)
        if os.path.isfile(p):
            self._labels_status[index].config(text="Đã có WAV", foreground="green")
        else:
            self._labels_status[index].config(text="Chưa ghi", foreground="gray")

    def _toggle_rec(self, index: int):
        if self._recording_index is None:
            self._start_rec(index)
        elif self._recording_index == index:
            self._stop_rec()
        else:
            messagebox.showinfo("Đang ghi", "Dừng ghi âm hiện tại trước khi ghi dòng khác.")

    def _start_rec(self, index: int):
        self._record_frames = []
        self._recording_index = index
        self._btns_rec[index].config(text="Dừng")
        self._labels_status[index].config(text="Đang ghi…", foreground="red")
        for j, b in enumerate(self._btns_rec):
            if j != index:
                b.config(state=tk.DISABLED)
        try:
            self._stream = open_mic_input_stream(
                self._audio_callback,
                sample_rate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=SD_DTYPE,
            )
            self._stream.start()
        except Exception as e:
            self._recording_index = None
            for b in self._btns_rec:
                b.config(state=tk.NORMAL)
                b.config(text="Ghi âm")
            self._labels_status[index].config(text=f"Lỗi: {e}", foreground="red")
            messagebox.showerror("Mic", str(e))

    def _audio_callback(self, indata, frames, time, status):
        if status and self._recording_index is not None:
            idx = self._recording_index
            self.after(0, lambda: self._labels_status[idx].config(text=f"Lỗi: {status}", foreground="red"))
        if self._recording_index is not None:
            self._record_frames.append(indata.copy())

    def _stop_rec(self):
        idx = self._recording_index
        if idx is None:
            return
        self._recording_index = None
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        for b in self._btns_rec:
            b.config(state=tk.NORMAL)
            b.config(text="Ghi âm")
        if not self._record_frames:
            self._labels_status[idx].config(text="Không có dữ liệu", foreground="orange")
            return
        path = self._wav_path(idx)
        dur = save_mic_frames_to_wav(self._record_frames, path, SAMPLE_RATE)
        self._labels_status[idx].config(text=f"Đã lưu ({dur:.1f}s)", foreground="green")
        self._write_manifest()

    def _collect_items(self) -> list[dict]:
        items = []
        for i in range(NUM_ITEMS):
            text = self._entries[i].get().strip()
            wav_name = f"{i:03d}.wav"
            rel = wav_name
            items.append(
                {
                    "index": i,
                    "text": text,
                    "wav": rel,
                    "wav_abs": os.path.abspath(self._wav_path(i)),
                }
            )
        return items

    def _write_manifest(self):
        os.makedirs(self._out_dir, exist_ok=True)
        manifest = {
            "sample_rate": SAMPLE_RATE,
            "channels": CHANNELS,
            "items": [
                {"index": it["index"], "text": it["text"], "wav": it["wav"]}
                for it in self._collect_items()
            ],
        }
        path = os.path.join(self._out_dir, "manifest.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

    def _save_manifest_only(self):
        self._write_manifest()
        messagebox.showinfo("OK", f"Đã ghi {os.path.join(self._out_dir, 'manifest.json')}")

    def _open_out_dir(self):
        os.makedirs(self._out_dir, exist_ok=True)
        p = self._out_dir
        if sys.platform == "darwin":
            os.system(f'open "{p}"')
        elif sys.platform == "win32":
            os.startfile(p)  # type: ignore[attr-defined]
        else:
            os.system(f'xdg-open "{p}"')


def main():
    app = DatasetBuilderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
