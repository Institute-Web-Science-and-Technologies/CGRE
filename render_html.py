from cefpython3 import cefpython as cef
import os
import platform
import sys
from multiprocessing import Process, Queue
from PIL import Image
from typing import Dict, Tuple
import time
import asyncio

# Main function
def main() -> None:

    if not os.path.isdir('./html/'):
        print('You need to create and fill the "html" folder.')
        return

    cef_handle = CefHandle()
    cef_handle.run_cef()


class Mediator(object):
    def __init__(self, browser: cef.PyBrowser):
        # self.loaded: bool = False
        self.viewport_size: Tuple[int, int] = (1024, 768)
        self.browser: cef.PyBrowser = browser
        self.buffer: str = ""
        
        # 
        if not os.path.isdir('./dataset'):
            os.mkdir('./dataset')
        self.out_dir: str = './dataset/'

        self.urls: [str] = [""]
        listOfFile: [str] = os.listdir('./html/')

        for f in listOfFile:
            if f.endswith(".html"):
                f = 'html/' + f
                self.urls.append('file://' + os.path.abspath(f))
        
        del self.urls[0]     
        self.count: int = 0

    def get_current_url(self) -> str:
        return self.urls[self.count]

    def next_url(self) -> None:
        # print('count: ' + str(self.count))
        if self.count < len(self.urls):
            self.browser.StopLoad()
            print('RENDER:  "' + self.urls[self.count] + '"')
            self.browser.LoadUrl(self.urls[self.count])
            self.browser.WasResized()

    # Compose viewport for display (collect screen pixels, blacken censored term)
    def save_image(self) -> None:
        #await self.buffer_event.wait()
        #self.buffer_event.clear()
        buffer_string = self.browser.GetUserData("OnPaint.buffer_string")
        if not buffer_string:
            raise Exception("buffer_string is empty, OnPaint never called?")
        image = Image.frombytes('RGBA', self.viewport_size, buffer_string,
                            'raw', 'RGBA', 0, 1)
        # Save image
        image.save(self.out_dir + str(self.count) + '.png', 'PNG')
        print('SAVE:    "' + str(self.count) + '.png"')
        self.count += 1



class CefHandle(object):
    #def __init__(self):

    def run_cef(self) -> None:

        # Setup CEF
        sys.excepthook = cef.ExceptHook  # to shutdown all CEF processes on error
        settings: Dict[str, bool] = { 
            'windowless_rendering_enabled': True,  # offscreen-rendering
        }
        switches: Dict[str, str] = {
            'disable-gpu': '',
            'disable-gpu-compositing': '',
            'enable-begin-frame-scheduling': '',
            'disable-surfaces': '',
            'disable-smooth-scrolling': '',
        }
        browser_settings: Dict[str, int] = {
            'windowless_frame_rate': 15,
        }
        cef.Initialize(settings=settings, switches=switches)
        print()
        self.create_browser(browser_settings)

        # Enter loop
        cef.MessageLoop()

        # Cleanup
        cef.Shutdown()

    # Create a browser
    def create_browser(self, settings):

        parent_window_handle = 0
        window_info = cef.WindowInfo()
        window_info.SetAsOffscreen(parent_window_handle)
        browser: cef.PyBrowser = cef.CreateBrowserSync(window_info=window_info, settings=settings, url="")
        
        mediator = Mediator(browser)
        mediator.next_url()

        #browser.SetClientHandler(LoadHandler(mediator))
        browser.SetClientHandler(RenderHandler(mediator))

        browser.SendFocusEvent(True)
        browser.WasResized()
        return browser

    # Exit the application
    def exit_app(self, browser: cef.PyBrowser) -> None:
        browser.CloseBrowser()
        cef.QuitMessageLoop()

# Handle the rendering
class RenderHandler(object):
    def __init__(self, mediator: Mediator):
        self.mediator = mediator

    def GetViewRect(self, rect_out: [int], **_) -> bool:
        rect_out.extend([0, 0, self.mediator.viewport_size[0], self.mediator.viewport_size[1]])
        return True

    def OnPaint(self, browser: cef.PyBrowser, element_type, paint_buffer, **_) -> None:
        if element_type == cef.PET_VIEW:
            self.mediator.loaded = False
            # print('OnPaint')
            # retrieve the image bytes
            buffer_string: str = paint_buffer.GetBytes(mode='rgba', origin='top-left')
            # initiate the image creation
            browser.SetUserData("OnPaint.buffer_string", buffer_string)
            self.mediator.save_image()
            self.mediator.next_url()

# class LoadHandler(object):
#     def __init__(self, mediator: Mediator):
#         self.mediator = mediator
# 
#     def OnLoadingStateChange(self, browser: cef.PyBrowser, is_loading, **_):
#         if not is_loading:
#             self.mediator.loaded = True
#             print('OnLoad')

if __name__ == '__main__':
    main()