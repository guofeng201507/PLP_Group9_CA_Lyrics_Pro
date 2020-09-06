import lyricsgenius

from static import TOKEN

genius = lyricsgenius.Genius(TOKEN)
artist = genius.search_artist("Andy Shauf", max_songs=3, sort="title")
print(artist.songs)

def retrieve_all_songs():
    try:
        song = api.search_song(song_title, artist=artist_name)
        song_album = song.album
        song_album_url = song.album_url
        featured_artists = song.featured_artists
        song_lyrics = re.sub("\n", " ", song.lyrics)
        song_media = song.media
        song_url = song.url
        song_writer_artists = song.writer_artists
        song_year = song.year
    except:
        song_album = "null"
        song_album_url = "null"
        featured_artists = "null"
        song_lyrics = "null"
        song_media = "null"
        song_url = "null"
        song_writer_artists = "null"
        song_year = "null"