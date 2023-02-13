import os
import base64
import asyncio

import aiofiles


def get_imgs_name(path) -> list[str]:
    try:
        imgs: list[str] = os.listdir(path)
        return imgs

    except FileNotFoundError:
        print('指定目录下未发现图片.')


async def get_bytes_str(img_path: str) -> str:
    file_name = img_path.split('/')[-1].replace('.', '_')

    async with aiofiles.open(f'{img_path}', 'rb') as f:
        content = await f.read()
        b64str = base64.b64encode(content)

        return f'{file_name} = {b64str}\n'


async def writh_py_file(file_name: str, img_data: list[str]) -> None:
    async with aiofiles.open(f'{file_name}.py', 'w+') as f:
        for data in img_data:
            await f.write(data)


async def main(path: str, py_file_name: str):
    img_list = get_imgs_name(path)

    if img_list is not None:
        file_contents = [await get_bytes_str(f'{path}/{img}') for img in img_list]
        await writh_py_file(py_file_name, file_contents)


if __name__ == '__main__':
    while True:
        images_path = input('请输入图片所在的绝对路径(输入"q"退出): ')
        if images_path == 'q':
            print('程序已退出.')
            break
        asyncio.run(main(images_path, 'logo'))
