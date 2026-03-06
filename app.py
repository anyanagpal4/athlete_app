from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///scout.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev-key-123"
db = SQLAlchemy(app)


# Database Model
class Athlete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    sport = db.Column(db.String(50))
    grad_year = db.Column(db.String(10))
    video_url = db.Column(db.String(255))
    bio = db.Column(db.Text)
    # Simple JSON-like storage for the MVP stats
    stats_json = db.Column(db.Text, default="GPA: 3.5, Vertical: 30in")


@app.route("/")
def home():
    return redirect(url_for("signup"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        new_athlete = Athlete(
            name=request.form["name"],
            sport=request.form["sport"],
            grad_year=request.form["grad_year"],
            video_url=request.form["video_url"],
            bio=request.form.get("bio", ""),
        )
        db.session.add(new_athlete)
        db.session.commit()
        return redirect(url_for("profile", athlete_id=new_athlete.id))
    return render_template("signup.html")


def _youtube_embed_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    if "watch?v=" in url:
        return url.replace("watch?v=", "embed/")
    if "youtu.be/" in url:
        # youtu.be/<id> -> youtube.com/embed/<id>
        video_id = url.split("youtu.be/", 1)[1].split("?", 1)[0].strip("/")
        return f"https://www.youtube.com/embed/{video_id}"
    return url


@app.route("/athlete/<int:athlete_id>")
def profile(athlete_id):
    athlete = Athlete.query.get_or_404(athlete_id)
    embed_url = _youtube_embed_url(athlete.video_url)
    return render_template("profile.html", athlete=athlete, embed_url=embed_url)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
