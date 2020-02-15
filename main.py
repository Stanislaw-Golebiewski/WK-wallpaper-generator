import random
import requests
import math
from PIL import Image, ImageDraw, ImageFont


def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def calc_rect_size(no_symbols, size,  margins=(0, 0, 0, 0), padding=0):

    width = size[0] - margins[2] - margins[3]
    height = size[1] - margins[0] - margins[1]

    print(f"> real size: {width} x {height}")
    leftover_y = -1
    single_square_area = math.floor(width * height / no_symbols)
    # print(f"> max square area: {single_square_area}")
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
    print(f"> number of columns: {columns} | leftover: {width - columns * size}")
    print(f"> number of rows: {rows} | leftover: {height - rows * size}")
    return (size, rows, columns)


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

padding = {"top": 20,
           "bottom": 20,
           "left": 20,
           "right": 20}

screen_size = {"width": 1920, "height": 1080}

# load kanji
with open("./kanji_order.txt") as file:
    all_kanji = "".join([line.strip() for line in file.readlines()])

count = len(all_kanji)

# GET DATA
next_url = "https://api.wanikani.com/v2/subjects?types=kanji"
kanji_list = []
while next_url:
    print(f"> GET request on {next_url}")
    response = requests.get(next_url,
                            headers={'Wanikani-Revision': '20170710',
                                     'Authorization': "Bearer deee2c84-d531-4218-8420-510362fba223"
                                     })
    response_body = response.json()
    next_url = response_body['pages']['next_url']
    kanji_list += [(kanji['id'], kanji['data']["characters"], kanji['data']["level"]) for kanji in response_body['data']]

kanji_dict_by_id = {}
for kanji in kanji_list:
    kanji_dict_by_id[kanji[0]] = kanji[1]

print(f"> total of {len(kanji_dict_by_id)} kanji found")

next_url = 'https://api.wanikani.com/v2/assignments?subject_types=kanji'
assigment_list = []
while next_url:
    print(f"> GET request on {next_url}")
    response = requests.get(next_url,
                            headers={'Wanikani-Revision': '20170710',
                                     'Authorization': "Bearer deee2c84-d531-4218-8420-510362fba223"
                                     })
    response_body = response.json()
    next_url = response_body['pages']['next_url']
    assigment_list += [(asg['data']['srs_stage_name'], kanji_dict_by_id[asg['data']['subject_id']]) for asg in response_body['data']]

# print(assigment_list, len(assigment_list))
assigment_dict_by_kanji = {}
for assigment in assigment_list:
    assigment_dict_by_kanji[assigment[1]] = assigment[0]

# print(assigment_dict_by_kanji)

# GENERATE IMG
img = Image.new("RGB", (screen_size["width"], screen_size["height"]), colors["background"])

d = ImageDraw.Draw(img)
square_size, no_rows, no_cols = calc_rect_size(count, (screen_size["width"], screen_size["height"]), (padding["top"], padding["bottom"], padding["left"], padding["right"]))
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
        if current_kanji in assigment_dict_by_kanji:
            kanji_srs_level = assigment_dict_by_kanji[current_kanji]
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


# img.show()
img.save('out.bmp')
