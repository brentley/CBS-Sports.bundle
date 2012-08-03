RE_CBS_JSON     = Regex('CBSi.app.VideoPlayer.Data = (\[.+?\])')
VIDEO_PREFIX    = "/video/cbssports"
BASE_URL        = "http://www.cbssports.com"
VIDEO_PAGE_URL  = "http://www.cbssports.com/video/player/play/videos/pid=%s"
ICON            = "icon-default.png"

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

def VideoSection(url):
    oc = ObjectContainer()
    content = HTTP.Request(BASE_URL+url).content
    json_string = RE_CBS_JSON.search(content).group(1)
    details = JSON.ObjectFromString(json_string)
    for item in details:
        title = item['title']
        thumbs = [item['large_thumbnail'], item['medium_thumbnail'], item['small_thumbnail']]
        summary = item['description']
        duration = convert(item['duration'])
        pid = item['pid']
        video_url = VIDEO_PAGE_URL % pid
        oc.add(VideoClipObject(url=video_url, title=title, summary=summary, duration=duration,
            thumb=Resource.ContentsOfURLWithFallback(url=thumbs, fallback=ICON)))
    return oc

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