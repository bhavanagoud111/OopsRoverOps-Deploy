from typing import Dict, Optional, List
import uuid
from datetime import datetime
import random

from app.models.schemas import (
    MissionState, 
    MissionStatus, 
    RoverPosition, 
    MissionStep,
    MissionLog,
    AgentType,
    AgentStatus
)

class MissionStateManager:
    def __init__(self):
        self.missions: Dict[str, MissionState] = {}
        self.grid_size = 10  # 10x10 grid

    def create_mission(self, goal: str, obstacles: Optional[List[RoverPosition]] = None) -> str:
        """Create a new mission and return mission_id"""
        mission_id = str(uuid.uuid4())
        
        # Generate obstacles if not provided
        if obstacles is None:
            obstacles = self._generate_obstacles(num_obstacles=5)
        
        mission_state = MissionState(
            mission_id=mission_id,
            goal=goal,
            status=MissionStatus.PENDING,
            rover_position=RoverPosition(x=0, y=0),  # Start at origin
            obstacles=obstacles,
            goal_positions=[],  # Will be set by planner
            steps=[],
            logs=[],
            agent_states={
                AgentType.PLANNER: AgentStatus.IDLE,
                AgentType.ROVER: AgentStatus.IDLE,
                AgentType.SAFETY: AgentStatus.IDLE,
                AgentType.REPORTER: AgentStatus.IDLE,
            }
        )
        
        self.missions[mission_id] = mission_state
        return mission_id

    def get_mission(self, mission_id: str) -> Optional[MissionState]:
        """Get mission state by ID"""
        return self.missions.get(mission_id)

    def update_mission_status(self, mission_id: str, status: MissionStatus):
        """Update mission status"""
        if mission_id in self.missions:
            self.missions[mission_id].status = status
            self.missions[mission_id].updated_at = datetime.now()

    def update_rover_position(self, mission_id: str, position: RoverPosition):
        """Update rover position"""
        if mission_id in self.missions:
            self.missions[mission_id].rover_position = position
            self.missions[mission_id].updated_at = datetime.now()

    def add_step(self, mission_id: str, step: MissionStep):
        """Add a mission step"""
        if mission_id in self.missions:
            self.missions[mission_id].steps.append(step)
            self.missions[mission_id].updated_at = datetime.now()

    def update_step(self, mission_id: str, step_number: int, completed: bool = True, nasa_image_url: Optional[str] = None):
        """Update a mission step"""
        if mission_id in self.missions:
            for step in self.missions[mission_id].steps:
                if step.step_number == step_number:
                    step.completed = completed
                    if nasa_image_url:
                        step.nasa_image_url = nasa_image_url
                    break
            self.missions[mission_id].updated_at = datetime.now()

    def add_log(self, mission_id: str, log: MissionLog):
        """Add a log entry"""
        if mission_id in self.missions:
            self.missions[mission_id].logs.append(log)
            self.missions[mission_id].updated_at = datetime.now()

    def update_agent_status(self, mission_id: str, agent_type: AgentType, status: AgentStatus):
        """Update agent status"""
        if mission_id in self.missions:
            self.missions[mission_id].agent_states[agent_type] = status
            self.missions[mission_id].updated_at = datetime.now()

    def set_current_step(self, mission_id: str, step_number: int):
        """Set current step number"""
        if mission_id in self.missions:
            self.missions[mission_id].current_step = step_number
            self.missions[mission_id].updated_at = datetime.now()

    def add_nasa_image(self, mission_id: str, image_url: str):
        """Add NASA image URL to mission"""
        if mission_id in self.missions:
            if image_url not in self.missions[mission_id].nasa_images:
                self.missions[mission_id].nasa_images.append(image_url)
            self.missions[mission_id].updated_at = datetime.now()

    def set_weather_data(self, mission_id: str, weather_data: dict):
        """Set weather data for mission"""
        if mission_id in self.missions:
            self.missions[mission_id].weather_data = weather_data
            self.missions[mission_id].updated_at = datetime.now()

    def set_goal_positions(self, mission_id: str, positions: List[RoverPosition]):
        """Set goal positions for mission"""
        if mission_id in self.missions:
            self.missions[mission_id].goal_positions = positions
            self.missions[mission_id].updated_at = datetime.now()

    def add_collected_data(self, mission_id: str, data: Dict):
        """Add collected data (samples, findings) to mission"""
        if mission_id in self.missions:
            if not self.missions[mission_id].collected_data:
                self.missions[mission_id].collected_data = []
            self.missions[mission_id].collected_data.append(data)
            self.missions[mission_id].updated_at = datetime.now()

    def is_position_valid(self, mission_id: str, position: RoverPosition) -> bool:
        """Check if a position is valid (within bounds and not an obstacle)"""
        # Check bounds
        if position.x < 0 or position.x >= self.grid_size or position.y < 0 or position.y >= self.grid_size:
            return False
        
        # Check obstacles
        mission = self.missions.get(mission_id)
        if mission:
            for obstacle in mission.obstacles:
                if obstacle.x == position.x and obstacle.y == position.y:
                    return False
        
        return True

    def is_position_obstacle(self, mission_id: str, position: RoverPosition) -> bool:
        """Check if a position is an obstacle"""
        mission = self.missions.get(mission_id)
        if mission:
            for obstacle in mission.obstacles:
                if obstacle.x == position.x and obstacle.y == position.y:
                    return True
        return False

    def get_path_distance(self, pos1: RoverPosition, pos2: RoverPosition) -> float:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    def _generate_obstacles(self, num_obstacles: int = 5) -> List[RoverPosition]:
        """Generate random obstacles (excluding start position 0,0)"""
        obstacles = []
        attempts = 0
        max_attempts = 100
        
        while len(obstacles) < num_obstacles and attempts < max_attempts:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            
            # Don't place obstacle at start position
            if x == 0 and y == 0:
                continue
            
            pos = RoverPosition(x=x, y=y)
            # Check if already added
            if not any(o.x == x and o.y == y for o in obstacles):
                obstacles.append(pos)
            
            attempts += 1
        
        return obstacles

    def get_mission_summary(self, mission_id: str) -> Optional[dict]:
        """Get mission summary"""
        mission = self.missions.get(mission_id)
        if not mission:
            return None
        
        completed_steps = sum(1 for step in mission.steps if step.completed)
        
        return {
            "mission_id": mission_id,
            "goal": mission.goal,
            "status": mission.status.value,
            "current_step": mission.current_step,
            "total_steps": len(mission.steps),
            "completed_steps": completed_steps,
            "rover_position": {
                "x": mission.rover_position.x,
                "y": mission.rover_position.y
            },
            "logs_count": len(mission.logs),
            "images_count": len(mission.nasa_images)
        }

# Global instance
mission_state_manager = MissionStateManager()

