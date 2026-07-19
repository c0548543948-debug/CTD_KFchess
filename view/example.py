import cv2
from img import Img


def main():
    # 1. הגדרת משתנים לניהול הגדלים במקום אחד
    SQUARE_SIZE = 100  # גודל משבצת בפיקסלים
    PIECE_SIZE = 80  # גודל החייל (טיפה קטן יותר מהמשבצת נראה יפה יותר)

    background = r"assets\board.png"
    logo = r"assets\pieces_classic\BB\states\idle\sprites\1 (38).png"

    canvas = Img().read(background)

    # 2. טעינת החייל בגודל המבוקש
    piece = Img().read(logo,
                       size=(PIECE_SIZE, PIECE_SIZE),
                       keep_aspect=True,
                       interpolation=cv2.INTER_AREA)

    # 3. חישוב מיקום למשבצת ספציפית (למשל עמודה 0, שורה 0)
    col = 0
    row = 0

    # חישוב מרכז המשבצת
    center_x = (col * SQUARE_SIZE) + (SQUARE_SIZE // 2)
    center_y = (row * SQUARE_SIZE) + (SQUARE_SIZE // 2)

    # חישוב נקודת הציור (פינה שמאלית עליונה של החייל כדי שהמרכז שלו יתלכד עם מרכז המשבצת)
    draw_x = center_x - (PIECE_SIZE // 2)
    draw_y = center_y - (PIECE_SIZE // 2)

    # 4. ציור החייל במיקום המחושב
    piece.draw_on(canvas, draw_x, draw_y)

    canvas.show()


if __name__ == "__main__":
    main()
