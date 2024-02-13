# https://whitechi73.github.io/OpenShamrock/message/format.html

from enum import IntEnum, Enum
from ..logger import logger


class ChainObj:
    category: str

    def __init__(self, cate: str):
        self.category = cate

    def __repr__(self):
        return '<ChainObj>'

    def data(self) -> dict:
        """
        返回最终编码中 data 的部分

        :return: dict
        """
        return {attr: getattr(self, attr) for attr in self.__annotations__ if hasattr(self, attr)}

    def decode(self) -> dict:
        """
        消息解封装

        :return: 原始消息，用于与后端交互
        """
        return {'type': self.category, 'data': self.data()}

    @classmethod
    def encode(cls, raw: dict) -> 'ChainObj':
        """
        消息封装，若从基类调用，则自动判断类别，否则 raw 应为原始 data 中成员

        :param raw: 原始消息，来自后端实现
        :return: 消息链封装成员
        """
        if cls != ChainObj:
            return cls(**raw)

        if 'type' not in raw and 'data' not in raw:
            logger.warn('Invalid data format')
            return Text('[Invalid]')

        category = raw['type']
        data = raw['data']

        if category == 'text':
            return Text(**data)
        if category == 'at':
            return At(**data)
        if category == 'image':
            return Image(**{
                'file': data['file'],
                'url': data['url'],
                'img_type': data['type'],
                'sub_type': data['subType'],
            })
        if category == 'reply':
            return Reply(data['id'])

        logger.warn(f'Unimplemented ElementType: {category}')
        return Text(f'[UE:{category}]')


class Text(ChainObj):
    text: str

    def __init__(self, text: str):
        super().__init__('text')
        self.text = text

    def __repr__(self):
        return self.text


class Face(ChainObj):
    id: int
    big: bool

    def __init__(self, fid: int, big: bool = None):
        super().__init__('face')
        self.id = fid
        if big:
            self.big = big

    def __repr__(self):
        return f'[Face:{self.id}]'


class At(ChainObj):
    qq: int

    def __init__(self, qq: int):
        super().__init__('at')
        self.qq = qq

    def __repr__(self):
        return f'[At:{self.qq}]'


class Reply(ChainObj):
    id: int

    def __init__(self, mid: int):
        """
        用在 Message 的开头，表示此消息为某消息的回复

        :param id: 回复消息的 Message ID
        """

        super().__init__('reply')
        self.id = mid

    def __repr__(self):
        return f'[Reply:{self.id}]'


class ImageCategory(IntEnum):
    NORMAL = 0  # 普通
    MEME = 1  # 表情包
    POP_PIC = 2  # 热图
    BAT_PIC = 3  # 斗图
    SMT_PIC = 4  # 智图?
    STICKER = 7  # 贴图
    SLF_PIC = 8  # 自拍


class ImageType(Enum):
    SHOW = 'show'
    FLASH = 'flash'
    ORIGINAL = 'original'


class Image(ChainObj):
    file: str
    url: str
    present: str
    sub_type: ImageCategory
    img_type: ImageType

    def __init__(self, file: str, sub_type: ImageCategory = ImageCategory.NORMAL, img_type: ImageType = ImageType.SHOW,
                 url: str = ''):
        """
        图片类型，请以 `Protocol://` 开头

        :param file: `http(s)`, `file`, `base64`
        """
        super().__init__('image')
        self.file = file
        self.url = url
        self.sub_type = sub_type
        self.img_type = img_type

    def data(self) -> dict:
        return {
            'file': self.file,
            'url': self.url,
            'type': self.img_type,
            'subType': self.sub_type,
        }

    def __repr__(self):
        return f'[Image: {self.file}]'


if __name__ == '__main__':
    a = At(114514191)
    b = Text('Hello world!')
    c = Image('url://a.webp')
    print(a.decode())
    print(b.decode())
    print(c.decode())
