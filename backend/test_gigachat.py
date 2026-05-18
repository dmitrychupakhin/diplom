from gigachat import GigaChat

giga = GigaChat(
   credentials="MDE5YjQ4MGYtNzg2ZS03OTAzLWI0MmItNTI0YjQzM2Y1MTE2OjVjZjIwNmQ4LTM0NDItNGE3NS04MDE2LTgzZWE4ZjNmZDAzMw==",
   scope="GIGACHAT_API_PERS",
   model="GigaChat",
   verify_ssl_certs=False
)
token = giga.get_token()  # Авторизоваться немедленно
print(f"Токен истекает: {token.expires_at}")