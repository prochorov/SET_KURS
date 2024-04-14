import socket
import threading
import os

# Максимальное количество подключений
MAX_CONNECTIONS = 3
# Папка с файлами на сервере
FILES_FOLDER = "files"
# Папка для хранения файлов каждого клиента
CLIENTS_FOLDER = "clients"


def handle_client(client_socket, address):
    try:
        print(f"Подключился клиент {address}")
        # Получаем имя пользователя от клиента
        username = client_socket.recv(1024).decode("utf-8")
        # Создаем папку с именем пользователя, если ее еще нет
        user_folder = os.path.join(CLIENTS_FOLDER, username)
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
                file_path = os.path.join(FILES_FOLDER, filename)
                if os.path.exists(file_path):
                    # Отправляем файл клиенту
                    send_file(client_socket, file_path)
                    print(f"Файл {filename} успешно отправлен клиенту {username}")
                    # Сохраняем файл в папку клиента
                    user_file_path = os.path.join(user_folder, filename)
                    with open(user_file_path, "wb") as f:
                        f.write(data)
                else:
                    client_socket.send("Файл не найден".encode("utf-8"))
            elif command == "list":
                # Отправляем список файлов клиенту
                file_list = "\n".join(os.listdir(FILES_FOLDER))
                client_socket.send(file_list.encode("utf-8"))

    except Exception as e:
        print(f"Ошибка обработки клиента {address}: {e}")
    finally:
        print(f"Клиент {address} отключен")
        client_socket.close()


def send_file(client_socket, file_path):
    # Открываем файл для чтения в бинарном режиме
    with open(file_path, "rb") as f:
        while True:
            # Читаем часть данных из файла
            file_data = f.read(1024)
            if not file_data:
                break
            # Отправляем часть данных клиенту
            client_socket.sendall(file_data)




def start_server():
    # Создаем папку для файлов каждого клиента, если ее еще нет
    if not os.path.exists(CLIENTS_FOLDER):
        os.makedirs(CLIENTS_FOLDER)

    # Создаем TCP сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Привязываем сокет к адресу и порту
    server_socket.bind(('localhost', 8080))
    # Начинаем слушать входящие соединения
    server_socket.listen()

    print("Сервер запущен и слушает подключения...")

    try:
        while True:
            # Принимаем входящее соединение
            client_socket, address = server_socket.accept()

            # Создаем новый поток для обработки клиента
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.start()

    except KeyboardInterrupt:
        print("Сервер остановлен")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()

