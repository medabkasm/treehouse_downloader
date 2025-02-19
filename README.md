# Treehouse video downloader

## Summary
Treehouse Video Downloader downloads videos (with optional subtitles) from the specified [Treehouse courses and workshops](http://www.teamtreehouse.com).

## Dependencies
Install all dependencies:
```
pip install -r requirements.txt
```
or install them separately
- [requests](http://docs.python-requests.org/en/master/)
```
pip install requests
```
- [youtube-dl](https://rg3.github.io/youtube-dl/)
```
pip install youtube_dl
```
- [BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
```
pip install beautifulsoup4
```

## Usage

2. define the **courses/workshops** you would like to download in the `links.txt` file. Example list of the courses/workshops is already in the file.
3. Go to file directory where `main.py` and `links.txt` are saved and run `main.py` from the terminal with: `python main.py`
4. Wait until all videos are downloaded and have fun watching them.

If the **download of the video fails**, the course URL will be saved in `log.txt`.

## Options

### Video format
The default video format is webm, but you can
also get mp4 files, just change `VIDEO_FORMAT = 'mp4'` in the `main.py` script.

One of the users noticed mp4 video format downloads only 30 sec clips so test it to make sure mp4 format is available for a particular course. 

### Downloader

Default downloader is `aria2c`. If you wish to change it, edit `EXTERNAL_DL = 'aria2c'`

### Additional options

You can extend the script by adding options in the `options` variable:
```
options = {
    'outtmpl': output,
    'external_downloader': EXTERNAL_DL
    # ,'verbose': True
}
```

Here is the list of all options (however not all of them work): https://github.com/rg3/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L129-L290

Feel free to experiment and test.

## Notes
Because youtube-dl login does not work for proper authentication of the Treehouse user I have used python 'requests' module to get the correct video link.

Hopefully youtube-dl will be extended to cover Treehouse soon. Here is the [issue](https://github.com/rg3/youtube-dl/issues/9836).

You can upgrade `youtube-dl` with `sudo -H pip install --upgrade youtube-dl`

Script was tested with the `youtube-dl 2017.12.14` and `Python 3.6.4`.
