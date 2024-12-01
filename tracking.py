import threading
from pynput import keyboard
from rx import create
from rx.core import Observer

class KeyboardEventTracker:
    def __init__(self):
        self.listeners = [] #список слушателей
        self.stop_event = threading.Event()  #событие для остановки трекера
        self.ctrl_pressed = False  #флаг для отслеживания состояния клавиши Ctrl

    #метод для запуска трекера
    def start(self):
        #обработчик события нажатия клавиши
        def on_press(key):
            try:
                #генерация исключений при нажатии клавиши Tab
                if key == keyboard.Key.tab:
                    raise Exception("Нажата клавиша Tab")
                #установка флага, если нажата клавиша Ctrl
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    self.ctrl_pressed = True
                event = f"Нажата клавиша: {key}"
            except AttributeError:
                event = f"Нажата специальная клавиша: {key}"
            except Exception as e:
                #уведомление подписчиков об ошибке
                self.notify_error_listeners(e)
                return
            #уведомление подписчиков о событии
            self.notify_listeners(event)

        #обработчик события отпускания клавиши
        def on_release(key):
            #остановка трекера при нажатии Ctrl+Esc
            if key == keyboard.Key.esc and self.ctrl_pressed:
                self.stop_event.set()
                return False
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False
            event = f"Клавиша отпущена: {key}"
            #уведомление подписчиков о событии
            self.notify_listeners(event)

        #запуск слушателя клавиатуры в отдельном потоке
        def run():
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()

        threading.Thread(target=run, daemon=True).start()  #запуск поток

    #метод для уведомления всех подписчиков о событии
    def notify_listeners(self, event):
        for listener in self.listeners:
            listener.on_next(event)

    #метод для уведомления всех подписчиков об ошибке
    def notify_error_listeners(self, error):
        for listener in self.listeners:
            listener.on_error(error)

    #метод для добавления подписчика
    def subscribe(self, listener):
        self.listeners.append(listener)

    #метод для остановки трекера
    def stop(self):
        self.stop_event.set()

class FileObserver(Observer):
    def __init__(self, filename):
        self.filename = filename  #имя файла для записи событий
        #запись сообщения о начале трекинга при создании файла
        with open(self.filename, 'a') as f:
            f.write("Трекинг начат.\n")
            
    #метод для обработки нового события
    def on_next(self, value):
        with open(self.filename, 'a') as f:
            f.write(f"{value}\n")  

    #метод для обработки ошибки
    def on_error(self, error):
        with open(self.filename, 'a') as f:
            f.write(f"Ошибка: {error}\n")  

    #метод для обработки завершения работы
    def on_completed(self):
        with open(self.filename, 'a') as f:
            f.write("Трекинг завершен.\n")  

def main():
    tracker = KeyboardEventTracker()  #создание экземпляра трекера
    observer = FileObserver("keyboard_tracking.txt") #создание наблюдателя  
    tracker.subscribe(observer)  #подпись наблюдателя на события трекера

    tracker.start()  #запуск трекера

    try:
        while not tracker.stop_event.is_set():  #ожидание завершения работы
            pass
    except KeyboardInterrupt:
        tracker.stop()  #остановка трекера при прерывании
    finally:
        observer.on_completed()  #уведомление о завершении

#запуск главной функции программы
if __name__ == "__main__":
    main()
