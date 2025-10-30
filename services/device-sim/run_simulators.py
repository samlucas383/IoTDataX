"""
Multi-Device Simulator Manager
Runs all microcontroller simulators simultaneously
"""
import subprocess
import sys
import os

SIMULATORS = {
    "ESP32": {
        "script": "sim_esp32.py",
        "devices": 2,
        "interval": 10,
        "description": "ESP32 with WiFi, battery, environmental sensors"
    },
    "Arduino": {
        "script": "sim_arduino.py",
        "devices": 2,
        "interval": 15,
        "description": "Arduino Nano 33 IoT with 9-axis IMU"
    },
    "Pico": {
        "script": "sim_pico.py",
        "devices": 2,
        "interval": 8,
        "description": "Raspberry Pi Pico W with GPIO and motion sensors"
    },
    "STM32": {
        "script": "sim_stm32.py",
        "devices": 1,
        "interval": 5,
        "description": "Industrial STM32 with high-precision sensors"
    },
    "Generic": {
        "script": "sim.py",
        "devices": 3,
        "interval": 5,
        "description": "Generic IoT device simulator"
    }
}

def run_simulator(name, config):
    """Run a single simulator in a subprocess"""
    env = os.environ.copy()
    env['NUM_DEVICES'] = str(config['devices'])
    env['INTERVAL'] = str(config['interval'])
    
    print(f"✓ Starting {name}: {config['description']}")
    return subprocess.Popen(
        [sys.executable, config['script']],
        env=env,
        cwd=os.path.dirname(__file__) or '.'
    )

def main():
    print("=" * 60)
    print("Multi-Device IoT Simulator Manager")
    print("=" * 60)
    
    # Show menu
    print("\nAvailable simulators:")
    for i, (name, config) in enumerate(SIMULATORS.items(), 1):
        print(f"{i}. {name}: {config['description']}")
        print(f"   ({config['devices']} devices, {config['interval']}s interval)")
    print(f"{len(SIMULATORS) + 1}. Run ALL simulators")
    print("0. Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "0":
        print("Exiting...")
        return
    
    processes = []
    
    try:
        if choice == str(len(SIMULATORS) + 1):
            # Run all simulators
            print("\nStarting all simulators...\n")
            for name, config in SIMULATORS.items():
                proc = run_simulator(name, config)
                processes.append((name, proc))
        else:
            # Run selected simulator
            try:
                idx = int(choice) - 1
                name = list(SIMULATORS.keys())[idx]
                config = SIMULATORS[name]
                print(f"\nStarting {name} simulator...\n")
                proc = run_simulator(name, config)
                processes.append((name, proc))
            except (ValueError, IndexError):
                print("Invalid selection!")
                return
        
        print("\n" + "=" * 60)
        print("Simulators running! Press Ctrl+C to stop all.")
        print("=" * 60 + "\n")
        
        # Wait for processes
        for name, proc in processes:
            proc.wait()
            
    except KeyboardInterrupt:
        print("\n\nStopping all simulators...")
        for name, proc in processes:
            proc.terminate()
            print(f"✓ Stopped {name}")
        print("\nAll simulators stopped.")

if __name__ == '__main__':
    main()
