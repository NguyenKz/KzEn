"""
UI đơn giản: ghi âm từ mic, nhập transcript, chạy ForceAlign.
Chạy: python app_ui.py
"""
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

import numpy as np

from utils import (
    CHANNELS,
    SD_DTYPE,
    SAMPLE_RATE,
    default_recording_wav_path,
    open_mic_input_stream,
    save_mic_frames_to_wav,
    try_force_align,
)


class RecAlignApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KzEn — Ghi âm & Force align")
        self.minsize(480, 420)
        self._recording = False
        self._record_frames: list[np.ndarray] = []
        self._last_wav: str | None = None
        self._align_busy = False

        pad = {"padx": 10, "pady": 6}

        ttk.Label(
            self,
            text="Transcript (tiếng Anh, khớp với nội dung bạn nói):",
        ).pack(anchor="w", **pad)
        self.transcript = ttk.Entry(self, width=64)
        self.transcript.insert(0, "hello world")
        self.transcript.pack(fill=tk.X, **pad)

        row = ttk.Frame(self)
        row.pack(fill=tk.X, **pad)
        self.btn_rec = ttk.Button(row, text="● Ghi âm", command=self._toggle_record)
        self.btn_rec.pack(side=tk.LEFT, padx=(0, 8))
        self.status = ttk.Label(row, text="Sẵn sàng", foreground="gray")
        self.status.pack(side=tk.LEFT)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=4)
        ttk.Label(self, text="Kết quả align:").pack(anchor="w", **pad)
        self.out = scrolledtext.ScrolledText(self, height=14, wrap=tk.WORD, font=("Menlo", 11))
        self.out.pack(fill=tk.BOTH, expand=True, **pad)

        row2 = ttk.Frame(self)
        row2.pack(fill=tk.X, **pad)
        self.btn_align = ttk.Button(
            row2, text="Chạy aligner", command=self._run_align, state=tk.NORMAL
        )
        self.btn_align.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(row2, text="Mở file WAV…", command=self._load_wav).pack(side=tk.LEFT)

    def _toggle_record(self):
        if self._align_busy:
            return
        if not self._recording:
            self._start_rec()
        else:
            self._stop_rec()

    def _start_rec(self):
        self._record_frames = []
        self._recording = True
        self.status.config(text="Đang ghi… (bấm lần nữa để dừng)", foreground="red")
        self.btn_rec.config(text="■ Dừng ghi")
        self._stream = open_mic_input_stream(
            self._audio_callback,
            sample_rate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=SD_DTYPE,
        )
        self._stream.start()

    def _audio_callback(self, indata, frames, time, status):
        if status:
            self.after(0, lambda: self.status.config(text=f"Lỗi: {status}", foreground="red"))
        if self._recording:
            self._record_frames.append(indata.copy())

    def _stop_rec(self):
        self._recording = False
        if hasattr(self, "_stream") and self._stream:
            self._stream.stop()
            self._stream.close()
        self._stream = None
        self.btn_rec.config(text="● Ghi âm")
        if not self._record_frames:
            self.status.config(text="Không có dữ liệu", foreground="orange")
            return
        path = default_recording_wav_path()
        dur = save_mic_frames_to_wav(self._record_frames, path, SAMPLE_RATE)
        self._last_wav = path
        self.status.config(
            text=f"Đã lưu tạm ({dur:.1f}s) — bấm «Chạy aligner»",
            foreground="green",
        )

    def _load_wav(self):
        p = filedialog.askopenfilename(
            filetypes=[("WAV", "*.wav"), ("Mọi file", "*.*")]
        )
        if p:
            self._last_wav = p
            self.status.config(text=f"File: {os.path.basename(p)}", foreground="blue")

    def _run_align(self):
        if self._align_busy:
            return
        wav = self._last_wav
        if not wav or not os.path.isfile(wav):
            messagebox.showwarning("Thiếu file", "Hãy ghi âm hoặc chọn file WAV trước.")
            return
        text = self.transcript.get().strip()
        if not text:
            messagebox.showwarning("Thiếu transcript", "Nhập transcript trước khi chạy.")
            return
        self._align_busy = True
        self.btn_align.config(state=tk.DISABLED)
        self.out.delete("1.0", tk.END)
        self.out.insert(tk.END, "Đang tải model và align… (có thể mất vài chục giây lần đầu)\n")
        self.update_idletasks()

        def work():
            err, lines = try_force_align(wav, text)
            self.after(0, lambda: self._align_done(err, lines))

        threading.Thread(target=work, daemon=True).start()

    def _align_done(self, err, lines: list[str]):
        self._align_busy = False
        self.btn_align.config(state=tk.NORMAL)
        self.out.delete("1.0", tk.END)
        if err is not None:
            self.out.insert(tk.END, f"Lỗi: {err}\n")
            self.status.config(text="Align thất bại", foreground="red")
            return
        self.out.insert(tk.END, "".join(lines) if lines else "(rỗng)\n")
        self.status.config(text="Align xong", foreground="green")


def main():
    app = RecAlignApp()
    app.mainloop()


if __name__ == "__main__":
    main()
