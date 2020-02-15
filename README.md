### WaniKani wallpaper generator

Generate wallpeaper filled with colorfull kanji signs, based on your progress on [WaniKani](https://www.wanikani.com/) platform!

![Example](/examples/big.png "Example of generated wallpaper")

##### Requirements

* python 3.6 <=
* [pipenv](https://pypi.org/project/pipenv/)

##### Installation

```
pipenv install
```

##### Usage

```
pipenv run python main.py --api-key <your api key> --file-out <path to out .bmp file>
```

#### Example

```
pipenv run python main.py --api-key abcdefgh-1234 --file-out ~/Pictures/WK-wallpeapers/out.bmp
```




