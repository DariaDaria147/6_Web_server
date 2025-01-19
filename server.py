# ИСАДИЧЕВА Д.А., ДПИ22-1    

import socket
import os
from datetime import datetime

# Настройки сервера
SERVER_HOST = 'localhost'  # Хост, на котором будет работать сервер
SERVER_PORT = 8080         # Порт для прослушивания входящих соединений
WEB_ROOT = os.path.join(os.getcwd(), "web")  # Директория с веб-контентом


def load_file_content(file_path):
    """
    Загружает содержимое указанного файла, если он существует.
    Если файл не найден, возвращает сообщение об ошибке 404.
    """
    try:
        with open(file_path, 'rb') as file:
            return file.read(), "200 OK"
    except FileNotFoundError:
        return "<h1>404 Not Found</h1>".encode('utf-8'), "404 Not Found"


def process_request(http_request):
    """
    Обрабатывает HTTP-запрос и формирует HTTP-ответ.
    """
    # Разбор HTTP-запроса
    request_lines = http_request.split("\r\n")
    if not request_lines:
        return b"HTTP/1.1 400 Bad Request\r\n\r\n", "400 Bad Request"

    # Извлечение первой строки запроса (метод, путь, версия протокола)
    request_line = request_lines[0]
    method, url_path, _ = request_line.split(" ")

    # Проверка на поддержку метода GET
    if method != "GET":
        return b"HTTP/1.1 405 Method Not Allowed\r\n\r\n", "405 Method Not Allowed"

    # Подстановка index.html для корневого пути
    if url_path == "/":
        url_path = "/index.html"

    # Полный путь к запрашиваемому файлу
    file_full_path = os.path.join(WEB_ROOT, url_path.lstrip("/"))
    file_content, status_code = load_file_content(file_full_path)

    # Формирование HTTP-заголовков
    response_headers = [
        f"HTTP/1.1 {status_code}",
        f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        "Content-Type: text/html; charset=utf-8",
        "Server: SimplePythonHTTPServer",
        f"Content-Length: {len(file_content)}",
        "Connection: close",
        "",
        ""
    ]

    # Формирование полного HTTP-ответа
    response_data = "\r\n".join(response_headers).encode('utf-8') + file_content
    return response_data, status_code


def start_server():
    """
    Запускает HTTP-сервер и обрабатывает входящие соединения.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(5)
        print(f"HTTP-сервер запущен на {SERVER_HOST}:{SERVER_PORT}...")

        while True:
            # Ожидание подключения клиента
            client_connection, client_address = server_socket.accept()
            with client_connection:
                print(f"Подключение от {client_address}")
                request_data = client_connection.recv(8192)

                if not request_data:
                    continue

                # Обработка запроса клиента
                http_request = request_data.decode('utf-8')
                http_response, response_status = process_request(http_request)

                print(f"Статус ответа: {response_status}")
                client_connection.sendall(http_response)


if __name__ == "__main__":
    # Создание директории и примерных файлов, если они отсутствуют
    os.makedirs(WEB_ROOT, exist_ok=True)
    with open(os.path.join(WEB_ROOT, "index.html"), "w", encoding='utf-8') as index_file:
        index_file.write("<h1>Добро пожаловать на сервер Исадичевой Д.А.!</h1>")

    with open(os.path.join(WEB_ROOT, "1.html"), "w", encoding='utf-8') as first_file:
        first_file.write("<h1>Первый файл</h1>")

    with open(os.path.join(WEB_ROOT, "2.html"), "w", encoding='utf-8') as second_file:
        second_file.write("<h1>Второй файл</h1>")

    # Запуск сервера
    start_server()
