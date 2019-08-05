"""
Treehouse Video Downloader downloads videos from
the specified Treehouseteam.com courses and workshops.

define the course/workshop you would like to download
in the links.txt file.

You can change the format - default is mp4, but you can
also get webm, just change VIDEO_FORMAT = 'webm' below.

If download fails, the link will be saved in log.txt
"""

import os
import re
import requests
import sys
from bs4 import BeautifulSoup
import youtube_dl
import tkinter as tk
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
from tkinter import ttk
import time
import threading
from variables import *   # import all global variables.
import platform  # to check which operation system we are running.

#USERNAME = 'pumlalolta@yevme.com'
#PASSWORD = 'pumlalolta2019'

HOME_DIR = os.getcwd()

DIR = str(os.getcwd())  # default links file path.



def do_auth():

    global root
    global myUserName
    global myPassword
    """Login using username and password, returns logged in session
    Source: https://github.com/dx0x58/Treehouse-dl
    """
    username = myUserName.get()
    username = username.rstrip()
    password = myPassword.get()
    password = password.rstrip()

    global session
    session = requests.Session()

    login_page = session.get('https://teamtreehouse.com/signin')
    login_page_soup = BeautifulSoup(login_page.text, "html.parser")

    token_val = login_page_soup.find('input', {'name': 'authenticity_token'}).get('value')
    utf_val = login_page_soup.find('input', {'name': 'utf8'}).get('value')

    post_data = {'user_session[email]': username, 'user_session[password]': password, 'utf8': utf_val,
                 'authenticity_token': token_val}

    profile_page = session.post('https://teamtreehouse.com/person_session', data=post_data)

    profile_page_soup = BeautifulSoup(profile_page.text, "html.parser")
    auth_sign = profile_page_soup.title.text
    if auth_sign:
        if auth_sign.lower().find('home') != -1:
            #print('[!] Login success!')
            if tkMessageBox.askokcancel("loged in", "Login success! , Continue ?",parent = root):
                root.destroy()
                root = None

            else:
                return None

        else:
            #print('[!!] Not found login attribute\nExit...')
            #passwordEntry.delete(0,tk.END)
            tkMessageBox.showwarning("Error","invalid credentials",parent = root)
            return None
            #sys.exit(0)
    else:
        raise Exception('Login failed!')
        return None






def http_get(url):
    """Returns text of url
    Source: https://github.com/dx0x58/Treehouse-dl
    """
    global session
    resp = session.get(url)
    return resp.text


def move_to_course_directory(title):
    """Check if current directory is home directory. If not, change to it.
    Make a course directory and move to it.
    If course directory already exists, just move to it.
    If everything fails break the program.
    """

    # Move to home directory if we are somewhere else (e.g. course subdir)
    if os.getcwd() != HOME_DIR:
        os.chdir(HOME_DIR)
    try:
        # Make a directory with course name
        os.mkdir(title)
        os.chdir(title)
    except FileExistsError:
        # Position yourself in course directory
        os.chdir(title)
    except:
        print('Could not create subdirectory for the course: {}'.format(title))


def getID(link):
    """Go to the web page with the video and extract its ID
    """
    html = http_get(link)
    soup = BeautifulSoup(html, "html.parser")

    for id in soup.select("div#questions-container > ul"):
        return id.attrs["data-step-id"]

def getIdWithNoAuth(videoTag):
    """Go to the web page with the video and extract its ID
    """
    return videoTag.attrs['data-video-id']


def removeReservedChars(value):
    """ Remove reserved characters because of Windows OS compatibility
    """
    return "".join(i for i in value if i not in r'\/:*?"<>|')


def getSubtitles(id, name):
    """ Download and rename subtitle file to match the downloaded videos.
    Subtitle is located at https://teamtreehouse.com/videos/{id}}/captions
    """
    subtitlesLink = 'https://teamtreehouse.com/videos/{}/captions'.format(id)

    response = requests.get(subtitlesLink)
    if response.status_code == 200:
        contentDisposition = response.headers['Content-Disposition']
        parts = contentDisposition.split('"')

        filename = removeReservedChars(parts[-2])
        title = '{}-{}'.format(name, filename)
        content = response.text

        with open(title, 'w') as f:
            f.write(content)
        return 0


