#!/usr/bin/env python3
"""
Pre-flight check tool for BitstreamEvolution hardware experiments.

This tool verifies that all hardware components are properly connected and configured
before starting a FULLY_INTRINSIC experiment. It checks:
1. USB device detection (FPGA and Arduino)
2. Arduino firmware and serial communication
3. FPGA programmer availability
4. Configuration file validity

Usage:
    python src/tools/preflight_check.py [--config path/to/config.ini] [--fix]

Options:
    --config    Path to config file (default: data/config.ini)
    --fix       Attempt to fix issues (e.g., upload Arduino firmware)
    --quiet     Only output errors and warnings
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_status(message: str, status: str) -> None:
    """Print a status message with color coding."""
    if status == "ok":
        print(f"  {GREEN}[OK]{RESET} {message}")
    elif status == "warn":
        print(f"  {YELLOW}[WARN]{RESET} {message}")
    elif status == "fail":
        print(f"  {RED}[FAIL]{RESET} {message}")
    elif status == "info":
        print(f"  [INFO] {message}")


def check_usb_devices() -> dict:
    """Check for connected FPGA and Arduino USB devices."""
    results = {
        "fpga_found": False,
        "arduino_found": False,
        "fpga_device": None,
        "arduino_device": None,
    }

    # Check for ttyUSB devices
    tty_devices = list(Path("/dev").glob("ttyUSB*"))

    for device in tty_devices:
        try:
            # Use udevadm to get device info
            output = subprocess.run(
                ["udevadm", "info", str(device)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            info = output.stdout.lower()

            # Check for FTDI (FPGA)
            if "ftdi" in info or "0403" in info:
                results["fpga_found"] = True
                if results["fpga_device"] is None:
                    results["fpga_device"] = str(device)

            # Check for CH340 (Arduino) or similar
            if "1a86" in info or "ch340" in info or "arduino" in info:
                results["arduino_found"] = True
                results["arduino_device"] = str(device)

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return results


def check_arduino_firmware(device: str, timeout: float = 5.0) -> dict:
    """Test Arduino serial communication and firmware."""
    results = {
        "serial_ok": False,
        "firmware_ok": False,
        "startup_message": None,
        "error": None,
    }

    try:
        import serial

        ser = serial.Serial(device, 115200, timeout=2)
        time.sleep(2)  # Wait for Arduino reset

        # Check for startup message
        if ser.in_waiting:
            startup = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            results["startup_message"] = startup.strip()
            if "Began serial" in startup:
                results["serial_ok"] = True

        # Send ADC measure command ('2') and check for START response
        ser.write(b"2")
        time.sleep(0.5)

        response = ser.read(100).decode("utf-8", errors="ignore")
        ser.close()

        if "START" in response:
            results["firmware_ok"] = True
        else:
            results["error"] = f"No START signal received. Got: {response[:30]}"

    except ImportError:
        results["error"] = "pyserial not installed"
    except Exception as e:
        results["error"] = str(e)

    return results


def check_iceprog() -> dict:
    """Check if iceprog is available."""
    results = {
        "installed": False,
        "path": None,
        "error": None,
    }

    try:
        output = subprocess.run(
            ["which", "iceprog"], capture_output=True, text=True, timeout=5
        )
        if output.returncode == 0:
            results["installed"] = True
            results["path"] = output.stdout.strip()
    except Exception as e:
        results["error"] = str(e)

    return results


def check_arduino_cli() -> dict:
    """Check if arduino-cli is available."""
    results = {
        "installed": False,
        "path": None,
        "avr_core": False,
    }

    try:
        output = subprocess.run(
            ["which", "arduino-cli"], capture_output=True, text=True, timeout=5
        )
        if output.returncode == 0:
            results["installed"] = True
            results["path"] = output.stdout.strip()

            # Check for AVR core
            core_output = subprocess.run(
                ["arduino-cli", "core", "list"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if "arduino:avr" in core_output.stdout:
                results["avr_core"] = True
    except Exception:
        pass

    return results


def check_seed_file() -> dict:
    """Check if the seed hardware file exists."""
    results = {
        "exists": False,
        "path": None,
        "is_symlink": False,
    }

    seed_path = Path("data/seed-hardware.asc")
    if seed_path.exists():
        results["exists"] = True
        results["path"] = str(seed_path.resolve())
        results["is_symlink"] = seed_path.is_symlink()

    return results


def check_config(config_path: str) -> dict:
    """Check the configuration file for hardware mode settings."""
    results = {
        "exists": False,
        "simulation_mode": None,
        "usb_path": None,
        "valid_for_hardware": False,
    }

    config_file = Path(config_path)
    if not config_file.exists():
        return results

    results["exists"] = True

    try:
        import configparser

        config = configparser.ConfigParser()
        config.read(config_path)

        if "TOP-LEVEL PARAMETERS" in config:
            results["simulation_mode"] = config["TOP-LEVEL PARAMETERS"].get(
                "simulation_mode"
            )

        if "SYSTEM PARAMETERS" in config:
            results["usb_path"] = config["SYSTEM PARAMETERS"].get("usb_path")

        if results["simulation_mode"] == "FULLY_INTRINSIC":
            results["valid_for_hardware"] = True

    except Exception:
        pass

    return results


def upload_arduino_firmware(device: str) -> bool:
    """Attempt to upload Arduino firmware."""
    firmware_path = Path("data/ReadSignal/ReadSignal.ino")

    if not firmware_path.exists():
        print_status(f"Firmware not found: {firmware_path}", "fail")
        return False

    try:
        # Try standard nano first
        print_status("Uploading firmware (arduino:avr:nano)...", "info")
        result = subprocess.run(
            [
                "arduino-cli",
                "upload",
                "-b",
                "arduino:avr:nano",
                "-p",
                device,
                str(firmware_path),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print_status("Firmware uploaded successfully", "ok")
            return True

        # Try old bootloader
        print_status("Trying old bootloader variant...", "info")
        result = subprocess.run(
            [
                "arduino-cli",
                "upload",
                "-b",
                "arduino:avr:nano:cpu=atmega328old",
                "-p",
                device,
                str(firmware_path),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print_status("Firmware uploaded successfully (old bootloader)", "ok")
            return True

        print_status(f"Upload failed: {result.stderr}", "fail")
        return False

    except Exception as e:
        print_status(f"Upload error: {e}", "fail")
        return False


def run_preflight_check(config_path: str, fix: bool = False, quiet: bool = False) -> int:
    """
    Run all pre-flight checks.

    :param config_path: Path to config file
    :param fix: Whether to attempt fixes
    :param quiet: Suppress informational output
    :returns: Exit code (0 = all OK, 1 = warnings, 2 = failures)
    """
    warnings = 0
    failures = 0

    print(f"\n{BOLD}BitstreamEvolution Pre-flight Check{RESET}")
    print("=" * 40)

    # 1. Check USB devices
    print(f"\n{BOLD}1. USB Devices{RESET}")
    usb = check_usb_devices()

    if usb["fpga_found"]:
        print_status(f"FPGA found: {usb['fpga_device']}", "ok")
    else:
        print_status("FPGA (FTDI) not detected", "fail")
        failures += 1

    if usb["arduino_found"]:
        print_status(f"Arduino found: {usb['arduino_device']}", "ok")
    else:
        print_status("Arduino (CH340) not detected", "fail")
        failures += 1

    # 2. Check iceprog
    print(f"\n{BOLD}2. FPGA Programmer (iceprog){RESET}")
    iceprog = check_iceprog()

    if iceprog["installed"]:
        print_status(f"iceprog found: {iceprog['path']}", "ok")
    else:
        print_status("iceprog not installed", "fail")
        print_status("Run 'make icestorm-tools' to install", "info")
        failures += 1

    # 3. Check arduino-cli
    print(f"\n{BOLD}3. Arduino CLI{RESET}")
    arduino_cli = check_arduino_cli()

    if arduino_cli["installed"]:
        print_status(f"arduino-cli found: {arduino_cli['path']}", "ok")
        if arduino_cli["avr_core"]:
            print_status("Arduino AVR core installed", "ok")
        else:
            print_status("Arduino AVR core not installed", "warn")
            print_status("Run 'arduino-cli core install arduino:avr'", "info")
            warnings += 1
    else:
        print_status("arduino-cli not installed", "warn")
        print_status("Needed to upload Arduino firmware", "info")
        warnings += 1

    # 4. Check Arduino firmware
    print(f"\n{BOLD}4. Arduino Firmware{RESET}")
    if usb["arduino_found"]:
        firmware = check_arduino_firmware(usb["arduino_device"])

        if firmware["firmware_ok"]:
            print_status("Arduino firmware responding correctly", "ok")
        elif firmware["error"]:
            print_status(f"Firmware check failed: {firmware['error']}", "fail")
            failures += 1

            if fix and arduino_cli["installed"] and arduino_cli["avr_core"]:
                print_status("Attempting to upload firmware...", "info")
                if upload_arduino_firmware(usb["arduino_device"]):
                    # Re-check
                    time.sleep(2)
                    firmware = check_arduino_firmware(usb["arduino_device"])
                    if firmware["firmware_ok"]:
                        print_status("Firmware now working", "ok")
                        failures -= 1
        else:
            print_status("Arduino not responding with START signal", "fail")
            print_status("Firmware may need to be uploaded", "info")
            failures += 1

            if fix and arduino_cli["installed"] and upload_arduino_firmware(usb["arduino_device"]):
                time.sleep(2)
                firmware = check_arduino_firmware(usb["arduino_device"])
                if firmware["firmware_ok"]:
                    failures -= 1
    else:
        print_status("Skipped (no Arduino detected)", "warn")

    # 5. Check seed file
    print(f"\n{BOLD}5. Seed Hardware File{RESET}")
    seed = check_seed_file()

    if seed["exists"]:
        print_status(f"Seed file found: {seed['path']}", "ok")
        if seed["is_symlink"]:
            print_status("(symlink)", "info")
    else:
        print_status("data/seed-hardware.asc not found", "fail")
        print_status(
            "Create symlink: ln -s seed-hardware-whitley.asc data/seed-hardware.asc",
            "info",
        )
        failures += 1

    # 6. Check config
    print(f"\n{BOLD}6. Configuration{RESET}")
    config = check_config(config_path)

    if config["exists"]:
        print_status(f"Config file found: {config_path}", "ok")
        print_status(f"Simulation mode: {config['simulation_mode']}", "info")
        print_status(f"USB path: {config['usb_path']}", "info")

        if config["simulation_mode"] != "FULLY_INTRINSIC":
            print_status("Config not set for hardware mode", "warn")
            warnings += 1
    else:
        print_status(f"Config file not found: {config_path}", "warn")
        warnings += 1

    # Summary
    print(f"\n{BOLD}Summary{RESET}")
    print("=" * 40)

    if failures == 0 and warnings == 0:
        print(f"{GREEN}All checks passed! Ready for hardware experiments.{RESET}")
        return 0
    elif failures == 0:
        print(f"{YELLOW}{warnings} warning(s). Hardware may work but check issues above.{RESET}")
        return 1
    else:
        print(f"{RED}{failures} failure(s), {warnings} warning(s). Fix issues before running.{RESET}")
        if not fix:
            print("\nTip: Run with --fix to attempt automatic fixes")
        return 2


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-flight check for BitstreamEvolution hardware experiments"
    )
    parser.add_argument(
        "--config",
        "-c",
        default="data/config.ini",
        help="Path to config file (default: data/config.ini)",
    )
    parser.add_argument(
        "--fix",
        "-f",
        action="store_true",
        help="Attempt to fix issues (e.g., upload Arduino firmware)",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Only output errors and warnings"
    )

    args = parser.parse_args()

    exit_code = run_preflight_check(args.config, args.fix, args.quiet)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
