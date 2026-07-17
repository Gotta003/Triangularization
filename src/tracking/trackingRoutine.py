import math
from src.serial.serialRoutine import SerialCoordinateSource
from config import Coordinates, TelemetrySample
from typing import Optional
from dataclasses import replace

class TrackingService:
    def __init__(self, source: SerialCoordinateSource | None=None):
        self.source=source
        self.stationary_ticks=0
        self.last_coordinates: Coordinates | None=None
        self.zone_history=[]
        self.filter_window=3
        
    def get_latest_data(self) -> Optional[TelemetrySample]:
        if self.source:
            sample = self.source.get_latest_sample()
            if sample:
                self.zone_history.append(sample.zone)
                if len(self.zone_history) > self.filter_window:
                    self.zone_history.pop(0)
                
                filtered_zone = max(set(self.zone_history), key=self.zone_history.count)
                
                # Recuperiamo le coordinate associate
                from config import ZONE_COORDINATES
                new_coords = ZONE_COORDINATES.get(filtered_zone, None)
                
                # CREIAMO UN NUOVO SAMPLE MODIFICATO (Risolve il problema del frozen=True)
                sample = replace(sample, coordinates=new_coords)
                
                # Gestione di sicurezza per le coordinate
                if sample.coordinates is not None:
                    self._update_stationarity(sample.coordinates)
                else:
                    self.stationary_ticks = 0
                    self.last_coordinates = None
                
                return sample
            else: 
                return None
        return None
    
    def _update_stationarity(self, current: Coordinates) -> None:
        if self.last_coordinates and self.distance(current, self.last_coordinates)<0.5:
            self.stationary_ticks+=1
        else:
            self.stationary_ticks=0
        self.last_coordinates=current
        
    def calculate_risk_score(self, in_triangle: bool) -> int:
        base_score=25 if in_triangle else 10
        movement_penalty=min(self.stationary_ticks*20, 80)
        return min(100, base_score+movement_penalty)
    
    @staticmethod
    def is_in_triangle(p: Coordinates, a: Coordinates, b: Coordinates, c: Coordinates) -> bool:
        denominator=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
        if denominator==0:
            return False
        alpha=((b.y-c.y)*(p.x-c.x)+(c.x-b.x)*(p.y-c.y))/denominator
        beta=((c.y-a.y)*(p.x-c.x)+(a.x-c.x)*(p.y-c.y))/denominator
        gamma=1.0-alpha-beta
        return 0<=alpha<=1 and 0<=beta<=1 and 0<=gamma<=1
    
    @staticmethod
    def distance(a: Coordinates, b: Coordinates) -> float:
        return math.hypot(b.x-a.x, b.y-a.y)