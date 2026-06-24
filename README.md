# Color Palette Generator
Creates a color palette based on colors extracted from the image

---

## Steps Done:
1. Extracts colors from the image provided
2. Provides an option to select base color
3. Creates palette based on base color

---

## Installation and Setup

### Prerequisites

- **Python 3.10+**


### Quick setup with uv

```bash
uv sync
```

---

## Running the code

Command to extract color palette from image
```bash
uv run wallpaper_file_loc
```
Command to extract n number of colors from the image. Default is 5
```bash
uv run wallpaper_file_loc -c n
```

Command to autogenerate palette with defaults selected
```bash
uv run wallpaper_file_loc -noq
```

---

> [!WARNING] 
> Doesn't work with SVG file format
