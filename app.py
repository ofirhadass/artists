import random

from flask import Flask, render_template, request
import requests


LANGUAGES = {"English": "strBiographyEN",
             "Deutsch": "strBiographyDE",
             "Français": "strBiographyFR",
             "中文": "strBiographyCN",
             "Italiano": "strBiographyIT",
             "日本語": "strBiographyJP",
             "Pусский": "strBiographyRU",
             "Español": "strBiographyES",
             "Português": "strBiographyPT",
             "Svenska": "strBiographySE",
             "Nederlands": "strBiographyNL",
             "Magyar": "strBiographyHU",
             "Norsk": "strBiographyNO",
             "עברית": "strBiographyIL"}
DEFAULT_LANGUAGE = "English"
NOT_EXIST_MESSAGE = "Sorry! We don't have any information in this language. Try it in another one, it is always good to learn new language :)"
DISPLAY_SONGS = 3
IMAGES_KEYS = ["strArtistThumb", "strArtistClearart", "strArtistWideThumb", "strArtistFanart", "strArtistFanart2", "strArtistFanart3"]
app = Flask(__name__)


@app.route("/")
def search():
    artist_name = request.args.get("artist name")
    if not artist_name:
        return render_template("index.html", languages=LANGUAGES.items())
    artist_name = artist_name.lower().replace(" ", "_")
    resp = requests.get(f"http://theaudiodb.com/api/v1/json/1/search.php?s={artist_name}")
    try:
        details = resp.json()["artists"][0]
    except TypeError:
        return render_template("does_not_exist.html", name=artist_name.replace("_", " "), languages=LANGUAGES.items())
    artist_id = details["idArtist"]
    songs = get_songs(artist_id)
    links = [("Official website", details["strWebsite"]),
             ("Facebook", details["strFacebook"]),
             ("Twitter", details["strTwitter"])]
    language = request.args.get("language")
    if not language:
        language = DEFAULT_LANGUAGE
    description = details[LANGUAGES[language]]
    if description is None:
        description = NOT_EXIST_MESSAGE
    return render_template("index.html",
                           languages=LANGUAGES.items(),
                           name=details["strArtist"],
                           image=details["strArtistThumb"],
                           logo=details["strArtistLogo"],
                           banner=details["strArtistBanner"],
                           description=description,
                           links=links,
                           songs=songs)


def get_songs(artist_id):
    resp = requests.get(f"http://theaudiodb.com/api/v1/json/1/mvid.php?i={artist_id}").json()
    songs = {(song["strTrack"], song["strMusicVid"]) for song in resp["mvids"]}
    songs = list(songs)
    random.shuffle(songs)
    return songs[:DISPLAY_SONGS]


@app.route("/<artist_name>/pictures")
def pictures(artist_name):
    resp = requests.get(f"http://theaudiodb.com/api/v1/json/1/search.php?s={artist_name}")
    details = resp.json()["artists"][0]
    images = []
    for item in IMAGES_KEYS:
        images.append(details[item])
    return render_template("pictures.html",
                           logo=details["strArtistLogo"],
                           banner=details["strArtistBanner"],
                           name=artist_name,
                           images=images)

