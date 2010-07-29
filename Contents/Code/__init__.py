import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

VIDEO_PREFIX      = "/video/cbssports"
BASE_URL = "http://www.cbssports.com"
VIDEO_PAGE_URL = "http://www.cbssports.com/video/player/play/videos/%s"
#VIDEO_PAGE_URL = "http://images.cbssports.com/video/uvp/Default.swf?r=843618235797&pid=%s&partner=cbssports&autoPlayVid=true"
SMIL_URL = "http://release.theplatform.com/content.select?format=SMIL&Tracking=true&balance=false&MBR=true&pid=%s"
CACHE_INTERVAL    = 1800
ICON = "icon-default.png"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenuVideo, "CBS Sports", ICON, "art-default.jpg")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.jpg')
  MediaContainer.title1 = 'CBS Sports'
  HTTP.SetCacheTime(CACHE_INTERVAL)
  
def MainMenuVideo():
    dir = MediaContainer(mediaType='video')  
    for item in XML.ElementFromURL(BASE_URL+"/video/player", True, errors='ignore').xpath('//div[@id="channelList"]/ul/li/a'):
        title = item.text
        if(title != None):
          url = item.get('href')
          dir.Append(Function(DirectoryItem(VideoSection, title=title.strip(), thumb=R(ICON)),  url=url))
          for child in item.xpath('../ul/li/a'):
            if child.text != None:
                Log("Child:"+str(child.text))
                childTitle = title + ": "+child.text
                #childTitle = title
                childUrl = child.get('href')
                dir.Append(Function(DirectoryItem(VideoSection, title=childTitle.strip(), thumb=R(ICON)),  url=childUrl))
    return dir
    
def VideoSection(sender, url):
    dir = MediaContainer(viewGroup='Details', mediaType='video')  
    content = HTTP.Request(BASE_URL+url)
    index = 25 + content.find("CBSi.app.VideoPlayer.Data")
    start = 1 + content.find("[", index)
    end = content.find("]", start)
    items = content[start:end].split("},{")
    for item in items:
        pieces = item.split(",")
        metaData = dict()
        for piece in pieces:
            tokens = piece.split('":"')
            if(len(tokens) > 1):
              metaData[tokens[0].replace('"','')] = tokens[1].replace('"','')
            
        if(metaData.has_key('title')):
          title = metaData['title'].replace('}','')
          thumb = metaData['large_thumbnail']
          summary = metaData['description']
          durationStr = metaData['duration']
          duration = convert(durationStr)
          pid = metaData['pid']
          dir.Append(Function(VideoItem(Video, title, thumb=thumb, summary=summary, duration=duration), pid=pid))
    return dir

# Extract the video source from the SMIL file. Sometimes direct flv file, sometimes rtmp.
def Video(sender, pid):
    smilUrl = SMIL_URL % pid
    for item in XML.ElementFromURL(smilUrl, True, errors='ignore',cacheTime=0).xpath('//switch/ref'):
        source = item.get('src')
        if source.startswith("http") and source.endswith(".flv"):
            return Redirect(source)
        elif source.startswith("rtmp"):
            player = source.split('?')[0]
            clip = source.split("<break>")[1].replace('.flv','')
            width = item.get('width')
            height = item.get('height')
            return Redirect(RTMPVideoItem(player, clip, width=width, height=height))
    return Redirect("")

# Convert the h:m:s string to milli-sec
def convert(durationStr):
    tokens = durationStr.split(":")
    hours = 0
    mins = 0
    sec = 0
    if len(tokens) == 3:
        hours = int(tokens[0])
        mins = int(tokens[1])
        sec = int(tokens[2])
    elif len(tokens) == 2:
        mins = int(tokens[0])
        sec = int(tokens[1])
    elif len(tokens) == 1:
        sec = int(tokens[0])
    duration = hours*60*60 + mins*60 + sec
    return 1000 * duration 