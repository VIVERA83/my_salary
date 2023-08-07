USER_CREDENTIALS_TEXT = """\
Здравствуйте {name}, Вас приветствует Сервис Мой Блог\n
Перейдите по ссылки для восстановления пароля: https://opyat-remont.ru/reset-password?{token}
"""
EMAIL_VERIFIER_TEXT = """\
Здравствуйте {name}, Вас приветствует Сервис Сервис Мой Блог\n
Для завершения регистрации пожалуйста подтвердите свой email\n
https://opyat-remont.ru/confirm-email?{token}
"""

TEMPLATE_HTML_TEXT = """\
<tr>
    <td style="width:598px;padding:20px;border:1px solid #d2d2d2;padding-bottom:15px;">
        <table width="598px" border="0" cellspacing="0" cellpadding="0" style="width:598px;">
            <tbody>
            <tr>
                <td valign="top" style="padding-bottom:10px;" dir="">
                    <img
                        src="https://cdn1.ozonusercontent.com/s3/marketing-api/banners/Hn/5S/c200/Hn5S4tZJd3LTWegJVJ0VnROFxd4OiE4N.jpg"
                        border="0" alt="Опять ремонт"></td>
            </tr>
            <tr>
                <td style="height:10px;"></td>
            </tr>
            <tr>
                <td valign="top"
                    style="padding:15px 20px 15px 20px;font:bold 16px Verdana,Arial;background-color:#a50034;color:#fff;">
                    {title}
                </td>
            </tr>
            <tr>
                <td style="height:10px;"></td>
            </tr>
            <tr>
                <td valign="top" style="padding:20px;">
                    <table width="558px" cellpadding="0" cellspacing="0" border="0" style="width:558px;">
                        <tbody>
                        <tr>
                            <td valign="top" style="font-size:12px;font-family:Verdana,Arial;line-height:18px;" dir="">
                                Здравствуйте {name}, Вас приветствует Сервис Сервис Мой Блог<br>
                                {text}
                                <a href="https://opyat-remont.ru/{link}?token={token}">{label}</a>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            </tbody>
        </table>
    </td>
</tr>
"""
