import os
import requests
import json
import time
from tqdm import tqdm


def full_path(folder_name, file_name):
    fpath = os.path.join(os.getcwd(), folder_name, file_name)
    return fpath


def get_token(file_name):
    path = full_path('files', file_name)
    with open(path, encoding='utf-8') as file:
        token = file.readline()
    return token


def get_id():
    path = full_path('files', 'id.txt')
    with open(path, encoding='utf-8') as file:
        u_id = file.readline()
    return u_id


class VK:
    def __init__(self, vk_access_token, vk_user_id, version='5.131'):
        self.token = vk_access_token
        self.id = vk_user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()


def get_albums_data():
    api = requests.get("https://api.vk.com/method/photos.getAlbums", params={
        'owner_id': vk.id,
        'access_token': vk.token,
        'need_system': 1,
        'v': vk.version
    })
    data = json.loads(api.text)
    count = data['response']['count']
    print(f'Найдено альбомов: {count}')
    i = 1
    albums_data = {}
    for album in data['response']['items']:
        album_id = album['id']
        album_size = album['size']
        album_title = album['title']
        print(f'{i}. "{album_title}" - {album_size} фото в альбоме.')
        albums_data[i] = {'album_id': album_id, 'album_size': album_size, 'album_title': album_title}
        i += 1
    return albums_data


def get_foto_data(album_id='wall', offset=0, count=50):
    api = requests.get("https://api.vk.com/method/photos.get", params={
        'owner_id': vk.id,
        'access_token': vk.token,
        'album_id': album_id,
        'offset': offset,
        'count': count,
        'photo_sizes': 1,
        'extended': 1,
        'v': vk.version
    })
    data = json.loads(api.text)
    i = 1
    photo_data = {}
    for photo in data['response']['items']:
        photo_id = photo['id']
        photo_url = ''
        photo_size = ''
        photo_likes = photo['likes']['count']
        for size in photo['sizes']:
            if size['type'] == 'w':
                photo_url = size['url']
                photo_size = size['type']
            elif size['type'] == 'z':
                photo_url = size['url']
                photo_size = size['type']
        photo_data[i] = {'photo_id': photo_id, 'photo_url': photo_url, 'photo_size': photo_size, 'photo_likes': photo_likes }
        i += 1
    return photo_data


def id_rw():
    new_id = input('Введите ваш VK_id: ')
    path = full_path('files', 'id.txt')
    with open(path, 'w', encoding='utf-8') as file:
        file.write(new_id)


def transfer_ya_disk(album, photo):
    ya_token = get_token('ya_token.txt')
    img_dir = input('Введите название папки на Яндекс.Диске: ')
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'OAuth {ya_token}',
    }
    requests.put(f'{url}?path={img_dir}', headers=headers)
    files_transfer = []
    if album == 0:
        for num in clear_album_data.keys():
            clear_photo_data = get_foto_data(clear_album_data[num]['album_id'])
            for i in tqdm(clear_photo_data.keys()):
                file_transfer = {'file_name': f'{clear_photo_data[i]["photo_likes"]}_{clear_photo_data[i]["photo_id"]}.jpg',
                                 'size': f'{clear_photo_data[i]["photo_size"]}'}
                files_transfer.append(file_transfer)
                time.sleep(0.1)
                file_path = f'{img_dir}/{clear_photo_data[i]["photo_likes"]}_{clear_photo_data[i]["photo_id"]}.jpg'
                res = requests.get(f'{url}/upload?path={file_path}&overwrite=True', headers=headers).json()
                file = requests.get(clear_photo_data[i]["photo_url"])
                try:
                    requests.put(res['href'], files={'file': file.content})
                except KeyError:
                    print(res)
    else:
        clear_photo_data = get_foto_data(clear_album_data[album]['album_id'])
        for i in tqdm(clear_photo_data.keys()):
            if i <= photo:
                file_transfer = {'file_name': f'{clear_photo_data[i]["photo_likes"]}_{clear_photo_data[i]["photo_id"]}.jpg',
                                 'size': f'{clear_photo_data[i]["photo_size"]}'}
                files_transfer.append(file_transfer)
                time.sleep(0.1)
                file_path = f'{img_dir}/{clear_photo_data[i]["photo_likes"]}_{clear_photo_data[i]["photo_id"]}.jpg'
                res = requests.get(f'{url}/upload?path={file_path}&overwrite=True', headers=headers).json()
                file = requests.get(clear_photo_data[i]["photo_url"])
                try:
                    requests.put(res['href'], files={'file': file.content})
                except KeyError:
                    print(res)
            else:
                break
    return files_transfer

def photo_data_file(done_files_list):
    data = done_files_list
    path = full_path('files', 'photo_transferred.json')
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

id_rw()
access_token = get_token('vk_token.txt')
user_id = get_id()
vk = VK(access_token, user_id)
clear_album_data = get_albums_data()

album_num = input('Введите номер альбома ("0" если хотите скопировать все альбомы): ')
flag = True
photo_count = 5
if album_num == '0':
    print('Качаем все изображения!')
    album_num = int(album_num)
    photo_count = -1
elif album_num in str(clear_album_data.keys()):
    album_num = int(album_num)
    photo_count_rw = input('Введите количество фото ("all" - для копирования всех фото): ')
    if photo_count_rw == 'all':
        photo_count = -1
    elif photo_count_rw.isnumeric():
        photo_count = int(photo_count_rw)
    else:
        print('Максимум 5 фото.')
else:
    print('Неверная команда!')
    flag = False

if flag:
    files_done = transfer_ya_disk(album_num, photo_count)
    photo_data_file(files_done)
