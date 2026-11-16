from datetime import datetime
from functools import wraps
import os
import sqlite3
import threading
import time
import cv2
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    Response,
    send_from_directory,
    session,
    url_for,
)
from ultralytics import YOLO

app = Flask(__name__)
app.secret_key = "edge_ai_surveillance_super_secret_key"

# Ensure required directories exist
os.makedirs("recorded_events", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

DB_FILE = "surveillance.db"


# Initialize SQLite Database for both Videos and Users
def init_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS recorded_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


init_db()


# --- Authentication Decorator to Protect Routes ---
def login_required(f):

  @wraps(f)
  def decorated_function(*args, **kwargs):
    if "user_id" not in session:
      flash(
          "Please login first to access the Camera Stream and Database.",
          "error",
      )
      return redirect(url_for("login"))
    return f(*args, **kwargs)

  return decorated_function


# Load YOLOv8 model on CPU
model = YOLO("yolov8n.pt")
model.to("cpu")

# Global variables for camera stream & thread control
is_streaming = False
stream_lock = threading.Lock()
current_frame = None

TARGET_CLASSES = [0, 15, 16, 19]  # 0: person, 15: cat, 16: dog, 19: cow
FPS = 6
CLIP_DURATION = 5  # 5 seconds per recorded clip
MAX_FRAMES = FPS * CLIP_DURATION


def surveillance_worker():
  global is_streaming, current_frame
  cap = cv2.VideoCapture(0)

  if not cap.isOpened():
    print("Error: Could not open camera stream.")
    with stream_lock:
      is_streaming = False
    return

  frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
  frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480

  recording_frames_left = 0
  out = None
  frame_interval = 1.0 / FPS

  while is_streaming:
    loop_start = time.time()

    ret, frame = cap.read()
    if not ret:
      break

    # Run YOLOv8 inference filtering strictly for targets
    results = model(
        frame, device="cpu", classes=TARGET_CLASSES, conf=0.5, verbose=False
    )
    target_detected = False

    for r in results:
      if len(r.boxes) > 0:
        target_detected = True
        break

    annotated_frame = results[0].plot()

    # Event-based recording logic
    if target_detected and recording_frames_left == 0:
      timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
      # Using .webm and VP80 codec — works 100% natively in all Windows browsers without extra DLLs
      filename = f"target_event_{timestamp_str}.webm"
      filepath = os.path.join("recorded_events", filename)

      fourcc = cv2.VideoWriter_fourcc(*"VP80")
      out = cv2.VideoWriter(
          filepath, fourcc, float(FPS), (frame_width, frame_height)
      )
      recording_frames_left = MAX_FRAMES
      print(f"[EVENT] Target detected! Recording started: {filename}")

      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO recorded_videos (filename, filepath, timestamp) VALUES"
          " (?, ?, ?)",
          (filename, filepath, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
      )
      conn.commit()
      conn.close()

    if recording_frames_left > 0:
      if out is not None:
        out.write(annotated_frame)
      recording_frames_left -= 1

      cv2.putText(
          annotated_frame,
          "RECORDING EVENT...",
          (30, 40),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.8,
          (0, 0, 255),
          2,
          cv2.LINE_AA,
      )

      if recording_frames_left == 0 and out is not None:
        out.release()
        out = None
        print("[EVENT] Clip saved successfully at normal speed.")

    _, buffer = cv2.imencode(".jpg", annotated_frame)
    with stream_lock:
      current_frame = buffer.tobytes()

    elapsed = time.time() - loop_start
    sleep_time = max(0, frame_interval - elapsed)
    time.sleep(sleep_time)

  cap.release()
  if out is not None:
    out.release()
  print("Camera worker stopped.")


def generate_frames():
  global current_frame
  while is_streaming:
    with stream_lock:
      frame = current_frame
    if frame is not None:
      yield (
          b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
      )
    time.sleep(0.04)


# --- Public Flask Web Routes ---


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/about")
def about():
  return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
      cursor.execute(
          "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
          (name, email, password),
      )
      conn.commit()
      conn.close()
      flash("Registration successful! Please log in below.", "success")
      return render_template(
          "auth.html", active_tab="login", prefill_email=email
      )
    except sqlite3.IntegrityError:
      conn.close()
      flash("Email already registered! Please log in.", "error")
      return render_template(
          "auth.html", active_tab="login", prefill_email=email
      )

  return render_template("auth.html", active_tab="register")


@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    email = request.form.get("email")
    password = request.form.get("password")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name FROM users WHERE email = ? AND password = ?",
        (email, password),
    )
    user = cursor.fetchone()
    conn.close()

    if user:
      session["user_id"] = user[0]
      session["user_name"] = user[1]
      return redirect(url_for("cam_stream"))
    else:
      flash("Invalid email or password. Please try again.", "error")
      return render_template(
          "auth.html", active_tab="login", prefill_email=email
      )

  return render_template("auth.html", active_tab="login")


@app.route("/logout")
def logout():
  global is_streaming
  with stream_lock:
    is_streaming = False
  session.clear()
  flash("You have been logged out securely.", "success")
  return redirect(url_for("login"))


# --- Protected Flask Routes (Requires Login) ---


@app.route("/cam")
@login_required
def cam_stream():
  return render_template("cam_stream.html", is_streaming=is_streaming)


@app.route("/toggle_camera", methods=["POST"])
@login_required
def toggle_camera():
  global is_streaming
  with stream_lock:
    if is_streaming:
      is_streaming = False
    else:
      is_streaming = True
      threading.Thread(target=surveillance_worker, daemon=True).start()
  return redirect(url_for("cam_stream"))


@app.route("/video_feed")
@login_required
def video_feed():
  return Response(
      generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
  )


@app.route("/database")
@login_required
def database_view():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, filename, filepath, timestamp FROM recorded_videos ORDER BY"
      " id DESC"
  )
  videos = cursor.fetchall()
  conn.close()
  return render_template("database.html", videos=videos)


@app.route("/delete_video/<int:video_id>", methods=["POST"])
@login_required
def delete_video(video_id):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT filepath FROM recorded_videos WHERE id = ?", (video_id,)
  )
  row = cursor.fetchone()
  if row:
    filepath = row[0]
    if os.path.exists(filepath):
      os.remove(filepath)
    cursor.execute("DELETE FROM recorded_videos WHERE id = ?", (video_id,))
    conn.commit()
  conn.close()
  return redirect(url_for("database_view"))


@app.route("/recorded_events/<path:filename>")
@login_required
def serve_recorded_video(filename):
  return send_from_directory("recorded_events", filename)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000, debug=True)