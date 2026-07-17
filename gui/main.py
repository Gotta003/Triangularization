import math
import random
import time
import tkinter as tk
from src.tracking.trackingRoutine import TrackingService
from config import WORLD_MIN, WORLD_MAX, BUOYS, Coordinates, SERIAL_PORT, BAUD_RATE
from src.serial.receiver import get_available_ports
from src.serial.serialRoutine import SerialCoordinateSource

class PosidoniaTrackerApp:
    def __init__(self, root, service: TrackingService):
        self.root = root
        self.service=service  
        self.root.title("Teti - Real-Time Boat Tracking")
        self.root.minsize(1100, 700)

        self.canvas_width = 900
        self.canvas_height = 900
        self.world_min = WORLD_MIN
        self.world_max = WORLD_MAX
        self.grid_pad = 44
        
        self.buoys = []
        for k, v in BUOYS.items():
            if isinstance(v, Coordinates):
                coords_obj = v
            else:
                # Se è una tupla (x, y), la istanziamo come oggetto Coordinates
                coords_obj = Coordinates(float(v[0]), float(v[1]))
            self.buoys.append({"id": k, "coords": coords_obj})
            
        self._setup_ui()
        self.boat_coords=Coordinates(35.0, 35.0)
        self.boat_radius=10
        self._init_canvas_objects()
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        self.drag_sensor_id=None
        self._draw_grid()
        self.update_layout()
        self.root.after(150, self.update_telemetry_loop)
        
    def _setup_ui(self):
        main_frame=tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        #Map
        self.canvas=tk.Canvas(main_frame, width=self.canvas_width, height=self.canvas_height, bg="#A8DDF0")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        #Lateral
        self.side_panel=tk.Frame(main_frame, padx=12, width=280)
        self.side_panel.grid(row=0, column=1, sticky="ns")
        self.side_panel.grid_propagate(False)
        #Telemetry
        self.coord_var=tk.StringVar(value="Boat: X=--, Y=--")
        self.rssi_var=tk.StringVar(value="RSSI: [A1=--, A2=--, A3=--]")
        self.score_var=tk.StringVar(value="SIRK risk: --%")
        self.status_var=tk.StringVar(value="Status: Waiting serial data...")
        #self.time_var=tk.StringVar(value="Last Update: --:--:--")
        tk.Label(self.side_panel, text="Real-Time Telemetry", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 12))
        tk.Label(self.side_panel, textvariable=self.coord_var, font=("Courier", 10, "bold")).pack(anchor="w", pady=2)
        tk.Label(self.side_panel, textvariable=self.rssi_var, font=("Courier", 10)).pack(anchor="w", pady=2)
        tk.Label(self.side_panel, textvariable=self.score_var, font=("Courier", 10, "bold")).pack(anchor="w", pady=2)
        #tk.Label(self.side_panel, textvariable=self.time_var, font=("Courier", 10)).pack(anchor="w", pady=2)
        self.status_label=tk.Label(self.side_panel, textvariable=self.status_var, fg="#333", font=("Arial", 10, "bold"), wraplength=240, justify="left")
        self.status_label.pack(anchor="w", pady=(15, 0))
        self._build_buoy_editor()
        
    def _build_buoy_editor(self):
        self.editor_frame=tk.LabelFrame(self.side_panel, text="Buoy Matrix Config", padx=8, pady=8)
        self.editor_frame.pack(fill="x", pady=(15, 0))
        self.buoy_vars={}
        for b in self.buoys:
            row=tk.Frame(self.editor_frame)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=b["id"][:6], width=6, anchor="w").pack(side="left")
            vx=tk.StringVar(value=f"{b['coords'].x:.1f}")
            vy=tk.StringVar(value=f"{b['coords'].y:.1f}")
            self.buoy_vars[b["id"]]=(vx, vy)
            tk.Entry(row, textvariable=vx, width=6, justify="center").pack(side="left", padx=2)
            tk.Entry(row, textvariable=vy, width=6, justify="center").pack(side="left", padx=2)
        self.apply_btn=tk.Button(self.editor_frame, text="Apply", command=self.apply_buoy_edits)
        self.apply_btn.pack(fill="x", pady=(8, 0))
        
    def apply_buoy_edits(self):
        new_coords={}
        for b in self.buoys:
            vx, vy=self.buoy_vars[b["id"]]
            try:
                x=float(vx.get())
                y=float(vy.get())
            except ValueError:
                self.status_var.set(f"Invalid Coordinates for {b['id']} - not applied")
                self.status_label.config(fg="#FF0000")
                return
            new_coords[b["id"]]=Coordinates(x, y)
        for b in self.buoys:
            b["coords"]=new_coords[b["id"]]
        self.status_var.set("Buoy positions updates")
        self.status_label.config(fg="#333")
        self.update_layout()
        
    def _init_canvas_objects(self):
        self.triangle_item=self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill="#FFD166", stipple="gray50", outline="#D18A00", width=2)
        self.buoy_canvas_items={}
        for b in self.buoys:
            marker=self.canvas.create_oval(0, 0, 0, 0, fill="white", outline="#264653", width=2)
            label=self.canvas.create_text(0, 0, text=b["id"], fill="#1B3A4B", font=("Arial", 9, "bold"))
            self.buoy_canvas_items[b["id"]]=(marker, label)
            
        self.boat_marker=self.canvas.create_oval(0, 0, 0, 0, fill="#C62828", outline="white", width=2)
        self.boat_label=self.canvas.create_text(0, 0, text="BOAT (MyPhone)", fill="#232323", font=("Arial", 9, "bold"))
    
    def update_telemetry_loop(self):
        sample=self.service.get_latest_data()
        if sample:
            if sample.coordinates is None:
                self.canvas.itemconfig(self.boat_marker, state="hidden")
                self.canvas.itemconfig(self.boat_label, state="hidden")
                self.coord_var.set("Boat: OUT OF RANGE")
                self.rssi_var.set(f"RSSI: [A1={sample.rssi[0]}, A2={sample.rssi[1]}, A3={sample.rssi[2]}]")
                self.score_var.set("SIRK Risk: 0%")
                self.status_var.set("Status: No boat detected inside monitored sectors")
                self.status_label.config(fg="#555555")
            else: 
                self.canvas.itemconfig(self.boat_marker, state="normal")
                self.canvas.itemconfig(self.boat_label, state="normal")
                
                self.boat_coords = sample.coordinates
                
                # Calcola l'inclusione nel triangolo basandosi sulla macroarea attiva
                in_triangle = self.service.is_in_triangle(
                    self.boat_coords, 
                    self.buoys[0]["coords"], 
                    self.buoys[1]["coords"], 
                    self.buoys[2]["coords"]
                )
                score = self.service.calculate_risk_score(in_triangle)
                
                self.coord_var.set(f"Boat: X={self.boat_coords.x:.1f}, Y={self.boat_coords.y:.1f}")
                self.rssi_var.set(f"RSSI: [A1={sample.rssi[0]}, A2={sample.rssi[1]}, A3={sample.rssi[2]}]")
                self.score_var.set(f"SIRK Risk: {score}%")
                #self.time_var.set(f"Time: {time.strftime('%H:%M:%S')}")
                
                # Gestione dinamica degli allarmi visivi basati sul settore
                if in_triangle and self.service.stationary_ticks >= 3:
                    self.canvas.itemconfig(self.boat_marker, fill="#FF0000")
                    self.status_var.set("CRITICAL: ILLEGAL ANCHORING DETECTED INSIDE POSIDONIA FIELD")
                    self.status_label.config(fg="#FF0000")
                elif in_triangle or self.service.stationary_ticks > 0:
                    self.canvas.itemconfig(self.boat_marker, fill="#FFCA3A")
                    self.status_var.set("WARNING: Boat detected inside region")
                    self.status_label.config(fg="#D18A00")
                else:
                    self.canvas.itemconfig(self.boat_marker, fill="#C62828")
                    self.status_var.set("Status: Boat is moving outside protected area")
                    self.status_label.config(fg="#1B5E20")
                
                self.update_layout()
        self.root.after(150, self.update_telemetry_loop)
    
    def update_layout(self):
        polygon_points=[]
        for b in self.buoys:
            cx, cy=self.world_to_canvas(b["coords"])
            polygon_points.extend((cx, cy))
        self.canvas.coords(self.triangle_item, *polygon_points)
        for b in self.buoys:
            marker, label=self.buoy_canvas_items[b["id"]]
            cx, cy=self.world_to_canvas(b["coords"])
            self.canvas.coords(marker, cx-8, cy-8, cx+8, cy+8)
            self.canvas.coords(label, cx, cy-18)
        if self.canvas.itemcget(self.boat_marker, "state")!="hidden":
            bx, by=self.world_to_canvas(self.boat_coords)
            self.canvas.coords(self.boat_marker, bx-self.boat_radius, by-self.boat_radius, bx+self.boat_radius, by+self.boat_radius)
            self.canvas.coords(self.boat_label, bx, by-18)
    
    def world_to_canvas(self, coords: Coordinates) -> tuple[float, float]:
        g_left, g_top, s_x, s_y=self._get_scaling_factors()
        cx=g_left+(coords.x-self.world_min)*s_x
        cy=g_top+(coords.y-self.world_min)*s_y
        return cx, cy
        
    def canvas_to_world(self, cx: float, cy: float)-> Coordinates:
        g_left, g_top, s_x, s_y=self._get_scaling_factors()
        wx=self.world_min+(cx-g_left)/s_x
        wy=self.world_min+(cy-g_top)/s_y
        return Coordinates(max(0.0, min(70.0, wx)), max(0.0, min(70.0, wy)))
        
    def _get_scaling_factors(self):
        grid_left=self.grid_pad
        grid_top=self.grid_pad
        grid_right=self.canvas_width-self.grid_pad
        grid_bottom=self.canvas_height-self.grid_pad
        scale_x=(grid_right-grid_left)/(self.world_max-self.world_min)
        scale_y=(grid_bottom-grid_top)/(self.world_max-self.world_min)
        return grid_left, grid_top, scale_x, scale_y
    
    def _draw_grid(self):
        self.canvas.delete("grid")
        g_left=self.grid_pad
        g_top=self.grid_pad
        g_right=self.canvas_width-self.grid_pad
        g_bottom=self.canvas_height-self.grid_pad
        self.canvas.create_rectangle(g_left, g_top, g_right, g_bottom, fill="#DFF3FB", outline="#7BB8CF", width=2, tags="grid")
        for val in range(0, 71, 10):
            cx, cy=self.world_to_canvas(Coordinates(val, val))
            self.canvas.create_line(cx, g_top, cx, g_bottom, fill="#9FD0E0", tags="grid")
            self.canvas.create_line(g_left, cy, g_right, cy, fill="#9Fd0E0", tags="grid")
            self.canvas.create_text(cx, g_top-12, text=str(val), fill="#335D6D", font=("Arial", 8, "bold"), tags="grid")
            self.canvas.create_text(g_left-16, cy, text=str(val), fill="#355D6D", font=("Arial", 8, "bold"), tags="grid")
        self.canvas.create_line(g_left, g_top, g_right, g_top, fill="#316B7D", width=2, tags="grid")
        self.canvas.create_line(g_left, g_top, g_left, g_bottom, fill="#316B7D", width=2, tags="grid")
        self.canvas.create_text(g_left+15, g_top+12, text="(0,0)", fill="#0A4760", font=("Arial", 8, "bold"), tags="grid")
        self.canvas.tag_lower("grid")
    
    def on_canvas_resize(self, event):
        self.canvas_width=event.width
        self.canvas_height=event.height
        self._draw_grid()
        self.update_layout()
    
    def on_canvas_click(self, event):
        for b in self.buoys:
            cx, cy=self.world_to_canvas(b["coords"])
            if math.hypot(event.x-cx, event.y-cy)<15:
                self.drag_sensor_id=b["id"]
                return
    
    def on_canvas_drag(self, event):
        if self.drag_sensor_id:
            new_world_coords=self.canvas_to_world(event.x, event.y)
            for b in self.buoys:
                if b["id"]==self.drag_sensor_id:
                    b["coords"]=new_world_coords
                    self.buoy_vars[b["id"]][0].set(f"{new_world_coords.x:.1f}")
                    self.buoy_vars[b["id"]][1].set(f"{new_world_coords.y:.1f}")
            self.update_layout()
    
    def on_canvas_release(self, event):
        self.drag_sensor_id=None
    
if __name__=="__main__":
    ports=get_available_ports()
    target_port=SERIAL_PORT
    if target_port not in ports and ports:
        target_port=ports[0]
        print(f"Port {target_port} not avail")
    try:
        source=SerialCoordinateSource(port=target_port, baud=BAUD_RATE)
        print(f"Connected Serial")
    except Exception as e:
        source=None
        print(f"Start Program")
    service=TrackingService(source)
    root=tk.Tk()
    app=PosidoniaTrackerApp(root, service)
    root.mainloop()