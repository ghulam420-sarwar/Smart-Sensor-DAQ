"""
Serial Data Logger for Smart Sensor DAQ
---------------------------------------
Reads CSV frames from the ESP32, logs to a timestamped CSV file, and
plots live data with matplotlib.

Usage:
    python serial_logger.py --port COM5 --baud 115200
    python serial_logger.py --port /dev/ttyUSB0 --plot

Author: Ghulam Sarwar
"""

import argparse
import csv
import datetime as dt
import pathlib
import sys
import time

import serial  # pip install pyserial

SANITY = {
    "TEMP_BME": (-40.0, 85.0),
    "HUM":      (0.0, 100.0),
    "PRES":     (300.0, 1100.0),
    "TEMP_DS":  (-55.0, 125.0),
}


def parse_args():
    p = argparse.ArgumentParser(description="Smart Sensor DAQ logger")
    p.add_argument("--port", required=True)
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--out", type=pathlib.Path, default=pathlib.Path("logs"))
    p.add_argument("--duration", type=float, default=0.0,
                   help="Stop after N seconds (0 = run forever)")
    p.add_argument("--plot", action="store_true", help="Live matplotlib plot")
    return p.parse_args()


def check_sanity(row):
    issues = []
    for k, (lo, hi) in SANITY.items():
        try:
            v = float(row[k])
            if not (lo <= v <= hi):
                issues.append(f"{k}={v} out of [{lo},{hi}]")
        except (ValueError, KeyError):
            pass
    return issues


def main():
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = args.out / f"daq_{stamp}.csv"

    print(f"[*] Opening {args.port} @ {args.baud}")
    ser = serial.Serial(args.port, args.baud, timeout=2)
    time.sleep(2)

    header = None
    rows = []
    t_start = time.time()

    with open(log_path, "w", newline="") as f:
        writer = None
        try:
            while True:
                line = ser.readline().decode("utf-8", errors="replace").strip()
                if not line or line.startswith("#"):
                    continue

                if header is None:
                    header = line.split(",")
                    writer = csv.DictWriter(f, fieldnames=header)
                    writer.writeheader()
                    print(f"[*] Header: {header}")
                    continue

                parts = line.split(",")
                if len(parts) != len(header):
                    continue

                row = dict(zip(header, parts))
                issues = check_sanity(row)
                if issues:
                    print(f"[!] {row['TS_MS']} range warning: {issues}")

                writer.writerow(row)
                f.flush()
                rows.append(row)
                print(f"  t={row['TS_MS']:>7} "
                      f"T={row['TEMP_BME']:>6}C  H={row['HUM']:>5}%  "
                      f"P={row['PRES']:>7}hPa  Tds={row['TEMP_DS']:>6}C  "
                      f"[{row['STATUS']}]")

                if args.duration and (time.time() - t_start) >= args.duration:
                    break
        except KeyboardInterrupt:
            print("\n[*] Stopped by user")
        finally:
            ser.close()

    print(f"[*] Logged {len(rows)} rows to {log_path}")

    if args.plot and rows:
        try:
            import matplotlib.pyplot as plt
            t  = [float(r["TS_MS"])/1000.0 for r in rows]
            tB = [float(r["TEMP_BME"]) for r in rows]
            h  = [float(r["HUM"])      for r in rows]

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
            ax1.plot(t, tB, "r-", label="Temp (C)")
            ax1.set_ylabel("Temperature (°C)")
            ax1.grid(True); ax1.legend()
            ax2.plot(t, h, "b-", label="Humidity (%)")
            ax2.set_ylabel("Humidity (%)")
            ax2.set_xlabel("Time (s)")
            ax2.grid(True); ax2.legend()
            fig.suptitle("Smart Sensor DAQ")
            plt.tight_layout()
            plt.savefig(args.out / f"daq_{stamp}.png", dpi=120)
            plt.show()
        except ImportError:
            print("[!] matplotlib not installed - skipping plot")


if __name__ == "__main__":
    sys.exit(main() or 0)
