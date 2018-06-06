import kivy

kivy.require('1.10.0')

import asyncio
import threading

from kivy.app import App
from kivy.clock import mainthread
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

KV = '''\
<NewLayout>:
    orientation: 'vertical'
    padding: 100
    Button:
        id: even
        text: 'Even Numbers'
        on_press: app.create_new_request('even')
    Button:
        id: odd
        text: 'Odd Numbers'
        on_press: app.create_new_request('odd')
    BoxLayout:
        Label:
            text:'Even numbers start here'
            id: even_text
        Label:
            text:' Odd numbers start here'
            id: odd_text
'''


class NewLayout(BoxLayout):
    pass


class EventLoopWorker(EventDispatcher):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loop = None
        self.state = None
        self.request = None
        self.is_running_odd_coroutine = False
        self.is_running_even_coroutine = False
        self.create_asyncio_thread = self._create_new_thread()
        print(threading.current_thread().ident)  # 'This print is to see the main thread id'

    def _create_new_thread(self):
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print(self._thread.ident)

    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def create_new_task(self, request):
        self.request = request
        self.system_state()

        if self.state == True:
            if self.request == 'odd':
                asyncio.run_coroutine_threadsafe(coro = self.odd(), loop= self.loop)
            else:
                asyncio.run_coroutine_threadsafe(coro = self.even(), loop= self.loop)

    def system_state(self):

        if self.is_running_even_coroutine == True and self.request == 'even':
            print('Even numbers counting is already running')
            self.state = False
            return

        elif self.is_running_odd_coroutine == True and self.request == 'odd':
            print('Odd numbers counting is already running')
            self.state = False
            return

        else:
            if self.request == 'even':
                self.is_running_even_coroutine = True
                self.state = True
                print('Even numbers counting will start')
            else:
                print('Odd numbers counting will start')
                self.is_running_odd_coroutine = True
                self.state = True



    async def odd(self):
        '''Coroutine to create a forever loop to print odd numbers'''
        i = 1
        while True:
            @mainthread
            def kivy_update_status(number):
                update_label = App.get_running_app().root.ids.odd_text
                update_label.text = str(number)

            kivy_update_status(i)
            i += 2
            await asyncio.sleep(1)

    async def even(self):
        '''Coroutine to create a forever loop to print even numbers'''
        i = 0
        while True:
            @mainthread
            def kivy_update_status(number):
                update_label = App.get_running_app().root.ids.even_text
                update_label.text = str(number)

            kivy_update_status(i)
            i += 2
            await asyncio.sleep(1)


class Even_OddApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.is_running_odd_coroutine = False
        self.is_running_even_coroutine = False
        self.worker = self.event_loop_worker = EventLoopWorker()


    def build(self):
        return NewLayout()

    def create_new_request(self, request):
        print('I got a request')
        self.worker.create_new_task(request)



if __name__ == '__main__':
    Builder.load_string(KV)
    Even_OddApp().run()