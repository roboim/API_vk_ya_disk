import requests
import os
from pprint import pprint


class VkDownloader:
    """API VK"""
    def __init__(self, token: str, version: str):
        self.token = token
        self.version = version

    def get_photos(self, vk_id_number, count_number="5"):
        """Метод получает информацию о фото в профиле в поле "profile",
        vk_id_number - id пользователя в сети,
        count_number - максимальное количество фото(но не более 10)."""

        if int(count_number) < 0:
            print("Количество фото должно быть положительным")
        elif int(count_number) > 10:
            count_number = "10"
            print("Максимальное количество фото - 10 шт.")

        url = "https://api.vk.com/method/photos.get"
        params = {
            "owner_id": vk_id_number, "access_token": self.token, "v": self.version,
            "album_id": "profile", "rev": "0", "extended": "0",
            "photo_sizes": "0", "count": count_number,
            "extended": "1"
        }
        response = requests.get(url, params=params)
        # pprint(response.json())
        return response.json()

    def get_user_data(self, vk_id_number):
        url = "https://api.vk.com/method/users.get"
        params = {"user_ids": vk_id_number, "access_token": self.token, "v": self.version}
        response = requests.get(url, params=params)
        # pprint(response.json())
        return response.json()


class YaUploader:
    """API Ya.Disk"""
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _get_folders_name(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        params = {"path": "/" + disk_file_path}
        response = requests.get(upload_url, headers=headers, params=params)
        if response.status_code == 200:
            print(f'Папка {disk_file_path} существует на диске ')
            return response.json()
        else:
            return self._make_dir(disk_file_path)

    def _make_dir(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        # print(headers)
        params = {"path": "/" + disk_file_path, "overwrite": "true"}
        response = requests.put(upload_url, headers=headers, params=params)
        # pprint(response.json())
        return response.json()

    def _get_upload_link(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        # pprint(response.json())
        return response.json()

    def upload_file_to_disk(self, filename, disk_file_path):
        f = os.path.basename(filename)
        print(f)
        disk_file_path = "/" + disk_file_path + "/" + f
        print(disk_file_path)
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=open(filename, 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            print("Success")

    def upload(self, file_path, disk_path: str):
        """Метод загружает файлы по списку file_list на яндекс диск"""
        self._get_folders_name(disk_path)
        self.upload_file_to_disk(file_path, path_disk)


def read_tokens(token_file_var) -> dict:
    with open(token_file_var, 'r', encoding='UTF-8') as token_file:
        token_vk_var = token_file.readline()
        token_ya_disk_var = token_file.readline()
    token_vk_var = token_vk_var.rstrip()
    token_ya_disk_var = token_ya_disk_var.rstrip()
    tokens_dict = {}
    tokens_dict.setdefault("vk", token_vk_var)
    tokens_dict.setdefault("ya_disk", token_ya_disk_var)
    return tokens_dict


def download_photo(folder_name, file_name, url):
    get_response = requests.get(url, stream=True)
    with open(file_name, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


if __name__ == '__main__':
    # Получить путь к загружаемому файлу и токенам от пользователя
    path_to_file = r'C:\Users\ILYA\Desktop\PYTHON\_final_API\file.txt'
    path_to_token_file = r'C:\Users\ILYA\Desktop\PYTHON\_final_API\user_data.txt'
    # Файл сохранится в папку NETOLOGY
    path_disk = "NETOLOGY"
    vk_id = "551682139"
    vk_version = "5.131"
    vk_qty_photo = "5"

    tokens = read_tokens(path_to_token_file)
    token_vk = tokens["vk"]

    # Написать в метод
    # Загрузить ссылки на фото с максимальным разрешением указанного профиля по API VK (по умолчанию 5)
    print(f'Загружается не более {vk_qty_photo} фото профиля.')
    user_data_downloader = VkDownloader(token_vk, vk_version)
    vk_data = user_data_downloader.get_photos(vk_id, vk_qty_photo)
    photo_items = vk_data['response']['count']
    print(f'Найдено {photo_items} фото профиля.')
    dict_of_photo_links = {}
    for data in vk_data['response']['items']:
        photo_profile = [data['sizes'][-1]['url'], data['likes']['count'], data['date']]
        if str(data['likes']['count']) not in dict_of_photo_links.keys():
            dict_of_photo_links.setdefault(str(data['likes']['count']), data['sizes'][-1]['url'])
        elif (str(data['likes']['count']) + str(data['date'])) not in dict_of_photo_links.keys():
            dict_of_photo_links.setdefault(str(data['likes']['count']) + str(data['date']), data['sizes'][-1]['url'])
    # pprint(dict_of_photo_links)

    for name,link in dict_of_photo_links.items():
        download_photo(path_disk, name, link)
        print(f'Загружен файл {name}.')

    # token_ya_disk = tokens["ya_disk"]
    # uploader = YaUploader(token_ya_disk)
    # result = uploader.upload(path_to_file, path_disk)
