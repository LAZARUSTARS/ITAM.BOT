from dataclasses import dataclass

@dataclass
class ButtonLinks:
    """Дополнительные ссылки клуба
        Attributes
        ----------
        buttton_text : str
            Текст кнопки
        link : str
            Ссылка
        """
    button_text: str
    link: str
@dataclass
class ClubInfo:
    """Информация о клубе
        Attributes
        ----------
        key_name : str
            Название клуба
        description : str
            Описание клуба
        link : str
            Ссылка на чат клуба
        additional_links: ButtonLinks
            Дополнительные ссылки клуба
        """
    key_name: str
    description: str
    link: str
    additional_links: list[ButtonLinks]
