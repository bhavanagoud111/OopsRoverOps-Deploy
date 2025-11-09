import json
from typing import List, Dict, Any
from app.agents.base import BaseAgent
from app.models.schemas import AgentType, AgentStatus, MissionStep, RoverPosition

class PlannerAgent(BaseAgent):
    """Agent that breaks down natural language missions into structured steps"""
    
    def __init__(self):
        system_prompt = """You are a mission planner for a Mars rover. Your job is to break down high-level mission goals into specific, actionable steps using clear, structured reasoning.

The rover operates on a 10x10 grid (coordinates 0-9 for both x and y). The rover starts at position (0, 0).

## REASONING PROCESS

You MUST follow this structured reasoning process:

### STEP 1: ANALYZE THE MISSION GOAL
- Read the mission goal carefully
- Identify the PRIMARY objective (what needs to be accomplished)
- Identify the SECONDARY objectives (any additional tasks)
- Extract any specific locations, coordinates, or targets mentioned

### STEP 2: EXTRACT KEY INFORMATION
- **Coordinates**: Look for patterns like:
  * "(5,9)" or "(5, 9)" or "5,9" or "5, 9"
  * "coordinates (x, y)" or "position (x, y)"
  * "go to (x, y)" or "move to (x, y)"
  * "x=5, y=9" or "x:5, y:9"
- **Actions**: Identify what actions are required:
  * "collect rock sample", "get sample", "collect sample" → requires "collect" action
  * "scan", "analyze", "examine" → requires "scan" action
  * "explore", "investigate" → requires "explore" action
- **Constraints**: Note any special requirements or constraints

### STEP 3: PLAN THE MISSION SEQUENCE
Think through the logical sequence:
1. **Navigation**: How to get to the target location(s)
2. **Primary Actions**: What needs to be done at the target
3. **Secondary Actions**: Any additional tasks
4. **Return**: How to safely return to base

### STEP 4: CREATE STEP-BY-STEP PLAN
Break down into 3-8 sequential steps that accomplish ALL parts of the goal.

## AVAILABLE ACTIONS
- **move**: Move the rover to a specific position (x, y)
- **explore**: Explore a specific area/position to gather information
- **return**: Return to the starting position (0, 0)
- **scan**: Scan the current area for obstacles, terrain features, or scientific data
- **collect**: Collect samples (rocks, soil, etc.) at the current position

## PLANNING RULES
1. **Coordinate Extraction**: If coordinates are specified, use EXACTLY those coordinates
2. **Action Completeness**: Include ALL actions mentioned in the goal
3. **Logical Sequence**: Steps must follow a logical order (navigate → act → return)
4. **Safety**: Always plan a safe route, considering obstacles
5. **Completeness**: Every part of the goal must be addressed in the plan
6. **Return**: Always include a final "return to base" step unless explicitly told otherwise

## RESPONSE FORMAT

You MUST respond with a JSON object containing:
1. **reasoning**: A clear explanation of your reasoning process, including:
   - What you understood from the mission goal
   - What coordinates/actions you extracted
   - Why you chose this sequence of steps
   - How the plan accomplishes the goal
2. **steps**: An array of mission steps

Each step must have:
- **step_number**: Sequential number starting from 1
- **action**: One of the available actions
- **target_position**: {{"x": number, "y": number}} if applicable (null for actions at current position)
- **description**: Clear description of what this step accomplishes

Example response format:
{{
  "reasoning": "The mission goal is to move to coordinates (5, 9) and collect rock samples. I extracted coordinates x=5, y=9 from the goal. The goal explicitly mentions 'collect samples', so I need to include a collect action. The logical sequence is: 1) Navigate to (5, 9), 2) Collect samples at that location, 3) Return to base. This ensures we reach the target, complete the collection task, and safely return.",
  "steps": [
    {{
      "step_number": 1,
      "action": "move",
      "target_position": {{"x": 5, "y": 9}},
      "description": "Move to target coordinates (5, 9) to reach the collection site"
    }},
    {{
      "step_number": 2,
      "action": "collect",
      "target_position": {{"x": 5, "y": 9}},
      "description": "Collect rock samples at the target location (5, 9)"
    }},
    {{
      "step_number": 3,
      "action": "return",
      "target_position": {{"x": 0, "y": 0}},
      "description": "Return to base at starting position (0, 0)"
    }}
  ]
}}"""
        
        super().__init__(AgentType.PLANNER, system_prompt, temperature=0.3)
    
    async def plan_mission(self, goal: str) -> List[MissionStep]:
        """Generate mission plan from natural language goal"""
        self.set_status(AgentStatus.PLANNING)

        # First, extract coordinates from goal to validate LLM response
        goal_coords = self._extract_coordinates_from_goal(goal)

        # Enhanced input prompt with structured reasoning request
        input_text = f"""Mission Goal: "{goal}"

Please analyze this mission goal and create a detailed plan. Follow the reasoning process:

1. ANALYZE: What is the primary objective? What are any secondary objectives?
2. EXTRACT: What coordinates are mentioned? What actions are required?
3. PLAN: What is the logical sequence of steps to accomplish this goal?
4. CREATE: Generate the step-by-step plan with clear reasoning.

Provide your reasoning clearly and then create the mission plan."""

        result = await self.process(input_text)

        if result["status"] == "error":
            # Fallback to simple plan
            return self._create_fallback_plan(goal)

        try:
            # Parse LLM response - it might be JSON or text with JSON
            response_text = result["response"]
            
            # Extract and log reasoning if present
            reasoning = None
            if '"reasoning"' in response_text or "'reasoning'" in response_text:
                # Try to extract reasoning from response
                reasoning_match = None
                import re
                # Look for reasoning field in JSON
                reasoning_pattern = r'"reasoning"\s*:\s*"([^"]+)"'
                match = re.search(reasoning_pattern, response_text)
                if match:
                    reasoning = match.group(1)
                else:
                    # Look for reasoning before JSON
                    reasoning_lines = []
                    in_reasoning = False
                    for line in response_text.split('\n'):
                        if 'reasoning' in line.lower() and not in_reasoning:
                            in_reasoning = True
                        if in_reasoning and line.strip().startswith('{'):
                            break
                        if in_reasoning:
                            reasoning_lines.append(line)
                    if reasoning_lines:
                        reasoning = '\n'.join(reasoning_lines).strip()
            
            if reasoning:
                print(f"\n🧠 PLANNER REASONING:\n{reasoning}\n")
            else:
                print(f"\n📋 PLANNER RESPONSE:\n{response_text[:500]}...\n")

            # Try to extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                plan_data = json.loads(json_text)
            else:
                # Try to parse the whole response as JSON
                plan_data = json.loads(response_text)

            # Extract reasoning from plan_data if present
            if "reasoning" in plan_data:
                reasoning = plan_data["reasoning"]
                print(f"\n🧠 PLANNER REASONING:\n{reasoning}\n")

            steps_data = plan_data.get("steps", [])

            mission_steps = []
            
            # CRITICAL FIX: If goal has coordinates, ALWAYS create a move step FIRST
            # Don't trust LLM - force the first step to be a move to extracted coordinates
            if goal_coords and (goal_coords["x"] is not None and goal_coords["y"] is not None):
                print(f"🎯 FORCING first step to target ({goal_coords['x']}, {goal_coords['y']}) from goal coordinates")
                
                # Filter out return steps from the beginning
                filtered_steps = []
                for step in steps_data:
                    action = step.get("action", "").lower()
                    if action != "return":
                        filtered_steps.append(step)
                    elif len(filtered_steps) > 0:
                        # Return step after other steps - keep it
                        filtered_steps.append(step)
                steps_data = filtered_steps
                
                # ALWAYS insert a move step at the beginning with extracted coordinates
                # This ensures the rover ALWAYS goes to the correct target first
                forced_move_step = {
                    "step_number": 1,
                    "action": "move",
                    "target_position": {"x": goal_coords["x"], "y": goal_coords["y"]},
                    "description": f"Move to target coordinates ({goal_coords['x']}, {goal_coords['y']}) from mission goal"
                }
                
                # Renumber all existing steps
                for i, step in enumerate(steps_data):
                    step["step_number"] = i + 2
                
                # Insert forced move step at the beginning
                steps_data.insert(0, forced_move_step)
                print(f"✅ INSERTED forced move step to ({goal_coords['x']}, {goal_coords['y']}) as step 1")

            for step_data in steps_data:
                target_pos = None
                if step_data.get("target_position"):
                    pos_data = step_data["target_position"]
                    target_x = pos_data["x"]
                    target_y = pos_data["y"]
                    
                    # For step 1, ALWAYS use extracted coordinates if available
                    if step_data.get("step_number") == 1 and goal_coords and (goal_coords["x"] is not None and goal_coords["y"] is not None):
                        action = step_data.get("action", "").lower()
                        if action in ["move", "explore"]:
                            # FORCE step 1 to use extracted coordinates
                            target_x = goal_coords["x"]
                            target_y = goal_coords["y"]
                            step_data["description"] = f"Move to target coordinates ({target_x}, {target_y}) from mission goal"
                            print(f"✅ FORCED step 1 target to ({target_x}, {target_y})")

                    target_pos = RoverPosition(x=target_x, y=target_y)

                step = MissionStep(
                    step_number=step_data["step_number"],
                    action=step_data["action"],
                    target_position=target_pos,
                    description=step_data.get("description", ""),
                    completed=False
                )
                mission_steps.append(step)

            # CRITICAL FIX: Always ensure return-to-base step is at the end
            # Check if last step is a return step
            if mission_steps and len(mission_steps) > 0:
                last_step = mission_steps[-1]
                if last_step.action != "return":
                    # Add return step if not present
                    return_step = MissionStep(
                        step_number=len(mission_steps) + 1,
                        action="return",
                        target_position=RoverPosition(x=0, y=0),
                        description="Return to base (0, 0)",
                        completed=False
                    )
                    mission_steps.append(return_step)
                    print(f"✅ Added return-to-base step as step {return_step.step_number}")
            elif len(mission_steps) == 0:
                # No steps at all - add return step
                return_step = MissionStep(
                    step_number=1,
                    action="return",
                    target_position=RoverPosition(x=0, y=0),
                    description="Return to base (0, 0)",
                    completed=False
                )
                mission_steps.append(return_step)

            return mission_steps
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing planner response: {e}")
            print(f"Response was: {result.get('response', '')}")
            return self._create_fallback_plan(goal)
    
    def _extract_coordinates_from_goal(self, goal: str) -> dict:
        """Extract coordinates from goal text using regex patterns"""
        import re
        
        coord_patterns = [
            r'\((\d+)\s*,\s*(\d+)\)',  # (5,9) or (5, 9)
            r'at\s+(\d+)\s*,\s*(\d+)',  # at 5,9 or at 5, 9
            r'at\s+(\d+)\s+(\d+)',      # at 5 9
            r'(\d+)\s*,\s*(\d+)',      # 5,9 or 5, 9
            r'x\s*[=:]\s*(\d+)\s*[,;]\s*y\s*[=:]\s*(\d+)',  # x=5, y=9
            r'x\s*:\s*(\d+)\s*[,;]\s*y\s*:\s*(\d+)',       # x:5, y:9
            r'coordinates?\s+(\d+)\s*,\s*(\d+)',  # coordinate 5,9 or coordinates 5,9
            r'position\s+(\d+)\s*,\s*(\d+)',     # position 5,9
        ]
        
        target_x, target_y = None, None
        
        for pattern in coord_patterns:
            match = re.search(pattern, goal, re.IGNORECASE)
            if match:
                try:
                    target_x = int(match.group(1))
                    target_y = int(match.group(2))
                    # Validate coordinates are within bounds
                    if 0 <= target_x <= 9 and 0 <= target_y <= 9:
                        break
                except (ValueError, IndexError):
                    continue
        
        return {"x": target_x, "y": target_y}
    
    def _create_fallback_plan(self, goal: str) -> List[MissionStep]:
        """Create a simple fallback plan if LLM parsing fails - extracts coordinates from goal"""
        # Use the coordinate extraction method
        goal_coords = self._extract_coordinates_from_goal(goal)
        
        target_x = goal_coords["x"]
        target_y = goal_coords["y"]
        
        # If no coordinates found, default to (5, 5) but log warning
        if target_x is None or target_y is None:
            print(f"Warning: Could not extract coordinates from goal '{goal}', using default (5, 5)")
            target_x, target_y = 5, 5
        
        return [
            MissionStep(
                step_number=1,
                action="move",
                target_position=RoverPosition(x=target_x, y=target_y),
                description=f"Move to target coordinates ({target_x}, {target_y}) from goal: {goal}",
                completed=False
            ),
            MissionStep(
                step_number=2,
                action="explore",
                target_position=RoverPosition(x=target_x, y=target_y),
                description=f"Explore the target area at ({target_x}, {target_y})",
                completed=False
            ),
            MissionStep(
                step_number=3,
                action="return",
                target_position=RoverPosition(x=0, y=0),
                description="Return to base",
                completed=False
            )
        ]

