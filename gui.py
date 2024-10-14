import tkinter as tk
from PIL import Image, ImageTk

def load_piece_images():
    pieces = ['bp', 'br', 'bn', 'bb', 'bq', 'bk', 'wp', 'wr', 'wn', 'wb', 'wq', 'wk']
    images = {}
    for piece in pieces:
        image = Image.open(f"pieceImages/{piece}.png")
        images[piece] = ImageTk.PhotoImage(image.resize((40, 40)))
    return images

def get_piece_image(piece, images):
    if piece.islower():
        return images[f"b{piece}"]
    else:
        return images[f"w{piece.lower()}"]

def draw(position):
    root = tk.Tk()
    root.title("Chess Position")

    canvas = tk.Canvas(root, width=320, height=320)
    canvas.pack()

    square_size = 40

    # Colors for the squares
    light_color = "#f0d9b5"
    dark_color = "#b58863"

    # Load piece images
    images = load_piece_images()

    # Draw the chessboard
    for row in range(8):
        for col in range(8):
            x1 = col * square_size
            y1 = row * square_size
            x2 = x1 + square_size
            y2 = y1 + square_size
            color = light_color if (row + col) % 2 == 0 else dark_color
            canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    # Draw the pieces
    rows = position.split('\n')
    for row in range(8):
        for col in range(8):
            piece = rows[row].split()[col]
            if piece != '.':
                x = col * square_size
                y = row * square_size
                image = get_piece_image(piece, images)
                canvas.create_image(x, y, anchor='nw', image=image)

    # Draw the column labels
    for col in range(8):
        x = col * square_size + square_size // 2
        canvas.create_text(x, 8 * square_size + 10, text=chr(ord('a') + col), font=("Arial", 14))

    # Draw the row labels
    for row in range(8):
        y = row * square_size + square_size // 2
        canvas.create_text(8 * square_size + 10, y, text=str(8 - row), font=("Arial", 14))

    root.mainloop()