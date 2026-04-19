import tkinter as tk


class RecordingOverlay:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.width = 140
        self.height = 76
        self.base_bars = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.is_animating = False
        self.is_processing = False
        self.animation_job = None
        self.processing_job = None
        self.processing_angle = 0
        self.audio_level = 0.0
        self.transparent_color = "#ff00ff"
        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg=self.transparent_color)
        try:
            self.window.wm_attributes("-transparentcolor", self.transparent_color)
        except tk.TclError:
            pass
        self.window.withdraw()

        self.canvas = tk.Canvas(
            self.window,
            width=self.width,
            height=self.height,
            highlightthickness=0,
            bg=self.transparent_color,
        )
        self.canvas.pack(fill="both", expand=True)
        self._draw()

    def _draw(self, bars=None) -> None:
        self.canvas.delete("all")
        self._rounded_rect(
            8,
            8,
            self.width - 8,
            self.height - 8,
            52,
            fill="#161616",
            outline="#4a4a4a",
        )

        center_x = self.width // 2
        bar_width = 5
        spacing = 8
        bars = bars if bars is not None else self.base_bars
        start_x = center_x - ((len(bars) - 1) * spacing) / 2
        base_y = self.height / 2

        for index, bar_height in enumerate(bars):
            x = start_x + index * spacing
            self.canvas.create_line(
                x,
                base_y - bar_height / 2,
                x,
                base_y + bar_height / 2,
                fill="#f5f5f5",
                width=bar_width,
                capstyle="round",
            )

    def _update_bars(self) -> None:
        if not self.is_animating:
            return

        center_index = (len(self.base_bars) - 1) / 2
        animated_bars = []

        for index, base_height in enumerate(self.base_bars):
            if index in (0, len(self.base_bars) - 1):
                animated_bars.append(base_height)
                continue

            distance_from_center = abs(index - center_index)
            center_influence = max(0.0, 1.0 - (distance_from_center / 4.0))
            input_boost = self.audio_level * 22 * center_influence
            height = base_height + input_boost
            animated_bars.append(int(max(1, min(35, height))))

        self._draw(animated_bars)
        self.animation_job = self.root.after(60, self._update_bars)

    def _draw_processing(self) -> None:
        self.canvas.delete("all")
        self._rounded_rect(
            8,
            8,
            self.width - 8,
            self.height - 8,
            52,
            fill="#161616",
            outline="#4a4a4a",
        )
        self.canvas.create_oval(
            self.width / 2 - 10,
            self.height / 2 - 10,
            self.width / 2 + 10,
            self.height / 2 + 10,
            outline="#3a3a3a",
            width=3,
        )
        self.canvas.create_arc(
            self.width / 2 - 10,
            self.height / 2 - 10,
            self.width / 2 + 10,
            self.height / 2 + 10,
            start=self.processing_angle,
            extent=110,
            style="arc",
            outline="#f5f5f5",
            width=3,
        )

    def _update_processing(self) -> None:
        if not self.is_processing:
            return

        self.processing_angle = (self.processing_angle + 8) % 360
        self._draw_processing()
        self.processing_job = self.root.after(16, self._update_processing)

    def animate_processing(self) -> None:
        if self.is_animating:
            self.is_animating = False
            if self.animation_job is not None:
                self.root.after_cancel(self.animation_job)
                self.animation_job = None
        self.is_processing = True
        self.processing_angle = 0
        self._draw_processing()
        if self.processing_job is None:
            self.processing_job = self.root.after(16, self._update_processing)

    def set_audio_level(self, level: float) -> None:
        clamped = max(0.0, min(1.0, level))
        self.audio_level = (self.audio_level * 0.75) + (clamped * 0.25) + 0.03

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        self.canvas.create_polygon(points, smooth=True, **kwargs)

    def show(self) -> None:
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = int((screen_width - self.width) / 2)
        y_position = int(screen_height - self.height - 60)
        self.window.geometry(f"{self.width}x{self.height}+{x_position}+{y_position}")
        self.window.deiconify()
        self.window.lift()
        if not self.is_animating:
            self.is_animating = True
            self._update_bars()

    def hide(self) -> None:
        self.is_animating = False
        self.is_processing = False
        if self.animation_job is not None:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        if self.processing_job is not None:
            self.root.after_cancel(self.processing_job)
            self.processing_job = None
        self.audio_level = 0.0
        self.processing_angle = 0
        self._draw(self.base_bars)
        self.window.withdraw()
