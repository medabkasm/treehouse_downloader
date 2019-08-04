
currentValueLinks = 0
maxValueLinks = 0
maxValueVideos = 0
currentValueVideos = 0
session = None
SKIP_LOGIN = False

# global variables for the login page .seted by the main function.
root = None
myUserName = None
myPassword = None
# global variables for the login home page .seted by the main function.
homePage = None
linksFileDir = None
aboveFrame = None
linksFileButton = None
linksFile = None
linksFileEntry = None
SUBTITLES_check = None
VIDEOS_check = None
centerFrame = None
subtitleCheck = None
videosChek = None
filling = None
linkText = None
videoText = None
videoLabel = None
linkLabel = None
progressBarLinks = None
progressBarVideos = None
downFrame2 = None
startButton = None
cancelButton = None
login = None
downFrame = None
progressText = None

# for pause downloading .

videoNumberPause = 0
linkNumberPause = 0
linksList = []

# Download subtitles of the videos - use 'True' to download subtitles
SUBTITLES = 0
VIDEOS = 1
TEXT = 'Nothing to download .'
# Download accelerator
EXTERNAL_DL = 'aria2c'

# Video format - webm or mp4
VIDEO_FORMAT = 'webm'
