

# https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/rocket-weight/
import time
import tkinter as tk

class RocketSimulator:
    FUEL_WEIGHT = 0
    ROCKET_WEIGHT = 4000

    EARTH_RADIUS = 6.371e6  # meters
    EARTH_MASS = 5.972e24   # kg
    GRAVITATIONAL_CONSTANT = 6.674e-11  # Nm^2/kg^2

    def __init__(self, fuel):
        self.slow_down_height = -1
        self.altitude = 0
        self.velocity = 0
        self.fuel = fuel
        self.thrust_power = 20
        self.gravity = self.calculate_gravity()  # Initial gravity at the surface
        self.parachute = Parachute()
        self.prechute = Parachute(self.calculate_gravity() * - 1, 25)
        self.start = False

    def calculate_gravity(self):
        """Calculate gravity based on current altitude."""
        return (self.GRAVITATIONAL_CONSTANT * self.EARTH_MASS) / (self.EARTH_RADIUS + self.altitude) ** 2

    def apply_thrust(self):
        self.start = True
        while self.fuel > 0:
            if self.fuel > 0:
                self.fuel -= 1
                self.velocity += self.thrust_power
            else:
                print("Out of fuel")

    def update(self):
        if self.start:
            self.gravity = self.calculate_gravity()
            self.velocity -= self.gravity
            if self.parachute.deployed:
                self.velocity += self.parachute.SLOW_DOWN_FACTOR
                self.parachute.damage()
                self.velocity = min(-4, self.velocity)
            if self.prechute.deployed and not self.parachute.deployed:
                self.velocity += self.prechute.SLOW_DOWN_FACTOR
                self.prechute.damage()
                self.velocity = min(-4, self.velocity)
            self.altitude += self.velocity
            if self.altitude < 1:
                self.altitude = 0

    def deploy_parachute(self):
        if self.velocity <= self.parachute.MIN_VELOCITY:
            self.parachute.open()
            self.velocity += self.parachute.SLOW_DOWN_INITIAL

    def deploy_prechute(self):
        if self.velocity <= self.prechute.MIN_VELOCITY:
            self.prechute.open()
            self.velocity += self.prechute.SLOW_DOWN_INITIAL


class Parachute:
    
    MIN_VELOCITY = -100
    def __init__(self, factor = 15, initial = 75):
        self.SLOW_DOWN_FACTOR = factor
        self.SLOW_DOWN_INITIAL = initial
        self.health = 100
        self.deployed = False
    def open(self):
        self.deployed = True
    def damage(self):
        self.health -= 1
        if self.health < 20:
            self.SLOW_DOWN_FACTOR = 0

class RocketSimulatorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Rocket Simulator")

        # Fuel input
        self.fuel_label = tk.Label(master, text="Enter fuel amount:")
        self.fuel_label.pack()
        self.fuel_entry = tk.Entry(master)
        self.fuel_entry.pack()

        # Start button
        self.start_button = tk.Button(master, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack()

        # Game status labels
        self.altitude_label = tk.Label(master, text="Altitude: 0 m")
        self.altitude_label.pack()
        self.velocity_label = tk.Label(master, text="Velocity: 0 m/s")
        self.velocity_label.pack()
        self.fuel_label = tk.Label(master, text="Fuel: 0")
        self.fuel_label.pack()
        self.prechute_label = tk.Label(master, text="Prechute Health: 100%")
        self.prechute_label.pack()
        self.parachute_label = tk.Label(master, text="Parachute Health: 100%")
        self.parachute_label.pack()

        # Thrust and parachute buttons (disabled until simulation starts)
        self.thrust_button = tk.Button(master, text="Apply Thrust", command=self.apply_thrust, state="disabled")
        self.thrust_button.pack()
        self.deploy_prechute_button = tk.Button(master, text="Deploy Prechute", command=self.deploy_prechute, state="disabled")
        self.deploy_prechute_button.pack()
        self.deploy_parachute_button = tk.Button(master, text="Deploy Parachute", command=self.deploy_parachute, state="disabled")
        self.deploy_parachute_button.pack()
        

    def start_simulation(self):
        try:
            # Get fuel from entry
            fuel = int(self.fuel_entry.get())
            self.rocket = RocketSimulator(fuel=fuel)

            # Disable entry and start button
            self.fuel_entry.config(state="disabled")
            self.start_button.config(state="disabled")

            # Enable thrust and parachute buttons
            self.thrust_button.config(state="normal")
            self.deploy_prechute_button.config(state="normal")
            self.deploy_parachute_button.config(state="normal")

            # Start the game update loop every second (1000 milliseconds)
            self.update_game()

        except ValueError:
            self.show_result("Invalid fuel amount. Please enter a valid number.")

    def apply_thrust(self):
        self.rocket.apply_thrust()

    def deploy_parachute(self):
        if not self.rocket.parachute.deployed:
            self.rocket.deploy_parachute()

    def deploy_prechute(self):
        if not self.rocket.prechute.deployed:
            self.rocket.deploy_prechute()

    def update_game(self):
        # Update the rocket simulation
        self.rocket.update()

        # Update labels to show the current state
        self.altitude_label.config(text=f"Altitude: {self.rocket.altitude:.2f} m")
        self.velocity_label.config(text=f"Velocity: {self.rocket.velocity:.2f} m/s")
        self.fuel_label.config(text=f"Fuel: {self.rocket.fuel}")
        self.prechute_label.config(text=f"Prechute Health: {self.rocket.prechute.health}%")

        self.parachute_label.config(text=f"Parachute Health: {self.rocket.parachute.health}%")

        # Check landing status when altitude is effectively zero
        if self.rocket.altitude <= 0 and self.rocket.fuel == 0:
            if self.rocket.velocity < -5:
                self.show_result("Crash Landing! Game Over.")
            else:
                self.show_result("Safe Landing! Congratulations!")
        else:
            # Call the update function again after 1000 milliseconds (1 second)
            self.master.after(750, self.update_game)

    def show_result(self, result_text):
        # Display result in a new window
        result_window = tk.Toplevel(self.master)
        result_window.title("Result")
        result_label = tk.Label(result_window, text=result_text)
        result_label.pack()

        # Play again button
        play_again_button = tk.Button(result_window, text="Play Again", command=lambda: self.reset_game(result_window))
        play_again_button.pack()

        # Close button to exit the game
        close_button = tk.Button(result_window, text="Close", command=self.master.quit)
        close_button.pack()

        # Disable other buttons after game ends
        self.thrust_button.config(state="disabled")
        self.deploy_prechute_button.config(state="disabled")
        self.deploy_parachute_button.config(state="disabled")

    def reset_game(self, result_window):
        # Close the result window
        result_window.destroy()

        # Reset input fields and buttons
        self.fuel_entry.config(state="normal")
        self.fuel_entry.delete(0, tk.END)
        self.start_button.config(state="normal")

        # Reset game status labels
        self.altitude_label.config(text="Altitude: 0 m")
        self.velocity_label.config(text="Velocity: 0 m/s")
        self.fuel_label.config(text="Fuel: 0")
        self.parachute_label.config(text="Prechute Health: 100%")
        self.parachute_label.config(text="Parachute Health: 100%")

        # Re-enable buttons
        self.thrust_button.config(state="disabled")
        self.deploy_prechute_button.config(state="disabled")
        self.deploy_parachute_button.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    game = RocketSimulatorGUI(root)
    root.mainloop()
