import time
import datetime as dt
from typing import Any

import matplotlib.pyplot as plt
import speedtest


RESULTS_COLS = [
    'download', 'upload', 'ping', 'timestamp', 'bytes_sent',
    'bytes_received'
]
SERVER_COLS = [
    'url', 'lat', 'lon', 'name', 'sponsor', 'id', 'host', 'd', 'latency'
]
SPEEDTEST_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DEFAULT_MAX_SPEED = 1000


def measure_speeds() -> dict[str, Any]:
    """Use the `speedtest` package to measure the download and upload speeds,
    using the default server settings.

    Returns
    -------
    results : dict[str, Any]
        Contains the measured download and upload speeds, as well as relevant
        associated information, like the timestamp and server location. Keys
        are contained the variables `RESULTS_COLS` and `SERVER_COLS`.
    """
    print('Connecting to best server ...')
    speed_tester = speedtest.Speedtest()

    print('Testing download speed ...')
    speed_tester.download()

    print('Testing upload speed ...')
    speed_tester.upload()

    print('Test completed.')
    results = speed_tester.results.dict()
    results = {
        **{k: results[k] for k in RESULTS_COLS},
        **{k: results['server'][k] for k in SERVER_COLS}
    }
    results['timestamp'] = dt.datetime.strptime(
        results['timestamp'], SPEEDTEST_TIMESTAMP_FORMAT
    )
    return results


def run_speed_experiment(
    frequency: int = 30, duration: int = 2, draw: bool = True,
) -> list[dict[str, Any]]:
    """Runs an experiment to measure internet speeds periodically over a given
    time interval, in order to test the variation in internet speeds.

    Parameters
    ----------
    frequency : int, optional
        How many samples should be drawn per hour, by default 30.
    duration : int, optional
        How many hours the experiment should last, by default 2.
    draw : bool, optional
        Whether or not to plot the speeds as a time-series while they're being
        measured.

    Returns
    -------
    all_results : pd.DataFrame
        Contains data for all iterations of the experiment. Columns can be
        found in the variables `RESULTS_COLS` and `SERVER_COLS`.
    """
    t_start = dt.datetime.now()
    t_stop = t_start + dt.timedelta(hours=duration)
    if draw:
        tt = []
        download_speeds = []
        upload_speeds = []
        plt.ion()
        fig, ax = plt.subplots()
        download_line, = ax.plot(tt, download_speeds, 'bo-', label='Download')
        upload_line, = ax.plot(tt, upload_speeds, 'gx-', label='Upload')
        ax.set(xlabel='Time', ylabel='Internet Speed (Mb/s)')
        ax.set_xlim(t_start, t_stop)
        ax.set_ylim(0, DEFAULT_MAX_SPEED)
        ax.legend()

    all_results = []
    i = 0
    max_iter = round(frequency * duration)
    while dt.datetime.now() < t_stop:
        i += 1
        if i >= max_iter:
            break
        t_start = dt.datetime.now()

        results = measure_speeds()
        all_results.append(results)

        if draw:
            tt.append(dt.datetime.now())
            download_speeds.append(results['download'] / 1e6)
            upload_speeds.append(results['upload'] / 1e6)

            download_line.set_xdata(tt)
            download_line.set_ydata(download_speeds)
            upload_line.set_xdata(tt)
            upload_line.set_ydata(upload_speeds)

            if (
                (results['download'] / 1e6 > DEFAULT_MAX_SPEED)
                or (results['upload'] / 1e6 > DEFAULT_MAX_SPEED)
            ):
                y_max = max(results['download'] / 1e6, results['upload'] / 1e6)
                ax.set_ylim(0, y_max)

            plt.draw()
            plt.pause(0.1)

        # Loop end maintenance
        t_end = dt.datetime.now()
        time_delta = (t_end - t_start).total_seconds()
        print(f'Time to measure iteration {i}: {time_delta:.2f} s')

        if i < max_iter - 1:
            delay = max(0, 60 * 60 / frequency - time_delta)
            print(f'Waiting {delay:.1f} s until next measurement...')
            time.sleep(delay)

    if draw:
        plt.ioff()
        plt.show()

    return all_results


if __name__ == '__main__':
    frequency = 60          # samples per hour
    duration = 10 / 60       # hours
    results = run_speed_experiment(frequency, duration)
    print(results)
