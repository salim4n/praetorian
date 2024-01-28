import asyncio
import sys
import threading
import time

import cv2
import numpy as np
from queue import Queue

from onpremise.detector.detrclass import DETRClass
from onpremise.recorder.recordclass import RecordClass

class AsyncWriter:
    """Async wrapper for VideoWriter."""

    def __init__(self, writer):
        self.writer = writer
        self.frames = []

    async def write_frame(self, frame):
        self.frames.append(frame)
        if len(self.frames) >= self.writer.fourcc.size // self.writer.elem_size:
            await self.flush_frames()

    async def flush_frames(self):
        for frame in self.frames:
            self.writer.write(frame)
        self.frames.clear()

class MainClass:
    def __init__(self, detect_interval=5, record_interval=60):
        """Initialization of MainClass."""
        self.detect_interval = detect_interval
        self.record_interval = record_interval

        self.output_folder_detect = "onpremise/screenshot/"
        self.output_folder_record = "onpremise/video_record/"

        self.detector = DETRClass(self.output_folder_detect)
        self.recorder = RecordClass(self.output_folder_record)

    async def run_detector(self, input_queue):
        """Runs person detection and takes screenshots upon detection."""
        self.detector()
        for frame, info in iter(input_queue.get, None):
            detections = self.detector.detect(frame)
            for detection in detections:
                if detection["class"] == "person":
                    await input_queue.put(None)
                    await self.handle_detection(frame, info)
            await asyncio.sleep(self.detect_interval)

    async def handle_detection(self, frame, info):
        """Handles detection and takes a screenshot."""
        snapshot, timestamp = self.detector.take_snapshot(frame)
        print(f"Detected person at {timestamp} ({info})")

    async def run_recorder(self, input_queue):
        """Records short clips of video periodically."""
        max_priority = max(threading.THREAD_PRIORITY_LEVELS)
        record_thread = threading.Thread(
            target=self.high_priority_recording,
            args=(input_queue,),
            name="HighPriorityRecordThread",
            daemon=True,
            prio=max_priority,
        )
        record_thread.start()

        while True:
            await asyncio.sleep(self.record_interval)
            await input_queue.put(None)

        record_thread.join()

    @staticmethod
    def high_priority_recording(input_queue):
        """Performs high-priority recording task."""
        writer = cv2.VideoWriter(
            "output.avi", cv2.VideoWriter_fourcc(*"XVID"), 20.0, (640, 480)
        )
        writer_wrapper = AsyncWriter(writer)

        try:
            while True:
                item = input_queue.get()
                if item is None:
                    asyncio.create_task(writer_wrapper.flush_frames())
                elif isinstance(item, tuple):
                    frame = item[0]
                    asyncio.create_task(writer_wrapper.write_frame(frame))
        finally:
            writer.release()

    async def main(self):
        """Starts detector and recorder tasks."""
        input_queue = Queue()

        detector_task = asyncio.create_task(self.run_detector(input_queue))
        print("Detector task created.")
        recorder_task = asyncio.create_task(self.run_recorder(input_queue))
        print("Recorder task created.")

        done, pending = await asyncio.wait(
            [detector_task, recorder_task], return_when=asyncio.ALL_COMPLETED
        )

        for task in pending:
            task.cancel()

if __name__ == "__main__":
    main = MainClass()
    try:
        asyncio.run(main.main())
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
        sys.exit(0)