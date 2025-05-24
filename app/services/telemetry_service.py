import asyncio
import random
import time
from datetime import datetime, timezone
from typing import List, Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.models.flight_plan import FlightPlan, FlightPlanStatus
from app.models.drone import Drone, DroneStatus
from app.models.telemetry_log import TelemetryLog
from app.schemas.telemetry import TelemetryLogCreate, LiveTelemetryMessage
from app.crud import telemetry_log as crud_telemetry_log
from app.crud import drone as crud_drone
from app.crud import flight_plan as crud_flight_plan # For completing flight
from app.db.session import SessionLocal # To create new sessions in async tasks
from app.services.nfz_service import nfz_service # For in-flight NFZ checks


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # For targeted messages if needed in future (e.g., per organization_id)
        # self.scoped_connections: Dict[Any, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            self.disconnect(websocket)
        except RuntimeError: # Handle cases where connection might be closing
            self.disconnect(websocket)


    async def broadcast(self, message_data: dict): # Changed to accept dict for JSON
        # message_json = json.dumps(message_data) # Pydantic model will be converted by FastAPI
        disconnected_sockets = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message_data)
            except (WebSocketDisconnect, RuntimeError):
                disconnected_sockets.append(connection)
        
        for ws in disconnected_sockets:
            self.disconnect(ws)


