from datetime import datetime
from tqdm import tqdm
import requests
import re
import sys
import json

# To check internet connection
def is_connected(url='http://www.google.com/', timeout=5):
    try:
        req = requests.get(url, timeout=timeout)
        req.raise_for_status()
        print("You're connected to internet\n")
        return True
    except requests.HTTPError as e:
        print("Error occured while checking internet connection, status code {0}.".format(e.response.status_code))
    except requests.ConnectionError:
        print("No internet available")
    return False

# To download image or video
def download_image_or_video():
    url = input("Please enter instagram media URL: ")
    # url = "https://www.instagram.com/p/B8ircBvH7Yw/?shared_with=chrome"
    x = re.match(r'^(https:)[\/][\/]www.([^\/]+[.])*instagram.com[\/](p\/)?\w+[\/]?', url)
    url = x.group()
    # print(url)

    if x:
        try:
            if url[-1] != "/":
                url += "/?__a=1"
            else:
                url += "?__a=1"
            # print(url)
            req = requests.get(url)

            json_src = json.loads(req.content.decode('utf-8'))
            # print(json_src)

            media_type = json_src["graphql"]["shortcode_media"]["__typename"]
            # print(media_type)

            if media_type == "GraphImage":
                print("\nDownloading the Image...")
                image_url = json_src["graphql"]["shortcode_media"]["display_url"]
                # print(image_url)

                download_media_using_url(media_type, image_url)

                print("Image downloaded successfully")

            elif media_type == "GraphVideo":
                print("\nDownloading the Video...")
                video_url = json_src["graphql"]["shortcode_media"]["video_url"]
                # print(video_url)

                download_media_using_url(media_type, video_url)

                print("Video downloaded successfully")

        except AttributeError as e:
            print("Invalid URL")
            print(e)

    else:
        print("Please enter the URL of Instagram Image or Video!")


def download_profile_picture():
    url = input("Please enter the URL of the profile: ")
    # url = "https://www.instagram.com/the.awkward.alpha/?hl=en"
    x = re.match(r'https?:\/\/(www\.)?instagram\.com\/([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)[\/]?(\?hl=[a-z-]{2,5})?', url)
    url = x.group()
    # print(url)

    if x:
        if "?hl" in url:
            url = re.sub('\\?hl=[a-z-]{2,5}', '?__a=1', url)
        elif url[-1] != "/":
            url += "/?__a=1"
        else:
            url += "?__a=1"

        # print(url)
        req = requests.get(url)
        json_src = json.loads(req.content.decode('utf-8'))

        media_type = "ProfilePicture" if "profilePage" in json_src["logging_page_id"] else None

        if media_type:
            pp_url = json_src["graphql"]["user"]["profile_pic_url_hd"]
            download_media_using_url(media_type, pp_url)

            print("Profile Picture downloaded successfully")


    else:
        print("Please enter the URL of Instagram profile!")

def download_media_using_url(media_type, url):
    try:
        file_request = requests.get(url, stream=True)
        file_size = int(file_request.headers['Content-Length'])
        # print(file_size)
        block_size = 1024

        if media_type == "GraphImage":
            filename = "Image_{}".format(datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S'))
        elif media_type == "GraphVideo":
            filename = "Video_{}".format(datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S'))
        elif media_type == "ProfilePicture":
            filename = "ProfilePicture_{}".format(datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S'))

        t = tqdm(total=file_size, unit='B', unit_scale=True, desc=filename, ascii=True)

        if media_type in ["GraphImage", "ProfilePicture"]:
            with open(filename + '.jpg', 'wb') as f:
                for data in file_request.iter_content(block_size):
                    t.update(len(data))
                    f.write(data)
            t.close()
        elif media_type == "GraphVideo":
            with open(filename + '.mp4', 'wb') as f:
                for data in file_request.iter_content(block_size):
                    t.update(len(data))
                    f.write(data)
            t.close()

        
    except Exception:
        print("Ooops! got an roadblock while downloading!")


if is_connected():
    try:
        while True:
            a = "\n\n\nPress 1 to download an instagram image or video.\nPress 2 to download an instagram profile picture.\nPress 0 to exit."
            print(a)
            option = int(input("Enter your choice : "))

            # option = 2
            if option == 1:
                download_image_or_video()
            elif option == 2:
                download_profile_picture()
            elif option == 0:
                sys.exit()
            else:
                sys.exit()
    except KeyboardInterrupt:
        print("Operation interrupted")

            