def getVideoFormat():
    """ Validate video format or return default format
    """
    default = 'mp4'
    if (VIDEO_FORMAT == 'mp4' or VIDEO_FORMAT == 'webm'):
        return VIDEO_FORMAT
    else:
        return default


def getLinksCourse(link):
    """ Get the content of stages and extract the links to videos
    """
    # Prepare URL with stages
    linkToStages = '{}{}'.format(link, '/stages')
    html = requests.get(linkToStages)
    soup = BeautifulSoup(html.text, "html.parser")

    # Find all urls of the videos (ignore reviews and questions)
    videos = []
    for a in soup.select('a[href^="/library/"]'):
        if (a.select('.video-22-icon')):  # if video icon is there
            videoLink = '{}{}'.format('https://teamtreehouse.com', a['href'])
            videos.append(videoLink)
    return videos


def getLinksWorkshop(link):
    """ Get the links to videos from workshop page
    """
    html = requests.get(link)
    soup = BeautifulSoup(html.text, "html.parser")
    # Find all urls of the videos
    videos = []
    for a in soup.select('li.workshop-video a[href^="/library/"]'):
        vidLink = '{}{}'.format('https://teamtreehouse.com', a['href'])
        print(videolink)
    return videos


def getLinkWorkshop(link):
    """ Get the link to video from workshop page - only one video workshop
    """
    html = requests.get(link)
    soup = BeautifulSoup(html.text, "html.parser")
    # Find all urls of the videos
    videos = []
    for a in soup.select('a#workshop-hero'):
        vidLink = '{}{}'.format('https://teamtreehouse.com', a['href'])
        videos.append(vidLink)
    return videos

def skipLogin(event = None):
    global SKIP_LOGIN
    global root
    if tkMessageBox.askokcancel("skip login", "skip login ! , Continue ?",parent = root):
        SKIP_LOGIN = True
        root.destroy()
        root = None
        return 1
    else:
        return -1


def loginFunc(event = None):
    global SKIP_LOGIN
    global homePage

    if(SKIP_LOGIN):    # the user is non authenticated. returns to the login page.
        SKIP_LOGIN = False
    else:
        pass

    homePage.destroy()
    homePage = None
    main()     # use this approach to prevent using goto statement.
    return 1

def exitLogin(event = None ):
    if tkMessageBox.askokcancel("Quit" , " Do you really want to quit?"):
        root.destroy()
        sys.exit(1)
    else:
        return None

def exitHome(event = None ):
    global homePage
    if tkMessageBox.askokcancel("Quit" , " Do you really want to quit?"):
        homePage.destroy()
        sys.exit(1)
    else:
        return None



def browse():

    global maxValue
    global linksFileEntry

    filePath = tkFileDialog.askopenfilename(defaultextension=".txt",initialdir = ".",
                                            filetypes =[("All Files","*.*"),("Text Documents","*.txt")])
    #with open(filePath) as file:
        #maxValue = len(file.readlines())

    global DIR
    DIR = filePath
    linksFileEntry.delete(tk.END,0)
    linksFileEntry.insert(tk.END,DIR)

    return DIR



def progressBarFunc():

    global currrentValueLinks
    global maxValueLinks
    global currrentValueVideos
    global maxValueVideos
    global progressBarLinks
    global progressBarVideos
    global homePage

    progressBarLinks['maximum'] = maxValueLinks
    progressBarLinks['value'] = currentValueLinks

    progressBarVideos['maximum'] = maxValueVideos
    progressBarVideos['value'] = currentValueVideos

    homePage.update_idletasks()
    homePage.after(500,progressBarFunc)

    return 1




