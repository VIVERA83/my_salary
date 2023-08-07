description_create_user = """
Создается временная учетная, которая хранится в кэше. 
Так же на адрес электронной почты пользователя отправляется
письмо для завершения процесса регистрации. 
Запись хранится в течение ограниченного времени. 
Эта запись будет использована, если пользователь подтвердит 
электронный почтовый адрес для завершения регистрации пользователя."""
description_registration_user = """
Окончательная процедура регистрации пользователя в Сервисе, данный метод вызывается после
`create_user`. Подразумевается что в headers Authorization указан токен который
 был отправлен пользователю по электронной почте. В случае успешной проверки 
Создается учетная запись в Базе данных, выдаются токены доступа.
пользователь может пользователя сервисом в пределах своей роли.
"""
description_login_user = """
Авторизация пользователя в системе. После успешной авторизации выдается два токена: \n
1. `access` - токен с коротким сроком жизни, его необходимо добавлять в headers: `Authorization Bearer <token>`\n
2. `refresh` - токен используется для обновления токенов когда протухает `access`токен. Возвращается в ответе в кеке \n
При успешной авторизации будут возращены еще данные пользователя без секретных данных.
"""
description_logout_user = """
Выход из системы, при выходе из системы обнуляются `refresh` токены, а `access` токен заносится 
в блок лист. Для входа нужно будет авторизоваться по новой. 
"""
description_refresh_tokens = """
Обновление `access` и `refresh` токенов, метод обычно вызывается когда протухает `access` токен.
Метод сработает при наличии в куках `refresh` токена и  если соблюдены следующие условия: \n
1. `refresh` токена - не протух
2. если перед вызовом не был вызван метод `logout` - это метод удаляет из системы информацию о токенах. 
"""
