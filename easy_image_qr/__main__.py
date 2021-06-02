import textwrap
import math
from PIL import Image, ImageDraw, ImageFont
import qrcode


def remove_transparency(image, bg_colour=(255, 255, 255)):
    if image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    ):
        alpha = image.convert("RGBA").split()[-1]
        background = Image.new("RGBA", image.size, bg_colour + (255,))
        background.paste(image, mask=alpha)
        return background
    return image


def create_qr_illustration(product, width, height, font_file):
    qr_image = Image.new(mode="RGB", size=(width, height), color=(255, 255, 255))
    illustration = ImageDraw.Draw(qr_image)

    # TEXT
    font = ImageFont.truetype(font_file, 110)
    margin = offset = 40
    for line in textwrap.wrap(product["text"], width=30):
        illustration.text((margin, offset), line, font=font, fill="#000000")
        offset += font.getsize(line)[1]

    # RAW QR
    qr_code = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=7,
        border=5,
    )
    qr_code.add_data(product["qr"])
    qr_img = qr_code.make_image(fill_color="black", back_color="white")
    qr_code_width, qr_code_height = qr_img.size

    # LOGO QR
    if "logo" in product:
        logo = remove_transparency(Image.open(product["logo"])).resize(
            (math.floor(qr_code_width / 3.5), math.floor(qr_code_height / 3.5))
        )
        qr_img.paste(
            logo,
            (math.floor(qr_code_width / 2.6), math.floor(qr_code_height / 2.6)),
        )

    # Append qr to ilustration
    qr_image.paste(qr_img, (width - 400, 80))
    return qr_image


def create_qr_illustrations_list_pdf(
    products,
    width=1800,
    height=500,
    images_per_page=7,
    font_file="assets/Fonts/Mukta/Mukta-medium.ttf",
):

    pages = []
    images_index = 0

    page = Image.new(mode="RGB", size=(2480, 3508), color=(255, 255, 255))
    for idx, product in enumerate(products):
        image = create_qr_illustration(
            product, width=width, height=height, font_file=font_file
        )
        page.paste(image, (0, image.height * images_index))
        images_index += 1

        # Last page
        if len(products) == idx + 1 and len(products) - idx + 1 < images_per_page:
            pages.append(page)

        else:
            # Next page
            if images_index == images_per_page:
                pages.append(page)
                images_index = 0
                page = Image.new(mode="RGB", size=(2480, 3508), color=(255, 255, 255))

    pages_to_append = list(pages)
    pages_to_append.pop(0)
    pages[0].save("renderedImages.pdf", save_all=True, append_images=pages_to_append)


create_qr_illustrations_list_pdf(
    products=[
        {
            "text": "Product 1",
            "qr": "QR data for product 1",
            "logo": "assets/Icons/leaf.png",
        },
        {
            "text": "Product 2",
            "qr": "QR data for product 2",
            "logo": "assets/Icons/leaf.png",
        },
        {
            "text": "Product 3",
            "qr": "QR data for product 2",
            "logo": "assets/Icons/leaf.png",
        }
    ]
)