def home():

    global session
    global SUBTITLES
    global VIDEOS
    global currentValueLinks
    global currentValueVideos
    global maxValueLinks
    global maxValueVideos
    global linkText
    global videoText
    global progressText
    global startButton
    global cancelButton
    global homePage
    global videoNumberPause
    global linkNumberPause
    global linksList
    global DIR

    SUBTITLES = SUBTITLES_check.get()
    VIDEOS = VIDEOS_check.get()

    with open(DIR,'r') as linksFile:

        #for linkNumber,link in enumerate(linksList[linkNumberPause:]):
        for linkNumber , link in enumerate(linksFile):

            #linkNumberPause = linkNumberPause + 1

            try:

                link = link.strip()
                #print('Downloading: {}'.format(link))

                linkText.set(str(link))   # for library link above the 1st progress bar.

                videos = getLinksWorkshop(link) or getLinkWorkshop(link) or getLinksCourse(link)

                maxValueVideos = len(videos) - 1

                if(VIDEOS or SUBTITLES):
                    #progressText.delete(1.0,tk.END)

                    # Generate folder name and move to it
                    parts = link.split('/')
                    title = parts[-1]
                    move_to_course_directory(title)

                else:
                    global TEXT
                    progressText.insert(tk.END,TEXT)
                    return -1

                for videoNumber,video in enumerate(videos):    # download from  pause to the end.
                #for videoNumber,video in enumerate(videos):    # download from  pause to the end.
                    #videoNumberPause = videoNumberPause + 1
                    videoText.set(str(video).rstrip())  # for video link above the 2end progress bar.

                    if(SKIP_LOGIN):  #  if login skipped ( skip button clicked )  get only previews videos.
                        html = requests.get(video)
                    else:   # if login is True , get the full length videos .
                        html = http_get(video)

                    soup = BeautifulSoup(html.text, "html.parser")

                    # Extract title for filename
                    h1 = soup.h1.text

                    # Output with the title of the video
                    output = u'%(id)s-' + removeReservedChars(h1) + u'.%(ext)s'

                    # Youtube-dl options
                    options = {
                        'outtmpl': output, 'external_downloader': EXTERNAL_DL
                        # ,'verbose': True
                    }

                    # Video source link
                    tag = soup.video
                    videolink = tag.find_all(type="video/{}".format(getVideoFormat()))[0].get('src')


                    currentValueLinks = linkNumber
                    currentValueVideos = videoNumber

                    if (VIDEOS):
                        with youtube_dl.YoutubeDL(options) as ydl:
                                ydl.download([videolink])

                        if (SUBTITLES):
                            ID = getIdWithNoAuth(tag)
                            info = ydl.extract_info(videolink, download=False)
                            name = info.get('title', None)
                            subs = getSubtitles(ID, name)

                            currentValueLinks = linkNumber
                            currentValueVideos = videoNumber

                    elif (SUBTITLES):
                        with youtube_dl.YoutubeDL(options) as ydl:
                            info = ydl.extract_info(videolink, download=False)
                            name = info.get('title', None)
                        ID = getIdWithNoAuth(tag)
                        subs = getSubtitles(ID, name)

                        currentValueLinks = linkNumber
                        currentValueVideos = videoNumber

                    else:
                        return -1


            except Exception as err:
                #print('Error :: ',str(err))
                #print()
                progressText.insert(tk.END,'> '+str(err) + '\n')

                os.chdir(HOME_DIR)
                with open('log.txt', 'a') as logFile:
                    logFile.write(link)
                    logFile.write('\n')




    # when downloading is finished.
    startButton.config(text = 'Exit', command = exitHome)
    cancelButton.pack_forget()
    #progressText.delete(1.0,tk.END)
    #progressText.config(fg = 'green')
    progressText.insert(tk.END,'> DONE !')

    homePage.update_idletasks()  # updated to prevent the cancel button from occuring.




