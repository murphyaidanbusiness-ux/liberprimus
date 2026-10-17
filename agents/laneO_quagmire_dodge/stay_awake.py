"""Hold the PC awake while one process runs, then let go. Changes no settings.

    python agents/laneO_quagmire_dodge/stay_awake.py PID [max_hours]

Calls SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED): the standard per-process request that video players and
downloads use. While this helper is alive, Windows does not idle-sleep or idle-hibernate (the display may still turn off,
and choosing Sleep still sleeps). It waits for process PID to exit, or for max_hours (default 12), whichever is first,
then clears the request and exits. The owner's power plan is never touched.
"""
import ctypes
import sys
import time

ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
SYNCHRONIZE, WAIT_TIMEOUT = 0x00100000, 0x102


def main():
    pid = int(sys.argv[1])
    max_hours = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
    k32 = ctypes.windll.kernel32
    handle = k32.OpenProcess(SYNCHRONIZE, False, pid)
    if not handle:
        print("process %d not found; nothing to hold" % pid)
        return
    if not k32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED):
        print("SetThreadExecutionState failed")
        return
    start = time.time()
    print("%s holding the PC awake while pid %d runs (cap %.1f h)" % (time.strftime("%H:%M:%S"), pid, max_hours), flush=True)
    try:
        while time.time() - start < max_hours * 3600:
            if k32.WaitForSingleObject(handle, 60_000) != WAIT_TIMEOUT:
                print("%s pid %d exited" % (time.strftime("%H:%M:%S"), pid), flush=True)
                break
        else:
            print("%s cap reached" % time.strftime("%H:%M:%S"), flush=True)
    finally:
        k32.SetThreadExecutionState(ES_CONTINUOUS)
        k32.CloseHandle(handle)
        print("released after %.1f h" % ((time.time() - start) / 3600), flush=True)


if __name__ == "__main__":
    main()
