from __future__ import annotations
import queue
import threading
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from config import TelemetrySample, ZONE_COORDINATES
try:
    import serial
except ImportError:
    serial=None

class SerialCoordinateSource:
    def __init__(self, port: str="/dev/cu.usbmodem1203", baud: int=115200):
        self.port=port
        self.baud=baud
        self._serial=serial.Serial(port=port, baudrate=baud, timeout=1)
        self._stop_event=threading.Event()
        self._queue: queue.Queue[TelemetrySample]=queue.Queue(maxsize=1)
        self._thread=threading.Thread(target=self._render_loop, daemon=True)
        self._thread.start()
        
    def close(self) -> None:
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=1)
        if self._serial.is_open:
            self._serial.close()
            
    def _render_loop(self) -> None:
        self._serial.reset_input_buffer()
        while not self._stop_event.is_set():
            try:
                if self._serial.in_waiting>0:
                    raw_line=self._serial.readline().decode('utf-8', errors="ignore").strip()
                    if not raw_line:
                        continue
                    sample=self.parse_line(raw_line)
                    if sample:
                        if self._queue.full():
                            try:
                                self._queue.get_nowait()
                            except queue.Empty:
                                pass
                        self._queue.put(sample)
            except Exception:
                continue
    
    @staticmethod
    def parse_line(line: str) -> Optional[TelemetrySample]:
        try:
            clean=line.replace('[', '').replace(']','')
            parts=[int(x.strip()) for x in clean.split(',')]
            if len(parts)!=4:
                return None
            rssi_vals=parts[0:3]
            zone_id=parts[3]
            coords=ZONE_COORDINATES.get(zone_id, ZONE_COORDINATES[11])
            
            return TelemetrySample(coordinates=coords, rssi=rssi_vals, zone=zone_id, timestamp=datetime.utcnow())
        except (ValueError, IndexError):
            return None
    
    def get_latest_sample(self) -> Optional[TelemetrySample]:
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None