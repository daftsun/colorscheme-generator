import argparse
import math
import pathlib

import rich
from PIL import Image
from rich.console import Console
from rich.table import Table

BLACK = "#36454F"
WHITE = "#C2C2C2"


class LocationError(Exception):
    def __init__(self, location: str) -> None:
        super().__init__(f"File doesn't exists at: {location}")


class PaletteError(Exception):
    def __init__(self) -> None:
        super().__init__("No color palette found for image")


class IndexChosenError(Exception):
    def __init__(self, max_idx: int, inp_idx: int) -> None:
        super().__init__(f"Index: {inp_idx} not between 0 and {max_idx - 1}")


def read_params() -> tuple[str, int]:
    parser = argparse.ArgumentParser()
    parser.add_argument("loc", type=str, help="location of the wallpaper")
    parser.add_argument("-c", "--count", type=int, default=20, help="number of colors to generate")
    args = parser.parse_args()
    return args.loc, args.count


def verify_image(location: str) -> None:
    path = pathlib.Path(location)
    if not (path.exists() and path.is_file()):
        raise LocationError(location)

    with Image.open(path) as img:
        img.verify()


def generate_colorscheme(location: str, color_count: int) -> list[tuple[int, int, int]]:
    with Image.open(location) as img:
        palette_img = img.quantize(colors=color_count)
        raw_palette = palette_img.getpalette()
        if raw_palette is None:
            raise PaletteError

        palette: list[tuple[int, int, int]] = []
        for i in range(0, len(raw_palette), 3):
            r, g, b = raw_palette[i : i + 3]
            palette.append((r, g, b))

        return palette


