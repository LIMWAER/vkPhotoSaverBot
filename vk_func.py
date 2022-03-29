from itertools import count

from config import VK_API_VER
from load_all import api


async def get_group_id(group_name: str):
    group_info = api('groups.getById', group_id=group_name, v=VK_API_VER)
    group_list = await group_info()
    group_id = group_list[0]['id']
    return -group_id


async def get_album_ids(group_id: int):
    album_list_ids = []
    albums_info = api('photos.getAlbums', owner_id=group_id, v=VK_API_VER)
    all_albums_dict = await albums_info()
    all_albums_list = all_albums_dict['items']
    for album in all_albums_list:
        album_list_ids.append(dict([('id', album['id'])]))
    return album_list_ids


async def get_photos(group_id: int, album_list_ids: list):
    for album_dict in album_list_ids:
        photo_list = []
        for offset in count(0, 50):
            get_photos_info = api('photos.get', owner_id=group_id, album_id=album_dict['id'],
                                  offset=offset, v=VK_API_VER)
            photo_info = await get_photos_info()
            if not photo_info['items']:
                break
            for photo_num, item in zip(count(offset, 1), photo_info['items']):
                photo_list.append(dict([(photo_num, item['sizes'])]))
        album_dict['photos'] = photo_list
    return album_list_ids


async def complete_albums(album_list_ids: list):
    types = ['s', 'm', 'x', 'o', 'p', 'q', 'r', 'y', 'z', 'w']
    for id in album_list_ids:
        for photo in id['photos']:
            for typ in types[::-1]:
                for key in photo:
                    for size in photo[key]:
                        if size.get('type') == typ:
                            photo.clear()
                            photo[key] = [size]
                            break
    return album_list_ids
