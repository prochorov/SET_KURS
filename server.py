import socket
import threading
import os

# Максимальное количество подключений
MAX_CONNECTIONS = 3
# Словарь для хранения подключенных клиентов
connected_clients = {}
# Папка с файлами на сервере
FILES_FOLDER = "files"


def handle_client(client_socket, address):
    try:
        print(f"Подключился клиент {address}")
        # Получаем имя пользователя от клиента
        username = client_socket.recv(1024).decode("utf-8")
        # Аутентификация пользователя
        if username not in connected_clients.values():
            connected_clients[address] = username
            print(f"Пользователь {username} успешно аутентифицирован")
        else:
            print(f"Пользователь {username} уже подключен")

        # Создаем папку с именем пользователя, если ее еще нет
        user_folder = os.path.join(FILES_FOLDER, username)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        while True:
            # Принимаем команду от клиента
            command = client_socket.recv(1024).decode("utf-8")
            if not command:
                break
            if command == "download":
                # Получаем имя файла от клиента
                filename = client_socket.recv(1024).decode("utf-8")
                # Проверяем, существует ли файл
                file_path = os.path.join(FILES_FOLDER, username, filename)
                if os.path.exists(file_path):
                    # Отправляем файл клиенту
                    with open(file_path, "rb") as f:
                        data = f.read(1024)
                        while data:
                            client_socket.send(data)
                            data = f.read(1024)
                    print(f"Файл {filename} успешно отправлен клиенту {username}")
                else:
                    client_socket.send("Файл не найден".encode("utf-8"))
            elif command == "list":
                # Отправляем список файлов клиенту
                file_list = "\n".join(os.listdir(user_folder))
                client_socket.send(file_list.encode("utf-8"))

    except Exception as e:
        print(f"Ошибка обработки клиента {address}: {e}")
    finally:
        # Удаление клиента из списка подключенных клиентов
        del connected_clients[address]
        print(f"Клиент {address} отключен")
        client_socket.close()


def start_server():
    # Создаем папку с файлами, если ее еще нет
    if not os.path.exists(FILES_FOLDER):
        os.makedirs(FILES_FOLDER)

    # Создаем TCP сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Привязываем сокет к адресу и порту
    server_socket.bind(('localhost', 5555))
    # Начинаем слушать входящие соединения
    server_socket.listen()

    print("Сервер запущен и слушает подключения...")

    try:
        while True:
            # Принимаем входящее соединение
            client_socket, address = server_socket.accept()

            # Проверка на максимальное количество подключений
            if len(connected_clients) >= MAX_CONNECTIONS:
                print(f"Превышено максимальное количество подключений, отклоняем запрос от {address}")
                client_socket.send("Ошибка: превышено максимальное количество подключений".encode("utf-8"))
                client_socket.close()
                continue

            # Создаем новый поток для обработки клиента
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.start()

    except KeyboardInterrupt:
        print("Сервер остановлен")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