class TelemetryService:
    def __init__(self):
        self.active_simulations: Dict[int, asyncio.Task] = {} # flight_plan_id -> Task
        self.simulation_stop_events: Dict[int, asyncio.Event] = {} # flight_plan_id -> Event

    async def _simulate_flight_telemetry(self, flight_plan_id: int, stop_event: asyncio.Event):
        """Simulates telemetry for a given flight plan."""
        # Create a new DB session for this long-running task
        # This is important because the original request's session will be closed.
        db: Session = SessionLocal()
        try:
            fp = crud_flight_plan.flight_plan.get_flight_plan_with_details(db, id=flight_plan_id)
            if not fp or not fp.waypoints:
                print(f"Flight plan {flight_plan_id} not found or no waypoints for simulation.")
                return

            # Update drone status to ACTIVE
            db_drone = crud_drone.drone.get(db, id=fp.drone_id)
            if db_drone:
                db_drone.current_status = DroneStatus.ACTIVE
                db.add(db_drone)
                db.commit()
                db.refresh(db_drone)

            current_waypoint_index = 0
            num_waypoints = len(fp.waypoints)
            
            # Simplified: Assume linear interpolation between waypoints
            # A real simulation would be much more complex (speed, turns, ascent/descent rates)
            
            # Simulation loop
            while current_waypoint_index < num_waypoints and not stop_event.is_set():
                if current_waypoint_index >= len(fp.waypoints): # Should not happen if loop condition is correct
                    break
                
                target_waypoint = fp.waypoints[current_waypoint_index]
                
                # Simulate movement towards target_waypoint (very basic)
                # For now, let's just "jump" to waypoints every few seconds
                # In a real sim, you'd calculate intermediate points.
                
                lat = target_waypoint.latitude
                lon = target_waypoint.longitude
                alt = target_waypoint.altitude_m
                timestamp = datetime.now(timezone.utc)
                speed_mps = random.uniform(5, 15) # m/s
                heading_degrees = random.uniform(0, 359.9)
                status_message = "ON_SCHEDULE"

                # In-flight NFZ check (using the new DB session)
                nfz_breaches = nfz_service.check_point_against_nfzs(db, lat, lon, alt)
                if nfz_breaches:
                    status_message = f"ALERT_NFZ: Breached {', '.join([b['name'] for b in nfz_breaches])}"
                    # Potentially trigger other alert mechanisms

                # Create and store telemetry log
                log_entry = TelemetryLogCreate(
                    flight_plan_id=fp.id,
                    drone_id=fp.drone_id,
                    timestamp=timestamp,
                    latitude=lat,
                    longitude=lon,
                    altitude_m=alt,
                    speed_mps=speed_mps,
                    heading_degrees=heading_degrees,
                    status_message=status_message,
                )
                db_log_entry = crud_telemetry_log.telemetry_log.create(db, obj_in=log_entry)

                # Update drone's last seen and last telemetry
                if db_drone:
                    db_drone.last_seen_at = timestamp
                    db_drone.last_telemetry_id = db_log_entry.id # type: ignore
                    db.add(db_drone)
                    db.commit() # Commit frequently for updates to be visible

                # Broadcast telemetry via WebSocket
                live_message = LiveTelemetryMessage(
                    flight_id=fp.id,
                    drone_id=fp.drone_id,
                    lat=lat,
                    lon=lon,
                    alt=alt,
                    timestamp=timestamp,
                    speed=speed_mps,
                    heading=heading_degrees,
                    status_message=status_message,
                )
                await connection_manager.broadcast(live_message.model_dump())
                
                # Move to next waypoint after a delay
                await asyncio.sleep(5) # Telemetry update interval
                current_waypoint_index += 1

                if stop_event.is_set():
                    print(f"Simulation for flight {flight_plan_id} stopped by event.")
                    status_message = "FLIGHT_INTERRUPTED" # Or similar
                    # Log one final telemetry point indicating interruption if needed
                    break
            
            # Simulation finished (either completed waypoints or stopped)
            final_status_message = "FLIGHT_COMPLETED"
            if stop_event.is_set() and current_waypoint_index < num_waypoints:
                final_status_message = "FLIGHT_CANCELLED_OR_STOPPED"

            # Update flight plan status to COMPLETED if all waypoints were reached
            # and it wasn't externally stopped (e.g., by cancellation)
            # Re-fetch flight plan to get its current status from DB
            db.refresh(fp) # Refresh fp object
            if not stop_event.is_set() and fp.status == FlightPlanStatus.ACTIVE:
                crud_flight_plan.flight_plan.complete_flight(db, db_obj=fp)
                final_status_message = "FLIGHT_COMPLETED"
            
            # Update drone status to IDLE
            if db_drone:
                db_drone.current_status = DroneStatus.IDLE
                db.add(db_drone)
                db.commit()
            
            print(f"Simulation for flight {flight_plan_id} ended with status: {final_status_message}.")

        except Exception as e:
            print(f"Error during flight simulation for {flight_plan_id}: {e}")
            # Attempt to set drone to UNKNOWN or IDLE on error
            if 'db_drone' in locals() and db_drone:
                db_drone.current_status = DroneStatus.UNKNOWN
                db.add(db_drone)
                db.commit()
        finally:
            db.close() # Ensure the session is closed for this task
            if flight_plan_id in self.active_simulations:
                del self.active_simulations[flight_plan_id]
            if flight_plan_id in self.simulation_stop_events:
                del self.simulation_stop_events[flight_plan_id]


    def start_flight_simulation(self, db: Session, flight_plan: FlightPlan):
        if flight_plan.id in self.active_simulations:
            print(f"Simulation for flight {flight_plan.id} is already active.")
            return

        stop_event = asyncio.Event()
        self.simulation_stop_events[flight_plan.id] = stop_event
        
        # We pass flight_plan.id instead of the whole object
        # because the object might become stale if the DB session that loaded it closes.
        # The async task will create its own DB session.
        task = asyncio.create_task(self._simulate_flight_telemetry(flight_plan.id, stop_event))
        self.active_simulations[flight_plan.id] = task
        print(f"Started simulation for flight {flight_plan.id}")

    def stop_flight_simulation(self, flight_plan_id: int):
        if flight_plan_id in self.simulation_stop_events:
            self.simulation_stop_events[flight_plan_id].set() # Signal the task to stop
            print(f"Stop signal sent for flight simulation {flight_plan_id}")
        else:
            print(f"No active simulation found to stop for flight {flight_plan_id}")
        
        # Task cancellation is an option too, but graceful stop via event is preferred.
        # if flight_plan_id in self.active_simulations:
        #     self.active_simulations[flight_plan_id].cancel()

telemetry_service = TelemetryService() # Singleton instance
connection_manager = ConnectionManager() # Singleton instance