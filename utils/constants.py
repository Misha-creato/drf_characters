CONFIRM_EMAIL = 'confirm_email'
PASSWORD_RESTORE = 'password_reset'


EMAIL_TYPES = (
    (CONFIRM_EMAIL, 'Подтверждение адреса электронной почты'),
    (PASSWORD_RESTORE, 'Восстановление пароля'),
)

ACCESS_LEVELS = (
    ('0', 'Бесплатный'),
    ('1', 'Базовый'),
    ('2', 'Продвинутый'),
    ('3', 'Премиум'),
)
