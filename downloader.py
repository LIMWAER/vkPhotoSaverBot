from urllib import request
import os
import asyncio


def fire_and_forget(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, *kwargs)

    return wrapped


@fire_and_forget
def downloader(album_list_id, path=f'{os.environ["HOMEPATH"]}\\Downloads'):
    os.mkdir(f'{path}\\Albums')
    for album in album_list_id:
        album_path = f'{path}\\Albums\\{album["id"]}'
        os.mkdir(album_path)
        for photo in album['photos']:
            for key in photo:
                url = photo[key][0]['url']
                split_name = url[::-1].split("/")
                photo_name = split_name[0][::-1].split("?")[0]
                resource = request.urlopen(url)
                out = open(f'{album_path}\\{photo_name}', 'wb')
                out.write(resource.read())
                out.close()
