"""TTS-Wrapper: Tolk (NVDA/JAWS) -> SAPI -> print Fallback"""
import ctypes, os, queue, threading, time

try:
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

class Speech:
    def __init__(self):
        self.tolk = None
        self.tolk_ok = False
        self.sapi = None
        self._q = queue.Queue()
        self._stop = False
        self._ie = threading.Event()
        self._last = ""
        self._last_t = 0.0

        # --- Tolk ---
        try:
            dll = os.path.join(os.path.dirname(__file__), "Tolk.dll")
            if os.path.exists(dll):
                t = ctypes.windll.LoadLibrary(dll)
                t.Tolk_Load.restype = ctypes.c_bool
                t.Tolk_IsLoaded.restype = ctypes.c_bool
                t.Tolk_Output.argtypes = [ctypes.c_wchar_p, ctypes.c_bool]
                t.Tolk_Output.restype = ctypes.c_bool
                t.Tolk_IsSpeaking.restype = ctypes.c_bool
                if hasattr(t, 'Tolk_Silence'):
                    t.Tolk_Silence.restype = ctypes.c_bool
                if hasattr(t, 'Tolk_TrySAPI'):
                    t.Tolk_TrySAPI.argtypes = [ctypes.c_bool]
                    t.Tolk_TrySAPI.restype = ctypes.c_bool
                if t.Tolk_Load():
                    self.tolk_ok = t.Tolk_IsLoaded()
                    if self.tolk_ok:
                        if hasattr(t, 'Tolk_TrySAPI'):
                            t.Tolk_TrySAPI(True)
                        self.tolk = t
        except Exception as e:
            print(f"Tolk: {e}")

        # --- SAPI Fallback ---
        if not self.tolk_ok and HAS_WIN32:
            try:
                self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
            except Exception as e:
                print(f"SAPI: {e}")

        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while not self._stop:
            try:
                text, intr = self._q.get(timeout=0.1)
                if self.tolk_ok and self.tolk:
                    if intr and hasattr(self.tolk, 'Tolk_Silence'):
                        self.tolk.Tolk_Silence()
                    else:
                        t0 = time.time()
                        while self.tolk.Tolk_IsSpeaking() and not self._ie.is_set():
                            if self._stop or time.time() - t0 > 5: break
                            time.sleep(0.01)
                    self._ie.clear()
                    self.tolk.Tolk_Output(text, intr)
                    time.sleep(0.05)
                elif self.sapi:
                    if intr:
                        self.sapi.Speak("", 3)
                    self.sapi.Speak(text, 1)
                    if not intr:
                        el = 0
                        while el < 10000 and not self._ie.is_set():
                            if self.sapi.WaitUntilDone(100): break
                            el += 100
                    self._ie.clear()
                else:
                    print(f"[TTS] {text}")
                self._q.task_done()
            except Exception as e:
                if "Empty" not in str(type(e)):
                    print(f"Speech worker: {e}")

    def say(self, text, interrupt=True):
        if not text: return
        now = time.time()
        if self._last == text and now - self._last_t < 0.3: return
        if interrupt:
            self._ie.set()
            while not self._q.empty():
                try:
                    self._q.get_nowait(); self._q.task_done()
                except: break
        self._last = text
        self._last_t = now
        self._q.put((str(text), interrupt))

    def stop(self):
        self._stop = True
        if self.tolk_ok and self.tolk:
            try: self.tolk.Tolk_Unload()
            except: pass
