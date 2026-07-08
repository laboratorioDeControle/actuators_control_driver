Motor_Clockwise: int = 0
Motor_CounterClockwise: int = 1


class Thruster:
    @property
    def rotation_percent(self) -> float:
        return self._rotation_percent

    @rotation_percent.setter
    def rotation_percent(self, value: float):
        if value < 0:
            self.direction = Motor_CounterClockwise
        else:
            self.direction = Motor_Clockwise

        if not self._stop:
            self._rotation_percent = abs(value)

    @property
    def stop(self) -> bool:
        return self._stop
    
    @stop.setter
    def stop(self, value: bool):
        if value:
            self.enable = 0
            self.rotation_percent = 0.0
        else:
            self.enable = 1
        self._stop = value

    @property
    def enable(self) -> bool:
        return self._enable != 0
    
    @enable.setter
    def enable(self, value: bool):
        self._enable = int(value)

    @property
    def direction(self) -> int:
        return self._direction

    @direction.setter
    def direction(self, value: int):
        self._direction = value

    @property
    def msg_field(self) -> list:
        result = []

        mapped_rotation: float = self.map(self._rotation_percent)
        int_rotation: int = round(mapped_rotation)

        if int_rotation >= self._output_max_value:
            int_rotation = self._output_max_value
        elif int_rotation <= self._output_min_value:
            int_rotation = self._output_min_value

        result.append(self.direction)
        result.append(int_rotation)
        result.append(self._enable)

        return result


    def __init__(self, output_min_value: int = 0, output_max_value: int = 255):
        self._output_min_value: int = output_min_value
        self._output_max_value: int = output_max_value

        self._stop: bool = False
        self._rotation_percent: float = 0.0
        self._direction: int = 0
        self._enable: int = 0

    def map(self, value: float, input_min: float = 0, input_max: float = 1.0, output_min: float = 0, output_max: float = 255.0):
        return (value - input_min) * (output_max - output_min) / (input_max - input_min) + output_min