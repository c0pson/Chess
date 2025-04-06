"""File with module Custom color picker to make user life easier.
"""

import customtkinter as ctk
import re

class ColorPicker(ctk.CTkToplevel):
    """Class used to pick custom theme color. Is also a module that can be reused with apps using customtkinter.

    Args:

     - ctk.CTkTopLevel : Inheritance from customtkinter CTkTopLevel window.
    """
    def __init__(self, fg_color: str | None=None, preview_size: int=100, r: int=0, g: int=0, b: int=0, font: ctk.CTkFont | None=None, 
                 border_color: str | None=None, slider_button_color: str | None=None, slider_progress_color: str | None=None, slider_fg_color: str | None=None, 
                 preview_border_color: str | None=None, button_fg_color: str | None=None, button_hover_color: str | None=None, icon: str | None=None) -> None:
        """Constructor handling most important function calls and variable setup.

        Args:
            fg_color (str | None, optional): Background color of the window. Defaults to None.
            preview_size (int, optional): _description_. Defaults to 100.
            r (int, optional): Default red intensity value. Defaults to 0.
            g (int, optional): Default green intensity value. Defaults to 0.
            b (int, optional): Default blue intensity value. Defaults to 0.
            font (ctk.CTkFont | None, optional): Custom font. Defaults to None.
        """
        super().__init__(fg_color=fg_color)
        self.fg_color: str| None = fg_color
        self.border_color: str| None = border_color
        self.slider_button_color: str| None = slider_button_color
        self.slider_progress_color: str| None = slider_progress_color
        self.slider_fg_color: str| None = slider_fg_color
        self.preview_border_color: str | None = preview_border_color
        self.button_fg_color: str | None = button_fg_color
        self.button_hover_color: str | None = button_hover_color
        self.grab_set()
        self.attributes('-topmost', True)
        self.title('Color Picker')
        self.font: ctk.CTkFont | None = font if font else None
        self.font_size: int = font.cget('size') if font else 15
        self.preview_size: int = preview_size
        self.r_val: int = r
        self.g_val: int = g
        self.b_val: int = b
        self.hex_val: str | None = self.convert_to_hex()
        self.main_frame: ctk.CTkFrame = ctk.CTkFrame(
            master        = self,
            corner_radius = 0,
            fg_color      = self.fg_color
        )
        self.main_frame.pack(side=ctk.TOP, expand=True, ipadx=10, ipady=10)
        self.color_preview()
        self.r_g_b_sliders()
        self.update_sliders(None)
        self.bottom_frame: ctk.CTkFrame = ctk.CTkFrame(
            master        = self.main_frame,
            corner_radius = 0,
            fg_color      = 'transparent'
        )
        self.bottom_frame.pack(side=ctk.BOTTOM, expand=True, ipadx=10, ipady=10)
        self.hex_color_label()
        self.ok_button()
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.lift()
        self.center_window()
        self.after(201, lambda: self.iconbitmap(icon))

    def center_window(self) -> None:
        """Function centering the TopLevel window. Screen size independent.
        """
        x: int = self.master.winfo_screenwidth()
        y: int = self.master.winfo_screenheight()
        app_width: int = self.winfo_width()
        app_height: int = self.winfo_height()
        self.geometry(f'+{(x//2)-app_width}+{(y//2)-app_height}')

    def color_preview(self) -> None:
        """Function creating frame for color preview.
        """
        self.color_prev_box: ctk.CTkFrame = ctk.CTkFrame(
            master        = self.main_frame,
            fg_color      = self.convert_to_hex(),
            border_width  = 3,
            width         = self.preview_size, 
            height        = self.preview_size,
            corner_radius = 0,
            border_color  = self.preview_border_color
        )
        self.color_prev_box.pack(side=ctk.RIGHT, padx=3, pady=3, expand=True)

    @staticmethod
    def validate_hex_color(value_if_allowed: str) -> bool:
        """Function validating new character in hex entry box. Can take one character or longer string to allow pasting.

        Args:
            value_if_allowed (str): New value to check.

        Returns:
            bool: True if hex color patter was met, False otherwise.
        """
        if len(value_if_allowed) == 0 or (re.compile(r'^#[0-9a-fA-F]{0,6}$').match(value_if_allowed)):
            for char in value_if_allowed[1:]:
                if char not in '0123456789ABCDEFabcdef':
                    return False
            return True
        return False

    def paste_hex_color(self, event) -> None:
        """Function handling pasting custom color into hex color entry box.

        Args:
            event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
        """
        clipboard = self.master.clipboard_get()
        if self.validate_hex_color(clipboard):
            self.hex_val_label.delete(0, ctk.END)
            self.hex_val_label.insert(0, clipboard)
        return None

    def update_on_hex(self, event) -> None:
        """Function handling all changes on entering last hex color. It changes RGB labels values, sliders values and color preview frame to the desired color.

        Args:
            event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
        """
        if len(self.hex_val_label.get()) == 7:
            self.r_val, self.g_val, self.b_val = self.convert_to_r_g_b()
            self.r_val_label.delete(0, ctk.END)
            self.g_val_label.delete(0, ctk.END)
            self.b_val_label.delete(0, ctk.END)
            self.r_val_label.insert(0, f'{self.r_val}')
            self.g_val_label.insert(0, f'{self.g_val}')
            self.b_val_label.insert(0, f'{self.b_val}')
            self.update_sliders(None, r=self.r_val, g=self.g_val, b=self.b_val)

    def hex_color_label(self) -> None:
        """Function creating entry box for hex color.
        """
        vcmd = (self.register(self.validate_hex_color), '%P')
        ctk.CTkLabel(self.bottom_frame, text='Hex: ', font=self.font if self.font else ctk.CTkFont('', self.font_size)).pack(side=ctk.LEFT, padx=3, pady=3)
        self.hex_val_label: ctk.CTkEntry = ctk.CTkEntry(
            master          = self.bottom_frame,
            validate        = 'key',
            validatecommand = vcmd,
            corner_radius   = 0,
            font            = self.font if self.font else ctk.CTkFont('', self.font_size),
            width           = (self.font_size*8),
            border_color    = self.border_color
        )
        self.hex_val_label.pack(side=ctk.LEFT, padx=3, pady=3)
        self.hex_val_label.insert(0, f'{self.hex_val}')
        self.hex_val_label.bind('<Control-v>', self.paste_hex_color)
        self.hex_val_label.bind('<KeyRelease>', lambda e: self.update_on_hex(e))

    def ok_button(self) -> None:
        """Function creating 'OK' button. After clicking the button if color is selected properly the value will be returned in master script.
        """
        ok_button: ctk.CTkButton = ctk.CTkButton(
            master = self.bottom_frame,
            text          = 'Ok',
            command       = self.on_ok_button,
            font          = self.font if self.font else ctk.CTkFont('', self.font_size),
            width         = (self.font_size*3),
            corner_radius = 0,
            border_width  = 2,
            border_color  = self.border_color,
            fg_color      = self.button_fg_color,
            hover_color   = self.button_hover_color
        )
        ok_button.pack(side=ctk.RIGHT, padx=3, pady=3)

    @staticmethod
    def new_slider_frame(frame: ctk.CTkFrame) -> ctk.CTkFrame:
        """Function creating frame for slider used to change R or G or B value.

        Args:
            frame (ctk.CTkFrame): Parent Frame on which cell will be represented.

        Returns:
            ctk.CTkFrame: Ready packed frame.
        """
        slider_frame: ctk.CTkFrame = ctk.CTkFrame(
            master        = frame,
            fg_color      = 'transparent',
            corner_radius = 0
        )
        slider_frame.pack(side=ctk.TOP, padx=3, pady=3)
        return slider_frame

    @staticmethod
    def validate_input(P: str) -> bool:
        """Validation of R,G,B inputs from entry boxes.

        Args:
            P (str): New input character.

        Returns:
            bool: True if RGB encoding requirements are met, False otherwise. 
        """
        if P == '':
            return True
        if not P.isdigit():
            return False
        value = int(P)
        if 0 <= value <= 255:
            return True
        return False

    def r_g_b_sliders(self) -> None:
        """Function creating sliders to change RGB values using interactive sliders.
        """
    # sliders frame
        vcmd = (self.register(self.validate_input), '%P')
        frame: ctk.CTkFrame = ctk.CTkFrame(
            master   = self.main_frame,
            fg_color = 'transparent'
        )
        frame.pack(side=ctk.TOP)
    # R value slider
        slider_frame: ctk.CTkFrame = self.new_slider_frame(frame)
        ctk.CTkLabel(
            master = slider_frame,
            text   = 'R: ',
            font   = self.font if self.font else ctk.CTkFont('', self.font_size)
        ).pack(side=ctk.LEFT, padx=3, pady=3)
        self.r_val_label: ctk.CTkEntry = ctk.CTkEntry(
            master          = slider_frame,
            validate        = 'key',
            validatecommand = vcmd,
            corner_radius   = 0,
            font            = self.font if self.font else ctk.CTkFont('', self.font_size),
            width           = (self.font_size*3),
            border_color    = self.border_color
        )
        self.r_val_label.pack(side=ctk.LEFT, padx=3, pady=3)
        self.r_slider: ctk.CTkSlider = ctk.CTkSlider(
            master               = slider_frame,
            from_                = 0,
            to                   = 255,
            number_of_steps      = 255,
            command              = lambda e: self.slider_on_change(e, r=True),
            button_corner_radius = 1,
            button_length        = 12,
            corner_radius        = 1,
            button_color         = self.slider_button_color,
            hover                = False,
            progress_color       = self.slider_progress_color,
            fg_color             = self.slider_fg_color
        )
    # G value slider
        slider_frame = self.new_slider_frame(frame)
        ctk.CTkLabel(slider_frame, text='G: ', font=self.font if self.font else ctk.CTkFont('', self.font_size)).pack(side=ctk.LEFT, padx=3, pady=3)
        self.g_val_label = ctk.CTkEntry(
            master          = slider_frame,
            validate        = 'key',
            validatecommand = vcmd,
            corner_radius   = 0,
            font            = self.font if self.font else ctk.CTkFont('', self.font_size),
            width           = (self.font_size*3),
            border_color    = self.border_color
        )
        self.g_val_label.pack(side=ctk.LEFT, padx=3, pady=3)
        self.g_slider: ctk.CTkSlider = ctk.CTkSlider(
            master               = slider_frame, 
            from_                = 0,
            to                   = 255,
            number_of_steps      = 255,
            command              = lambda e: self.slider_on_change(e, g=True),
            button_corner_radius = 1,
            button_length        = 12,
            corner_radius        = 1,
            button_color         = self.slider_button_color,
            hover                = False,
            progress_color       = self.slider_progress_color,
            fg_color             = self.slider_fg_color
        )
    # B value slider
        slider_frame = self.new_slider_frame(frame)
        ctk.CTkLabel(slider_frame, text='B: ', font=self.font if self.font else ctk.CTkFont('', self.font_size)).pack(side=ctk.LEFT, padx=3, pady=3)
        self.b_val_label: ctk.CTkEntry = ctk.CTkEntry(
            master          = slider_frame,
            validate        = 'key',
            validatecommand = vcmd,
            corner_radius   = 0,
            font            = self.font if self.font else ctk.CTkFont('', self.font_size), 
            width           = (self.font_size*3),
            border_color    = self.border_color
        )
        self.b_val_label.pack(side=ctk.LEFT, padx=3, pady=3)
        self.b_slider: ctk.CTkSlider = ctk.CTkSlider(
            master               = slider_frame,
            from_                = 0,
            to                   = 255,
            number_of_steps      = 255,
            command              = lambda e: self.slider_on_change(e, b=True),
            button_corner_radius = 1,
            button_length        = 12,
            corner_radius        = 1,
            button_color         = self.slider_button_color,
            hover                = False,
            progress_color       = self.slider_progress_color,
            fg_color             = self.slider_fg_color
        )
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

    def update_sliders(self, event, r: int=-1, g: int=-1, b: int=-1) -> None:
        """Function updating position of sliders and its corresponding RGB entry boxes to proper value after changing hex entry box.

        Args:
            event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
            r (int, optional): Given red color intensity. Defaults to -1.
            g (int, optional): Given green color intensity. Defaults to -1.
            b (int, optional): Given blue color intensity. Defaults to -1.
        """
        if r == -1:
            r = int(self.r_val_label.get()) if self.r_val_label.get() != '' else 0
        if g == -1:
            g = int(self.g_val_label.get()) if self.g_val_label.get() != '' else 0
        if b == -1:
            b = int(self.b_val_label.get()) if self.b_val_label.get() != '' else 0
        self.r_val = r
        self.g_val = g
        self.b_val = b
        self.r_slider.set(r) if 0 < r <= 255 else self.r_slider.set(0)
        self.g_slider.set(g) if 0 < g <= 255 else self.g_slider.set(0)
        self.b_slider.set(b) if 0 < b <= 255 else self.b_slider.set(0)
        self.color_prev_box.configure(fg_color=self.convert_to_hex())

    def slider_on_change(self, event, r: bool=False, g: bool=False, b: bool=False) -> None:
        """Updates corresponding RGB color code and hex color value based on value of slider.

        Args:
            event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
            r (bool, optional): Flag to set which slider was changed [r]. Defaults to False.
            g (bool, optional): Flag to set which slider was changed [g]. Defaults to False.
            b (bool, optional): Flag to set which slider was changed [b]. Defaults to False.
        """
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
        """Function converting RGB value to hex color code.

        Returns:
            str: f'{6 digit code}' | Regex example: ^#[0-9a-fA-F]{6}
        """
        return f'#{self.r_val:02x}{self.g_val:02x}{self.b_val:02x}'

    def convert_to_r_g_b(self) -> tuple[int, int , int]:
        """Function converting hex color code to RGB value.

        Returns:
            tuple[int, int , int]: Tuple of R, G and B values.
        """
        self.hex_val = self.hex_val_label.get()
        hex_code: str = self.hex_val.lstrip('#') if self.hex_val else '000000'
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        return (r, g, b)

    def on_close(self) -> None:
        """Custom closing function ensuring proper closing of the window. Sets hex_val to None to omit color change.
        """
        self.hex_val = None
        self.grab_release()
        self.destroy()

    def on_ok_button(self) -> None:
        """Custom closing function.
        """
        self.destroy()

    def get_color(self) -> str | None:
        """Function waiting for the window being destroyed.

        Returns:
            str | None: Hex color code if closed with OK button or None if closed with ❌.
        """
        self.master.wait_window(self)
        return self.convert_to_hex() if self.hex_val else None
