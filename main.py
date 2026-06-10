import keyboard
import win32clipboard
import time
import math

class LinearEquationSystem:
    def __init__(self):
        self.coefficients = []
        self.constants = []

        self.num_equations = 0
        self.num_variables = 2

    def add_equation(self, coefficients, constant):
        self.coefficients.append(coefficients)
        self.constants.append(constant)
        self.num_equations += 1

    def row_interchange(self, left_row_index, right_row_index):
        for i in range(self.num_variables):
            self.coefficients[left_row_index][i], self.coefficients[right_row_index][i] = \
                self.coefficients[right_row_index][i], self.coefficients[left_row_index][i]

        self.constants[left_row_index], self.constants[right_row_index] = \
            self.constants[right_row_index], self.constants[left_row_index]

    def row_scale(self, row_index, scale):
        for i in range(self.num_variables):
            self.coefficients[row_index][i] *= scale
        self.constants[row_index] *= scale

    def row_add(self, modifying_row_index, scale_row_index, scale):
        for i in range(self.num_variables):
            self.coefficients[modifying_row_index][i] += self.coefficients[scale_row_index][i] * scale
        self.constants[modifying_row_index] += self.constants[scale_row_index] * scale

    def convert_to_reduced_echelon_form(self):
        highest_available_row = 0
        for col in range(self.num_variables):
            non_zero_containing_column = False
            for row in range(highest_available_row, self.num_equations):
                coefficient = self.coefficients[row][col]
                if coefficient != 0:
                    self.row_scale(row, 1 / coefficient)
                    self.row_interchange(row, highest_available_row)
                    highest_available_row += 1
                    non_zero_containing_column = True
                    break

            if not non_zero_containing_column:
                continue

            for row in range(highest_available_row, self.num_equations):
                coefficient = self.coefficients[row][col]
                if col == 1:
                    self.row_add(row, highest_available_row - 1, -coefficient + 1)
                else:
                    self.row_add(row, highest_available_row - 1, -coefficient)

    def get_transpose(self):
        transpose = []
        for i in range(self.num_variables):
            transpose.append([None] * self.num_equations)
        for i in range(self.num_equations):
            for j in range(self.num_variables):
                transpose[j][i] = self.coefficients[i][j]
        return transpose

    def normalize(self):
        transpose = self.get_transpose()

        result_coefficients = []
        for i in range(self.num_variables):
            result_coefficients.append([0] * self.num_variables)

        for i in range(self.num_variables):
            for j in range(self.num_variables):
                for k in range(self.num_equations):
                    result_coefficients[i][j] += transpose[i][k] * self.coefficients[k][j]

        result_constants = [0] * self.num_variables

        for i in range(self.num_variables):
            for j in range(self.num_equations):
                result_constants[i] += transpose[i][j] * self.constants[j]

        self.coefficients = result_coefficients
        self.constants = result_constants

        self.num_equations = self.num_variables

    def solve_underdetermined(self):
        a = self.coefficients[0][-1]
        b = 1
        c = -self.constants[0]

        slope = -b
        y_intercept = self.constants[0]

        possible_stronghold_locations = []
        for dist in range(-100, 100):
            x = math.sin(math.atan(1 / slope)) * dist
            pos = (round(x), round(slope * x + y_intercept))
            error = abs(a * pos[0] + b * pos[1] + c) / math.sqrt(a ** 2 + b ** 2)
            possible_stronghold_locations.append((pos, error))

        possible_stronghold_locations.sort(key=lambda e: e[1], reverse=True)
        origin_distance = lambda p: math.sqrt(p[0] ** 2 + p[1] ** 2)
        best_guess = possible_stronghold_locations[-1][0]
        while not (80 < origin_distance(best_guess) < 176):
            best_guess = possible_stronghold_locations.pop()[0]
        return best_guess

    def solve(self):
        if self.num_equations < self.num_variables:
            return self.solve_underdetermined()

        self.normalize()
        self.convert_to_reduced_echelon_form()
        result = [0] * self.num_variables

        for i in range(self.num_variables - 1, -1, -1):
            result[i] = self.constants[i]
            for j in range(self.num_variables - 1, i, -1):
                result[i] -= result[j] * self.coefficients[i][j]

        result.reverse()
        return round(result[0]), round(result[1])

system = LinearEquationSystem()

data_points = []

running = True
measurement_taken = False

def add_data_point():
    global system
    time.sleep(0.1)
    win32clipboard.OpenClipboard()
    try:
        data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        data = data.split(" ")
        data = ((float(data[-5]) - 8) / 16, (float(data[-3]) - 8) / 16, float(data[-2]))
        data_points.append(data)

        system = LinearEquationSystem()
        for i in range(len(data_points)):
            angle = math.radians(data_points[i][2] - 90)
            system.add_equation([1, -math.tan(angle)],
                                -math.tan(angle) * data_points[i][0] + data_points[i][1])
    finally:
        win32clipboard.CloseClipboard()

def reset_measurement(_):
    global measurement_taken
    measurement_taken = False

keyboard.on_release_key("c", reset_measurement)

while running:
    if keyboard.is_pressed('q'):
        print("Quit")
        running = False

    if keyboard.is_pressed('f3'):
        if keyboard.is_pressed('c'):
            if not measurement_taken:
                add_data_point()
                solution = system.solve()
                print((solution[0] * 16 + 4, solution[1] * 16 + 4))
                measurement_taken = True
