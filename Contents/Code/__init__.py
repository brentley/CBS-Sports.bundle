VIDEO_PREFIX      = "/video/cbssports"
BASE_URL = "http://www.cbssports.com"
VIDEO_PAGE_URL = "http://www.cbssports.com/video/player/play/videos/%s"
ICON = "icon-default.png"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenuVideo, "CBS Sports", ICON, "art-default.jpg")
  
  ObjectContainer.art = R('art-default.jpg')
  ObjectContainer.title1 = 'CBS Sports'
  
def MainMenuVideo():
    oc = ObjectContainer()
    for item in HTML.ElementFromURL(BASE_URL+"/video/player", errors='ignore').xpath('//div[@id="channelList"]/ul/li/a'):
        title = item.text
        if(title != None):
          url = item.get('href')
          oc.add(DirectoryObject(key=Callback(VideoSection, url=url), title=title.strip(), thumb=R(ICON)))
          for child in item.xpath('../ul/li/a'):
            if child.text != None:
                childTitle = title + ": "+child.text
                childUrl = child.get('href')
                oc.add(DirectoryObject(key=Callback(VideoSection, url=childUrl), title=childTitle.strip(), thumb=R(ICON)))
    return oc
    
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