def lunchThreads():

    global maxValueLinks
    global linksList
    global homePage


    if platform.system() == 'Linux':
        if '/' in DIR:
            fileName = DIR.split('/')[-1]
            if '.txt' in fileName:
                with open(DIR) as file:
                    maxValueLinks = len(file.readlines()) - 1
                    for link in file:
                        linksList.append(link.strip())
            else:
                if tkMessageBox.askokcancel("file error", "invalid file format ,Choose another file ?",parent = homePage):
                    browse()
                    return 1
                else:
                    return -1
        else:
            tkMessageBox.showerror("path error","not valid path for the links file.")
            return -1

    elif platform.system() == 'Windows':
        if '\\' in DIR:
            fileName = DIR.split('/')[-1]
            if '.txt' in fileName:
                with open(DIR) as file:
                    maxValueLinks = len(file.readlines()) - 1
                    for link in file:
                        linksList.append(link.strip())
            else:
                if tkMessageBox.askokcancel("file error", "Chose another links file ?",parent = homePage):
                    browse()
                    return 1
                else:
                    return -1
        else:
            tkMessageBox.showerror("path error","not valid path for the links file.")
            return -1


    homeThread = threading.Thread(target = home ,name = 'homeThread' , daemon = True)
    homeThread.start()
    progressBarThread = threading.Thread(target = progressBarFunc , name = 'progressThread' , daemon = True)
    progressBarThread.start()  # begin progressing after clickng on start button.




 # this is the login page .
