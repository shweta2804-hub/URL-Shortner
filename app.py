from flask import Flask, render_template, request, redirect
from flask_jwt_extended import JWTManager
from config import Config
from database import init_db
from routes.auth import auth_bp
from routes.urls import urls_bp

jwt = JWTManager()


def create_app():
    """
    Application factory.

    Creates and configures the Flask application with:
      - JWT authentication
      - PostgreSQL via connection pool
      - REST API blueprints
      - Legacy HTML form routes

    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Validate critical config in production
    Config.validate()

    # Initialize JWT
    jwt.init_app(app)

    # Initialize database tables on startup
    with app.app_context():
        init_db()

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(urls_bp)

    # ===== HTML FORM-BASED ROUTES (preserved for backward compat) =====

    @app.route('/')
    def home():
        return render_template("login.html")

    @app.route('/register', methods=['GET', 'POST'])
    def register_page():
        from werkzeug.security import generate_password_hash
        from database import get_db

        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = generate_password_hash(request.form['password'])

            with get_db() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password)
                )
                cur.close()
            return redirect('/')

        return render_template('register.html')

    @app.route('/login', methods=['POST'])
    def login_page():
        from werkzeug.security import check_password_hash
        from flask_jwt_extended import create_access_token
        from database import get_db

        email = request.form['email']
        password = request.form['password']

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, username, email, password FROM users WHERE email = %s",
                (email,)
            )
            user = cur.fetchone()
            cur.close()

        if user and check_password_hash(user[3], password):
            token = create_access_token(identity=email)
            return render_template("dashboard.html", token=token)

        return "Invalid Login"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