def check_similarity(color_palette: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    result_palette: list[tuple[int, int, int]] = []
    n = len(color_palette)
    ignore = set()

    for i in range(n):
        if color_palette[i] in ignore:
            continue
        result_palette.append(color_palette[i])
        r1, g1, b1 = color_palette[i]
        for j in range(i + 1, n):
            if color_palette[j] in ignore:
                continue
            r2, g2, b2 = color_palette[j]
            dist_r = (r1 - r2) ** 2
            dist_g = (g1 - g2) ** 2
            dist_b = (b1 - b2) ** 2
            extra_delta = math.sqrt(((r1 + r2) / 2) * abs(dist_r - dist_b) / 256)
            similarity_score = math.sqrt(2 * dist_r + 4 * dist_g + 3 * dist_g + extra_delta)
            if similarity_score < 100:
                ignore.add(color_palette[j])
                continue

    return result_palette


def rgb_to_hex(red: int, green: int, blue: int) -> str:
    r, g, b = min(red, 255), min(green, 255), min(blue, 255)
    return f"#{r:02x}{g:02x}{b:02x}".upper()


def rgb_to_hsl(red: int, green: int, blue: int) -> tuple[float, float, float]:
    r = red / 255.0
    g = green / 255.0
    b = blue / 255.0

    c_max = max(r, g, b)
    c_min = min(r, g, b)
    delta = c_max - c_min

    lightness = (c_max + c_min) / 2.0
    saturation = 0.0 if delta == 0 else delta / (1.0 - abs(2.0 * lightness - 1.0))

    if delta == 0:
        hue = 0.0
    elif c_max == r:
        hue = ((g - b) / delta) % 6
    elif c_max == g:
        hue = ((b - r) / delta) + 2
    else:
        hue = ((r - g) / delta) + 4

    hue = hue * 60
    if hue < 0:
        hue += 360

    return round(hue, 1), round(saturation * 100, 1), round(lightness * 100, 1)


def hsl_to_rgb(hue: float, saturation: float, lightness: float) -> tuple[int, int, int]:
    # Convert saturation and lightness to fractions
    saturation /= 100.0
    lightness /= 100.0

    def value(n: int) -> float:
        k = (n + hue / 30.0) % 12
        a = saturation * min(lightness, 1.0 - lightness)
        return lightness - a * max(-1.0, min(k - 3.0, 9.0 - k, 1.0))

    r = round(255 * value(0))
    g = round(255 * value(8))
    b = round(255 * value(4))

    return (r, g, b)


def show_extracted_color(color_codes: list[int]) -> None:
    print()
    console = Console()
    table = Table(title="Extracted Color Palette")

    for column in ["Index", "Color", "RGB Code", "Hex Code"]:
        table.add_column(column, justify="center")

    for idx in range(0, len(color_codes), 3):
        red, green, blue = color_codes[idx : idx + 3]
        color = rgb_to_hex(red, green, blue)
        table.add_row(f"{idx // 3}", f"[{color}]███[/]", f"{red} {green} {blue}", color.upper())

    console.print(table)


def show_generated_palette(generated_palette: dict[str, str]) -> None:
    print()
    console = Console()
    table = Table(title="Generated Color Palette")
    for column in ["Name", "Color", "Hex Code"]:
        justify = "left" if column == "Name" else "center"
        table.add_column(column, justify=justify)

    for name, color in generated_palette.items():
        table.add_row(name, f"[{color}]███[/]", color.upper())

    console.print(table)


def generate_table(title: str, column_names: list[str], palette: list[tuple[int, int, int]] | dict[str, str]) -> None:
    print()
    console = Console()
    table = Table(title=title)
    for column in column_names:
        justify = "left" if column == "Name" else "center"
        table.add_column(column, justify=justify)

    if isinstance(palette, list):
        for idx, (red, green, blue) in enumerate(palette):
            color = rgb_to_hex(red, green, blue)
            table.add_row(f"{idx}", f"[{color}]███[/]", f"{red} {green} {blue}", color.upper())
    elif isinstance(palette, dict):
        for name, color in palette.items():
            table.add_row(name, f"[{color}]███[/]", color.upper())

    console.print(table)


def generate_palette(palette: list[tuple[int, int, int]]) -> dict[str, str]:
    print()
    max_idx = len(palette)
    idx = input("Enter base color index: ")
    idx = int(idx)
    if idx < 0 or idx >= max_idx:
        raise IndexChosenError(max_idx=max_idx, inp_idx=idx)

    r, g, b = palette[idx]
    hue, sat, light = rgb_to_hsl(r, g, b)

    # 1. Monochromatic: Vary lightness
    mono_light = hsl_to_rgb(hue, sat, min(100, light + 20))
    mono_dark = hsl_to_rgb(hue, sat, max(5, light - 20))

    # 2. Analogous: Shift hue by +/- 30 degrees (30/360)
    analogous_1 = hsl_to_rgb((hue + 30) % 360, sat, light)
    analogous_2 = hsl_to_rgb((hue - 30) % 360, sat, light)

    # 3. Complementary: Shift hue by 180 degrees (180/360)
    complementary = hsl_to_rgb((hue + 180) % 360, sat, light)

    return {
        "base": rgb_to_hex(r, g, b),
        "light": rgb_to_hex(*mono_light),
        "dark": rgb_to_hex(*mono_dark),
        "analog_1": rgb_to_hex(*analogous_1),
        "analog_2": rgb_to_hex(*analogous_2),
        "complimentary": rgb_to_hex(*complementary),
        "black": BLACK,
        "white": WHITE,
    }


def main() -> None:
    wallpaper_location, count = read_params()
    verify_image(wallpaper_location)
    color_palette = generate_colorscheme(wallpaper_location, count)
    updated_palette = check_similarity(color_palette)
    generate_table("Extracted Color Palette", ["Index", "Color", "RGB Code", "Hex Code"], updated_palette)
    gen_palette = generate_palette(updated_palette)
    generate_table("Generated Color Palette", ["Name", "Color", "Hex Code"], gen_palette)


if __name__ == "__main__":
    main()
