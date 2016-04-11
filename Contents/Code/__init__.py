TITLE = 'Test'
PREFIX = '/video/test'

ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'https://www.youtube.com'
TEST_URL = 'http://www.tested.com/videos/'
# This gets the related video sections http://www.cnn.com/specials/videos/digital-shorts
RELATED_JSON = 'http://www.cnn.com/video/data/3.0/video/%s/relateds.json'
RELATED_SECTION = ['Business', 'Entertainment', 'Health', 'Justice', 'Living', 'CNNMoney', 'Politics', 'Style', 'Technology', 'Travel', 'TV', 'US', 'World', 'Weather']

###################################################################################################
# Set up containers for all possible objects
def Start():

    ObjectContainer.title1 = TITLE

    DirectoryObject.thumb = R(ICON)
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
 
#####################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
    oc = ObjectContainer()
  
    oc.add(DirectoryObject(key=Callback(GetVideos, url=TEST_URL, title='Videos'), title='Videos')) 
    oc.add(DirectoryObject(key=Callback(PlaylistPull, title='CNN Videos'), title='CNN Videos')) 
    oc.add(InputDirectoryObject(key=Callback(InputTest), title='Input Test Without Variable')) 
    oc.add(InputDirectoryObject(key=Callback(InputTestAlso, title='Input Test Without Variable'), title='Input Test With Variable')) 

    return oc

#########################################################################################
# To test input
@route(PREFIX + '/inputtest')
def InputTest(query):

    oc = ObjectContainer()
    
    local_url = TEST_URL
    data = HTML.ElementFromURL(local_url)
    input = query
    Log('the value of input is %s' %input)
    
    return ObjectContainer(header="Test", message="This test is complete.")
    
#########################################################################################
# To also test input
@route(PREFIX + '/inputtestalso')
def InputTestAlso(title, query):

    oc = ObjectContainer(title2=title)
    
    local_url = TEST_URL
    data = HTML.ElementFromURL(local_url)
    input = query
    Log('the value of input is %s' %input)
    
    return ObjectContainer(header="Test", message="This test is complete.")
    
##############################################################################
# Basic Vidoe pull for Twitch
@route(PREFIX + '/getvideos')
def GetVideos(title, url):

    oc = ObjectContainer(title2=title)
    page = HTML.ElementFromURL(url)
    data = page.xpath('//section[@class="content"]/ul/li')

    for video in data:

        title = video.xpath('.//span[contains(@class, "title")]/text()')[0]
        link = video.xpath('./a/@href')[0]
        thumb_url = video.xpath('.//img/@src')[0]

        oc.add(VideoClipObject(
            url = BASE_URL + link,
            title = title, 
            thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
        ))
        
    if len(oc) < 1:
        return ObjectContainer(header=L('Empty'), message=L('There are no videos to display right now'))
    else:
        return oc

####################################################################################################
# This function creates the list of known sections for the CNN related json playlists
@route(PREFIX + '/playlistpull')
def PlaylistPull(title):  

    oc = ObjectContainer(title2 = title)

    for item in RELATED_SECTION:
        playlist_url = RELATED_JSON %item.lower()
        oc.add(DirectoryObject(
            key = Callback(PlaylistJSON, title = item, url = playlist_url), 
            title = item))

    return oc

####################################################################################################
# This function uses the related json url to pull a playlist of top videos
@route(PREFIX + '/playlistjson')
def PlaylistJSON(title, url):  

    oc = ObjectContainer(title2 = title)

    json = JSON.ObjectFromURL(url)

    for item in json['videos']:
        url = BASE_URL + item['clickback_url']
        duration = Datetime.MillisecondsFromString(item['duration'])

        oc.add(VideoClipObject(
            url = url,
            title = item['headline'],
            summary = item['description'],
            thumb = Resource.ContentsOfURLWithFallback(url=item['fullsize_url']),
            duration = duration))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    else:
        return oc

