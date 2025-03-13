import customtkinter as ctk

from properties import COLOR

class ColorPicker(ctk.CTkToplevel):
    def __init__(self, fg_color: str | None = None, preview_size: int = 100, r: int = 0, g: int = 0, b: int = 0, font: ctk.CTkFont | None = None) -> None:
        super().__init__(fg_color=fg_color)
        self.grab_set()
        self.attributes('-topmost', True)
        self.title('Color Picker')
        self.font = font if font else None
        self.font_size = font.cget('size') if font else 15
        self.preview_size = preview_size
        self.r_val: int = r
        self.g_val: int = g
        self.b_val: int = b
        self.hex_val: str | None = self.convert_to_hex()
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR.BACKGROUND)
        self.main_frame.pack(side=ctk.TOP, expand=True, ipadx=10, ipady=10)
        self.color_preview()
        self.r_g_b_sliders()
        self.update_sliders(None)
        self.bottom_frame = ctk.CTkFrame(self.main_frame, corner_radius=0, fg_color='transparent')
        self.bottom_frame.pack(side=ctk.BOTTOM, expand=True, ipadx=10, ipady=10)
        self.hex_color_label()
        self.ok_button()
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.lift()
        self.center_window()

    def center_window(self) -> None:
        x = self.master.winfo_screenwidth()
        y = self.master.winfo_screenheight()
        app_width = self.winfo_width()
        app_height = self.winfo_height()
        self.geometry(f'+{(x//2)-app_width}+{(y//2)-app_height}')

    def color_preview(self) -> None:
        self.color_prev_box = ctk.CTkFrame(self.main_frame, fg_color=self.convert_to_hex(), border_width=3, width=self.preview_size, 
                                            height=self.preview_size, corner_radius=0, border_color=COLOR.TILE_2)
        self.color_prev_box.pack(side=ctk.RIGHT, padx=3, pady=3, expand=True)

    @staticmethod
    def validate_hex_color(value_if_allowed):
        if len(value_if_allowed) == 0 or (value_if_allowed.startswith('#') and len(value_if_allowed) <= 7):
            for char in value_if_allowed[1:]:
                if char not in '0123456789ABCDEFabcdef':
                    return False
            return True
        return False

    def paste_hex_color(self, event):
        clipboard = self.master.clipboard_get()
        if self.validate_hex_color(clipboard):
            self.hex_val_label.delete(0, ctk.END)
            self.hex_val_label.insert(0, clipboard)
        return 'break'

    def update_on_hex(self, event) -> None:
        if len(self.hex_val_label.get()) == 7:
            self.r_val, self.g_val, self.b_val = self.convert_to_r_g_b()
            self.update_sliders(None)

    def hex_color_label(self) -> None:
        vcmd = (self.register(self.validate_hex_color), '%P')
        ctk.CTkLabel(self.bottom_frame, text='Hex: ', font=self.font if self.font else ctk.CTkFont('', self.font_size)).pack(side=ctk.LEFT, padx=3, pady=3)
        self.hex_val_label = ctk.CTkEntry(self.bottom_frame, validate='key', validatecommand=vcmd, corner_radius=0,
                                        font=self.font if self.font else ctk.CTkFont('', self.font_size),
                                        width=(self.font_size*8), border_color=COLOR.TILE_2)
        self.hex_val_label.pack(side=ctk.LEFT, padx=3, pady=3)
        self.hex_val_label.insert(0, f'{self.hex_val}')
        self.hex_val_label.bind('<Control-v>', self.paste_hex_color)
        self.hex_val_label.bind('<KeyRelease>', lambda e: self.update_on_hex(e))

    def ok_button(self) -> None:
        ok = ctk.CTkButton(self.bottom_frame, text='Ok', command=self.on_ok_button, font=self.font if self.font else ctk.CTkFont('', self.font_size),
                            width=(self.font_size*3), corner_radius=0, border_width=2, border_color=COLOR.TILE_2,
                            fg_color=COLOR.NOTATION_BACKGROUND_B, hover_color=COLOR.NOTATION_BACKGROUND_W)
        ok.pack(side=ctk.RIGHT, padx=3, pady=3)

    @staticmethod
    def new_slider_frame(frame) -> ctk.CTkFrame:
        slider_frame = ctk.CTkFrame(frame, fg_color='transparent', corner_radius=0)
        slider_frame.pack(side=ctk.TOP, padx=3, pady=3)
        return slider_frame

    @staticmethod
    def validate_input(P) -> bool:
        if P == '':
            return True
        if not P.isdigit():
            return False
        value = int(P)
        if 0 <= value <= 255:
            return True
        return False

    def r_g_b_sliders(self) -> None:
    # sliders frame
        vcmd = (self.register(self.validate_input), '%P')
        frame = ctk.CTkFrame(self.main_frame, fg_color='transparent')
        frame.pack(side=ctk.TOP)
    # R value slider
        slider_frame = self.new_slider_frame(frame)
        ctk.CTkLabel(slider_frame, text='R: ', font=self.font if self.font else ctk.CTkFont('', self.font_size)).pack(side=ctk.LEFT, padx=3, pady=3)
        self.r_val_label = ctk.CTkEntry(slider_frame, validate='key', validatecommand=vcmd, corner_radius=0,
                                        font=self.font if self.font else ctk.CTkFont('', self.font_size),
                                        width=(self.font_size*3), border_color=COLOR.TILE_2)
        self.r_val_label.pack(side=ctk.LEFT, padx=3, pady=3)
        self.r_slider = ctk.CTkSlider(slider_frame, from_=0, to=255, number_of_steps=255, command=lambda e: self.slider_on_change(e, r=True),
                                    button_corner_radius=1, button_length=12, corner_radius=1, button_color=COLOR.TILE_2,
                                    hover=False, progress_color=COLOR.TEXT, fg_color=COLOR.DARK_TEXT)
    # G value slider
        slider_frame = self.new_slider_frame(frame)
        ctk.CTkLabel(slider_frame, text='G: ', font=self.font if self.font else ctk.CTkFont('', self.font_size)).pack(side=ctk.LEFT, padx=3, pady=3)
        self.g_val_label = ctk.CTkEntry(slider_frame,
                                        validate='key', validatecommand=vcmd, corner_radius=0,
                                        font=self.font if self.font else ctk.CTkFont('', self.font_size),
                                        width=(self.font_size*3), border_color=COLOR.TILE_2)
        self.g_val_label.pack(side=ctk.LEFT, padx=3, pady=3)
        self.g_slider = ctk.CTkSlider(slider_frame, from_=0, to=255, number_of_steps=255, command=lambda e: self.slider_on_change(e, g=True),
                                    button_corner_radius=1, button_length=12, corner_radius=1, button_color=COLOR.TILE_2,
                                    hover=False, progress_color=COLOR.TEXT, fg_color=COLOR.DARK_TEXT)
    # B value slider
        slider_frame = self.new_slider_frame(frame)
        ctk.CTkLabel(slider_frame, text='B: ', font=self.font if self.font else ctk.CTkFont('', self.font_size)).pack(side=ctk.LEFT, padx=3, pady=3)
        self.b_val_label = ctk.CTkEntry(slider_frame, validate='key', validatecommand=vcmd, corner_radius=0,
                                        font=self.font if self.font else ctk.CTkFont('', self.font_size), 
                                        width=(self.font_size*3), border_color=COLOR.TILE_2)
        self.b_val_label.pack(side=ctk.LEFT, padx=3, pady=3)
        self.b_slider = ctk.CTkSlider(slider_frame, from_=0, to=255, number_of_steps=255, command=lambda e: self.slider_on_change(e, b=True),
                                    button_corner_radius=1, button_length=12, corner_radius=1, button_color=COLOR.TILE_2,
                                    hover=False, progress_color=COLOR.TEXT, fg_color=COLOR.DARK_TEXT)
    # initial setup of all labels
        self.r_val_label.insert(0, self.r_val)
        self.g_val_label.insert(0, self.g_val)
        self.b_val_label.insert(0, self.b_val)
        self.r_slider.set(self.r_val)
        self.g_slider.set(self.g_val)
        self.b_slider.set(self.b_val)
        self.r_slider.pack(side=ctk.LEFT, padx=3, pady=3)
        self.g_slider.pack(side=ctk.LEFT, padx=3, pady=3)
        self.b_slider.pack(side=ctk.LEFT, padx=3, pady=3)
    # binding for preview update
        self.r_val_label.bind('<KeyRelease>', lambda e: self.update_sliders(e))
        self.g_val_label.bind('<KeyRelease>', lambda e: self.update_sliders(e))
        self.b_val_label.bind('<KeyRelease>', lambda e: self.update_sliders(e))

    def update_sliders(self, event) -> None:
        r = int(self.r_val_label.get()) if self.r_val_label.get() != '' else 0
        g = int(self.g_val_label.get()) if self.g_val_label.get() != '' else 0
        b = int(self.b_val_label.get()) if self.b_val_label.get() != '' else 0
        self.r_val = r
        self.g_val = g
        self.b_val = b
        self.r_slider.set(r) if 0 < r <= 255 else self.r_slider.set(0)
        self.g_slider.set(g) if 0 < g <= 255 else self.g_slider.set(0)
        self.b_slider.set(b) if 0 < b <= 255 else self.b_slider.set(0)
        self.color_prev_box.configure(fg_color=self.convert_to_hex())

    def slider_on_change(self, event, r: bool = False, g: bool = False, b: bool = False) -> None:
        if r:
            self.r_val = int(self.r_slider.get())
            self.r_val_label.delete(0, ctk.END)
            self.r_val_label.insert(0, self.r_val)
        elif g:
            self.g_val = int(self.g_slider.get())
            self.g_val_label.delete(0, ctk.END)
            self.g_val_label.insert(0, self.g_val)
        elif b:
            self.b_val = int(self.b_slider.get())
            self.b_val_label.delete(0, ctk.END)
            self.b_val_label.insert(0, self.b_val)
        self.color_prev_box.configure(fg_color=self.convert_to_hex())
        self.hex_val_label.delete(0, ctk.END)
        self.hex_val_label.insert(0, f'{self.convert_to_hex()}')

    def convert_to_hex(self) -> str:
        return f'#{self.r_val:02x}{self.g_val:02x}{self.b_val:02x}'

    def convert_to_r_g_b(self) -> tuple[int, int , int]:
        hex_code = self.hex_val.lstrip('#') if self.hex_val else '000000'
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        return (r, g, b)

    def on_close(self) -> None:
        self.hex_val = None
        self.grab_release()
        self.destroy()

    def on_ok_button(self) -> None:
        self.destroy()

    def get_color(self) -> str | None:
        self.master.wait_window(self)
        return self.convert_to_hex() if self.hex_val else None

if __name__ == "__main__":
    ColorPicker()