def main():

    global root
    global myUserName
    global myPassword

    global homePage
    global linksFileDir
    global aboveFrame
    global linksFileButton
    global linksFile
    global linksFileEntry
    global SUBTITLES_check
    global VIDEOS_check
    global centerFrame
    global subtitleCheck
    global videosChek
    global filling
    global linkText
    global videoText
    global videoLabel
    global linkLabel
    global progressBarLinks
    global progressBarVideos
    global downFrame2
    global startButton
    global cancelButton
    global login
    global downFrame
    global progressText

    root = tk.Tk()
    root.resizable(0,0)
    root.title('treehouse downloader - Login')
    root.geometry('450x180+450+250')
    root.protocol("WM_DELETE_WINDOW",exitLogin)

    myUserName = tk.StringVar()
    username = tk.Label(root,text = 'Email :',font = '3')
    username.grid(row = 0 , column = 0 , padx = 4 , pady = 10 , sticky = 'e')
    usernameEntry = tk.Entry(root,font = '7',width = 30 , textvariable = myUserName)
    usernameEntry.grid(row = 0 , column = 1, padx = 6 , pady = 10,columnspan = 4 ,sticky = 'we')

    myPassword = tk.StringVar()
    password = tk.Label(root,text = 'Password :',font = '3')
    password.grid(row = 2 , column = 0 , padx = 4 ,pady = 10 , sticky = 'e')
    passwordEntry = tk.Entry(root,font = '7',width = 30 ,show = "*" ,textvariable = myPassword)
    passwordEntry.grid(row = 2 , column = 1 ,padx = 6 , pady = 10,columnspan = 4,sticky = 'we')

    text = ' You can skip this step by pressing the Skip button you will be only able \nto download videos previews and subtitles files .'
    alert = tk.Label(root,text = text )
    alert.grid(row = 3 , column = 0 ,columnspan = 4, padx = 2 , pady = 10 , sticky = 'we')
    skip = tk.Button(text = 'Skip' , command = skipLogin )
    skip.grid(row = 4, column = 3 ,columnspan = 2 ,padx = 5, sticky = 'we')
    login = tk.Button(text = 'Login in' , command = do_auth )
    login.grid(row = 4, column = 0 ,columnspan = 2 ,padx = 5, sticky = 'w')

    root.mainloop()





    # this is the home page.

    if(SKIP_LOGIN):
        title = 'threehouse downloader - non authenticated user '
        loginButtonText = 'login'   # shows when user press skip key.
        user = 'not authenticated'
        logStutus = 'login'

    else:
        title = 'treehouse downloader - Home '
        loginButtonText = 'logout'  # show when user enters valid authentication informations.
        user = myUserName.get()
        logStutus = 'logout'

    logCommand = 'loginFunc'

    homePage = tk.Tk()
    homePage.resizable(0,0)
    homePage.title(title)
    homePage.geometry('700x400+450+250')
    homePage.protocol("WM_DELETE_WINDOW",exitHome)


    menuBar = tk.Menu(homePage)
    accountMenu = tk.Menu(menuBar,tearoff = 0)
    menuBar.add_cascade(label = "Account",menu = accountMenu)
    accountMenu.add_command(label = user)
    accountMenu.add_separator()
    accountMenu.add_command(label = logStutus,command = eval(logCommand))


    linksFileDir = tk.StringVar()
    linksFileDir.set(DIR)
    aboveFrame = tk.Frame(homePage,height = 50,highlightbackground = 'black' ,highlightthickness = 1)
    linksFileButton = tk.Button(aboveFrame,text = 'Browse',command = browse)
    linksFile = tk.Label(aboveFrame,text = ' Import links file :')
    linksFileEntry = tk.Entry(aboveFrame ,width = 50 , font = '4')
    linksFileEntry.insert(tk.END,linksFileDir.get())

    linksFile.pack(side = tk.LEFT , padx = 2 , pady = 10 , anchor = 'w')
    linksFileEntry.pack(side = tk.LEFT , padx = 2 , pady = 10, anchor = 'w')
    linksFileButton.pack(side = tk.RIGHT , padx = 5 , pady = 10 )
    aboveFrame.pack(fill = tk.X , anchor = 'n', padx = 5 , pady = 5)

    SUBTITLES_check = tk.IntVar()
    VIDEOS_check = tk.IntVar()
    centerFrame = tk.Frame(homePage)
    subtitleCheck = tk.Checkbutton(centerFrame, text = 'get subtitles files' ,variable = SUBTITLES_check ,onvalue = 1 , offvalue = 0)
    videosChek = tk.Checkbutton(centerFrame, text = 'get videos' ,variable = VIDEOS_check ,onvalue = 1 , offvalue = 0)
    filling = tk.Label(centerFrame , width = 50)
    centerFrame.pack(anchor = 'n' , pady = 5 )
    subtitleCheck.pack(side = tk.LEFT , anchor = 'w')
    videosChek.pack(side = tk.LEFT , anchor = 'w')

    linkText = tk.StringVar()
    videoText = tk.StringVar()
    videoLabel = tk.Label(homePage,textvariable = videoText)
    linkLabel = tk.Label(homePage,textvariable = linkText)
    progressBarLinks = ttk.Progressbar(homePage,orient ="horizontal",length = 100, mode ="determinate")
    progressBarVideos = ttk.Progressbar(homePage,orient ="horizontal",length = 100, mode ="determinate")
    filling.pack( padx = 5 , pady = 5 )
    linkLabel.pack( anchor = 'w',padx = 10)
    progressBarLinks.pack( padx = 10, fill = tk.X )
    videoLabel.pack( anchor = 'w',padx = 10)
    progressBarVideos.pack( padx = 10  ,fill = tk.X )

    downFrame2 = tk.Frame(homePage)
    startButton = tk.Button(downFrame2,text = 'start',command = lunchThreads )
    cancelButton = tk.Button(downFrame2,text = 'cancel',command = exitHome )
    login = tk.Button(downFrame2,text = loginButtonText , command = loginFunc )

    startButton.pack(expand = tk.NO , side = tk.RIGHT ,padx = 5 )
    cancelButton.pack(expand = tk.NO , side = tk.RIGHT )
    login.pack(expand = tk.NO , side = tk.RIGHT ,padx = 5 )

    downFrame2.pack(fill = tk.BOTH , padx = 5 , pady = 5 )
    downFrame = tk.Frame(homePage)
    progressText = tk.Text(downFrame ,bg = 'black' , fg = 'white')

    progressText.pack(fill = tk.X )
    downFrame.pack(fill = tk.BOTH , padx = 10 , pady = 5  , ipadx = 3, ipady = 3)

    homePage.mainloop()



if __name__ == '__main__':      # run the program.
    main()
