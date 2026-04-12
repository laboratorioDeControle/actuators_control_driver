import math

class Servo:
    @property
    def angle(self) -> float:
        return self._angle
    
    @angle.setter
    def angle(self, value: float):
        if not self._stop:
            self._angle = value

    @property
    def stop(self) -> bool:
        return self._stop
    
    @stop.setter
    def stop(self, value: bool):        
        if value:
            self.angle = 0.0
        self._stop = value

    @property
    def msg_field(self) -> int:
        float_angle: float = self.map(self.angle, self._min_angle, self._max_angle,
                                      float(self._min_output), float(self._max_output))
        
        int_angle: int = round(float_angle)

        if int_angle >= self._max_output:
            int_angle = self._max_output
        elif int_angle <= self._min_output:
            int_angle = self._min_output

        return int_angle
        

    def __init__(self, min_angle: float = -math.pi/2, max_angle: float = math.pi/2, 
                 min_output: int = 0x2a, max_output: int = 0xff):
        
        self._min_angle: float = min_angle
        self._max_angle: float = max_angle

        self._min_output: int = min_output
        self._max_output: int = max_output

        self._angle: float = 0.0
        self._stop: bool = False
    
    def map(self, value: float, input_min: float = 0, input_max: float = 1.0, output_min: float = 0, output_max: float = 255.0):
        return (value - input_min) * (output_max - output_min) / (input_max - input_min) + output_min
