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
    def offset_deg(self) -> float:
        return self._offset_deg
    
    @offset_deg.setter
    def offset_deg(self, value: float):
        self._offset_deg = value
        offset_rad: float = math.radians(value)
        self._offset_rad_mapped: int = round(
            offset_rad * (self._max_output - self._min_output) / (self._max_angle - self._min_angle)
        )

    @property
    def msg_field(self) -> int:
        float_angle: float = self.map(self.angle, self._min_angle, self._max_angle,
                                      float(self._min_output), float(self._max_output))
        
        int_angle: int = round(float_angle)

        if int_angle >= self._max_output:
            int_angle = self._max_output
        elif int_angle <= self._min_output:
            int_angle = self._min_output

        # Offset é aplicado após o mapeamento, não sujeito às restrições do ângulo
        int_angle += self._offset_rad_mapped

        return int_angle
        

    def __init__(self, min_angle: float = -math.pi/4, max_angle: float = math.pi/4, 
                 min_output: int = 0x4e, max_output: int = 0xb2,
                 offset_deg: float = 0.0):
        
        self._min_angle: float = min_angle
        self._max_angle: float = max_angle

        self._min_output: int = min_output
        self._max_output: int = max_output

        self._angle: float = 0.0
        self._stop: bool = False

        # Usar o setter para inicializar o offset
        self._offset_deg: float = 0.0
        self._offset_rad_mapped: int = 0
        self.offset_deg = offset_deg
    
    def map(self, value: float, input_min: float = 0, input_max: float = 1.0, output_min: float = 0, output_max: float = 255.0):
        return (value - input_min) * (output_max - output_min) / (input_max - input_min) + output_min
