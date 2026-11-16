"""Local MQTT lab launcher and real-traffic fixtures; no Agent or LLM required."""

import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
CONTAINER = "mcp-start-mqtt"
IMAGE = "eclipse-mosquitto@sha256:860aeb5d63ce509508f6dcfb2bc8a1c1dd2bc60555b562b45ce90e52d8dabb0f"
USER = "mqtt_lab"
PASSWORD = "mqtt-lab-demo"  # Public, disposable lab credential; not a real secret.


def find_docker():
    candidates = [
        shutil.which("docker"),
        str(Path(os.getenv("LOCALAPPDATA", "")) / "Programs/DockerDesktop/resources/bin/docker.exe"),
        r"C:\Program Files\Docker\Docker\resources\bin\docker.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("Docker CLI not found. Install/start Docker Desktop first.")


DOCKER = find_docker()


def run(args, *, check=True, timeout=30, stdin=None):
    result = subprocess.run(
        [DOCKER, *args], input=stdin, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result


def compose(*args, timeout=60):
    return run(["compose", "-f", str(ROOT / "compose.yaml"), *args], timeout=timeout)


def client_args(program, *, port=1883, password=PASSWORD, client_id=None, interactive=False):
    args = ["exec", CONTAINER]
    if not interactive:
        args += ["timeout", "15" if program == "mosquitto_sub" else "8"]
    args += [program, "-h", "127.0.0.1", "-p", str(port),
            "-u", USER, "-P", password, "-V", "mqttv5", "-d"]
    if client_id:
        args += ["-i", client_id]
    return args


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_command(folder, name, args, result):
    safe_args = list(args)
    if "-P" in safe_args:
        safe_args[safe_args.index("-P") + 1] = "<redacted>"
    write_json(folder / f"{name}.json", {
        "command": ["docker", *safe_args], "exit_code": result.returncode,
        "stdout": result.stdout, "stderr": result.stderr,
    })


def broker_logs(since=None):
    args = ["logs", "--timestamps"]
    if since:
        args += ["--since", since]
    result = run([*args, CONTAINER])
    return result.stdout + result.stderr


def host_probe():
    # Full MQTT 3.1.1 CONNECT/CONNACK on the Windows-mapped port.
    # Real traffic still uses Mosquitto clients; this just checks the host route.
    def mqtt_string(value):
        raw = value.encode("utf-8")
        return len(raw).to_bytes(2, "big") + raw

    variable_header = b"\x00\x04MQTT\x04\xc2\x00\x0a"
    payload = mqtt_string("lab-host-probe") + mqtt_string(USER) + mqtt_string(PASSWORD)
    body = variable_header + payload
    if len(body) >= 128:
        raise RuntimeError("Probe packet unexpectedly large")
    with socket.create_connection(("127.0.0.1", 1883), timeout=3) as connection:
        connection.sendall(b"\x10" + bytes([len(body)]) + body)
        reply = b""
        while len(reply) < 4:
            chunk = connection.recv(4 - len(reply))
            if not chunk:
                break
            reply += chunk
        if reply != b"\x20\x02\x00\x00":
            raise RuntimeError(f"Host MQTT authentication failed: {reply.hex()}")
        connection.sendall(b"\xe0\x00")
    return {"host": "127.0.0.1", "port": 1883, "connack": "20020000", "authenticated": True}


def start():
    run(["info", "--format", "{{.ServerVersion}}"])
    password_file = ROOT / "config/passwords"
    if not password_file.exists():
        # Generate a password hash in a short-lived container; no host install.
        generated = run([
            "run", "--rm", "--network", "none", "--entrypoint", "sh", IMAGE, "-c",
            "mosquitto_passwd -b -c /tmp/lab-passwords mqtt_lab mqtt-lab-demo "
            ">/dev/null && cat /tmp/lab-passwords",
        ], timeout=60)
        if not generated.stdout.startswith(USER + ":"):
            raise RuntimeError("Password hash generation failed")
        password_file.write_text(generated.stdout, encoding="utf-8")
    compose("up", "-d", timeout=120)
    deadline = time.monotonic() + 15
    while True:
        try:
            host_probe()
            break
        except (OSError, RuntimeError):
            if time.monotonic() > deadline:
                raise RuntimeError("Broker did not become ready:\n" + broker_logs())
            time.sleep(0.5)
    print("MQTT ready: 127.0.0.1:1883 (authenticated, local only)")


def exchange(folder, *, mismatch=False):
    token = uuid4().hex[:12]
    client_id = f"lab-sub-{token}"
    sent_topic = f"lab/{token}/status"
    received_topic = f"lab/{token}/alarm" if mismatch else sent_topic
    marker = f"message-{token}"
    args = client_args("mosquitto_sub", client_id=client_id) + [
        "-t", received_topic, "-q", "1", "-C", "1", "-W", "10", "-v",
    ]
    subscriber = subprocess.Popen(
        [DOCKER, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace",
    )
    try:
        # Observe the actual SUBACK, rather than guessing with a fixed sleep.
        deadline = time.monotonic() + 7
        while f"Sending SUBACK to {client_id}" not in broker_logs():
            if subscriber.poll() is not None or time.monotonic() >= deadline:
                raise RuntimeError("Subscriber not ready; no broker SUBACK observed")
            time.sleep(0.15)
        pub_args = client_args("mosquitto_pub", client_id=f"lab-pub-{token}") + [
            "-t", sent_topic, "-m", marker, "-q", "1",
        ]
        published = run(pub_args, check=False, timeout=12)
        stdout, stderr = subscriber.communicate(timeout=15)
        received = subprocess.CompletedProcess(args, subscriber.returncode, stdout, stderr)
        save_command(folder, "publisher", pub_args, published)
        save_command(folder, "subscriber", args, received)
        write_json(folder / "traffic.json", {
            "client_network_namespace": "broker container",
            "published_topic": sent_topic, "subscribed_filter": received_topic,
            "message_marker": marker, "qos": 1, "subscription_confirmed_before_publish": True,
            "subscriber_wait_seconds": 10,
        })
        if published.returncode != 0:
            raise RuntimeError("Publisher failed; this is not the requested fixture")
        if mismatch:
            passed = received.returncode != 0 and marker not in stdout and "timed out" in (stdout + stderr).lower()
        else:
            passed = received.returncode == 0 and f"{sent_topic} {marker}" in stdout
        return passed
    finally:
        if subscriber.poll() is None:
            # The client also has its own 10-second deadline inside the container.
            try:
                subscriber.communicate(timeout=12)
            except subprocess.TimeoutExpired:
                subscriber.kill()
                subscriber.communicate()


def cases():
    probe = host_probe()
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex[:6]
    output = ROOT / "artifacts" / run_id
    evidence = output / "cases"
    evidence.mkdir(parents=True)
    checks = {}
    answers = {}
    scenarios = ["normal", "wrong_port", "bad_password", "topic_mismatch"]
    for number, scenario in enumerate(scenarios, 1):
        case_id = f"case-{number:02}"
        folder = evidence / case_id
        folder.mkdir()
        (folder / "mosquitto.conf").write_text((ROOT / "config/mosquitto.conf").read_text(encoding="utf-8"), encoding="utf-8")
        since = datetime.now(timezone.utc).isoformat()
        if scenario in ("normal", "topic_mismatch"):
            passed = exchange(folder, mismatch=scenario == "topic_mismatch")
        else:
            args = client_args("mosquitto_pub", port=1884 if scenario == "wrong_port" else 1883,
                               password="intentionally-wrong" if scenario == "bad_password" else PASSWORD,
                               client_id=f"lab-check-{uuid4().hex[:12]}") + ["-t", "lab/check", "-m", "test", "-q", "1"]
            result = run(args, check=False, timeout=12)
            save_command(folder, "publisher", args, result)
            combined = (result.stdout + result.stderr).lower()
            if scenario == "wrong_port":
                listeners = run(["exec", CONTAINER, "sh", "-c", "cat /proc/net/tcp /proc/net/tcp6"])
                (folder / "tcp_sockets.txt").write_text(listeners.stdout, encoding="utf-8")
                unused = not any(len(row.split()) > 3 and row.split()[1].endswith(":075C") and row.split()[3] == "0A" for row in listeners.stdout.splitlines())
                # This build may print 'Bad file descriptor' for a refused socket.
                # Use the actual socket table, not a particular error wording.
                passed = unused and result.returncode not in (0, 124, 137) and "error" in combined
            else:
                passed = result.returncode != 0 and ("authoriz" in combined or "username or password" in combined)
        logs = broker_logs(since)
        (folder / "broker.log").write_text(logs, encoding="utf-8")
        checks[case_id] = {"fixture": scenario, "verified": passed}
        answers[case_id] = {
            "injected_condition": scenario,
            "expected": {
                "normal": "Successful QoS1 publication and reception.",
                "wrong_port": "Client targets container port 1884; broker listens on 1883 and 1884 has no listener.",
                "bad_password": "Broker rejects the explicitly incorrect lab password.",
                "topic_mismatch": "Publisher topic and confirmed subscriber filter differ; subscriber times out.",
            }[scenario],
        }
        print(f"{case_id}: {'PASS' if passed else 'FAIL'} ({scenario})")
    # Recovery control after all injected cases; keep it outside Agent evidence.
    recovery = output / "verification/recovery"
    recovery.mkdir(parents=True)
    checks["recovery"] = {"verified": exchange(recovery)}
    write_json(output / "answer_key.json", answers)
    write_json(output / "verification.json", {"host_probe": probe, "checks": checks})
    print(f"Evidence: {evidence}")
    print("Give the diagnostic Agent only cases/; keep all answer and verification files separate.")
    if not all(value["verified"] for value in checks.values()):
        raise RuntimeError("Some fixture checks failed; inspect verification.json")
    (ROOT / "artifacts/latest.txt").write_text(run_id + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["start", "stop", "status", "cases", "pub", "sub"])
    parser.add_argument("--topic", default="lab/demo")
    parser.add_argument("--message", default="hello")
    args = parser.parse_args()
    if args.action == "start":
        start()
    elif args.action == "stop":
        print(compose("down").stdout)
    elif args.action == "status":
        print(compose("ps").stdout)
        print(json.dumps(host_probe(), indent=2))
    elif args.action == "cases":
        cases()
    else:
        program = "mosquitto_pub" if args.action == "pub" else "mosquitto_sub"
        command = client_args(program, interactive=args.action == "sub") + ["-t", args.topic, "-q", "1"]
        command += ["-m", args.message] if args.action == "pub" else ["-v"]
        if args.action == "sub":
            # A terminal lets Ctrl+C reach the interactive subscriber.
            command[1:1] = ["-it"] if sys.stdin.isatty() else ["-i"]
        subprocess.run([DOCKER, *command], check=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
