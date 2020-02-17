### WaniKani wallpaper generator

Generate wallpeaper filled with colorfull kanji signs, based on your progress on [WaniKani](https://www.wanikani.com/) platform!

![Example](/examples/big.png "Example of generated wallpaper")

#### Requirements

* python 3.6 <=
* [pipenv](https://pypi.org/project/pipenv/)

#### Installation

```
pipenv install
```

#### Basic usage

```
pipenv run python main.py --api-key <your api key> --file-out <path to out .bmp file>
```

##### Available configuration flags

| argument     | required? | default | description          |
|--------------|-----------|---------|----------------------|
| `--api-key`  | **yes**   | -       | WaniKani API key     |
| `--out-path` | **yes**   | -       | Where to put result? |



#### Examples

```
pipenv run python main.py --api-key abcdefgh-1234 --file-out ~/Pictures/WK-wallpeapers/out.bmp
```

#### TO DO:

* [ ] - add leftovers mods; center or shrink
* [ ] - configurable size (basic width and height)
* [ ] - configurable colors
* [ ] - configurable font
* [ ] - configurable kanji list
* [ ] - configurable kanji order
* [ ] - configurable seed for random shuffle




