import psutil


def get_available_memory():
    total_memory = psutil.virtual_memory()
    print(total_memory.total / (1024 * 1024 * 1024))
    available_memory = total_memory.available / (1024 * 1024)
    return available_memory


if __name__ == "__main__":
    available_memory = get_available_memory()
    print(available_memory)
