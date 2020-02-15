from argparse import ArgumentParser
import random
import requests
import math
from PIL import Image, ImageDraw, ImageFont

# TO DO:
# * functions annotate types
# * functions docstrings
# * move image generation to separeted function
# * validate --file-out argument
# * distribute leftover space equally to margins
# * config from .json file; --config argument
# * catch resposne code exceptions
# * use logger
# * allow additional fonts; --font argument


def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def calc_rect_size(no_symbols, size,  margins=(0, 0, 0, 0), padding=0):
    width = size[0] - margins[2] - margins[3]
    height = size[1] - margins[0] - margins[1]

    # print(f"> real size: {width} x {height}")
    leftover_y = -1
    single_square_area = math.floor(width * height / no_symbols)
    size = math.floor(math.sqrt(single_square_area))
    while(leftover_y < 0):
        # print(f"> max square size: {size}")
        columns = math.floor(width / size)
        rows = math.ceil(no_symbols / columns)
        leftover_y = height - rows * size
        if leftover_y < 0:
            size -= 1
            # print(math.ceil((-1 * leftover_y) / rows))
            # size -= math.ceil((-1 * leftover_y) / rows)
    # print(
    #     f"> number of columns: {columns} | leftover: {width - columns * size}")
    # print(f"> number of rows: {rows} | leftover: {height - rows * size}")
    return (size, rows, columns)


def load_kanji_set(path: str) -> list:
    with open(path) as file:
        all_kanji = "".join([line.strip() for line in file.readlines()])
        return all_kanji


def api_get_assignments_data(api_key):
    # get kanji data
    next_url = "https://api.wanikani.com/v2/subjects?types=kanji"
    kanji_list = []
    while next_url:
        print(f"> GET request on {next_url}")
        response = requests.get(next_url,
                                headers={'Wanikani-Revision': '20170710',
                                         'Authorization': f"Bearer {api_key}"
                                         })
        if response.status_code != 200:
            response.raise_for_status()
        response_body = response.json()
        next_url = response_body['pages']['next_url']
        kanji_list += [(kanji['id'], kanji['data']["characters"],
                        kanji['data']["level"]) for kanji in response_body['data']]

    kanji_dict_by_id = {}
    for kanji in kanji_list:
        kanji_dict_by_id[kanji[0]] = kanji[1]

    # get assignments data
    next_url = 'https://api.wanikani.com/v2/assignments?subject_types=kanji'
    assignment_list = []
    while next_url:
        print(f"> GET request on {next_url}")
        response = requests.get(next_url,
                                headers={'Wanikani-Revision': '20170710',
                                         'Authorization': f"Bearer {api_key}"
                                         })
        response_body = response.json()
        next_url = response_body['pages']['next_url']
        assignment_list += [(asg['data']['srs_stage_name'], kanji_dict_by_id[asg['data']
                                                                            ['subject_id']]) for asg in response_body['data']]

    assignment_dict_by_kanji = {}
    for assignment in assignment_list:
        assignment_dict_by_kanji[assignment[1]] = assignment[0]
    return assignment_dict_by_kanji


def shuffle_kanji_order(all_kanji_str) -> str:
    temp = [chr for chr in all_kanji_str]
    random.shuffle(temp)
    return "".join(temp)


def get_config():
    # --- defaults ---
    colors = {
        "background": (0, 0, 0),
        "kanji_unknown": (120, 120, 120),
        "Initiate": (200, 200, 200),
        "Apprentice I": (227, 0, 151),
        "Apprentice II": (227, 0, 151),
        "Apprentice III": (227, 0, 151),
        "Apprentice IV": (227, 0, 151),
        "Guru I": (163, 54, 190),
        "Guru II": (163, 54, 190),
        "Master": (77, 106, 225),
        "Enlightened": (0, 153, 230),
        "Burned": (255, 215, 0)
    }

    margins = {"top": 0,
               "bottom": 25,
               "left": 0,
               "right": 0}

    screen_size = {"width": 1920, "height": 1080}
    # screen_size = {"width": 800, "height": 600}
    # ---

    parser = ArgumentParser(description='WK wallpeaper config')
    parser.add_argument("--api-key", required=True, metavar="API_KEY")
    parser.add_argument("--file-out", required=True, metavar="PATH")
    args = parser.parse_args()

    out_config = {
        "api_key": args.api_key,
        "out_path": args.file_out,
        "colors": colors,
        "margins": margins,
        "screen_size": screen_size
    }

    return out_config


def main():
    # get config
    config = get_config()
    colors = config["colors"]
    padding = config["margins"]
    screen_size = config["screen_size"]
    api_key = config["api_key"]
    file_out_path = config["out_path"]

    random.seed(1)

    # load kanji list
    all_kanji = load_kanji_set("./kanji_order.txt")
    all_kanji = shuffle_kanji_order(all_kanji)
    count = len(all_kanji)

    # get assignments data from api
    assignment_dict_by_kanji = api_get_assignments_data(api_key)

    img = Image.new(
        "RGB", (screen_size["width"], screen_size["height"]), colors["background"])

    d = ImageDraw.Draw(img)

    # get best font size
    square_size, no_rows, no_cols = calc_rect_size(count, (screen_size["width"], screen_size["height"]), (
        padding["top"], padding["bottom"], padding["left"], padding["right"]))
    print(f"size: {square_size} | {no_cols} x {no_rows}")

    # show padded area
    # d.rectangle([padding["top"], padding["left"], screen_size["width"] - padding["right"], screen_size["height"] - padding["bottom"]], fill=(128, 0, 0))

    fnt = ImageFont.truetype('./fonts/ipag.ttf', square_size)
    # d.text((20, 20), "ご", font=fnt, fill=(0, 0, 0))
    counter = 0
    y = padding["top"]
    for row in range(no_rows):
        x = padding["left"]
        for column in range(no_cols):
            current_kanji = all_kanji[counter]
            kanji_color = colors["kanji_unknown"]
            if current_kanji in assignment_dict_by_kanji:
                kanji_srs_level = assignment_dict_by_kanji[current_kanji]
                kanji_color = colors[kanji_srs_level]
            # d.rectangle([x, y, x+square_size, y+square_size], fill=random_color())
            d.text((x, y), all_kanji[counter], font=fnt, fill=kanji_color)
            x += square_size
            counter += 1
            if counter == count:
                break
        y += square_size
        if counter == count:
            break

    img.save(file_out_path)


if __name__ == "__main__":
    main()
