import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import aiohttp
import requests
from requests.exceptions import RequestException
import socket
import time
import random
import string
from concurrent.futures import ThreadPoolExecutor
import os
import tempfile
import subprocess
import psutil


SEMAPHORE_LIMIT = 50  
REQUEST_TIMEOUT = 10  
HTTP_CHECK_URL = "https://github.com/tiwerty"  
SOCKS_CHECK_URL = "https://github.com/tiwerty"  

# Proxy lists
http_links = [
    "https://api.proxyscrape.com/?request=getproxies&proxytype=https&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/saisuiu/Lionkings-Http-Proxys-Proxies/main/cnfree.txt",
    "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
    "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt"
]

socks5_list = [
    "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt",
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
    "https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks5.txt",
    "https://api.openproxylist.xyz/socks5.txt",
    "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5",
    "https://proxyspace.pro/socks5.txt",
    "https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies_anonymous/socks5.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt",
    "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt",
    "https://spys.me/socks.txt",
    "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt"
]


def scrape_proxy_links_https(link):
    try:
        response = requests.get(link, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            proxies = response.text.splitlines()
            return proxies
    except requests.RequestException as e:
        print(f"Ошибка при получении прокси из {link}: {e}")
    return []



def generate_proxies(proxy_type, num_proxies):
    proxies = []
    if proxy_type.lower() == "http":
        links = http_links
    elif proxy_type.lower() == "socks":
        links = socks5_list
    else:
        return []

    num_threads = 100
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        if proxy_type.lower() == "http":
            results = executor.map(scrape_proxy_links_https, links)
        elif proxy_type.lower() == "socks":
            results = executor.map(scrape_proxy_links_socks5, links)
        
        for result in results:
            proxies.extend(result)


    proxies = list(set(proxies))
    random.shuffle(proxies)


    return proxies[:num_proxies]


async def check_http_proxy(proxy, session, semaphore, progress_callback):
    try:
        async with session.get(HTTP_CHECK_URL, proxy=f"http://{proxy}", timeout=REQUEST_TIMEOUT) as response:
            if response.status == 200:
                result = f"{proxy} - Доступен (HTTP)"
            else:
                result = f"{proxy} - Недоступен (HTTP, Статус: {response.status})"
    except asyncio.TimeoutError:
        result = f"{proxy} - Время ожидания истекло (HTTP)"
    except Exception as e:
        result = f"{proxy} - Ошибка (HTTP): {str(e)}"

    progress_callback()
    return result

def check_socks_proxy(proxy, progress_callback):
    try:
        response = requests.get(SOCKS_CHECK_URL, proxies={"http": f"socks5://{proxy}", "https": f"socks5://{proxy}"}, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            result = f"{proxy} - Доступен (SOCKS)"
        else:
            result = f"{proxy} - Недоступен (SOCKS, Статус: {response.status_code})"
    except RequestException as e:
        result = f"{proxy} - Ошибка (SOCKS): {str(e)}"

    progress_callback()
    return result


async def process_all_proxies(proxies, session, semaphore, progress_callback):
    tasks = []
    for proxy in proxies:
        if proxy_var.get().lower() == "http":
            tasks.append(check_http_proxy(proxy, session, semaphore, progress_callback))
        elif proxy_var.get().lower() == "socks":
            tasks.append(asyncio.to_thread(check_socks_proxy, proxy, progress_callback))
    results = await asyncio.gather(*tasks)
    return results


async def check_proxies(proxies, progress_callback):
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

    async with aiohttp.ClientSession() as session:
        total_proxies = len(proxies)
        print(f"Всего прокси: {total_proxies}")

        results = await process_all_proxies(proxies, session, semaphore, progress_callback)

        for result in results:
            listbox.insert(tk.END, result)
            root.update_idletasks()  


def update_progress():
    progress_var.set(progress_var.get() + 1)
    progress['value'] = progress_var.get()
    root.update_idletasks()


async def start_process():
    try:
        num_proxies = int(num_proxies_entry.get())
        if num_proxies <= 0:
            raise ValueError("Количество прокси должно быть положительным числом.")
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))
        return

    proxy_type = proxy_var.get()
    proxies = generate_proxies(proxy_type, num_proxies)
    listbox.delete(0, tk.END)
    listbox.insert(tk.END, "Генерация прокси...")
    listbox.update()


    await asyncio.sleep(2)

    listbox.delete(0, tk.END)
    listbox.insert(tk.END, "Проверка прокси...")
    listbox.update()

    progress_var.set(0)
    progress['value'] = 0
    progress['maximum'] = num_proxies

    await check_proxies(proxies, update_progress)


def copy_to_clipboard(event):
    try:
        selected_index = listbox.curselection()[0]
        selected_item = listbox.get(selected_index)
        root.clipboard_clear()
        root.clipboard_append(selected_item)
        root.update()  
        messagebox.showinfo("Информация", "Выбранный элемент скопирован в буфер обмена.")
    except IndexError:
        messagebox.showwarning("Предупреждение", "Ничего не выбрано.")


root = tk.Tk()
root.title("Proxy Generator and Checker")
root.geometry("600x500")


proxy_var = tk.StringVar(value="HTTP")
http_radio = ttk.Radiobutton(root, text="HTTP", variable=proxy_var, value="HTTP")
http_radio.grid(row=0, column=0, padx=10, pady=10)



num_proxies_label = ttk.Label(root, text="Количество прокси:")
num_proxies_label.grid(row=1, column=0, padx=10, pady=10)
num_proxies_entry = ttk.Entry(root)
num_proxies_entry.grid(row=1, column=1, padx=10, pady=10)
num_proxies_entry.insert(0, "10")  

start_button = ttk.Button(root, text="Сгенерировать и Проверить Прокси", command=lambda: asyncio.run(start_process()))
start_button.grid(row=2, column=0, columnspan=2, pady=10)

progress_var = tk.IntVar()
progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", variable=progress_var)
progress.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

listbox = tk.Listbox(root, width=70, height=15)
listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10)


context_menu = tk.Menu(listbox, tearoff=0)
context_menu.add_command(label="Копировать", command=lambda: copy_to_clipboard(None))


listbox.bind("<Button-3>", lambda event: show_context_menu(event))

def show_context_menu(event):
    try:
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(listbox.nearest(event.y))
        listbox.activate(listbox.nearest(event.y))
        context_menu.post(event.x_root, event.y_root)
    except Exception as e:
        print(f"Ошибка контекстного меню: {e}")


root.mainloop()