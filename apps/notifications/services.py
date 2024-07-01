from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from notifications.models import (
    EmailSettings,
    EmailTemplate,
)
from utils.logger import get_logger


User = get_user_model
logger = get_logger(__name__)


class Email:
    email_host_user = EMAIL_HOST_USER

    def __init__(self, email_type: str, mail_data: dict, recipient: User):
        self.email_type = email_type
        self.mail_data = mail_data
        self.recipient = recipient

    def _get_email_template(self):
        '''
        Получение шаблона письма

        Returns:
            Шаблон письма или None
        '''

        logger.info(
            msg=f'Поиск шаблона для письма {self.email_type}',
        )
        try:
            mail = EmailTemplate.objects.filter(email_type=self.email_type).first()
        except Exception as exc:
            logger.error(
                msg=f'Не удалось найти шаблон для письма {self.email_type} '
                    f'Ошибки: {exc}',
            )
            return None
        return mail

    @property
    def get_send_email_settings(self) -> EmailSettings | None:
        '''
        Получение настроек email

        Returns:
            Объект EmailSettings или None
        '''

        logger.info(
            msg='Получение настроек email',
        )
        try:
            settings = EmailSettings.get_solo()
        except Exception as exc:
            logger.error(
                msg=f'Не удалось получить настройки email'
                    f'Ошибки: {exc}',
            )
            return None
        logger.info(
            msg='Настройки email получены',
        )
        return settings

    def formate_email_text(self) -> (int, dict):
        '''
        Форматирование текста для письма

        Returns:
            Кортеж из статуса и словаря данных
        '''

        logger.info(
            msg=f'Формирование текста для письма {self.email_type} '
                f'с данными {self.mail_data} пользователю {self.recipient}'
        )

        mail = self._get_email_template()
        if mail is None:
            logger.error(
                msg=f'Шаблон письма {self.email_type} не найден',
            )
            return 501, {}

        logger.info(
            msg=f'Шаблон письма {self.email_type} найден',
        )

        subject = mail.subject
        try:
            message = mail.message.format(**self.mail_data)
        except Exception as exc:
            logger.error(
                msg=f'Не удалось сформатировать текст для письма {mail} '
                    f'с данными {self.mail_data} пользователю {self.recipient}'
                    f'Ошибки: {exc}',
            )
            return 500, {}

        logger.info(
            msg=f'Текст для письма {mail} успешно сформирован',
        )
        return 200, {
            'subject': subject,
            'message': message,
        }

    def send(self) -> int:
        '''
        Отправка письма

        Returns:
            Статус
        '''

        email_settings = self.get_send_email_settings
        if not email_settings or not email_settings.send_emails:
            logger.warning(
                msg='Отправка писем отключена',
            )
            return 403

        status_code, email_text = self.formate_email_text()
        if status_code != 200:
            logger.error(
                msg=f'Не удалось сформировать текст для письма {self.email_type} '
                    f'пользователю {self.recipient}'
            )
            return status_code

        subject = email_text["subject"]
        logger.info(
            msg=f'Отправка письма {subject} пользователю {self.recipient}',
        )
        try:
            send_mail(
                subject=subject,
                message=email_text['message'],
                from_email=self.email_host_user,
                recipient_list=[self.recipient],
            )
        except Exception as exc:
            logger.error(
                msg=f'Не удалось отправить письмо {subject} '
                    f'пользователю {self.recipient}'
                    f'Ошибки: {exc}',
            )
            return 500

        logger.info(
            msg=f'Письмо {subject} пользователю {self.recipient} успешно отправлено',
        )
        return 200
