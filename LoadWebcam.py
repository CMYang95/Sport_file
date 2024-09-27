import threading
import queue
import cv2
class LoadWebcam(threading.Thread):
    def __init__(self, source, name=None, skip=0, buffer_size=1):
        print(f"LoadWebcam: {source} ({name})")
        threading.Thread.__init__(self)
        self._skip = skip
        self.name = name
        self._buffer_size = buffer_size
        self._img0s = queue.Queue(maxsize=self._buffer_size)

        self._source = source
        self._cap = cv2.VideoCapture(self._source)
        fourcc = cv2.VideoWriter.fourcc('M', 'J', 'P', 'G')
        self._cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        self._cap.set(cv2.CAP_PROP_FPS, 60)
        #self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        #self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.isLooping = True
        # self.start()

    def run(self):
        while self.isLooping:
            for _ in range(self._skip+1):
                self._cap.grab()
            ret, img0 = self._cap.retrieve()
            assert ret, f"Camera Error {self._source}"
            if self._img0s.full():
                self._img0s.get()
            self._img0s.put(img0)

    def get_origin_shape(self):
        width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)
    def get_FPS(self):
        return int(self._cap.get(cv2.CAP_PROP_FPS))

    def stop(self):
        self.isLooping = False

    def __iter__(self):
        return self

    def __next__(self):
        img0 = self._img0s.get()
        return img0

    def __len__(self):
        return 0